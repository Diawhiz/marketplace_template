# accounts/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('profile/', views.ProfileUpdateView.as_view(), name='profile'),
]