import requests
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import TemplateView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
 

# Home Page View
class HomeView(TemplateView):
    template_name = "bankapp/home.html"

# Dashboard View
class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "bankapp/dashboard.html"

# Project Overview View
class ProjectOverviewView(LoginRequiredMixin, TemplateView):
    template_name = "bankapp/project_overview.html"

class LoginView(View):
    template_name = "bankapp/login.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        # Get form data
        email = request.POST.get("email")
        password = request.POST.get("password")

        # Send login request to FastAPI
        payload = {"username": email, "password": password}
        response = requests.post("http://127.0.0.1:8001/auth/login", data=payload)

        if response.status_code == 200:
            # Store the JWT token in session
            request.session["access_token"] = response.json().get("token")
            messages.success(request, "Logged in successfully!")
            return redirect("loan_predict")
        else:
            messages.error(request, "Login failed. Please check your credentials.")
            return render(request, self.template_name)


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


class LogoutView(View):
    def get(self, request):
        if token := request.session.get("access_token"):
            # Send logout request to FastAPI
            headers = {"Authorization": f"Bearer {token}"}
            requests.post("http://127.0.0.1:8001/auth/logout", headers=headers)

            # Clear the session
            request.session.flush()

        messages.success(request, "Logged out successfully!")
        return redirect("login")
