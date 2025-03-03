"""Формы для приложения users."""
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

# from .models import CustomUser


# Получаем модель пользователя
User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    # Наследуем класс Meta от соответствующего класса родительской формы.
    # Так этот класс будет не перезаписан, а расширен.
    class Meta(UserCreationForm.Meta):
        model = User
        #fields = UserCreationForm.Meta.fields + ('username', 'bio',)
        fields = ('username', 'bio',)
