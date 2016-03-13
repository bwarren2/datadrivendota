from django import forms
from django.core.validators import MinLengthValidator


class PasswordField(forms.CharField):
    validators = [MinLengthValidator]
    widget = forms.PasswordInput
    max_length = 50
    min_length = 8


class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(label='Your email', max_length=100)


class ResetPasswordForm(forms.Form):
    password = PasswordField(
        label='New Password',
    )
    password_check = PasswordField(
        label='New Password Check',
    )
