from django.urls import path
from . import views

urlpatterns = [
    path('webhook/', views.paystack_webhook, name='paystack_webhook'),
]