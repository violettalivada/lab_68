from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from django.conf import settings
from django import forms
from django.contrib.auth import get_user_model

from .models import AuthToken, Profile


class MyUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        fields = ['username', 'password1', 'password2',
                  'first_name', 'last_name', 'email']

    def save(self, commit=True):
        if settings.ACTIVATE_USERS_EMAIL:
            user: AbstractUser = super().save(commit=False)
            user.is_active = False
            if commit:
                user.save()
                token = self.create_token(user)
                self.send_email(user, token)
        else:
            user = super().save(commit=commit)
            Profile.objects.create(user=user)
        return user

    # def save(self, commit=True):
    #     user = super().save(commit=commit)
    #     Profile.objects.create(user=user)
    #     return user

    def create_token(self, user):
        return AuthToken.objects.create(user=user)

    def send_email(self, user, token):
        if user.email:
            subject = 'Вы создали учётную запись на сайте "Мой Блог"'
            link = settings.BASE_HOST + reverse('accounts:activate', kwargs={'token': token.token})
            message = f'''Здравствуйте, {user.username}!
Вы создали учётную запись на сайте "Мой Блог"
Активируйте её, перейдя по ссылке {link}.
Если вы считаете, что это ошибка, просто игнорируйте это письмо.'''
            html_message = f'''Здравствуйте, {user.username}!
Вы создали учётную запись на сайте "Мой Блог"
Активируйте её, перейдя по ссылке <a href="{link}">{link}</a>.
Если вы считаете, что это ошибка, просто игнорируйте это письмо.'''
            try:
                user.email_user(subject, message, html_message=html_message)
            except Exception as e:
                print(e)


class UserChangeForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ['first_name', 'last_name', 'email']
        labels = {'first_name': 'Имя', 'last_name': 'Фамилия', 'email': 'Email'}


class ProfileChangeForm(forms.ModelForm):
    class Meta:
        model = Profile
        exclude = ['user']


class PasswordChangeForm(forms.ModelForm):
    password = forms.CharField(label="Новый пароль", strip=False, widget=forms.PasswordInput)
    password_confirm = forms.CharField(label="Подтвердите пароль", widget=forms.PasswordInput, strip=False)
    old_password = forms.CharField(label="Старый пароль", strip=False, widget=forms.PasswordInput)

    def clean_password_confirm(self):
        password = self.cleaned_data.get("password")
        password_confirm = self.cleaned_data.get("password_confirm")
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError('Пароли не совпадают!')
        return password_confirm

    def clean_old_password(self):
        old_password = self.cleaned_data.get('old_password')
        if not self.instance.check_password(old_password):
            raise forms.ValidationError('Старый пароль неправильный!')
        return old_password

    def save(self, commit=True):
        user = self.instance
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

    class Meta:
        model = get_user_model()
        fields = ['password', 'password_confirm', 'old_password']
