"""
Django views for a banking application.

This module defines views for:
- User authentication (registration, login, logout)
- Dashboard and profile management
- Messaging system
- News management
- Loan request processing and predictions
"""

# Standard Libraries
import os
import time
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

# Third-party Libraries
from dotenv import load_dotenv
import requests

# Django Core
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model, authenticate, login as auth_login
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q, Count
from django.http import JsonResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import (
    TemplateView, CreateView, FormView, ListView,
    DetailView, UpdateView, DeleteView
)

# Local imports
from .forms import RegisterForm, CustomLoginForm, MessageForm, LoanRequestForm
from .models import (
    AdvisorClientPairing, Conversation, Message, NewsArticle,
    CannedMessageCategory, CannedMessage, LoanRequest, TokenModel
)

# Get User model
User = get_user_model()

# Authentication Views
class RegisterView(FormView):
    """
    User registration view that handles:
    - User creation with role assignment
    - Advisor pairing for clients
    - Initial conversation setup
    - Automatic login after registration
    """
    template_name = "bankapp/register.html"
    form_class = RegisterForm
    success_url = '/dashboard/'

    def form_valid(self, form):
        user = form.save()

        if user.role == 'client':
            # Assign advisor and create conversation
            AdvisorClientPairing.auto_assign(user)
            pairing = AdvisorClientPairing.objects.get(client=user)
            Conversation.objects.get_or_create(client=user, advisor=pairing.advisor)

        # Authenticate and login
        authenticated_user = authenticate(
            self.request,
            email=user.email,
            password=form.cleaned_data['password1']
        )
        
        if authenticated_user:
            auth_login(self.request, authenticated_user)
            return super().form_valid(form)
        
        form.add_error(None, "Authentication failed. Please check your credentials.")
        return self.form_invalid(form)

class CustomLoginView(LoginView):
    """Custom login view using email authentication."""
    form_class = CustomLoginForm
    template_name = "bankapp/login.html"

    def form_valid(self, form):
        email = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(self.request, email=email, password=password)

        if user:
            auth_login(self.request, user)
            return super().form_valid(form)
        
        form.add_error(None, "Invalid email or password.")
        return self.form_invalid(form)

    def get_success_url(self):
        return reverse('advisor_dashboard' if self.request.user.role == 'advisor' else 'client_dashboard')

class CustomLogoutView(LogoutView):
    """Logout view with success message."""
    next_page = 'login'

    def dispatch(self, request, *args, **kwargs):
        messages.success(request, "You have successfully logged out.")
        return super().dispatch(request, *args, **kwargs)

# Website Views
class HomeView(TemplateView):
    """Landing page view."""
    template_name = "bankapp/home.html"

class ProjectOverviewView(LoginRequiredMixin, TemplateView):
    """Project overview page."""
    template_name = "bankapp/project_overview.html"

# Dashboard Views
class DashboardView(LoginRequiredMixin, TemplateView):
    """
    Role-based dashboard view that displays:
    - Latest news
    - Unread messages count
    - Loan application statistics
    - Client/advisor specific information
    """
    def get_template_names(self):
        return [
            f'bankapp/{"advisor" if self.request.user.role == "advisor" else "client"}_dashboard.html'
        ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Common context
        context['latest_news'] = NewsArticle.objects.order_by('-published_date')[:5]
        context['unread_messages_count'] = Message.objects.filter(
            receiver=user, read=False
        ).count()

        if user.role == 'client':
            # Client-specific context
            context.update({
                'total_applications': LoanRequest.objects.filter(client=user).count(),
                'approved_loans': LoanRequest.objects.filter(client=user, status='approved').count(),
                'pending_requests': LoanRequest.objects.filter(client=user, status='pending').count(),
            })
        elif user.role == 'advisor':
            # Advisor-specific context
            paired_clients = AdvisorClientPairing.objects.filter(advisor=user).values_list('client', flat=True)
            today = datetime.now().date()
            
            context.update({
                'active_clients_count': len(paired_clients),
                'pending_reviews_count': LoanRequest.objects.filter(
                    client__in=paired_clients,
                    status='pending'
                ).count(),
                'approved_today_count': LoanRequest.objects.filter(
                    client__in=paired_clients,
                    status='approved',
                    updated_at__date=today
                ).count(),
                'recent_applications': LoanRequest.objects.filter(
                    client__in=paired_clients
                ).order_by('-created_at')[:10],
            })

        return context

# Messaging Views
class MessageListView(ListView):
    """View for displaying user conversations."""
    template_name = "bankapp/messages_list.html"
    context_object_name = "conversations"
    
    def get_queryset(self):
        user = self.request.user
        
        if user.role == 'client':
            try:
                pairing = AdvisorClientPairing.objects.get(client=user)
                conversation, _ = Conversation.objects.get_or_create(
                    client=user,
                    advisor=pairing.advisor
                )
                return Conversation.objects.filter(client=user)
            except AdvisorClientPairing.DoesNotExist:
                return Conversation.objects.none()
        elif user.role == 'advisor':
            clients = AdvisorClientPairing.objects.filter(advisor=user).values_list('client', flat=True)
            return Conversation.objects.filter(advisor=user, client__in=clients)
        
        return Conversation.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_role'] = self.request.user.role
        
        conversation_id = self.kwargs.get('pk')
        if conversation_id:
            context['active_conversation'] = get_object_or_404(Conversation, id=conversation_id)
        
        return context

class MessageDetailView(LoginRequiredMixin, DetailView):
    """View for displaying individual conversations."""
    model = Conversation
    template_name = "bankapp/messages_list.html"
    context_object_name = "active_conversation"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context.update({
            'user_role': user.role,
            'conversations': Conversation.objects.filter(
                **{'client' if user.role == 'client' else 'advisor': user}
            )
        })
        return context

class MessageCreateView(CreateView):
    """View for creating new messages."""
    model = Message
    fields = ['content', 'attachment']
    template_name = 'bankapp/messages_list.html'

    def form_valid(self, form):
        conversation = get_object_or_404(Conversation, pk=self.kwargs['pk'])
        form.instance.conversation = conversation
        form.instance.sender = self.request.user
        form.instance.receiver = (
            conversation.advisor if self.request.user == conversation.client
            else conversation.client
        )

        form.save()
        return redirect(reverse(
            'client_message_detail' if self.request.user.role == 'client'
            else 'advisor_message_detail',
            kwargs={'pk': conversation.pk}
        ))

class CannedMessageListView(View):
    """View for handling canned messages for advisors."""
    def get(self, request, pk):
        if not (request.user.is_authenticated and request.user.role == 'advisor'):
            return JsonResponse({'error': 'Unauthorized'}, status=403)

        try:
            conversation = Conversation.objects.get(pk=pk, advisor=request.user)
        except Conversation.DoesNotExist:
            return JsonResponse(
                {'error': 'Conversation not found or not authorized.'},
                status=404
            )

        categories = CannedMessageCategory.objects.prefetch_related('canned_messages').all()
        data = []

        for category in categories:
            messages = category.canned_messages.all().order_by('title')
            if messages.exists():
                data.append({
                    'category': category.name,
                    'messages': [
                        {
                            'id': msg.id,
                            'title': msg.title,
                            'content': msg.content
                        } for msg in messages
                    ]
                })
        
        return JsonResponse({'canned_messages': data})

# News Views
class NewsListView(LoginRequiredMixin, ListView):
    """View for displaying news articles."""
    model = NewsArticle
    template_name = 'bankapp/news_list.html'
    context_object_name = 'news_articles'

    def get_queryset(self):
        return NewsArticle.objects.all().order_by('-published_date')

    def get_template_names(self):
        if self.request.user.role == 'advisor':
            return ['bankapp/advisor_news_list.html']
        return ['bankapp/client_news_list.html']

class NewsDetailView(LoginRequiredMixin, DetailView):
    """View for displaying individual news articles."""
    model = NewsArticle
    template_name = 'bankapp/news_detail.html'
    context_object_name = 'news_article'

class NewsCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """View for creating news articles (advisor only)."""
    model = NewsArticle
    fields = ['title', 'content', 'image']
    template_name = 'bankapp/news_form.html'
    success_url = reverse_lazy('advisor_news_list')

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        return self.request.user.role == 'advisor'

class NewsUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """View for updating news articles (advisor only)."""
    model = NewsArticle
    fields = ['title', 'content', 'image']
    template_name = 'bankapp/news_form.html'
    success_url = reverse_lazy('advisor_news_list')

    def test_func(self):
        return self.request.user.role == 'advisor'

class NewsDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """View for deleting news articles (advisor only)."""
    model = NewsArticle
    template_name = 'bankapp/news_confirm_delete.html'
    success_url = reverse_lazy('advisor_news_list')

    def test_func(self):
        return self.request.user.role == 'advisor'

# Authentication Service
class AuthService:
    """Service for handling authentication and token management."""
    def __init__(self, db):
        self.db = db
        self.token_check_interval = 86400  # 1 day
        self.token_thread = None

    def start_token_refresh_timer(self, user: User):
        """Start a background thread to refresh tokens periodically."""
        if not self.token_thread:
            self.token_thread = threading.Thread(target=self._refresh_token_periodically, args=(user,))
            self.token_thread.daemon = True
            self.token_thread.start()

    def _refresh_token_periodically(self, user: User):
        """Periodically refresh the user's token."""
        while True:
            time.sleep(self.token_check_interval)
            try:
                self.get_valid_token(user)
            except HTTPException as e:
                print(f"Token refresh error: {e.detail}")

    def activate_user_and_fetch_token(self, email: str, password: str):
        """Activate a user and get their authentication token."""
        load_dotenv()

        username = os.getenv("USERNAME_")
        email = os.getenv("EMAIL")
        password = os.getenv("DEFAULT_PASSWORD")
        is_superuser = False
        is_staff = False
        first_name = os.getenv("FIRST_NAME")
        last_name = os.getenv("LAST_NAME")
        date_joined = timezone.now()
        role = os.getenv("ROLE", "user")
        is_active = True

        try:
            with transaction.atomic():
                user, created = User.objects.get_or_create(
                    email=email,
                    defaults={
                        "username": username,
                        "first_name": first_name,
                        "last_name": last_name,
                        "password": password,
                        "is_superuser": is_superuser,
                        "is_staff": is_staff,
                        "date_joined": date_joined,
                        "is_active": is_active,
                        "role": role,
                    }
                )

        except Exception as e:
            print(f"Database Error: {e}")
            return {"error": "Database error while creating user"}

        access_token, expires_at = self._request_new_token(user.email, password)

        expires_at_datetime = timezone.now() + timedelta(seconds=expires_at)
        TokenModel.objects.update_or_create(
            user=user,
            defaults={"token": access_token, "expires_at": expires_at_datetime}
        )

        self.start_token_refresh_timer(user)
        return {"message": "Activation successful. You can now login.", "access_token": access_token}

    def _request_new_token(self, email: str, password: str):
        """Request a new token from the FastAPI service."""
        fastapi_url = settings.FASTAPI_URL + "/auth/login"
        response = requests.post(fastapi_url, data={"email": email, "password": password})

        if response.status_code != 200:
            print(f"FastAPI Authentication Failed: {response.status_code} - {response.text}")
            raise HTTPException(status_code=500, detail="Failed to retrieve FastAPI token")

        token_data = response.json()
        return token_data.get("access_token"), 86400

    def get_valid_token(self, user: User):
        """Get a valid token for the user, refreshing if necessary."""
        token_obj = TokenModel.objects.filter(user=user).first()

        if not token_obj or token_obj.expires_at < timezone.now():
            access_token, _ = self._request_new_token(user.email, user.password)
            token_obj, created = TokenModel.objects.update_or_create(
                user=user,
                defaults={"token": access_token, "expires_at": timezone.now() + timedelta(seconds=86400)}
            )

        return token_obj.token

# Loan Request Views - Client
class ClientLoanRequestCreateView(LoginRequiredMixin, View):
    """View for creating new loan requests."""
    template_name = 'bankapp/loan_request_form.html'

    def get(self, request):
        draft = LoanRequest.objects.filter(client=request.user, status='draft').first()

        if draft:
            form = LoanRequestForm(instance=draft)
        else:
            initial_data = {
                "state": "",
                "zip_code": "",
                "bank_state": "",
                "approval_fy": 2024,
                "term": 36,
                "no_emp": 0,
                "new_exist": 1,
                "create_job": 0,
                "retained_job": 0,
                "franchise_code": 0,
                "urban_rural": 1,
                "rev_line_cr": 0,
                "low_doc": 0,
                "disbursement_gross": 0.0,
                "gr_appv": 0.0,
                "approval_month": "",
                "naics_code": ""
            }
            form = LoanRequestForm(initial=initial_data)
        
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        draft = LoanRequest.objects.filter(client=request.user, status='draft').first()

        if draft:
            form = LoanRequestForm(request.POST, instance=draft)
        else:
            form = LoanRequestForm(request.POST)

        if form.is_valid():
            loan_request = form.save(commit=False)
            loan_request.client = request.user
            loan_request.status = 'draft'
            loan_request.save()

            messages.success(request, "Loan request saved as draft.")
            return redirect('client_loan_list')
        
        messages.error(request, "There was an error saving your loan request. Please check the form and try again.")
        return render(request, self.template_name, {'form': form})

class ClientLoanRequestEditView(LoginRequiredMixin, View):
    """View for editing existing loan requests."""
    template_name = 'bankapp/loan_request_form.html'

    def get(self, request, pk):
        loan_request = get_object_or_404(LoanRequest, pk=pk, client=request.user)
        form = LoanRequestForm(instance=loan_request)
        return render(request, self.template_name, {'form': form})

    def post(self, request, pk):
        loan_request = get_object_or_404(LoanRequest, pk=pk, client=request.user)
        form = LoanRequestForm(request.POST, instance=loan_request)
        
        if form.is_valid():
            form.save()
            messages.success(request, "Loan request updated successfully.")
            return redirect('client_loan_list')
        
        return render(request, self.template_name, {'form': form})

class ClientLoanRequestPredictView(LoginRequiredMixin, View):
    """View for getting loan request predictions."""
    template_name = 'bankapp/loan_prediction_result.html'
    login_url = "login"

    def post(self, request, pk):
        loan_request = get_object_or_404(LoanRequest, pk=pk, client=request.user)
        token = get_jwt_token()

        if not token:
            messages.error(request, "Failed to retrieve a valid token. Please try again later.")
            return redirect('client_loan_list')

        payload = {
            "State": loan_request.state,
            "Zip": loan_request.zip_code,
            "BankState": loan_request.bank_state,
            "ApprovalFY": int(loan_request.approval_fy),
            "Term": int(loan_request.term),
            "NoEmp": int(loan_request.no_emp),
            "NewExist": int(loan_request.new_exist),
            "CreateJob": int(loan_request.create_job),
            "RetainedJob": int(loan_request.retained_job),
            "FranchiseCode": int(loan_request.franchise_code),
            "UrbanRural": int(loan_request.urban_rural),
            "RevLineCr": int(loan_request.rev_line_cr),
            "LowDoc": int(loan_request.low_doc),
            "DisbursementGross": float(loan_request.disbursement_gross),
            "GrAppv": float(loan_request.gr_appv),
            "ApprovalMonth": int(loan_request.approval_month),
            "NAICS_CODE": loan_request.naics_code
        }

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        fastapi_url = settings.FASTAPI_URL + "/loans/predict"
        try:
            response = requests.post(fastapi_url, json=payload, headers=headers)
            response.raise_for_status()
            
            prediction = response.json().get("prediction", None)

            if prediction is not None:
                loan_request.prediction_result = 'charged off' if prediction == 1 else 'pif'
                loan_request.save()

                context = {
                    'loan_request': loan_request,
                    'prediction_result': loan_request.prediction_result
                }
                return render(request, self.template_name, context)
            
            messages.error(request, "No prediction returned from the model.")
            return redirect('client_loan_list')

        except requests.exceptions.RequestException as e:
            messages.error(request, f"API Error: {str(e)}")
            return redirect('client_loan_list')

class ClientLoanRequestSubmitView(LoginRequiredMixin, View):
    """View for submitting loan requests for review."""
    def post(self, request, pk):
        loan_request = get_object_or_404(LoanRequest, pk=pk, client=request.user)
        if loan_request.prediction_result == 'charged off':
            loan_request.status = 'rejected'
            messages.error(request, "Your loan request was rejected.")
        else:
            loan_request.status = 'pending'
            messages.success(request, "Your loan request is pending advisor review.")
        loan_request.save()
        return redirect('client_loan_list')

class ClientLoanRequestListView(LoginRequiredMixin, View):
    """View for listing all loan requests for a client."""
    template_name = 'bankapp/client_loan_list.html'

    def get(self, request):
        loan_requests = LoanRequest.objects.filter(client=request.user)
        return render(request, self.template_name, {'loan_requests': loan_requests})

# Loan Request Views - Advisor
class AdvisorLoanRequestDetailView(LoginRequiredMixin, View):
    """View for displaying loan request details to advisors."""
    template_name = 'bankapp/advisor_loan_detail.html'

    def get(self, request, pk):
        loan_request = get_object_or_404(LoanRequest, pk=pk)
        
        is_paired = AdvisorClientPairing.objects.filter(
            advisor=request.user,
            client=loan_request.client
        ).exists()

        if not is_paired:
            raise Http404("You are not authorized to view this loan request.")

        return render(request, self.template_name, {'loan_request': loan_request})

class AdvisorLoanRequestApproveView(LoginRequiredMixin, View):
    """View for approving loan requests."""
    def post(self, request, pk):
        loan_request = get_object_or_404(LoanRequest, pk=pk)

        is_paired = AdvisorClientPairing.objects.filter(
            advisor=request.user,
            client=loan_request.client
        ).exists()

        if not is_paired:
            raise Http404("You are not authorized to approve this loan request.")
        
        loan_request.status = 'approved'
        loan_request.save()
        messages.success(request, "Loan request approved.")
        return redirect('advisor_loan_list')

class AdvisorLoanRequestRejectView(LoginRequiredMixin, View):
    """View for rejecting loan requests."""
    def post(self, request, pk):
        loan_request = get_object_or_404(LoanRequest, pk=pk)

        is_paired = AdvisorClientPairing.objects.filter(
            advisor=request.user,
            client=loan_request.client
        ).exists()

        if not is_paired:
            raise Http404("You are not authorized to reject this loan request.")
        
        loan_request.status = 'rejected'
        loan_request.save()
        messages.error(request, "Loan request rejected.")
        return redirect('advisor_loan_list')

class AdvisorLoanRequestListView(LoginRequiredMixin, View):
    """View for listing all loan requests for an advisor."""
    template_name = 'bankapp/advisor_loan_list.html'

    def get(self, request):
        paired_clients = AdvisorClientPairing.objects.filter(advisor=request.user).values_list('client', flat=True)
        
        status_filter = request.GET.get('status', '')
        search_term = request.GET.get('search', '')
        
        loan_requests_query = LoanRequest.objects.filter(client__in=paired_clients)
        
        if status_filter:
            loan_requests_query = loan_requests_query.filter(status=status_filter)
        
        if search_term:
            loan_requests_query = loan_requests_query.filter(
                Q(client__first_name__icontains=search_term) | 
                Q(client__last_name__icontains=search_term)
            )
        
        pending_count = LoanRequest.objects.filter(client__in=paired_clients, status='pending').count()
        
        paginator = Paginator(loan_requests_query, 10)
        page = request.GET.get('page')
        loan_requests = paginator.get_page(page)
        
        context = {
            'loan_requests': loan_requests,
            'pending_count': pending_count,
            'status_filter': status_filter,
            'search_term': search_term,
        }
        
        return render(request, self.template_name, context)