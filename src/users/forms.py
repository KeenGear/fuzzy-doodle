from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.forms import fields
from .models import Profile


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        models = User
        fields = ['username', 'email', 'password']


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        models = User
        fields = ['username', 'password']


class ProfileUpdateForm(forms.ModelForm):
    
    class Meta:
        moodel = Profile
        fields = ['image']