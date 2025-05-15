from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile
from django.core.exceptions import ValidationError


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email")
    first_name = forms.CharField(required=True, label="First Name")
    last_name = forms.CharField(required=True, label="Last Name")
    user_type = forms.ChoiceField(choices=Profile.USER_TYPE_CHOICES, widget=forms.Select, label="Role")

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'user_type']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].help_text = None
        self.fields['password1'].help_text = None
        self.fields['password2'].help_text = None
        self.fields['password2'].label = "Confirm Password"

    def clean_email(self):
        email = self.cleaned_data.get('email')
        domain = email.split('@')[-1]
        
        allowed_domains = ['gmail.com', 'yahoo.com', 'outlook.com', 'icloud.com', 'mail.com', 'hotmail.com']
        if domain not in allowed_domains:
            raise ValidationError("Please use an email address with one of the following domains: @%s" % ', @'.join(allowed_domains))
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            user_profile = Profile.objects.create(user=user, user_type=self.cleaned_data['user_type'])
            user_profile.save()
        return user