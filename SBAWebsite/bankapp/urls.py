from django.urls import path

from .views import (CustomLoginView,RegisterView,HomeView,DashboardView,ProjectOverviewView,LoanPredictionView, CustomLogoutView,
                   MessageListView, MessageCreateView
                    )

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('register/', RegisterView.as_view(), name='register'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('project/<int:project_id>/', ProjectOverviewView.as_view(), name='project_overview'),
    #path('auth/login/', LoginView.as_view(), name='login'),
    #path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('loans/predict/', LoanPredictionView.as_view(), name='loan_predict'),
   # path('auth/login/', CustomLoginView.as_view(), name='login'),
    #path('auth/logout/', LogoutView.as_view(next_page='login'), name='logout'),

    # Authentication URLs
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(next_page='login'), name='logout'),

    # Role-Based Dashboards
    path('advisor/dashboard/', DashboardView.as_view(), name='advisor_dashboard'),
    path('client/dashboard/', DashboardView.as_view(), name='client_dashboard'),
     # Message URLs
    



    path('messages/', MessageListView.as_view(), name='messages_list'),
    path('messages/<int:pk>/', MessageListView.as_view(), name='message_detail'),
    path('messages/<int:pk>/send/', MessageCreateView.as_view(), name='message_create'),


        # Role-Based Messages URLs
    # Client Messages
    path('client/messages/', MessageListView.as_view(), name='client_messages_list'),
    path('client/messages/<int:pk>/', MessageListView.as_view(), name='client_message_detail'),
    path('client/messages/<int:pk>/send/', MessageCreateView.as_view(), name='client_message_create'),

    # Advisor Messages
    path('advisor/messages/', MessageListView.as_view(), name='advisor_messages_list'),
    path('advisor/messages/<int:pk>/', MessageListView.as_view(), name='advisor_message_detail'),
    path('advisor/messages/<int:pk>/send/', MessageCreateView.as_view(), name='advisor_message_create'),

]