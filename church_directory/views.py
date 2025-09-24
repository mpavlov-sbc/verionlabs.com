from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.conf import settings
from decimal import Decimal
import json
import uuid

from .models import PricingTier, Coupon, Subscription, Lead, WebsiteConfig
from .forms import LeadForm, CheckoutForm


def home(request):
    """Church Directory marketing homepage"""
    try:
        config = WebsiteConfig.objects.first()
    except WebsiteConfig.DoesNotExist:
        config = None
    
    # Get featured pricing tiers (max 3)
    featured_tiers = PricingTier.objects.filter(is_active=True)[:3]
    
    context = {
        'config': config,
        'featured_tiers': featured_tiers,
        'page_title': 'Church Directory - Stay Connected with Your Church Family',
    }
    
    return render(request, 'church_directory/home.html', context)


def pricing(request):
    """Pricing page with all available tiers"""
    tiers = PricingTier.objects.filter(is_active=True)
    
    try:
        config = WebsiteConfig.objects.first()
    except WebsiteConfig.DoesNotExist:
        config = None
    
    context = {
        'tiers': tiers,
        'config': config,
        'page_title': 'Pricing - Church Directory',
    }
    
    return render(request, 'church_directory/pricing.html', context)


def features(request):
    """Features page view."""
    return render(request, 'church_directory/features.html')


def about(request):
    """About page view."""
    from .models import TeamMember
    team_members = TeamMember.objects.filter(is_active=True)
    return render(request, 'church_directory/about.html', {
        'team_members': team_members
    })


def about(request):
    """About page"""
    try:
        config = WebsiteConfig.objects.first()
    except WebsiteConfig.DoesNotExist:
        config = None
    
    context = {
        'config': config,
        'page_title': 'About - Church Directory',
    }
    
    return render(request, 'church_directory/about.html', context)


def contact(request):
    """Contact page with lead capture form"""
    try:
        config = WebsiteConfig.objects.first()
    except WebsiteConfig.DoesNotExist:
        config = None
    
    if request.method == 'POST':
        form = LeadForm(request.POST)
        if form.is_valid():
            lead = form.save(commit=False)
            lead.source = 'contact_page'
            lead.save()
            messages.success(request, 'Thank you for your interest! We\'ll be in touch soon.')
            return redirect('church_directory:contact')
    else:
        form = LeadForm()
    
    context = {
        'form': form,
        'config': config,
        'page_title': 'Contact Us - Church Directory',
    }
    
    return render(request, 'church_directory/contact.html', context)


def checkout(request, tier_id):
    """Checkout page for a specific pricing tier"""
    tier = get_object_or_404(PricingTier, id=tier_id, is_active=True)
    
    # Get billing period from query params (default to monthly)
    billing_period = request.GET.get('billing', 'monthly')
    if billing_period not in ['monthly', 'annual']:
        billing_period = 'monthly'
    
    # Calculate base price
    if billing_period == 'annual' and tier.annual_price:
        base_price = tier.annual_price
    else:
        base_price = tier.monthly_price
    
    # Handle coupon application
    coupon = None
    coupon_code = request.GET.get('coupon', '').strip().upper()
    if coupon_code:
        try:
            coupon = Coupon.objects.get(code=coupon_code, is_active=True)
            is_valid, message = coupon.is_valid()
            if not is_valid or not coupon.can_apply_to_tier(tier):
                coupon = None
                if request.GET.get('coupon'):  # Only show error if coupon was actually submitted
                    messages.error(request, f'Coupon "{coupon_code}" is not valid or cannot be applied.')
        except Coupon.DoesNotExist:
            if request.GET.get('coupon'):  # Only show error if coupon was actually submitted
                messages.error(request, f'Coupon "{coupon_code}" does not exist.')
    
    # Calculate pricing
    discount_amount = Decimal('0.00')
    if coupon:
        discount_amount = coupon.calculate_discount(base_price)
    
    final_price = base_price - discount_amount
    
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # Create subscription record
            subscription = Subscription.objects.create(
                email=form.cleaned_data['email'],
                church_name=form.cleaned_data['church_name'],
                contact_name=form.cleaned_data['contact_name'],
                phone=form.cleaned_data.get('phone', ''),
                pricing_tier=tier,
                billing_period=billing_period,
                base_amount=base_price,
                discount_amount=discount_amount,
                final_amount=final_price,
                coupon_used=coupon,
                status='pending'
            )
            
            # Redirect to payment processing
            return redirect('church_directory:payment_process', subscription_id=subscription.id)
    else:
        form = CheckoutForm()
    
    context = {
        'tier': tier,
        'billing_period': billing_period,
        'base_price': base_price,
        'discount_amount': discount_amount,
        'final_price': final_price,
        'coupon': coupon,
        'coupon_code': coupon_code,
        'form': form,
        'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
        'page_title': f'Checkout - {tier.name} Plan',
    }
    
    return render(request, 'church_directory/checkout.html', context)


@require_http_methods(["POST"])
def validate_coupon(request):
    """AJAX endpoint to validate coupon codes"""
    data = json.loads(request.body)
    coupon_code = data.get('coupon_code', '').strip().upper()
    tier_id = data.get('tier_id')
    billing_period = data.get('billing_period', 'monthly')
    
    if not coupon_code:
        return JsonResponse({'valid': False, 'message': 'Please enter a coupon code.'})
    
    try:
        tier = PricingTier.objects.get(id=tier_id, is_active=True)
        coupon = Coupon.objects.get(code=coupon_code, is_active=True)
        
        is_valid, message = coupon.is_valid()
        if not is_valid:
            return JsonResponse({'valid': False, 'message': message})
        
        if not coupon.can_apply_to_tier(tier):
            return JsonResponse({'valid': False, 'message': 'This coupon cannot be applied to the selected plan.'})
        
        # Calculate pricing
        if billing_period == 'annual' and tier.annual_price:
            base_price = tier.annual_price
        else:
            base_price = tier.monthly_price
        
        if coupon.minimum_amount and base_price < coupon.minimum_amount:
            return JsonResponse({
                'valid': False, 
                'message': f'Minimum order amount of ${coupon.minimum_amount} required for this coupon.'
            })
        
        discount_amount = coupon.calculate_discount(base_price)
        final_price = base_price - discount_amount
        
        return JsonResponse({
            'valid': True,
            'message': coupon.description,
            'discount_amount': float(discount_amount),
            'final_price': float(final_price)
        })
        
    except (PricingTier.DoesNotExist, Coupon.DoesNotExist):
        return JsonResponse({'valid': False, 'message': 'Invalid coupon code.'})


def payment_process(request, subscription_id):
    """Process payment for subscription (Stripe integration stub)"""
    subscription = get_object_or_404(Subscription, id=subscription_id, status='pending')
    
    if request.method == 'POST':
        # This is a stub implementation for Stripe payment processing
        # In a real implementation, you would integrate with Stripe's API here
        
        # Simulate payment processing
        payment_method = request.POST.get('payment_method')
        
        if payment_method == 'card':
            # Simulate successful payment
            subscription.status = 'active'
            subscription.stripe_payment_intent_id = f'pi_stub_{uuid.uuid4().hex[:8]}'
            subscription.stripe_customer_id = f'cus_stub_{uuid.uuid4().hex[:8]}'
            subscription.save()
            
            # Update coupon usage if applicable
            if subscription.coupon_used:
                subscription.coupon_used.used_count += 1
                subscription.coupon_used.save()
            
            messages.success(request, 'Payment successful! Your subscription is now active.')
            return redirect('church_directory:payment_success', subscription_id=subscription.id)
        else:
            messages.error(request, 'Payment failed. Please try again.')
    
    context = {
        'subscription': subscription,
        'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
        'page_title': 'Payment - Church Directory',
    }
    
    return render(request, 'church_directory/payment_process.html', context)


def payment_success(request, subscription_id):
    """Payment success page"""
    subscription = get_object_or_404(Subscription, id=subscription_id)
    
    context = {
        'subscription': subscription,
        'page_title': 'Payment Successful - Church Directory',
    }
    
    return render(request, 'church_directory/payment_success.html', context)


def payment_cancel(request):
    """Payment cancelled page"""
    context = {
        'page_title': 'Payment Cancelled - Church Directory',
    }
    
    return render(request, 'church_directory/payment_cancel.html', context)
