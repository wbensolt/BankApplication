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
 
 ##### Login and registration #####

User = get_user_model()

class RegisterView(FormView):
    template_name = "bankapp/register.html"
    form_class = RegisterForm
    success_url = '/dashboard/'  # Redirect to login after registration

    def form_valid(self, form):
        # Save the new user
        user = form.save()

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

