from django.urls import reverse_lazy
from django.views.generic.edit import CreateView

from .forms import CustomUserCreationForm


class RegisterView(CreateView):
    template_name = "users/register.html"
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("mailing_service:main_page")


class LoginView(CreateView):
    template_name = "users/login.html"
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("mailing_service:main_page")
