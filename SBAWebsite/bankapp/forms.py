from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User
from django.contrib.auth import authenticate

#Connexion and authentification
class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'role']

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        self.fields['role'].initial = 'client'  # Default role as client
        self.fields['role'].widget = forms.HiddenInput()  # Hide role field
        
        # Consistent styling with Tailwind CSS
        for fieldname in ['username', 'email', 'password1', 'password2']:
            self.fields[fieldname].widget.attrs.update({
                'class': 'appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm'
            })

    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Check for email uniqueness
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered. Please use a different email.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        
        # Automatically assign role
        if user.is_superuser:
            user.role = 'advisor'
        else:
            user.role = 'client'
        
        if commit:
            user.save()
        return user

# Login Form Using Email
class CustomLoginForm(AuthenticationForm):
    # Change the username field to email
    username = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={
            'class': 'appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm',
            'placeholder': 'Email'
        })
    )

    def clean(self):
        email = self.cleaned_data.get('username')  # Get email from username field
        password = self.cleaned_data.get('password')

        # Use email for authentication
        if email and password:
            self.user_cache = authenticate(self.request, email=email, password=password)
            if self.user_cache is None:
                raise forms.ValidationError("Invalid email or password.")
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data