import requests
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import TemplateView, CreateView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from .forms import RegisterForm, CustomLoginForm
from django.urls import reverse
from django.contrib.auth import login as auth_login  # Avoid conflict with the view name
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
 
 ##### Login and registration #####

 #Register
class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = "bankapp/register.html"
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        # Save the new user
        user = form.save()
        # Automatically log in the user after registration
        auth_login(self.request, user)
        return super().form_valid(form)

#Login
class CustomLoginView(LoginView):
    form_class = CustomLoginForm
    template_name = "bankapp/login.html"

    def form_valid(self, form):
        # Get the authenticated user
        user = form.get_user()

        # Explicitly log in the user
        auth_login(self.request, user)
        
        # Redirect to the appropriate dashboard
        return super().form_valid(form)

    def get_success_url(self):
        # Redirect based on user role
        if self.request.user.role == 'advisor':
            return reverse('advisor_dashboard')
        else:
            return reverse('client_dashboard')
        
#Backend for e-mail authentification
class EmailAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        try:
            # Check for email instead of username
            user = UserModel.objects.get(email=username)
        except UserModel.DoesNotExist:
            return None
        
        # Verify the password
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None

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
    def get_template_names(self):
        if self.request.user.role == 'advisor':
            return ['bankapp/advisor_dashboard.html']
        else:
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

