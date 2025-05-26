from django import forms
from django.contrib.auth.models import User
from .models import Profile

class UserRegisterForm(forms.ModelForm):
    username = forms.CharField(label='Имя пользователя', max_length=150, help_text='Только буквы, цифры и символы @/./+/-/_.')
    email = forms.EmailField(label='Электронная почта')
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)
    role = forms.ChoiceField(
        label='Роль',
        choices=[('student', 'Студент'), ('teacher', 'Преподаватель'), ('admin', 'Администратор')]
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password'] 