from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth import login,authenticate
from .models import Profile
from django.contrib.auth.models import User

# Create your models here.
class UserForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ["first_name","last_name","username","email","password","password"]

class ProfileForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields = ['url', 'location', 'company']
