from django.urls import path

from .views import HomeView,DashboardView,ProjectOverviewView,LoginView,LogoutView, LoanPredictionView

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('project/<int:project_id>/', ProjectOverviewView.as_view(), name='project_overview'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('loans/predict/', LoanPredictionView.as_view(), name='loan_predict'),
]