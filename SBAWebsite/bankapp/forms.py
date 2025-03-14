"""
Forms module for handling user authentication, messaging, and loan requests.

This module contains form classes for:
- User registration and authentication
- Messaging system
- Loan request processing with validation
"""

# Standard library imports
from typing import Any, Dict

# Django imports
from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.validators import RegexValidator

# Local imports
from .models import User, Message, LoanRequest

# Constants
STATE_CHOICES = [
    ('AL', 'Alabama'), ('AK', 'Alaska'), ('AZ', 'Arizona'), ('AR', 'Arkansas'),
    ('CA', 'California'), ('CO', 'Colorado'), ('CT', 'Connecticut'), ('DE', 'Delaware'),
    ('FL', 'Florida'), ('GA', 'Georgia'), ('HI', 'Hawaii'), ('ID', 'Idaho'),
    ('IL', 'Illinois'), ('IN', 'Indiana'), ('IA', 'Iowa'), ('KS', 'Kansas'),
    ('KY', 'Kentucky'), ('LA', 'Louisiana'), ('ME', 'Maine'), ('MD', 'Maryland'),
    ('MA', 'Massachusetts'), ('MI', 'Michigan'), ('MN', 'Minnesota'), ('MS', 'Mississippi'),
    ('MO', 'Missouri'), ('MT', 'Montana'), ('NE', 'Nebraska'), ('NV', 'Nevada'),
    ('NH', 'New Hampshire'), ('NJ', 'New Jersey'), ('NM', 'New Mexico'), ('NY', 'New York'),
    ('NC', 'North Carolina'), ('ND', 'North Dakota'), ('OH', 'Ohio'), ('OK', 'Oklahoma'),
    ('OR', 'Oregon'), ('PA', 'Pennsylvania'), ('RI', 'Rhode Island'), ('SC', 'South Carolina'),
    ('SD', 'South Dakota'), ('TN', 'Tennessee'), ('TX', 'Texas'), ('UT', 'Utah'),
    ('VT', 'Vermont'), ('VA', 'Virginia'), ('WA', 'Washington'), ('WV', 'West Virginia'),
    ('WI', 'Wisconsin'), ('WY', 'Wyoming')
]

NAICS_CODE_CHOICES = [
    ('11', '11 - Agriculture, forestry, fishing and hunting'),
    ('21', '21 - Mining, quarrying, and oil and gas extraction'),
    ('22', '22 - Utilities'),
    ('23', '23 - Construction'),
    ('31', '31 - Manufacturing'),
    ('32', '32 - Manufacturing'),
    ('33', '33 - Manufacturing'),
    ('42', '42 - Wholesale trade'),
    ('44', '44 - Retail trade'),
    ('45', '45 - Retail trade'),
    ('48', '48 - Transportation and warehousing'),
    ('49', '49 - Transportation and warehousing'),
    ('51', '51 - Information'),
    ('52', '52 - Finance and insurance'),
    ('53', '53 - Real estate and rental and leasing'),
    ('54', '54 - Professional, scientific, and technical services'),
    ('55', '55 - Management of companies and enterprises'),
    ('56', '56 - Administrative and support and waste management and remediation services'),
    ('61', '61 - Educational services'),
    ('62', '62 - Health care and social assistance'),
    ('71', '71 - Arts, entertainment, and recreation'),
    ('72', '72 - Accommodation and food services'),
    ('81', '81 - Other services (except public administration)'),
    ('92', '92 - Public administration'),
]

BINARY_CHOICES = [
    (1, '1 - Yes'),
    (0, '0 - No'),
]

NEW_EXIST_CHOICES = [
    (1, '1 - New Business'),
    (0, '0 - Existing Business'),
]

URBAN_RURAL_CHOICES = [
    (1, 'Urban'),
    (2, 'rural'),
    (0, 'undefined'),
]

MONTH_CHOICES = [
    (1, 'January'), (2, 'February'), (3, 'March'),
    (4, 'April'), (5, 'May'), (6, 'June'),
    (7, 'July'), (8, 'August'), (9, 'September'),
    (10, 'October'), (11, 'November'), (12, 'December'),
]

class RegisterForm(UserCreationForm):
    """
    Custom registration form extending Django's UserCreationForm.
    
    Handles user registration with automatic role assignment and email validation.
    Includes custom styling for form fields using Tailwind CSS.
    """

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
        """Validate email uniqueness."""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered. Please use a different email.")
        return email

    def save(self, commit=True):
        """Save user with automatic role assignment."""
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

class CustomLoginForm(AuthenticationForm):
    """
    Custom login form using email instead of username.
    
    Extends Django's AuthenticationForm to use email for authentication
    with custom styling using Tailwind CSS.
    """

    username = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={
            'class': 'appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm',
            'placeholder': 'Email'
        })
    )

    def clean(self):
        """Authenticate user using email instead of username."""
        email = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if email and password:
            self.user_cache = authenticate(self.request, email=email, password=password)
            if self.user_cache is None:
                raise forms.ValidationError("Invalid email or password.")
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data

class MessageForm(forms.ModelForm):
    """
    Form for handling message creation with attachments.
    
    Includes custom styling using Tailwind CSS for the message input field.
    """

    class Meta:
        model = Message
        fields = ['content', 'attachment']
        widgets = {
            'content': forms.TextInput(attrs={
                'class': 'appearance-none rounded-full border border-gray-300 px-4 py-2 w-full focus:outline-none focus:border-blue-500',
                'placeholder': 'Type a message...'
            }),
        }

class LoanRequestForm(forms.ModelForm):
    """
    Form for handling loan requests with comprehensive validation.
    
    Includes fields for:
    - Location information (state, ZIP code)
    - Business details (NAICS code, employee count)
    - Loan specifics (term, amount, type)
    - Additional classifications (urban/rural, franchise status)
    """

    state = forms.ChoiceField(
        choices=STATE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-input'}),
        help_text="Select your state"
    )
    bank_state = forms.ChoiceField(
        choices=STATE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-input'}),
        help_text="Select the bank's state"
    )
    zip_code = forms.CharField(
        max_length=5,
        validators=[RegexValidator(r'^\d{5}$', message="ZIP Code must be exactly 5 digits.")],
        widget=forms.TextInput(attrs={'class': 'form-input'}),
        help_text="5-digit ZIP Code"
    )
    naics_code = forms.ChoiceField(
        choices=NAICS_CODE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-input'}),
        help_text="Select your industry (NAICS Code)"
    )
    urban_rural = forms.ChoiceField(
        choices=URBAN_RURAL_CHOICES,
        widget=forms.Select(attrs={'class': 'form-input'}),
        help_text="Urban or Rural?"
    )
    franchise_code = forms.ChoiceField(
        choices=BINARY_CHOICES,
        widget=forms.Select(attrs={'class': 'form-input'}),
        help_text="Is this a franchise?"
    )
    rev_line_cr = forms.ChoiceField(
        choices=BINARY_CHOICES,
        widget=forms.Select(attrs={'class': 'form-input'}),
        help_text="Revolving Line of Credit?"
    )
    low_doc = forms.ChoiceField(
        choices=BINARY_CHOICES,
        widget=forms.Select(attrs={'class': 'form-input'}),
        help_text="Low Documentation?"
    )
    new_exist = forms.ChoiceField(
        choices=NEW_EXIST_CHOICES,
        widget=forms.Select(attrs={'class': 'form-input'}),
        help_text="New or Existing Business?"
    )
    approval_month = forms.ChoiceField(
        choices=MONTH_CHOICES,
        widget=forms.Select(attrs={'class': 'form-input'}),
        help_text="Select a month"
    )

    class Meta:
        model = LoanRequest
        fields = [
            'state', 'zip_code', 'bank_state', 'approval_fy', 'term',
            'no_emp', 'new_exist', 'create_job', 'retained_job',
            'franchise_code', 'urban_rural', 'rev_line_cr', 'low_doc',
            'disbursement_gross', 'gr_appv', 'approval_month', 'naics_code'
        ]

        widgets = {
            field: forms.TextInput(attrs={'class': 'form-input'})
            for field in fields if field not in ['state', 'bank_state', 'zip_code']
        }

    def clean_approval_fy(self):
        """Validate approval fiscal year."""
        approval_fy = self.cleaned_data.get('approval_fy')
        if approval_fy < 1962:
            raise forms.ValidationError("Approval Fiscal Year must be 1962 or later.")
        return approval_fy

    def clean_term(self):
        """Validate loan term."""
        term = self.cleaned_data.get('term')
        if term <= 0:
            raise forms.ValidationError("Loan Term must be longer than 0 months")
        return term
    
    def clean_create_job(self):
        """Validate job creation count."""
        create_job = self.cleaned_data.get('create_job')
        if create_job < 0:
            raise forms.ValidationError("Please enter a valid number.")
        return create_job
    
    def clean_retained_job(self):
        """Validate retained job count."""
        retained_job = self.cleaned_data.get('retained_job')
        if retained_job < 0:
            raise forms.ValidationError("Please enter a valid number.")
        return retained_job
    
    def clean_no_emp(self):
        """Validate employee count."""
        no_emp = self.cleaned_data.get('no_emp')
        if no_emp < 0:
            raise forms.ValidationError("Please enter a valid number.")
        return no_emp
    
    def clean(self):
        """Validate form-wide constraints."""
        cleaned_data = super().clean()
        disbursement_gross = cleaned_data.get('disbursement_gross')
        gr_appv = cleaned_data.get('gr_appv')

        if gr_appv and disbursement_gross and gr_appv < disbursement_gross:
            raise forms.ValidationError("Gross Approved Amount cannot be less than Disbursement Gross Amount.")
        return cleaned_data