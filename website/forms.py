from django import forms
from django.core.validators import EmailValidator
from .models import ContactInquiry


class ContactForm(forms.ModelForm):
    """Contact form with validation"""
    
    class Meta:
        model = ContactInquiry
        fields = ['full_name', 'email', 'subject', 'message']
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
                'placeholder': 'Your full name',
                'required': True,
            }),
            'email': forms.EmailInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
                'placeholder': 'your.email@example.com',
                'required': True,
            }),
            'subject': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
                'placeholder': 'Brief subject of your inquiry',
                'required': True,
            }),
            'message': forms.Textarea(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
                'rows': 6,
                'placeholder': 'Tell us about your project or inquiry...',
                'required': True,
            }),
        }
        labels = {
            'full_name': 'Full Name',
            'email': 'Email Address',
            'subject': 'Subject',
            'message': 'Message',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add required asterisk to labels
        for field_name, field in self.fields.items():
            if field.required:
                field.label = f"{field.label} *"
    
    def clean_full_name(self):
        """Validate full name"""
        full_name = self.cleaned_data.get('full_name')
        if full_name:
            full_name = full_name.strip()
            if len(full_name) < 2:
                raise forms.ValidationError("Please enter your full name.")
            # Basic check for at least two words (first and last name)
            if len(full_name.split()) < 2:
                raise forms.ValidationError("Please enter both your first and last name.")
        return full_name
    
    def clean_email(self):
        """Validate email address"""
        email = self.cleaned_data.get('email')
        if email:
            email = email.lower().strip()
            # Additional email validation
            validator = EmailValidator()
            try:
                validator(email)
            except forms.ValidationError:
                raise forms.ValidationError("Please enter a valid email address.")
        return email
    
    def clean_subject(self):
        """Validate subject"""
        subject = self.cleaned_data.get('subject')
        if subject:
            subject = subject.strip()
            if len(subject) < 5:
                raise forms.ValidationError("Please provide a more descriptive subject (at least 5 characters).")
            if len(subject) > 200:
                raise forms.ValidationError("Subject is too long (maximum 200 characters).")
        return subject
    
    def clean_message(self):
        """Validate message"""
        message = self.cleaned_data.get('message')
        if message:
            message = message.strip()
            if len(message) < 10:
                raise forms.ValidationError("Please provide more details in your message (at least 10 characters).")
            if len(message) > 2000:
                raise forms.ValidationError("Message is too long (maximum 2000 characters).")
        return message