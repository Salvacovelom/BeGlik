# myapp/urls.py
from django.urls import path
from . import views
from rest_framework.authtoken import views as auth_views

urlpatterns = [
    path('login', views.LoginView.as_view()),
    path('logout', views.LogoutView.as_view()),
    path('forgot-password', views.ForgotPasswordView.as_view()),
]

