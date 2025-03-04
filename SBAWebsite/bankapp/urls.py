from django.urls import path

from .views import (CustomLoginView,RegisterView,HomeView,DashboardView,ProjectOverviewView, CustomLogoutView,
                   MessageListView, MessageCreateView, MessageDetailView, NewsListView, NewsDetailView, NewsCreateView,NewsUpdateView,NewsDeleteView,
                   CannedMessageListView, ClientLoanRequestCreateView, ClientLoanRequestEditView, ClientLoanRequestPredictView, 
    ClientLoanRequestSubmitView, ClientLoanRequestListView,
    AdvisorLoanRequestListView, AdvisorLoanRequestDetailView, 
    AdvisorLoanRequestApproveView, AdvisorLoanRequestRejectView
)
                    

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('register/', RegisterView.as_view(), name='register'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('project/<int:project_id>/', ProjectOverviewView.as_view(), name='project_overview'),
    #path('loans/predict/', LoanPredictionView.as_view(), name='loan_predict'),

    # Authentication URLs
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(next_page='login'), name='logout'),

    # Role-Based Dashboards
    path('advisor/dashboard/', DashboardView.as_view(), name='advisor_dashboard'),
    path('client/dashboard/', DashboardView.as_view(), name='client_dashboard'),
    

    # Role-Based Messages URLs

    # Client Message URLs
    path('client/messages/', MessageListView.as_view(), name='client_messages_list'),
    path('client/messages/<int:pk>/', MessageDetailView.as_view(), name='client_message_detail'),
    path('client/messages/<int:pk>/send/', MessageCreateView.as_view(), name='client_message_create'),

    # Advisor Message URLs
    path('advisor/messages/', MessageListView.as_view(), name='advisor_messages_list'),
    path('advisor/messages/<int:pk>/', MessageDetailView.as_view(), name='advisor_message_detail'),
    path('advisor/messages/<int:pk>/send/', MessageCreateView.as_view(), name='advisor_message_create'),
    path('advisor/messages/<int:pk>/canned/', CannedMessageListView.as_view(), name='advisor_canned_messages'),


#News Urls

  # News URLs
    path('news/', NewsListView.as_view(), name='news_list'),
    path('news/<int:pk>/', NewsDetailView.as_view(), name='news_detail'),


    # Client URLs
 
    path('client/news/', NewsListView.as_view(), name='client_news_list'),
    path('client/news/<int:pk>/', NewsDetailView.as_view(), name='client_news_detail'),

    # Advisor URLs
    
    path('advisor/news/', NewsListView.as_view(), name='advisor_news_list'),
    path('advisor/news/<int:pk>/', NewsDetailView.as_view(), name='advisor_news_detail'),
    path('advisor/news/create/', NewsCreateView.as_view(), name='news_create'),
    path('advisor/news/<int:pk>/edit/', NewsUpdateView.as_view(), name='news_update'),
    path('advisor/news/<int:pk>/delete/', NewsDeleteView.as_view(), name='news_delete'),

     #Client URLs
    path('client/loans/create/', ClientLoanRequestCreateView.as_view(), name='client_loan_create'),
    path('client/loans/<int:pk>/edit/', ClientLoanRequestEditView.as_view(), name='client_loan_edit'),
    path('client/loans/<int:pk>/predict/', ClientLoanRequestPredictView.as_view(), name='client_loan_predict'),
    path('client/loans/<int:pk>/submit/', ClientLoanRequestSubmitView.as_view(), name='client_loan_submit'),
    path('client/loans/', ClientLoanRequestListView.as_view(), name='client_loan_list'),

    # Advisor URLs
    path('advisor/loans/', AdvisorLoanRequestListView.as_view(), name='advisor_loan_list'),
    path('advisor/loans/<int:pk>/', AdvisorLoanRequestDetailView.as_view(), name='advisor_loan_detail'),
    path('advisor/loans/<int:pk>/approve/', AdvisorLoanRequestApproveView.as_view(), name='advisor_loan_approve'),
    path('advisor/loans/<int:pk>/reject/', AdvisorLoanRequestRejectView.as_view(), name='advisor_loan_reject'),
]