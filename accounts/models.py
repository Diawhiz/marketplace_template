from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    email = models.EmailField(unique=True)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.TextField(blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    stripe_customer_id = models.CharField(max_length=100, blank=True)  # For Stripe