from django.contrib.auth.models import User
from django import forms


class UserForm(forms.ModelForm):
    username = forms.CharField(max_length = 20)
    password = forms.CharField(widget=forms.PasswordInput, max_length = 30)
    email = forms.CharField(label='Email')

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
