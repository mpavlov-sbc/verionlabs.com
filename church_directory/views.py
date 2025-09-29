from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.views.decorators.http import require_http_methods, require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from django.core.exceptions import ValidationError
from decimal import Decimal
import json
import uuid
import logging
import stripe
import requests

from .models import PricingTier, Coupon, Subscription, Lead, WebsiteConfig, PaymentIntent
from .forms import LeadForm, CheckoutForm, CouponForm
from .stripe_service import StripeService
from .backend_api import BackendApiService

logger = logging.getLogger(__name__)


def subscription_auth_required(view_func):
    """
    Decorator that ensures the user is authenticated via subscription session.
    Supports both web session auth and mobile token auth.
    """
    def wrapper(request, *args, **kwargs):
        # Check for existing session authentication
        user_session = request.session.get('subscription_user')
        if user_session:
            # Verify session is still valid (not expired)
            try:
                auth_time = timezone.datetime.fromisoformat(user_session.get('authenticated_at', ''))
                if timezone.now() - auth_time < timezone.timedelta(hours=24):  # 24 hour session
                    return view_func(request, *args, **kwargs)
            except (ValueError, TypeError):
                pass
            # Session expired, clear it
            del request.session['subscription_user']
        
        # Check for mobile auth token in request
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header[7:]  # Remove 'Bearer ' prefix
            
            # Validate mobile auth token
            from .models import MobileAuthToken
            try:
                auth_token = MobileAuthToken.objects.get(token=token)
                if auth_token.is_valid():
                    # Create temporary session data for this request
                    backend_service = BackendApiService()
                    auth_result = backend_service.verify_mobile_session(
                        auth_token.user_id,
                        auth_token.organization_schema
                    )
                    
                    if auth_result['success']:
                        # Set temporary user session for this request
                        request.session['subscription_user'] = {
                            'email': auth_result.get('email'),
                            'user_id': auth_result.get('user_id'),
                            'organization_schema': auth_token.organization_schema,
                            'organization_name': auth_token.organization_name,
                            'authenticated_at': timezone.now().isoformat(),
                        }
                        return view_func(request, *args, **kwargs)
            except MobileAuthToken.DoesNotExist:
                pass
        
        # No valid authentication found
        if request.headers.get('Accept') == 'application/json' or request.path.startswith('/api/'):
            return JsonResponse({'error': 'Authentication required'}, status=401)
        else:
            return redirect('church_directory:subscription_login')
    
    return wrapper


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


@require_http_methods(["POST"])
@subscription_auth_required
def cancel_subscription(request, subscription_id):
    """Cancel a subscription with comprehensive error handling"""
    try:
        subscription = get_object_or_404(Subscription, id=subscription_id)
        
        # Verify user owns this subscription
        user_session = request.session.get('subscription_user')
        if not user_session or subscription.backend_tenant_slug != user_session.get('organization_schema'):
            return JsonResponse({'error': 'Unauthorized access to subscription'}, status=403)
        
        if subscription.status == 'cancelled':
            return JsonResponse({'error': 'Subscription already cancelled'}, status=400)
        
        logger.info(f"Starting cancellation process for subscription {subscription.id} (Church: {subscription.church_name})")
        
        cancellation_errors = []
        
        # Cancel in Stripe if subscription exists
        if subscription.stripe_subscription_id:
            try:
                cancelled_subscription = StripeService.cancel_subscription(subscription.stripe_subscription_id)
                logger.info(f"Successfully cancelled Stripe subscription {subscription.stripe_subscription_id}")
            except Exception as e:
                error_msg = f"Failed to cancel Stripe subscription: {str(e)}"
                logger.error(f"Error cancelling Stripe subscription {subscription.stripe_subscription_id}: {e}")
                cancellation_errors.append(error_msg)
                # Continue with local cancellation even if Stripe fails
        else:
            logger.info(f"No Stripe subscription ID found for subscription {subscription.id}")
        
        # Cancel in backend if integrated
        if subscription.backend_organization_id:
            try:
                from .backend_api import BackendApiService
                backend_api = BackendApiService()
                success, response_data = backend_api.handle_subscription_cancellation(subscription)
                
                if success:
                    logger.info(f"Successfully cancelled backend organization for subscription {subscription.id}")
                else:
                    error_msg = f"Backend cancellation failed: {response_data.get('error', 'Unknown error')}"
                    logger.warning(f"Backend cancellation failed for subscription {subscription.id}: {response_data}")
                    cancellation_errors.append(error_msg)
                    # Continue with local cancellation
                    
            except Exception as e:
                error_msg = f"Backend cancellation error: {str(e)}"
                logger.error(f"Error cancelling backend organization for subscription {subscription.id}: {e}")
                cancellation_errors.append(error_msg)
                # Continue with local cancellation
        else:
            logger.info(f"No backend organization ID found for subscription {subscription.id}")
        
        # Update local subscription (always do this)
        old_status = subscription.status
        subscription.status = 'cancelled'
        subscription.end_date = timezone.now().date()
        subscription.save()
        
        logger.info(f"Successfully updated local subscription {subscription.id} status from '{old_status}' to 'cancelled'")
        
        # Prepare response
        response_data = {
            'success': True,
            'message': 'Subscription cancelled successfully',
            'subscription': {
                'id': subscription.id,
                'status': subscription.status,
                'end_date': subscription.end_date.isoformat() if subscription.end_date else None
            }
        }
        
        # Add warnings if there were partial failures
        if cancellation_errors:
            response_data['warnings'] = cancellation_errors
            response_data['message'] = 'Subscription cancelled with some warnings (see details in logs)'
            logger.warning(f"Subscription {subscription.id} cancelled with warnings: {cancellation_errors}")
        
        return JsonResponse(response_data)
        
    except Exception as e:
        logger.error(f"Unexpected error cancelling subscription {subscription_id}: {e}")
        return JsonResponse({'error': 'Failed to cancel subscription'}, status=500)


@require_http_methods(["POST"])
@subscription_auth_required
def retry_backend_integration(request, subscription_id):
    """Retry backend integration for a subscription"""
    try:
        subscription = get_object_or_404(Subscription, id=subscription_id)
        
        # Verify user owns this subscription
        user_session = request.session.get('subscription_user')
        if not user_session or subscription.backend_tenant_slug != user_session.get('organization_schema'):
            return JsonResponse({'error': 'Unauthorized access to subscription'}, status=403)
        
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


@require_http_methods(["GET"])
@subscription_auth_required
def subscription_detail(request, subscription_id):
    """Detailed view of a specific subscription for management"""
    try:
        subscription = get_object_or_404(Subscription, id=subscription_id)
        
        # Verify user owns this subscription (authorization check)
        user_session = request.session.get('subscription_user')
        if not user_session or subscription.backend_tenant_slug != user_session.get('organization_schema'):
            logger.warning(f"Unauthorized access attempt to subscription {subscription_id} by user {user_session}")
            messages.error(request, 'You do not have permission to view this subscription.')
            return redirect('church_directory:subscription_login')
        
        # Get Stripe subscription details if available
        stripe_details = None
        invoices = []
        if subscription.stripe_subscription_id:
            try:
                stripe_details = StripeService.get_subscription_details(subscription.stripe_subscription_id)
                if subscription.stripe_customer_id:
                    invoices = StripeService.get_customer_invoices(subscription.stripe_customer_id, limit=5)
            except Exception as e:
                logger.error(f"Error fetching Stripe details for subscription {subscription_id}: {e}")
        
        context = {
            'subscription': subscription,
            'stripe_details': stripe_details,
            'invoices': invoices,
            'page_title': f'Subscription - {subscription.church_name}',
        }
        
        return render(request, 'church_directory/subscription_detail.html', context)
        
    except Exception as e:
        logger.error(f"Error viewing subscription detail {subscription_id}: {e}")
        messages.error(request, 'Failed to load subscription details')
        return redirect('church_directory:subscription_dashboard')


@require_http_methods(["POST"])
@subscription_auth_required
def create_customer_portal_session(request, subscription_id):
    """Create Stripe Customer Portal session for subscription management"""
    try:
        subscription = get_object_or_404(Subscription, id=subscription_id)
        
        # Verify user owns this subscription
        user_session = request.session.get('subscription_user')
        if not user_session or subscription.backend_tenant_slug != user_session.get('organization_schema'):
            return JsonResponse({'error': 'Unauthorized access to subscription'}, status=403)
        
        if not subscription.stripe_customer_id:
            return JsonResponse({'error': 'No Stripe customer ID found'}, status=400)
        
        # Create return URL
        return_url = request.build_absolute_uri(
            reverse('church_directory:subscription_detail', kwargs={'subscription_id': subscription_id})
        )
        
        # Create customer portal session
        portal_url = StripeService.create_customer_portal_session(
            subscription.stripe_customer_id,
            return_url
        )
        
        return JsonResponse({
            'success': True,
            'portal_url': portal_url
        })
        
    except Exception as e:
        logger.error(f"Error creating customer portal session for subscription {subscription_id}: {e}")
        return JsonResponse({'error': 'Failed to create portal session'}, status=500)


@require_http_methods(["POST"])
@subscription_auth_required
def change_billing_cycle(request, subscription_id):
    """Change subscription billing cycle between monthly and annual"""
    try:
        subscription = get_object_or_404(Subscription, id=subscription_id)
        
        # Verify user owns this subscription
        user_session = request.session.get('subscription_user')
        if not user_session or subscription.backend_tenant_slug != user_session.get('organization_schema'):
            return JsonResponse({'error': 'Unauthorized access to subscription'}, status=403)
        
        if not subscription.stripe_subscription_id:
            return JsonResponse({'error': 'No Stripe subscription ID found'}, status=400)
        
        if subscription.status != 'active':
            return JsonResponse({'error': 'Subscription must be active to change billing cycle'}, status=400)
        
        data = json.loads(request.body)
        new_billing_cycle = data.get('billing_cycle')
        
        if new_billing_cycle not in ['monthly', 'annual']:
            return JsonResponse({'error': 'Invalid billing cycle'}, status=400)
        
        if new_billing_cycle == subscription.billing_period:
            return JsonResponse({'error': 'Subscription is already on this billing cycle'}, status=400)
        
        # Get the new price based on billing cycle
        pricing_tier = subscription.pricing_tier
        if new_billing_cycle == 'annual':
            new_price = pricing_tier.annual_price
            # You'll need to map this to Stripe price IDs
            stripe_price_id = getattr(pricing_tier, 'stripe_annual_price_id', None)
        else:
            new_price = pricing_tier.monthly_price  
            stripe_price_id = getattr(pricing_tier, 'stripe_monthly_price_id', None)
        
        if not stripe_price_id:
            return JsonResponse({'error': 'Stripe price ID not configured for this billing cycle'}, status=400)
        
        # Update in Stripe
        updated_subscription = StripeService.update_subscription_billing_cycle(
            subscription.stripe_subscription_id,
            stripe_price_id
        )
        
        # Update local subscription
        subscription.billing_period = new_billing_cycle
        subscription.base_amount = new_price
        subscription.final_amount = new_price  # Assume no discount for simplicity
        subscription.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Billing cycle changed to {new_billing_cycle}',
            'new_amount': float(new_price),
            'next_invoice_amount': updated_subscription.get('latest_invoice', {}).get('amount_due', 0) / 100
        })
        
    except Exception as e:
        logger.error(f"Error changing billing cycle for subscription {subscription_id}: {e}")
        return JsonResponse({'error': 'Failed to change billing cycle'}, status=500)


@require_http_methods(["GET"])
def organization_subscription_status_api(request):
    """
    API endpoint for backend to check organization subscription status.
    Used by the church directory backend to verify subscription status.
    """
    # Check API key authentication
    auth_header = request.META.get('HTTP_AUTHORIZATION', '')
    if not auth_header.startswith('Bearer '):
        return JsonResponse({'error': 'Missing API key'}, status=401)
    
    api_key = auth_header[7:]  # Remove 'Bearer ' prefix
    expected_api_key = getattr(settings, 'CHURCH_DIRECTORY_INTEGRATION_API_KEY', '')
    
    if not expected_api_key or api_key != expected_api_key:
        return JsonResponse({'error': 'Invalid API key'}, status=401)
    
    try:
        # Get parameters
        organization_id = request.GET.get('organization_id')
        schema_name = request.GET.get('schema_name')
        contact_email = request.GET.get('contact_email')
        
        if not any([organization_id, schema_name, contact_email]):
            return JsonResponse({'error': 'Missing required parameters'}, status=400)
        
        # Try to find subscription by various identifiers
        subscription = None
        
        # First try by backend organization ID
        if organization_id:
            subscription = Subscription.objects.filter(
                backend_organization_id=organization_id,
                status='active'
            ).first()
        
        # Then try by tenant slug
        if not subscription and schema_name:
            subscription = Subscription.objects.filter(
                backend_tenant_slug=schema_name,
                status='active'
            ).first()
        
        # Finally try by email
        if not subscription and contact_email:
            subscription = Subscription.objects.filter(
                email__iexact=contact_email,
                status='active'
            ).first()
        
        if not subscription:
            return JsonResponse({'error': 'Subscription not found'}, status=404)
        
        # Return subscription details
        return JsonResponse({
            'subscription_id': str(subscription.id),
            'status': subscription.status,
            'tier': subscription.pricing_tier.name,
            'billing_period': subscription.billing_period,
            'amount': float(subscription.final_amount),
            'next_billing_date': subscription.next_billing_date.isoformat() if subscription.next_billing_date else None,
            'start_date': subscription.start_date.isoformat() if subscription.start_date else None,
            'church_name': subscription.church_name,
            'contact_name': subscription.contact_name,
            'email': subscription.email,
            'backend_integration_status': subscription.backend_integration_status,
        })
        
    except Exception as e:
        logger.error(f"Error getting organization subscription status: {e}")
        return JsonResponse({'error': 'Failed to get subscription status'}, status=500)


@require_http_methods(["POST"])
@csrf_exempt
def _render_subscription_dashboard(request, user_session):
    """Helper method to render subscription dashboard with user session data"""
    organization_schema = user_session.get('organization_schema')
    
    # Get subscription for this organization
    try:
        logger.info(f"Looking for subscription with schema: {organization_schema}")
        subscription = Subscription.objects.filter(
            backend_tenant_slug=organization_schema,
            status='active'
        ).first()
        
        logger.info(f"Found subscription: {subscription.id if subscription else None}")
        
        if subscription:
            # Show subscription detail directly
            try:
                stripe_details = None
                invoices = []
                if subscription.stripe_subscription_id:
                    try:
                        from .stripe_service import StripeService
                        stripe_details = StripeService.get_subscription_details(subscription.stripe_subscription_id)
                        if subscription.stripe_customer_id:
                            invoices = StripeService.get_customer_invoices(subscription.stripe_customer_id, limit=5)
                    except Exception as e:
                        logger.error(f"Error fetching Stripe details: {e}")
                
                context = {
                    'subscription': subscription,
                    'stripe_details': stripe_details,
                    'invoices': invoices,
                    'user_session': user_session,
                    'page_title': f'Subscription Management - {subscription.church_name}',
                }
                
                return render(request, 'church_directory/subscription_detail.html', context)
                
            except Exception as e:
                logger.error(f"Error rendering subscription detail: {e}")
        
        # No subscription found, show customer portal to start subscription
        try:
            config = WebsiteConfig.objects.first()
        except WebsiteConfig.DoesNotExist:
            config = None
        
        # Get available pricing tiers
        from .models import PricingTier
        pricing_tiers = PricingTier.objects.filter(is_active=True)
        
        context = {
            'config': config,
            'user_session': user_session,
            'pricing_tiers': pricing_tiers,
            'organization_name': user_session.get('organization_name'),
            'page_title': f'Subscription Portal - {user_session.get("organization_name")}',
        }
        return render(request, 'church_directory/customer_subscription_portal.html', context)
        
    except Exception as e:
        logger.error(f"Error in dashboard rendering: {e}")
        return redirect('church_directory:subscription_login')


@require_http_methods(["GET"])
def subscription_portal(request):
    """Subscription portal with mobile authentication - redirect to login"""
    token = request.GET.get('token')
    
    if token:
        # Check for mobile auth token in database
        from .models import MobileAuthToken
        
        try:
            auth_token = MobileAuthToken.objects.get(token=token)
            
            if not auth_token.is_valid():
                if auth_token.is_expired():
                    logger.warning(f"Mobile auth token {token} has expired")
                else:
                    logger.warning(f"Mobile auth token {token} already used")
                auth_token.delete()  # Clean up
                return redirect('church_directory:subscription_login')
            
            # Perform authentication directly instead of redirecting
            # Use mobile auth data to authenticate with backend
            backend_service = BackendApiService()
            auth_result = backend_service.verify_mobile_session(
                auth_token.user_id,
                auth_token.organization_schema
            )
            
            if auth_result['success']:
                # Store user info in session for the new browser session
                user_session_data = {
                    'email': auth_result.get('email'),
                    'user_id': auth_result.get('user_id'),
                    'organization_schema': auth_token.organization_schema,
                    'organization_name': auth_token.organization_name,
                    'authenticated_at': timezone.now().isoformat(),
                }
                request.session['subscription_user'] = user_session_data
                request.session.set_expiry(86400)  # 24 hours session
                request.session.save()  # Force session save
                
                # Mark token as used and clean up
                auth_token.used = True
                auth_token.save()
                
                logger.info(f"Mobile session verified and authenticated for user: {auth_token.user_id}")
                
                # Instead of redirecting, show the dashboard directly
                # This avoids session continuity issues
                return _render_subscription_dashboard(request, user_session_data)
            else:
                logger.error(f"Backend authentication failed: {auth_result}")
                auth_token.delete()  # Clean up failed token
                return redirect('church_directory:subscription_login')
            
        except MobileAuthToken.DoesNotExist:
            logger.warning(f"Mobile auth token {token} not found in database")
    
    # If no valid token, redirect to login
    logger.warning(f"No valid token provided, redirecting to login")
    return redirect('church_directory:subscription_login')


@require_http_methods(["GET", "POST"])
@csrf_exempt  # Allow API calls without CSRF token
def subscription_login(request):
    """Login page for subscription management"""
    if request.method == 'POST':
        # Handle JSON API requests
        if request.content_type == 'application/json':
            try:
                import json
                data = json.loads(request.body)
                username = data.get('username', '').strip()
                password = data.get('password', '')
            except (json.JSONDecodeError, ValueError):
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid JSON data'
                }, status=400)
        else:
            # Handle form POST requests
            username = request.POST.get('username', '').strip()
            password = request.POST.get('password', '')
        
        if not username or not password:
            # Return JSON response for API calls
            if request.content_type == 'application/json':
                return JsonResponse({
                    'success': False,
                    'error': 'Please enter both username and password.'
                }, status=400)
            
            # Return HTML response for form submissions
            context = {
                'error': 'Please enter both username and password.',
                'username': username,
            }
            return render(request, 'church_directory/subscription_login.html', context)
        
        # Authenticate with backend
        backend_service = BackendApiService()
        auth_result = backend_service.authenticate_user(username, password)
        
        if auth_result['success']:
            # Store user info in session
            request.session['subscription_user'] = {
                'username': username,
                'email': auth_result.get('email'),
                'user_id': auth_result.get('user_id'),
                'organization_schema': auth_result.get('organization_schema'),
                'organization_name': auth_result.get('organization_name'),
                'authenticated_at': timezone.now().isoformat(),
            }
            
            # Return JSON response for API calls
            if request.content_type == 'application/json':
                return JsonResponse({
                    'success': True,
                    'message': 'Authentication successful',
                    'user': {
                        'username': username,
                        'email': auth_result.get('email'),
                        'organization_name': auth_result.get('organization_name'),
                    },
                    'redirect_url': reverse('church_directory:subscription_dashboard_authenticated')
                })
            
            # Redirect to subscription dashboard for form submissions
            return redirect('church_directory:subscription_dashboard_authenticated')
        else:
            # Return JSON response for API calls
            if request.content_type == 'application/json':
                return JsonResponse({
                    'success': False,
                    'error': auth_result.get('error', 'Invalid username or password.')
                }, status=401)
            
            # Return HTML response for form submissions
            context = {
                'error': auth_result.get('error', 'Invalid username or password.'),
                'username': username,
            }
            return render(request, 'church_directory/subscription_login.html', context)
    
    # GET request - show login form
    try:
        config = WebsiteConfig.objects.first()
    except WebsiteConfig.DoesNotExist:
        config = None
    
    context = {
        'config': config,
        'page_title': 'Subscription Login - Church Directory',
    }
    
    return render(request, 'church_directory/subscription_login.html', context)


@require_http_methods(["GET"])
def subscription_auto_login(request):
    """Auto-login from mobile authentication"""
    # Check for URL parameters first (new method)
    user_id = request.GET.get('user_id')
    organization_schema = request.GET.get('organization_schema')
    
    # Fallback to session data (legacy method)
    mobile_auth_data = request.session.get('mobile_auth_data')
    
    logger.info(f"Auto-login attempt - URL params: user_id={user_id is not None}, org_schema={organization_schema is not None}, session_data={mobile_auth_data is not None}")
    
    if user_id and organization_schema:
        # Use URL parameters (new method from mobile app)
        auth_user_id = user_id
        auth_org_schema = organization_schema
    elif mobile_auth_data:
        # Use session data (legacy method)
        auth_user_id = mobile_auth_data.get('user_id')
        auth_org_schema = mobile_auth_data.get('organization_schema')
    else:
        logger.warning("No authentication data found in URL params or session")
        return redirect('church_directory:subscription_login')
    
    # Use auth data to authenticate with backend
    backend_service = BackendApiService()
    auth_result = backend_service.verify_mobile_session(
        auth_user_id,
        auth_org_schema
    )
    
    logger.info(f"Backend auth result: {auth_result}")
    
    if auth_result['success']:
        # Store user info in session
        request.session['subscription_user'] = {
            'email': auth_result.get('email'),
            'user_id': auth_result.get('user_id'),
            'organization_schema': auth_org_schema,
            'organization_name': auth_result.get('organization_name'),
            'authenticated_at': timezone.now().isoformat(),
        }
        
        # Clean up mobile auth data from session if it exists
        if 'mobile_auth_data' in request.session:
            del request.session['mobile_auth_data']
        
        logger.info("Auto-login successful, redirecting to dashboard")
        # Redirect to subscription dashboard
        return redirect('church_directory:subscription_dashboard_authenticated')
    else:
        logger.error(f"Backend authentication failed: {auth_result}")
        # Clean up and redirect to manual login
        if 'mobile_auth_data' in request.session:
            del request.session['mobile_auth_data']
        return redirect('church_directory:subscription_login')


@require_http_methods(["GET"])
@subscription_auth_required
def subscription_dashboard_authenticated(request):
    """Authenticated subscription dashboard"""
    user_session = request.session.get('subscription_user')
    
    logger.info(f"Subscription dashboard access, user_session: {user_session is not None}")
    
    if not user_session:
        logger.warning("No user session found, redirecting to login")
        return redirect('church_directory:subscription_login')
    
    organization_schema = user_session.get('organization_schema')
    logger.info(f"Looking for subscription for schema: {organization_schema}")
    
    # Get subscription for this organization
    try:
        subscription = Subscription.objects.filter(
            backend_tenant_slug=organization_schema,
            status='active'
        ).first()
        
        if subscription:
            logger.info(f"Found subscription {subscription.id}, redirecting to detail view")
            return redirect('church_directory:subscription_detail', subscription_id=subscription.id)
        else:
            logger.info("No active subscription found, showing dashboard template")
            # No active subscription found
            try:
                config = WebsiteConfig.objects.first()
            except WebsiteConfig.DoesNotExist:
                config = None
            
            context = {
                'config': config,
                'user_session': user_session,
                'error': 'No active subscription found for your organization.',
                'page_title': 'Subscription Dashboard - Church Directory',
            }
            return render(request, 'church_directory/subscription_dashboard.html', context)
            
    except Exception as e:
        logger.error(f"Error finding subscription for schema {organization_schema}: {e}")
        logger.warning("Exception in dashboard, redirecting to login")
        return redirect('church_directory:subscription_login')


# API endpoints for syncing data to backend
def api_pricing_tiers(request):
    """API endpoint to get pricing tiers for syncing to backend"""
    # Check API key authentication
    auth_header = request.META.get('HTTP_AUTHORIZATION', '')
    if not auth_header.startswith('Bearer '):
        return JsonResponse({'error': 'Missing API key'}, status=401)
    
    api_key = auth_header[7:]  # Remove 'Bearer ' prefix
    expected_api_key = getattr(settings, 'CHURCH_DIRECTORY_INTEGRATION_API_KEY', '')
    
    if not expected_api_key or api_key != expected_api_key:
        return JsonResponse({'error': 'Invalid API key'}, status=401)
    
    try:
        tiers = PricingTier.objects.filter(is_active=True)
        tiers_data = []
        
        for tier in tiers:
            tiers_data.append({
                'id': tier.id,
                'name': tier.name,
                'description': tier.description,
                'max_users': tier.max_users,
                'monthly_price': float(tier.monthly_price),
                'annual_price': float(tier.annual_price) if tier.annual_price else None,
                'features': tier.features,  # JSON field with feature list
                'is_popular': tier.is_popular,
                'is_active': tier.is_active,
                'sort_order': tier.sort_order,
                'created_at': tier.created_at.isoformat(),
                'updated_at': tier.updated_at.isoformat(),
            })
        
        return JsonResponse({
            'success': True,
            'tiers': tiers_data,
            'count': len(tiers_data)
        })
        
    except Exception as e:
        logger.error(f"Error fetching pricing tiers for API: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


def api_features(request):
    """API endpoint to get features for syncing to backend"""
    # Check API key authentication
    auth_header = request.META.get('HTTP_AUTHORIZATION', '')
    if not auth_header.startswith('Bearer '):
        return JsonResponse({'error': 'Missing API key'}, status=401)
    
    api_key = auth_header[7:]  # Remove 'Bearer ' prefix
    expected_api_key = getattr(settings, 'CHURCH_DIRECTORY_INTEGRATION_API_KEY', '')
    
    if not expected_api_key or api_key != expected_api_key:
        return JsonResponse({'error': 'Invalid API key'}, status=401)
    
    try:
        from .models import Feature
        features = Feature.objects.filter(is_active=True)
        features_data = []
        
        for feature in features:
            features_data.append({
                'id': feature.id,
                'title': feature.title,
                'description': feature.description,
                'icon': feature.icon,
                'featured_on_homepage': feature.featured_on_homepage,
                'is_active': feature.is_active,
                'order': feature.order,
                'created_at': feature.created_at.isoformat(),
                'updated_at': feature.updated_at.isoformat(),
            })
        
        return JsonResponse({
            'success': True,
            'features': features_data,
            'count': len(features_data)
        })
        
    except Exception as e:
        logger.error(f"Error fetching features for API: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
