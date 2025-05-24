from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile

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

    def clean(self):
        cleaned_data = super().clean()

        first_name = cleaned_data.get('first_name', '').strip().lower()
        last_name = cleaned_data.get('last_name', '').strip().lower()
        username = cleaned_data.get('username', '').strip().lower()
        email = cleaned_data.get('email', '').strip().lower()
        user_type = cleaned_data.get('user_type')

        # ✅ Check username format: must be firstname.lastname
        expected_username = f"{first_name}.{last_name}"
        if username and username != expected_username:
            self.add_error('username', f"Username must be in the format: firstname.lastname (e.g., {expected_username})")

        # ✅ Check email domain based on user type
        supplier_domains = [
            'gmail.com', 'yahoo.com', 'outlook.com',
            'hotmail.com', 'icloud.com', 'mail.com', 'protonmail.com'
        ]

        if email and user_type:
            domain = email.split('@')[-1]
            if user_type in ['procurement', 'manager', 'warehouse']:
                if domain != 'coredwell.com':
                    self.add_error('email', "Users with this role must use an @coredwell.com email.")
            elif user_type == 'supplier':
                if domain not in supplier_domains:
                    self.add_error('email', f"Suppliers must use a common email provider such as: {', '.join(supplier_domains)}")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name'].strip()
        user.last_name = self.cleaned_data['last_name'].strip()
        user.username = self.cleaned_data['username'].strip().lower()
        user.email = self.cleaned_data['email'].strip().lower()

        if commit:
            user.save()
            # 🔒 Create the profile after user is saved
            Profile.objects.create(user=user, user_type=self.cleaned_data['user_type'])

        return user
