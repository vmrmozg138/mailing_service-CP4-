from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from users.models import CustomUser


# Форма регистрации
class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ("email", "phone_number")


# Форма авторизации
class CustomAuthenticationForm(AuthenticationForm):
    pass
