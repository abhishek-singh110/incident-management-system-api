from django.contrib import admin
from django.urls import path
from .views import RegisterAPIView, LoginAPIView, IncidentView, RetrieveIncidentByIdView, ForgotPasswordAPIView, ResetPasswordAPIView

urlpatterns = [
    # API view
    path('api/register/', RegisterAPIView.as_view(), name='register'),
    path('api/login/', LoginAPIView.as_view(), name='login'),
    path('api/incident/', IncidentView.as_view(), name='login'),
    path('api/incidents/<int:pk>/', IncidentView.as_view(), name='incident-detail'),
    path('api/incidents/search/', RetrieveIncidentByIdView.as_view(), name='incident-search'),
    path('forgot-password/', ForgotPasswordAPIView.as_view(), name='forgot-password'),
    path('reset-password/', ResetPasswordAPIView.as_view(), name='reset_password_api'),
]

