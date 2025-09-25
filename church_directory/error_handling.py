"""
Error handling utilities for the church directory payment system.
Provides comprehensive error logging, monitoring, and user-friendly error responses.
"""

import logging
import traceback
from functools import wraps
from typing import Dict, Any, Optional, Callable
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.conf import settings
from django.utils import timezone
from church_directory.models import Subscription
import uuid

logger = logging.getLogger(__name__)


class PaymentError(Exception):
    """Base exception for payment-related errors"""
    
    def __init__(self, message: str, error_code: str = None, details: Dict[str, Any] = None):
        self.message = message
        self.error_code = error_code or 'PAYMENT_ERROR'
        self.details = details or {}
        self.timestamp = timezone.now()
        self.error_id = str(uuid.uuid4())[:8]
        super().__init__(message)


class StripePaymentError(PaymentError):
    """Stripe-specific payment error"""
    
    def __init__(self, message: str, stripe_error=None, **kwargs):
        self.stripe_error = stripe_error
        error_code = kwargs.get('error_code', 'STRIPE_ERROR')
        details = kwargs.get('details', {})
        
        if stripe_error:
            details.update({
                'stripe_type': type(stripe_error).__name__,
                'stripe_code': getattr(stripe_error, 'code', None),
                'stripe_param': getattr(stripe_error, 'param', None),
            })
        
        super().__init__(message, error_code, details)


class BackendIntegrationError(PaymentError):
    """Backend integration error"""
    
    def __init__(self, message: str, response_data: Dict = None, **kwargs):
        self.response_data = response_data or {}
        error_code = kwargs.get('error_code', 'BACKEND_INTEGRATION_ERROR')
        details = kwargs.get('details', {})
        details['backend_response'] = self.response_data
        super().__init__(message, error_code, details)


class ErrorLogger:
    """Centralized error logging with context"""
    
    @staticmethod
    def log_payment_error(error: PaymentError, subscription: Optional[Subscription] = None, 
                         request=None, extra_context: Dict = None):
        """Log payment error with full context"""
        
        context = {
            'error_id': error.error_id,
            'error_type': type(error).__name__,
            'error_code': error.error_code,
            'error_message': error.message,
            'error_details': error.details,
            'timestamp': error.timestamp.isoformat(),
        }
        
        # Add subscription context
        if subscription:
            context['subscription'] = {
                'id': str(subscription.id),
                'church_name': subscription.church_name,
                'email': subscription.email,
                'status': subscription.status,
                'amount': float(subscription.final_amount),
                'stripe_customer_id': subscription.stripe_customer_id,
                'stripe_payment_intent_id': subscription.stripe_payment_intent_id,
                'backend_integration_status': subscription.backend_integration_status,
            }
        
        # Add request context
        if request:
            context['request'] = {
                'method': request.method,
                'path': request.path,
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                'ip_address': ErrorLogger._get_client_ip(request),
                'referer': request.META.get('HTTP_REFERER', ''),
            }
        
        # Add extra context
        if extra_context:
            context['extra'] = extra_context
        
        logger.error(f"Payment Error [{error.error_id}]: {error.message}", extra=context)
        
        # Send to monitoring service if configured
        if hasattr(settings, 'SENTRY_DSN') and settings.SENTRY_DSN:
            try:
                import sentry_sdk
                with sentry_sdk.configure_scope() as scope:
                    scope.set_tag("error_type", "payment")
                    scope.set_tag("error_code", error.error_code)
                    if subscription:
                        scope.set_user({"email": subscription.email, "id": str(subscription.id)})
                    scope.set_context("payment_error", context)
                sentry_sdk.capture_exception(error)
            except ImportError:
                logger.warning("Sentry not available for error reporting")
    
    @staticmethod
    def _get_client_ip(request):
        """Get client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


def handle_payment_errors(view_func: Callable) -> Callable:
    """Decorator to handle payment errors gracefully"""
    
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        try:
            return view_func(request, *args, **kwargs)
        
        except StripePaymentError as e:
            ErrorLogger.log_payment_error(e, request=request)
            
            if request.content_type == 'application/json' or 'api/' in request.path:
                return JsonResponse({
                    'error': True,
                    'error_code': e.error_code,
                    'error_id': e.error_id,
                    'message': 'Payment processing failed. Please try again or contact support.',
                    'user_message': ErrorLogger._get_user_friendly_message(e),
                }, status=400)
            else:
                return render(request, 'church_directory/payment_error.html', {
                    'error_message': ErrorLogger._get_user_friendly_message(e),
                    'error_code': e.error_code,
                    'error_id': e.error_id,
                    'support_email': getattr(settings, 'SUPPORT_EMAIL', 'support@verionlabs.com'),
                })
        
        except BackendIntegrationError as e:
            ErrorLogger.log_payment_error(e, request=request)
            
            if request.content_type == 'application/json' or 'api/' in request.path:
                return JsonResponse({
                    'error': True,
                    'error_code': e.error_code,
                    'error_id': e.error_id,
                    'message': 'Backend integration failed. Support has been notified.',
                    'user_message': 'Your payment was successful, but there was an issue setting up your account. Our support team will contact you shortly.',
                }, status=500)
            else:
                return render(request, 'church_directory/integration_error.html', {
                    'error_message': 'Your payment was successful, but there was an issue setting up your account.',
                    'error_id': e.error_id,
                    'support_message': 'Our support team has been automatically notified and will contact you within 24 hours to complete your setup.',
                })
        
        except PaymentError as e:
            ErrorLogger.log_payment_error(e, request=request)
            
            if request.content_type == 'application/json' or 'api/' in request.path:
                return JsonResponse({
                    'error': True,
                    'error_code': e.error_code,
                    'error_id': e.error_id,
                    'message': e.message,
                    'user_message': ErrorLogger._get_user_friendly_message(e),
                }, status=400)
            else:
                return render(request, 'church_directory/payment_error.html', {
                    'error_message': ErrorLogger._get_user_friendly_message(e),
                    'error_code': e.error_code,
                    'error_id': e.error_id,
                })
        
        except Exception as e:
            # Log unexpected errors
            error_id = str(uuid.uuid4())[:8]
            logger.exception(f"Unexpected error [{error_id}] in payment flow: {str(e)}")
            
            # Create generic PaymentError for consistent handling
            payment_error = PaymentError(
                message=f"Unexpected error: {str(e)}",
                error_code='UNEXPECTED_ERROR',
                details={'original_error': str(e), 'traceback': traceback.format_exc()}
            )
            payment_error.error_id = error_id
            
            ErrorLogger.log_payment_error(payment_error, request=request)
            
            if request.content_type == 'application/json' or 'api/' in request.path:
                return JsonResponse({
                    'error': True,
                    'error_code': 'UNEXPECTED_ERROR',
                    'error_id': error_id,
                    'message': 'An unexpected error occurred. Please try again or contact support.',
                }, status=500)
            else:
                return render(request, 'church_directory/payment_error.html', {
                    'error_message': 'An unexpected error occurred. Please try again or contact support.',
                    'error_code': 'UNEXPECTED_ERROR',
                    'error_id': error_id,
                })
    
    return wrapper


def monitor_subscription_health():
    """Monitor subscription health and send alerts"""
    from django.db.models import Count, Q
    from datetime import timedelta
    
    now = timezone.now()
    recent_cutoff = now - timedelta(hours=24)
    
    # Check for failed integrations
    failed_integrations = Subscription.objects.filter(
        status='active',
        backend_integration_status='failed',
        created_at__gte=recent_cutoff
    ).count()
    
    # Check for pending payments
    old_pending = Subscription.objects.filter(
        status='pending',
        created_at__lt=now - timedelta(hours=6)
    ).count()
    
    # Check for webhook processing failures
    from church_directory.models import WebhookEvent
    failed_webhooks = WebhookEvent.objects.filter(
        processed=False,
        processing_error__isnull=False,
        created_at__gte=recent_cutoff
    ).count()
    
    alerts = []
    
    if failed_integrations > 0:
        alerts.append(f"{failed_integrations} failed backend integrations in the last 24 hours")
    
    if old_pending > 0:
        alerts.append(f"{old_pending} payments have been pending for over 6 hours")
    
    if failed_webhooks > 0:
        alerts.append(f"{failed_webhooks} webhook processing failures in the last 24 hours")
    
    if alerts:
        alert_message = "Church Directory Payment System Alerts:\n\n" + "\n".join(f"• {alert}" for alert in alerts)
        logger.critical(alert_message)
        
        # Send to monitoring service
        if hasattr(settings, 'SENTRY_DSN') and settings.SENTRY_DSN:
            try:
                import sentry_sdk
                sentry_sdk.capture_message(alert_message, level='error')
            except ImportError:
                pass
    
    return alerts


# Add to ErrorLogger class
ErrorLogger._get_user_friendly_message = lambda error: {
    'CARD_DECLINED': 'Your card was declined. Please try a different payment method or contact your bank.',
    'INSUFFICIENT_FUNDS': 'Your card has insufficient funds. Please try a different payment method.',
    'EXPIRED_CARD': 'Your card has expired. Please check your card details and try again.',
    'INCORRECT_CVC': 'Your card\'s security code is incorrect. Please check and try again.',
    'PROCESSING_ERROR': 'There was a temporary issue processing your payment. Please try again.',
    'INVALID_REQUEST': 'There was an issue with your payment information. Please check your details and try again.',
    'STRIPE_ERROR': 'There was an issue with the payment processor. Please try again.',
    'BACKEND_INTEGRATION_ERROR': 'Your payment was successful, but there was an issue setting up your account. Our support team will contact you.',
    'UNEXPECTED_ERROR': 'An unexpected error occurred. Please try again or contact support.',
}.get(error.error_code, error.message)