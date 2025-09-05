from django.views.generic import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import UserProfile
from django.urls import reverse_lazy

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = UserProfile
    fields = ['address', 'phone_number']
    template_name = 'accounts/profile.html'
    success_url = reverse_lazy('profile')

    def get_object(self):
        return self.request.user.userprofile