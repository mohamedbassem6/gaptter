from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm
from .models import Profile
from datetime import date

class RegisterAuthForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['password1'].label = 'Password'
        self.fields['password2'].label = 'Confirm Password'

        self.fields['username'].help_text = '35 characters or fewer.'
        self.fields['password1'].help_text = 'Must be 8+ characters long, not a commonly used password, and not entirely numeric.'
        self.fields['password2'].help_text = ''

class RegisterProfileForm(forms.ModelForm):
    profile_image = forms.ImageField(widget=forms.FileInput)
    cover_image = forms.ImageField(widget=forms.FileInput)

    class Meta:
        model = Profile
        fields = ['name', 'profile_image', 'cover_image']






class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].help_text = '35 characters or fewer.'

class ProfileUpdateForm(forms.ModelForm):
    profile_image = forms.ImageField(widget=forms.FileInput)
    cover_image = forms.ImageField(widget=forms.FileInput)
    dob = forms.DateField(widget=forms.SelectDateWidget(years=range(date.today().year - 100, date.today().year)), label='Date of Birth')
    

    class Meta:
        model = Profile
        fields = ['name', 'dob', 'profile_image', 'cover_image', 'bio']