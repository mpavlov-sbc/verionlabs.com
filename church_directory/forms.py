from django import forms
from .models import Lead, Subscription


class LeadForm(forms.ModelForm):
    """Form for capturing marketing leads"""
    
    class Meta:
        model = Lead
        fields = ['email', 'church_name', 'contact_name', 'phone', 'message']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-input w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'your.email@church.org'
            }),
            'church_name': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'First Baptist Church'
            }),
            'contact_name': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'John Smith'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'placeholder': '(555) 123-4567'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-textarea w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'Tell us about your church and how we can help...',
                'rows': 4
            }),
        }
        labels = {
            'email': 'Email Address *',
            'church_name': 'Church Name',
            'contact_name': 'Your Name',
            'phone': 'Phone Number',
            'message': 'Message',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].required = True
        self.fields['church_name'].required = False
        self.fields['contact_name'].required = False
        self.fields['phone'].required = False
        self.fields['message'].required = False


class CheckoutForm(forms.Form):
    """Form for checkout process"""
    
    # Customer Information
    email = forms.EmailField(
        label="Email Address *",
        widget=forms.EmailInput(attrs={
            'class': 'form-input w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
            'placeholder': 'your.email@church.org'
        })
    )
    
    church_name = forms.CharField(
        label="Church Name *",
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-input w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
            'placeholder': 'First Baptist Church'
        })
    )
    
    contact_name = forms.CharField(
        label="Contact Person *",
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-input w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
            'placeholder': 'John Smith'
        })
    )
    
    phone = forms.CharField(
        label="Phone Number",
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
            'placeholder': '(555) 123-4567'
        })
    )
    
    # Terms and Conditions
    agree_terms = forms.BooleanField(
        label="I agree to the Terms of Service and Privacy Policy",
        widget=forms.CheckboxInput(attrs={
            'class': 'form-checkbox h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded'
        })
    )
    
    def clean_email(self):
        email = self.cleaned_data['email']
        # Basic email validation (Django handles most of this)
        if not email:
            raise forms.ValidationError("Email address is required.")
        return email.lower()
    
    def clean_church_name(self):
        church_name = self.cleaned_data['church_name']
        if not church_name or not church_name.strip():
            raise forms.ValidationError("Church name is required.")
        return church_name.strip()
    
    def clean_contact_name(self):
        contact_name = self.cleaned_data['contact_name']
        if not contact_name or not contact_name.strip():
            raise forms.ValidationError("Contact person name is required.")
        return contact_name.strip()


class CouponForm(forms.Form):
    """Form for applying coupon codes"""
    
    coupon_code = forms.CharField(
        label="Coupon Code",
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 uppercase',
            'placeholder': 'Enter coupon code',
            'style': 'text-transform: uppercase;'
        })
    )
    
    def clean_coupon_code(self):
        code = self.cleaned_data['coupon_code']
        if code:
            return code.strip().upper()
        return code