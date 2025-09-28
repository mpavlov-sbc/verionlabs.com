from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.views.decorators.http import require_http_methods, require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.conf import settings
from django.views import View
from django.urls import reverse
from django.utils import timezone
from django.core.exceptions import ValidationError
from decimal import Decimal
import json
import uuid
import logging
import stripe

from .models import PricingTier, Coupon, Subscription, Lead, WebsiteConfig, PaymentIntent
from .forms import LeadForm, CheckoutForm, CouponForm
from .stripe_service import StripeService

logger = logging.getLogger(__name__)


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


def checkout(request):
    """Checkout page with pricing tier selection and payment form"""
    tier_id = request.GET.get('tier')
    if not tier_id:
        return redirect('church_directory:pricing')
    
    try:
        tier = get_object_or_404(PricingTier, id=tier_id, is_active=True)
    except (ValueError, PricingTier.DoesNotExist):
        messages.error(request, 'Invalid pricing tier selected.')
        return redirect('church_directory:pricing')
    
    try:
        config = WebsiteConfig.objects.first()
    except WebsiteConfig.DoesNotExist:
        config = None
    
    billing_period = request.GET.get('billing', 'monthly')
    if billing_period not in ['monthly', 'annual']:
        billing_period = 'monthly'
    
    # Calculate pricing
    if billing_period == 'annual' and tier.annual_price:
        base_amount = tier.annual_price
    else:
        base_amount = tier.monthly_price
        billing_period = 'monthly'  # Force to monthly if no annual price
    
    # Initialize forms
    checkout_form = CheckoutForm()
    coupon_form = CouponForm()
    
    # Handle coupon application
    applied_coupon = None
    discount_amount = Decimal('0.00')
    final_amount = base_amount
    
    if request.method == 'POST':
        if 'apply_coupon' in request.POST:
            coupon_form = CouponForm(request.POST)
            if coupon_form.is_valid() and coupon_form.cleaned_data['coupon_code']:
                coupon_code = coupon_form.cleaned_data['coupon_code']
                try:
                    coupon = Coupon.objects.get(code=coupon_code, is_active=True)
                    is_valid, message = coupon.is_valid()
                    
                    if is_valid and coupon.can_apply_to_tier(tier):
                        if not coupon.minimum_amount or base_amount >= coupon.minimum_amount:
                            applied_coupon = coupon
                            discount_amount = coupon.calculate_discount(base_amount)
                            final_amount = max(base_amount - discount_amount, Decimal('0.00'))
                            messages.success(request, f'Coupon "{coupon_code}" applied successfully!')
                        else:
                            messages.error(request, f'Minimum purchase amount of ${coupon.minimum_amount} required.')
                    else:
                        messages.error(request, f'Coupon "{coupon_code}" is not valid: {message}')
                        
                except Coupon.DoesNotExist:
                    messages.error(request, f'Coupon "{coupon_code}" not found.')
        
        elif 'remove_coupon' in request.POST:
            applied_coupon = None
            discount_amount = Decimal('0.00')
            final_amount = base_amount
            messages.info(request, 'Coupon removed.')
        
        elif 'submit_payment' in request.POST:
            checkout_form = CheckoutForm(request.POST)
            if checkout_form.is_valid():
                return _process_checkout(request, checkout_form, tier, billing_period, applied_coupon, base_amount, discount_amount, final_amount)
    
    context = {
        'tier': tier,
        'billing_period': billing_period,
        'base_amount': base_amount,
        'discount_amount': discount_amount,
        'final_amount': final_amount,
        'applied_coupon': applied_coupon,
        'checkout_form': checkout_form,
        'coupon_form': coupon_form,
        'config': config,
        'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
        'page_title': f'Checkout - {tier.name} Plan',
    }
    
    return render(request, 'church_directory/checkout.html', context)


def _process_checkout(request, form, tier, billing_period, coupon, base_amount, discount_amount, final_amount):
    """Process the checkout form and create subscription with checkout session"""
    try:
        email = form.cleaned_data['email']
        
        # Check if user already has an active subscription with row locking to prevent race conditions
        from django.db import transaction
        with transaction.atomic():
            existing_active_subscription = Subscription.objects.select_for_update().filter(
                email=email,
                status__in=['active', 'processing', 'pending']  # Include pending to prevent race conditions
            ).first()
            
            if existing_active_subscription:
                logger.warning(f"User {email} attempted to purchase new subscription but already has active/processing subscription {existing_active_subscription.id} (status: {existing_active_subscription.status})")
                messages.error(
                    request, 
                    'You already have an active subscription. Please cancel your existing subscription before purchasing a new one, or contact support if you need assistance.'
                )
                checkout_url = reverse('church_directory:checkout') + f'?tier={tier.id}&billing={billing_period}'
                return HttpResponseRedirect(checkout_url)
            
            # Create subscription record
            subscription = Subscription.objects.create(
                email=email,
                church_name=form.cleaned_data['church_name'],
                contact_name=form.cleaned_data['contact_name'],
                phone=form.cleaned_data.get('phone', ''),
                pricing_tier=tier,
                billing_period=billing_period,
                base_amount=base_amount,
                discount_amount=discount_amount,
                final_amount=final_amount,
                coupon_used=coupon,
                status='pending'
            )
        
            # Create Stripe customer (optional for checkout)
            stripe_customer_id = None
            try:
                stripe_customer = StripeService.create_customer(
                    email=subscription.email,
                    name=subscription.contact_name,
                    church_name=subscription.church_name,
                    phone=subscription.phone
                )
                stripe_customer_id = stripe_customer.id
                subscription.stripe_customer_id = stripe_customer_id
                subscription.save()
                
            except stripe.error.StripeError as e:
                logger.warning(f"Failed to create Stripe customer for subscription {subscription.id}: {e}")
                # Continue without customer - Stripe Checkout will create one
            
            # Create Checkout Session
            try:
                success_url = request.build_absolute_uri(
                    reverse('church_directory:payment_success', kwargs={'subscription_id': subscription.id})
                )
                cancel_url = request.build_absolute_uri(
                    reverse('church_directory:payment_cancel')
                ) + f'?subscription_id={subscription.id}'
                
                checkout_session, local_payment_intent = StripeService.create_checkout_session(
                    subscription=subscription,
                    success_url=success_url,
                    cancel_url=cancel_url,
                    customer_id=stripe_customer_id
                )
                
                subscription.stripe_payment_intent_id = checkout_session.id  # Store session ID
                subscription.status = 'processing'
                subscription.save()
                
                # Update coupon usage
                if coupon:
                    coupon.used_count += 1
                    coupon.save()
                
                # Redirect to Stripe Checkout
                return redirect(checkout_session.url)
                
            except stripe.error.StripeError as e:
                logger.error(f"Failed to create Checkout Session for subscription {subscription.id}: {e}")
                subscription.status = 'failed'
                subscription.notes = f"Failed to create Checkout Session: {str(e)}"
                subscription.save()
                
                # Revert coupon usage if it was applied
                if coupon:
                    coupon.used_count = max(0, coupon.used_count - 1)
                    coupon.save()
                
                messages.error(request, 'Payment processing failed. Please try again.')
                checkout_url = reverse('church_directory:checkout') + f'?tier={tier.id}&billing={billing_period}'
                return HttpResponseRedirect(checkout_url)
    
    except Exception as e:
        logger.error(f"Unexpected error during checkout processing: {e}")
        messages.error(request, 'An unexpected error occurred. Please try again.')
        checkout_url = reverse('church_directory:checkout') + f'?tier={tier.id}&billing={billing_period}'
        return HttpResponseRedirect(checkout_url)


# PaymentProcessView is no longer needed with Stripe Checkout
# Users are redirected directly to Stripe's hosted checkout page
# and return to payment_success or payment_cancel URLs


def apply_coupon_ajax(request):
    """AJAX endpoint for coupon validation and application"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST required'})
    
    try:
        data = json.loads(request.body)
        coupon_code = data.get('coupon_code', '').strip().upper()
        tier_id = data.get('tier_id')
        base_amount = Decimal(str(data.get('base_amount', 0)))
        
        if not coupon_code:
            return JsonResponse({'success': False, 'error': 'Coupon code required'})
        
        try:
            coupon = Coupon.objects.get(code=coupon_code, is_active=True)
            tier = PricingTier.objects.get(id=tier_id)
        except (Coupon.DoesNotExist, PricingTier.DoesNotExist):
            return JsonResponse({'success': False, 'error': 'Invalid coupon code'})
        
        # Validate coupon
        is_valid, message = coupon.is_valid()
        if not is_valid:
            return JsonResponse({'success': False, 'error': message})
        
        if not coupon.can_apply_to_tier(tier):
            return JsonResponse({'success': False, 'error': 'Coupon not applicable to this plan'})
        
        if coupon.minimum_amount and base_amount < coupon.minimum_amount:
            return JsonResponse({
                'success': False, 
                'error': f'Minimum purchase amount of ${coupon.minimum_amount} required'
            })
        
        # Calculate discount
        discount_amount = coupon.calculate_discount(base_amount)
        final_amount = max(base_amount - discount_amount, Decimal('0.00'))
        
        return JsonResponse({
            'success': True,
            'coupon': {
                'code': coupon.code,
                'description': coupon.description,
                'discount_type': coupon.discount_type,
                'discount_value': float(coupon.discount_value),
            },
            'discount_amount': float(discount_amount),
            'final_amount': float(final_amount)
        })
        
    except (json.JSONDecodeError, ValueError, KeyError) as e:
        return JsonResponse({'success': False, 'error': 'Invalid request data'})
    except Exception as e:
        logger.error(f"Error applying coupon: {e}")
        return JsonResponse({'success': False, 'error': 'An error occurred'})


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


def payment_success(request, subscription_id):
    """Payment success page"""
    try:
        subscription = get_object_or_404(Subscription, id=subscription_id)
        
        try:
            config = WebsiteConfig.objects.first()
        except WebsiteConfig.DoesNotExist:
            config = None
        
        # Create or update lead record for follow-up
        lead = Lead.objects.filter(email=subscription.email).order_by('-created_at').first()
        
        if lead:
            # Update existing lead with payment information
            lead.church_name = subscription.church_name
            lead.contact_name = subscription.contact_name
            lead.phone = subscription.phone
            lead.source = 'successful_payment'
            lead.interested_tier = subscription.pricing_tier
            lead.message = f'Successfully paid for {subscription.pricing_tier.name} plan ({subscription.billing_period}). Amount: ${subscription.final_amount}'
            lead.save()
        else:
            # Create new lead record
            Lead.objects.create(
                email=subscription.email,
                church_name=subscription.church_name,
                contact_name=subscription.contact_name,
                phone=subscription.phone,
                source='successful_payment',
                interested_tier=subscription.pricing_tier,
                message=f'Successfully paid for {subscription.pricing_tier.name} plan ({subscription.billing_period}). Amount: ${subscription.final_amount}'
            )
        
        context = {
            'subscription': subscription,
            'config': config,
            'page_title': 'Payment Successful - Welcome to Church Directory!',
        }
        
        return render(request, 'church_directory/payment_success.html', context)
        
    except Exception as e:
        logger.error(f"Error loading payment success page for subscription {subscription_id}: {e}")
        messages.error(request, 'An error occurred loading your subscription details.')
        return redirect('church_directory:home')


def payment_failed(request, subscription_id=None):
    """Payment failure page"""
    subscription = None
    if subscription_id:
        try:
            subscription = Subscription.objects.get(id=subscription_id)
        except Subscription.DoesNotExist:
            subscription = None
    
    try:
        config = WebsiteConfig.objects.first()
    except WebsiteConfig.DoesNotExist:
        config = None
    
    context = {
        'subscription': subscription,
        'config': config,
        'page_title': 'Payment Failed - Church Directory',
    }
    
    return render(request, 'church_directory/payment_failed.html', context)


class SubscriptionStatusView(View):
    """Check subscription status - for customer service and debugging"""
    
    def get(self, request):
        email = request.GET.get('email')
        subscription_id = request.GET.get('id')
        
        if not (email or subscription_id):
            return JsonResponse({'error': 'Email or subscription ID required'}, status=400)
        
        try:
            if subscription_id:
                subscription = Subscription.objects.get(id=subscription_id)
            else:
                subscription = Subscription.objects.filter(email=email).order_by('-created_at').first()
                if not subscription:
                    return JsonResponse({'error': 'Subscription not found'}, status=404)
            
            # Don't expose sensitive information
            return JsonResponse({
                'subscription_id': str(subscription.id),
                'church_name': subscription.church_name,
                'pricing_tier': subscription.pricing_tier.name,
                'billing_period': subscription.billing_period,
                'status': subscription.status,
                'amount': float(subscription.final_amount),
                'created_at': subscription.created_at.isoformat(),
                'start_date': subscription.start_date.isoformat() if subscription.start_date else None,
                'end_date': subscription.end_date.isoformat() if subscription.end_date else None,
            })
            
        except Subscription.DoesNotExist:
            return JsonResponse({'error': 'Subscription not found'}, status=404)
        except Exception as e:
            logger.error(f"Error checking subscription status: {e}")
            return JsonResponse({'error': 'An error occurred'}, status=500)


@csrf_exempt
def stripe_webhook(request):
    """Handle Stripe webhook events"""
    if request.method != 'POST':
        return HttpResponse(status=405)
    
    # Validate webhook origin for additional security
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    if not user_agent.startswith('Stripe/'):
        logger.warning(f'Invalid webhook user agent: {user_agent}')
        return HttpResponse(status=400)
    
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    if not sig_header:
        logger.warning('Stripe webhook received without signature')
        return HttpResponse(status=400)
    
    try:
        # Verify webhook signature and construct event
        event = StripeService.construct_webhook_event(payload, sig_header)
        
        logger.info(f"Received Stripe webhook event: {event['type']} - {event['id']}")
        
        # Handle the event
        success = StripeService.handle_webhook_event(event)
        
        if success:
            return HttpResponse(status=200)
        else:
            logger.error(f"Failed to process webhook event {event['id']}")
            return HttpResponse(status=500)
            
    except ValueError as e:
        logger.error(f"Invalid payload in Stripe webhook: {e}")
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Invalid signature in Stripe webhook: {e}")
        return HttpResponse(status=400)
    except Exception as e:
        logger.error(f"Unexpected error processing Stripe webhook: {e}")
        return HttpResponse(status=500)


def payment_cancel(request):
    """Payment cancelled page"""
    subscription_id = request.GET.get('subscription_id')
    subscription = None
    
    if subscription_id:
        try:
            subscription = Subscription.objects.get(id=subscription_id)
            # Mark subscription as cancelled if it was pending
            if subscription.status in ['pending', 'processing']:
                subscription.status = 'cancelled'
                subscription.notes = 'Payment cancelled by user'
                subscription.save()
                
                # Revert coupon usage
                if subscription.coupon_used:
                    subscription.coupon_used.used_count = max(0, subscription.coupon_used.used_count - 1)
                    subscription.coupon_used.save()
                    
        except Subscription.DoesNotExist:
            subscription = None
    
    try:
        config = WebsiteConfig.objects.first()
    except WebsiteConfig.DoesNotExist:
        config = None
    
    context = {
        'subscription': subscription,
        'config': config,
        'page_title': 'Payment Cancelled - Church Directory',
    }
    
    return render(request, 'church_directory/payment_cancel.html', context)


@require_http_methods(["GET"])
def subscription_status(request, subscription_id):
    """Get subscription status for AJAX requests"""
    try:
        subscription = get_object_or_404(Subscription, id=subscription_id)
        
        # Check backend integration status
        backend_status = 'not_integrated'
        backend_data = {}
        
        if subscription.backend_integration_status == 'completed':
            backend_status = 'completed'
            backend_data = {
                'organization_id': subscription.backend_organization_id,
                'tenant_slug': subscription.backend_tenant_slug,
                'login_url': f"/{subscription.backend_tenant_slug}/admin/" if subscription.backend_tenant_slug else None
            }
        elif subscription.backend_integration_status == 'failed':
            backend_status = 'failed'
        elif subscription.backend_integration_status == 'pending':
            backend_status = 'pending'
        
        return JsonResponse({
            'subscription': {
                'id': subscription.id,
                'status': subscription.status,
                'church_name': subscription.church_name,
                'contact_name': subscription.contact_name,
                'email': subscription.email,
                'plan': subscription.pricing_tier.name,
                'billing_period': subscription.billing_period,
                'amount': float(subscription.final_amount),
                'created_at': subscription.created_at.isoformat(),
                'start_date': subscription.start_date.isoformat() if subscription.start_date else None,
                'end_date': subscription.end_date.isoformat() if subscription.end_date else None,
            },
            'backend_integration': {
                'status': backend_status,
                'data': backend_data
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting subscription status: {e}")
        return JsonResponse({'error': 'Failed to get subscription status'}, status=500)


@require_http_methods(["POST"])
def cancel_subscription(request, subscription_id):
    """Cancel a subscription"""
    try:
        subscription = get_object_or_404(Subscription, id=subscription_id)
        
        if subscription.status == 'cancelled':
            return JsonResponse({'error': 'Subscription already cancelled'}, status=400)
        
        # Cancel in Stripe if subscription exists
        if subscription.stripe_subscription_id:
            try:
                cancelled_subscription = StripeService.cancel_subscription(subscription.stripe_subscription_id)
                logger.info(f"Cancelled Stripe subscription {subscription.stripe_subscription_id}")
            except Exception as e:
                logger.error(f"Error cancelling Stripe subscription {subscription.stripe_subscription_id}: {e}")
                return JsonResponse({'error': 'Failed to cancel Stripe subscription'}, status=500)
        
        # Cancel in backend if integrated
        if subscription.backend_organization_id:
            try:
                from .backend_api import BackendApiService
                backend_api = BackendApiService()
                success, response_data = backend_api.handle_subscription_cancellation(subscription)
                
                if not success:
                    logger.warning(f"Backend cancellation failed for subscription {subscription.id}: {response_data}")
                    # Don't fail the request - subscription can still be cancelled locally
                    
            except Exception as e:
                logger.error(f"Error cancelling backend organization for subscription {subscription.id}: {e}")
                # Continue with local cancellation
        
        # Update local subscription
        subscription.status = 'cancelled'
        subscription.end_date = timezone.now().date()
        subscription.save()
        
        logger.info(f"Successfully cancelled subscription {subscription.id}")
        
        return JsonResponse({
            'success': True,
            'message': 'Subscription cancelled successfully',
            'subscription': {
                'id': subscription.id,
                'status': subscription.status,
                'end_date': subscription.end_date.isoformat() if subscription.end_date else None
            }
        })
        
    except Exception as e:
        logger.error(f"Error cancelling subscription {subscription_id}: {e}")
        return JsonResponse({'error': 'Failed to cancel subscription'}, status=500)


@require_http_methods(["POST"])
def retry_backend_integration(request, subscription_id):
    """Retry backend integration for a subscription"""
    try:
        subscription = get_object_or_404(Subscription, id=subscription_id)
        
        if subscription.status != 'active':
            return JsonResponse({'error': 'Subscription must be active to retry integration'}, status=400)
        
        if subscription.backend_integration_status == 'completed':
            return JsonResponse({'error': 'Backend integration already completed'}, status=400)
        
        # Retry backend integration
        from .backend_api import BackendApiService
        backend_api = BackendApiService()
        success, response_data = backend_api.retry_organization_creation(subscription)
        
        if success:
            return JsonResponse({
                'success': True,
                'message': 'Backend integration successful',
                'organization_id': response_data.get('organization_id'),
                'tenant_slug': response_data.get('tenant_slug'),
                'login_url': f"/{response_data.get('tenant_slug')}/admin/" if response_data.get('tenant_slug') else None
            })
        else:
            return JsonResponse({
                'error': 'Backend integration failed',
                'details': response_data.get('error', 'Unknown error')
            }, status=500)
            
    except Exception as e:
        logger.error(f"Error retrying backend integration for subscription {subscription_id}: {e}")
        return JsonResponse({'error': 'Failed to retry backend integration'}, status=500)


def subscription_dashboard(request):
    """Dashboard for managing subscriptions (admin only)"""
    if not request.user.is_staff:
        return redirect('church_directory:home')
    
    # Get subscription statistics
    from django.db.models import Count, Q
    from datetime import datetime, timedelta
    
    total_subscriptions = Subscription.objects.count()
    active_subscriptions = Subscription.objects.filter(status='active').count()
    pending_subscriptions = Subscription.objects.filter(status='pending').count()
    failed_subscriptions = Subscription.objects.filter(status='failed').count()
    cancelled_subscriptions = Subscription.objects.filter(status='cancelled').count()
    
    # Recent subscriptions
    recent_subscriptions = Subscription.objects.all().order_by('-created_at')[:10]
    
    # Backend integration status
    integration_stats = Subscription.objects.filter(status='active').aggregate(
        completed=Count('id', filter=Q(backend_integration_status='completed')),
        failed=Count('id', filter=Q(backend_integration_status='failed')),
        pending=Count('id', filter=Q(backend_integration_status='pending')),
        not_set=Count('id', filter=Q(backend_integration_status__in=['', None]))
    )
    
    context = {
        'page_title': 'Subscription Dashboard',
        'stats': {
            'total': total_subscriptions,
            'active': active_subscriptions,
            'pending': pending_subscriptions,
            'failed': failed_subscriptions,
            'cancelled': cancelled_subscriptions,
        },
        'integration_stats': integration_stats,
        'recent_subscriptions': recent_subscriptions,
    }
    
    return render(request, 'church_directory/subscription_dashboard.html', context)
