from django import forms
from django.contrib.auth import get_user_model

class CustomUserChangeForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ['username', 'email']  # Adjust fields based on your User model