import requests
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import TemplateView, CreateView, FormView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from .forms import RegisterForm, CustomLoginForm
from django.urls import reverse
from django.contrib.auth import login as auth_login  # Avoid conflict with the view name
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate
from .models import AdvisorClientPairing, Conversation

 ##### Login and registration #####

User = get_user_model()

class RegisterView(FormView):
    template_name = "bankapp/register.html"
    form_class = RegisterForm
    success_url = '/dashboard/'  # Redirect to dashboard after registration

    def form_valid(self, form):
        # Save the new user
        user = form.save()

        # Automatically assign an advisor if the user is a client
        if user.role == 'client':
            AdvisorClientPairing.auto_assign(user)
            # Fetch the paired advisor
            pairing = AdvisorClientPairing.objects.get(client=user)
            advisor = pairing.advisor

            # Create a conversation between the client and the assigned advisor
            Conversation.objects.get_or_create(client=user, advisor=advisor)

        # Authenticate the user using email and password
        authenticated_user = authenticate(self.request, email=user.email, password=form.cleaned_data['password1'])
        
        # Check if the user is authenticated
        if authenticated_user:
            # Log the user in using ModelBackend
            auth_login(self.request, authenticated_user)
            return super().form_valid(form)
        else:
            # If authentication failed
            form.add_error(None, "Authentication failed. Please check your credentials.")
            return self.form_invalid(form)


#Login
class CustomLoginView(LoginView):
    form_class = CustomLoginForm
    template_name = "bankapp/login.html"

    def form_valid(self, form):
        # Get the email and password from the form
        email = form.cleaned_data.get('username')  # Using username field for email
        password = form.cleaned_data.get('password')

        # Explicitly authenticate using email
        user = authenticate(self.request, email=email, password=password)

        # Check if the user is authenticated
        if user is not None:
            auth_login(self.request, user)
            return super().form_valid(form)
        else:
            form.add_error(None, "Invalid email or password.")
            return self.form_invalid(form)

    def get_success_url(self):
        # Redirect based on user role
        if self.request.user.role == 'advisor':
            return reverse('advisor_dashboard')
        else:
            return reverse('client_dashboard')



#Logout message
class CustomLogoutView(LogoutView):
    next_page = 'login'

    def dispatch(self, request, *args, **kwargs):
        # Add logout success message
        messages.success(request, "You have successfully logged out.")
        return super().dispatch(request, *args, **kwargs)
        
  ##### Website Views #####      

# Home Page View
class HomeView(TemplateView):
    template_name = "bankapp/home.html"


##### Profile Views #####

class DashboardView(LoginRequiredMixin, TemplateView):
    """
    Role-Based Dashboard View
    - Redirects to advisor_dashboard.html if the user is an advisor.
    - Redirects to client_dashboard.html if the user is a client.
    """
    def get_template_names(self):
        if self.request.user.role == 'advisor':
            return ['bankapp/advisor_dashboard.html']
        elif self.request.user.role == 'client':
            return ['bankapp/client_dashboard.html']
        else:
            # Default to client dashboard if role is undefined
            return ['bankapp/client_dashboard.html']

# Project Overview View
class ProjectOverviewView(LoginRequiredMixin, TemplateView):
    template_name = "bankapp/project_overview.html"

##### Predictions View #####

class LoanPredictionView(View):
    template_name = "bankapp/loan_predict.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        # Get token from session
        token = request.session.get("access_token")
        headers = {"Authorization": f"Bearer {token}"}

        # Get form data
        payload = {
            "State": request.POST.get("state"),
            "Zip": request.POST.get("zip"),
            "BankState": request.POST.get("bankstate"),
            "ApprovalFY": int(request.POST.get("approvalfy")),
            "Term": int(request.POST.get("term")),
            "NoEmp": int(request.POST.get("noemp")),
            "NewExist": int(request.POST.get("newexist")),
            "CreateJob": int(request.POST.get("createjob")),
            "RetainedJob": int(request.POST.get("retainedjob")),
            "FranchiseCode": int(request.POST.get("franchisecode")),
            "UrbanRural": int(request.POST.get("urbanrural")),
            "RevLineCr": int(request.POST.get("revlinecr")),
            "LowDoc": int(request.POST.get("lowdoc")),
            "DisbursementGross": float(request.POST.get("disbursementgross")),
            "GrAppv": float(request.POST.get("grappv")),
            "ApprovalMonth": request.POST.get("approvalmonth"),
            "NAICS_CODE": request.POST.get("naics_code"),
        }

        # Send request to FastAPI
        response = requests.post(
            "http://127.0.0.1:8001/loans/predict", json=payload, headers=headers
        )

        if response.status_code == 200:
            prediction = response.json()
            return render(request, self.template_name, {"prediction": prediction})
        else:
            messages.error(request, "Prediction failed. Please check the input data.")
            return render(request, self.template_name)

########################################### Messages ############################################################
from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, redirect
from .models import Conversation, Message
from django.urls import reverse

User = get_user_model()

class MessageListView(ListView):
    template_name = "bankapp/messages_list.html"
    context_object_name = "conversations"
    
    def get_queryset(self):
        user = self.request.user
        
        # If the user is a client, get their assigned advisor and conversations
        if user.role == 'client':
            try:
                pairing = AdvisorClientPairing.objects.get(client=user)
                advisor = pairing.advisor
                
                # Ensure a conversation exists between the client and advisor
                conversation, created = Conversation.objects.get_or_create(client=user, advisor=advisor)
                
                return Conversation.objects.filter(client=user)
            except AdvisorClientPairing.DoesNotExist:
                return Conversation.objects.none()

        # If the user is an advisor, get all paired clients and their conversations
        elif user.role == 'advisor':
            # Get all clients paired with this advisor
            clients = AdvisorClientPairing.objects.filter(advisor=user).values_list('client', flat=True)
            return Conversation.objects.filter(advisor=user, client__in=clients)
        
        return Conversation.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_role'] = self.request.user.role
        
        # Get the active conversation if it exists
        conversation_id = self.kwargs.get('pk')
        if conversation_id:
            context['active_conversation'] = get_object_or_404(Conversation, id=conversation_id)
        else:
            context['active_conversation'] = None
        
        return context

class MessageDetailView(DetailView):
    model = Conversation
    template_name = "bankapp/messages_list.html"
    context_object_name = "active_conversation"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_role'] = self.request.user.role
        
        # Fetch conversations for the sidebar
        user = self.request.user
        if user.role == 'client':
            context['conversations'] = Conversation.objects.filter(client=user)
        elif user.role == 'advisor':
            context['conversations'] = Conversation.objects.filter(advisor=user)
        else:
            context['conversations'] = Conversation.objects.none()
        
        return context

class MessageCreateView(CreateView):
    model = Message
    fields = ['content']

    def form_valid(self, form):
        conversation = get_object_or_404(Conversation, pk=self.kwargs['pk'])
        form.instance.conversation = conversation
        form.instance.sender = self.request.user
        form.save()
        return redirect(reverse('message_detail', kwargs={'pk': conversation.pk}))
