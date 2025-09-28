"""
Stripe service for handling payment processing and subscription management.

This service now uses Stripe Checkout instead of Stripe Elements for improved
reliability and security. Key changes:

- create_checkout_session() replaces create_payment_intent()
- Users are redirected to Stripe's hosted checkout page
- Payment processing is handled entirely by Stripe
- Webhook events handle payment completion
- Simplified error handling and better UX

For more details, see: STRIPE_CHECKOUT_GUIDE.md
"""

import stripe
import logging
from decimal import Decimal
from django.conf import settings
from django.utils import timezone
from typing import Dict, Any, Optional, Tuple
from .models import Subscription, PricingTier, Coupon, PaymentIntent, WebhookEvent
from .backend_api import BackendApiService

# Configure Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

logger = logging.getLogger(__name__)


class StripeService:
    """Service class for Stripe payment operations"""
    
    # Valid status transitions to prevent invalid state changes
    VALID_STATUS_TRANSITIONS = {
        'pending': ['processing', 'active', 'expired', 'failed', 'cancelled'],
        'processing': ['active', 'expired', 'failed', 'cancelled'],
        'active': ['cancelled', 'suspended'],  # Active subscriptions can only be cancelled or suspended
        'expired': [],  # Terminal state
        'failed': ['active'],  # Failed payments can be retried to active
        'cancelled': [],  # Terminal state
        'suspended': ['active', 'cancelled'],  # Suspended can be reactivated or cancelled
    }
    
    @staticmethod
    def _validate_status_transition(current_status: str, new_status: str) -> bool:
        """Validate that a status transition is allowed"""
        if current_status == new_status:
            return True  # Allow same status (idempotent)
        
        allowed_transitions = StripeService.VALID_STATUS_TRANSITIONS.get(current_status, [])
        return new_status in allowed_transitions
    
    @staticmethod
    def create_customer(email: str, name: str, church_name: str, phone: str = None) -> Dict[str, Any]:
        """Create a Stripe customer"""
        try:
            customer_data = {
                'email': email,
                'name': name,
                'description': f"Contact: {name} from {church_name}",
                'metadata': {
                    'church_name': church_name,
                    'contact_name': name,
                }
            }
            
            if phone:
                customer_data['phone'] = phone
            
            customer = stripe.Customer.create(**customer_data)
            logger.info(f"Created Stripe customer {customer.id} for {email}")
            return customer
            
        except stripe.error.StripeError as e:
            logger.error(f"Failed to create Stripe customer for {email}: {e}")
            raise
    
    @staticmethod
    def create_checkout_session(
        subscription: Subscription,
        success_url: str,
        cancel_url: str,
        customer_id: str = None
    ) -> Tuple[Dict[str, Any], PaymentIntent]:
        """Create a Stripe Checkout Session"""
        try:
            # Convert amount to cents
            amount_cents = int(subscription.final_amount * 100)
            
            # Build line items
            line_items = [{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': f'{subscription.pricing_tier.name} Plan',
                        'description': f'Church Directory Management - {subscription.billing_period.title()} Subscription',
                        'metadata': {
                            'church_name': subscription.church_name,
                            'pricing_tier': subscription.pricing_tier.name,
                        }
                    },
                    'unit_amount': amount_cents,
                },
                'quantity': 1,
            }]
            
            # If there's a discount, add it as a separate line item
            if subscription.discount_amount and subscription.discount_amount > 0:
                discount_cents = int(subscription.discount_amount * 100)
                line_items.append({
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': 'Discount Applied',
                            'description': f'Coupon: {subscription.coupon_used.code}' if subscription.coupon_used else 'Promotional Discount',
                        },
                        'unit_amount': -discount_cents,  # Negative amount for discount
                    },
                    'quantity': 1,
                })
            
            checkout_session_data = {
                'payment_method_types': ['card'],
                'line_items': line_items,
                'mode': 'payment',
                'success_url': success_url,
                'cancel_url': cancel_url,
                'metadata': {
                    'subscription_id': str(subscription.id),
                    'church_name': subscription.church_name,
                    'contact_name': subscription.contact_name,
                    'pricing_tier': subscription.pricing_tier.name,
                    'billing_period': subscription.billing_period,
                },
                'customer_creation': 'always',
                'phone_number_collection': {
                    'enabled': True,
                },
            }
            
            # If customer exists, use it
            if customer_id:
                checkout_session_data['customer'] = customer_id
                del checkout_session_data['customer_creation']
            else:
                # Pre-fill customer details
                checkout_session_data['customer_email'] = subscription.email
            
            # Create Checkout Session in Stripe
            checkout_session = stripe.checkout.Session.create(**checkout_session_data)
            
            # Create local PaymentIntent record (reusing existing model for tracking)
            payment_intent = PaymentIntent.objects.create(
                stripe_payment_intent_id=checkout_session.id,  # Store checkout session ID
                subscription=subscription,
                amount=subscription.final_amount,
                status='pending',  # Checkout sessions start as pending
                client_secret=checkout_session.url,  # Store checkout URL in client_secret field
                stripe_metadata=checkout_session.metadata
            )
            
            logger.info(f"Created Checkout Session {checkout_session.id} for subscription {subscription.id}")
            return checkout_session, payment_intent
            
        except stripe.error.StripeError as e:
            logger.error(f"Failed to create Checkout Session for subscription {subscription.id}: {e}")
            raise
    
    @staticmethod
    def retrieve_checkout_session(session_id: str) -> Dict[str, Any]:
        """Retrieve a Checkout Session from Stripe"""
        try:
            return stripe.checkout.Session.retrieve(session_id)
        except stripe.error.StripeError as e:
            logger.error(f"Failed to retrieve Checkout Session {session_id}: {e}")
            raise
    
    @staticmethod
    def retrieve_payment_intent(payment_intent_id: str) -> Dict[str, Any]:
        """Retrieve a Payment Intent from Stripe"""
        try:
            return stripe.PaymentIntent.retrieve(payment_intent_id)
        except stripe.error.StripeError as e:
            logger.error(f"Failed to retrieve Payment Intent {payment_intent_id}: {e}")
            raise
    
    @staticmethod
    def create_subscription_for_customer(
        customer_id: str,
        price_id: str,
        subscription_obj: Subscription
    ) -> Dict[str, Any]:
        """Create a Stripe subscription for recurring billing"""
        try:
            subscription_data = {
                'customer': customer_id,
                'items': [{'price': price_id}],
                'metadata': {
                    'subscription_id': str(subscription_obj.id),
                    'church_name': subscription_obj.church_name,
                    'contact_name': subscription_obj.contact_name,
                },
                'expand': ['latest_invoice.payment_intent']
            }
            
            # Add trial period if applicable
            if subscription_obj.trial_end_date:
                subscription_data['trial_end'] = int(subscription_obj.trial_end_date.timestamp())
            
            stripe_subscription = stripe.Subscription.create(**subscription_data)
            
            # Update local subscription record
            subscription_obj.stripe_subscription_id = stripe_subscription.id
            subscription_obj.status = 'processing'
            subscription_obj.save()
            
            logger.info(f"Created Stripe subscription {stripe_subscription.id} for customer {customer_id}")
            return stripe_subscription
            
        except stripe.error.StripeError as e:
            logger.error(f"Failed to create Stripe subscription for customer {customer_id}: {e}")
            raise
    
    @staticmethod
    def cancel_subscription(subscription_id: str) -> Dict[str, Any]:
        """Cancel a Stripe subscription"""
        try:
            subscription = stripe.Subscription.delete(subscription_id)
            logger.info(f"Cancelled Stripe subscription {subscription_id}")
            return subscription
        except stripe.error.StripeError as e:
            logger.error(f"Failed to cancel subscription {subscription_id}: {e}")
            raise
    
    @staticmethod
    def construct_webhook_event(payload: bytes, signature: str) -> Dict[str, Any]:
        """Construct and verify a Stripe webhook event"""
        try:
            event = stripe.Webhook.construct_event(
                payload,
                signature,
                settings.STRIPE_WEBHOOK_SECRET
            )
            return event
        except (ValueError, stripe.error.SignatureVerificationError) as e:
            logger.error(f"Failed to construct webhook event: {e}")
            raise
    
    @staticmethod
    def handle_webhook_event(event: Dict[str, Any]) -> bool:
        """Handle a Stripe webhook event"""
        from django.db import transaction
        
        try:
            # Check if webhook event already exists and is processed
            with transaction.atomic():
                try:
                    webhook_event = WebhookEvent.objects.select_for_update().get(stripe_event_id=event['id'])
                    if webhook_event.processed:
                        logger.info(f"Webhook event {event['id']} already processed")
                        return True
                    # Process the existing event
                except WebhookEvent.DoesNotExist:
                    webhook_event = WebhookEvent.objects.create(
                        stripe_event_id=event['id'],
                        event_type=event['type'],
                        event_data=event,
                    )
                    # Process the new event
                
                # Process based on event type with transaction
                if event['type'] == 'checkout.session.completed':
                    return StripeService._handle_checkout_session_completed(event, webhook_event)
                elif event['type'] == 'checkout.session.expired':
                    return StripeService._handle_checkout_session_expired(event, webhook_event)
                elif event['type'] == 'payment_intent.succeeded':
                    return StripeService._handle_payment_intent_succeeded(event, webhook_event)
                elif event['type'] == 'payment_intent.payment_failed':
                    return StripeService._handle_payment_intent_failed(event, webhook_event)
                elif event['type'] == 'invoice.payment_succeeded':
                    return StripeService._handle_invoice_payment_succeeded(event, webhook_event)
                elif event['type'] == 'invoice.payment_failed':
                    return StripeService._handle_invoice_payment_failed(event, webhook_event)
                elif event['type'] == 'customer.subscription.updated':
                    return StripeService._handle_subscription_updated(event, webhook_event)
                elif event['type'] == 'customer.subscription.deleted':
                    return StripeService._handle_subscription_deleted(event, webhook_event)
                else:
                    logger.info(f"Unhandled webhook event type: {event['type']}")
                    webhook_event.processed = True
                    webhook_event.processed_at = timezone.now()
                    webhook_event.save()
                    return True
                
        except Exception as e:
            logger.error(f"Error processing webhook event {event['id']}: {e}")
            if 'webhook_event' in locals():
                webhook_event.processing_error = str(e)
                webhook_event.save()
            return False
    
    @staticmethod
    def _handle_checkout_session_completed(event: Dict[str, Any], webhook_event: WebhookEvent) -> bool:
        """Handle completed checkout session"""
        try:
            checkout_session = event['data']['object']
            session_id = checkout_session['id']
            
            # Find related subscription
            subscription_id = checkout_session['metadata'].get('subscription_id')
            if subscription_id:
                try:
                    subscription = Subscription.objects.get(id=subscription_id)
                    
                    # Idempotency check: Don't reprocess if already active
                    if subscription.status == 'active' and subscription.start_date:
                        logger.info(f"Subscription {subscription_id} already activated, skipping duplicate processing")
                        webhook_event.processed = True
                        webhook_event.processed_at = timezone.now()
                        webhook_event.save()
                        return True
                    
                    # Validate status transition
                    if not StripeService._validate_status_transition(subscription.status, 'active'):
                        logger.warning(f"Invalid status transition for subscription {subscription_id}: {subscription.status} -> active")
                        webhook_event.processed = True
                        webhook_event.processed_at = timezone.now()
                        webhook_event.save()
                        return True
                    
                    # Use consistent timestamp for all date calculations
                    activation_time = timezone.now()
                    
                    # Update subscription with Stripe customer info
                    if checkout_session.get('customer'):
                        subscription.stripe_customer_id = checkout_session['customer']
                    
                    # Update subscription status
                    subscription.status = 'active'
                    subscription.start_date = activation_time
                    
                    # Set end date based on billing period
                    if subscription.billing_period == 'annual':
                        from dateutil.relativedelta import relativedelta
                        subscription.end_date = activation_time + relativedelta(years=1)
                        subscription.next_billing_date = subscription.end_date
                    else:
                        from dateutil.relativedelta import relativedelta
                        subscription.end_date = activation_time + relativedelta(months=1)
                        subscription.next_billing_date = subscription.end_date
                    
                    # Store payment intent ID if available
                    if checkout_session.get('payment_intent'):
                        subscription.stripe_payment_intent_id = checkout_session['payment_intent']
                    
                    subscription.save()
                    webhook_event.subscription = subscription
                    
                    logger.info(f"Activated subscription {subscription_id} from checkout session {session_id}")
                    
                    # Update local PaymentIntent record (which stores checkout session data)
                    try:
                        local_pi = PaymentIntent.objects.get(stripe_payment_intent_id=session_id)
                        local_pi.status = 'completed'
                        local_pi.save()
                    except PaymentIntent.DoesNotExist:
                        logger.warning(f"Local PaymentIntent record not found for checkout session {session_id}")
                    
                    # Integrate with backend API to create organization (only if not already done)
                    if (getattr(settings, 'BACKEND_INTEGRATION_ENABLED', True) and 
                        subscription.backend_integration_status != 'completed'):
                        try:
                            backend_api = BackendApiService()
                            success, response_data = backend_api.create_organization(subscription)
                            
                            if success:
                                logger.info(f"Successfully created backend organization for subscription {subscription_id}")
                            else:
                                logger.error(f"Failed to create backend organization for subscription {subscription_id}: {response_data}")
                                # Don't fail the webhook - the subscription is still active
                                
                        except Exception as e:
                            logger.error(f"Unexpected error during backend integration for subscription {subscription_id}: {e}")
                            subscription.backend_integration_status = 'failed'
                            subscription.backend_integration_data = {'error': str(e)}
                            subscription.save()
                    
                except Subscription.DoesNotExist:
                    logger.error(f"Subscription {subscription_id} not found for checkout session {session_id}")
            
            webhook_event.processed = True
            webhook_event.processed_at = timezone.now()
            webhook_event.save()
            
            return True
            
        except Exception as e:
            logger.error(f"Error handling checkout.session.completed: {e}")
            webhook_event.processing_error = str(e)
            webhook_event.save()
            return False
    
    @staticmethod
    def _handle_checkout_session_expired(event: Dict[str, Any], webhook_event: WebhookEvent) -> bool:
        """Handle expired checkout session"""
        try:
            checkout_session = event['data']['object']
            session_id = checkout_session['id']
            
            # Find related subscription
            subscription_id = checkout_session['metadata'].get('subscription_id')
            if subscription_id:
                try:
                    subscription = Subscription.objects.get(id=subscription_id)
                    subscription.status = 'expired'
                    subscription.save()
                    webhook_event.subscription = subscription
                    
                    logger.info(f"Marked subscription {subscription_id} as expired from checkout session {session_id}")
                    
                except Subscription.DoesNotExist:
                    logger.error(f"Subscription {subscription_id} not found for checkout session {session_id}")
            
            # Update local PaymentIntent record
            try:
                local_pi = PaymentIntent.objects.get(stripe_payment_intent_id=session_id)
                local_pi.status = 'expired'
                local_pi.save()
            except PaymentIntent.DoesNotExist:
                logger.warning(f"Local PaymentIntent record not found for checkout session {session_id}")
            
            webhook_event.processed = True
            webhook_event.processed_at = timezone.now()
            webhook_event.save()
            
            return True
            
        except Exception as e:
            logger.error(f"Error handling checkout.session.expired: {e}")
            webhook_event.processing_error = str(e)
            webhook_event.save()
            return False
    
    @staticmethod
    def _handle_payment_intent_succeeded(event: Dict[str, Any], webhook_event: WebhookEvent) -> bool:
        """Handle successful payment intent"""
        try:
            payment_intent = event['data']['object']
            payment_intent_id = payment_intent['id']
            
            # Find related subscription
            subscription_id = payment_intent['metadata'].get('subscription_id')
            if subscription_id:
                try:
                    subscription = Subscription.objects.get(id=subscription_id)
                    
                    # Idempotency check: Don't reprocess if already active
                    if subscription.status == 'active' and subscription.start_date:
                        logger.info(f"Subscription {subscription_id} already activated, skipping duplicate processing")
                        webhook_event.processed = True
                        webhook_event.processed_at = timezone.now()
                        webhook_event.save()
                        return True
                    
                    # Only process if subscription is in pending/processing state
                    if subscription.status not in ['pending', 'processing']:
                        logger.warning(f"Subscription {subscription_id} in unexpected state {subscription.status} for payment success")
                        webhook_event.processed = True
                        webhook_event.processed_at = timezone.now()
                        webhook_event.save()
                        return True
                    
                    # Use consistent timestamp for all date calculations
                    activation_time = timezone.now()
                    
                    subscription.stripe_payment_intent_id = payment_intent_id
                    subscription.status = 'active'
                    subscription.start_date = activation_time
                    
                    # Set end date based on billing period
                    if subscription.billing_period == 'annual':
                        from dateutil.relativedelta import relativedelta
                        subscription.end_date = activation_time + relativedelta(years=1)
                        subscription.next_billing_date = subscription.end_date
                    else:
                        from dateutil.relativedelta import relativedelta
                        subscription.end_date = activation_time + relativedelta(months=1)
                        subscription.next_billing_date = subscription.end_date
                    
                    subscription.save()
                    
                    webhook_event.subscription = subscription
                    
                    logger.info(f"Activated subscription {subscription_id} from payment intent {payment_intent_id}")
                    
                    # Integrate with backend API to create organization (only if not already done)
                    if (getattr(settings, 'BACKEND_INTEGRATION_ENABLED', True) and 
                        subscription.backend_integration_status != 'completed'):
                        try:
                            backend_api = BackendApiService()
                            success, response_data = backend_api.create_organization(subscription)
                            
                            if success:
                                logger.info(f"Successfully created backend organization for subscription {subscription_id}")
                            else:
                                logger.error(f"Failed to create backend organization for subscription {subscription_id}: {response_data}")
                                # Don't fail the webhook - the subscription is still active
                                # The integration can be retried later
                                
                        except Exception as e:
                            logger.error(f"Unexpected error during backend integration for subscription {subscription_id}: {e}")
                            # Set integration status to failed but don't fail the webhook
                            subscription.backend_integration_status = 'failed'
                            subscription.backend_integration_data = {'error': str(e)}
                            subscription.save()
                    
                except Subscription.DoesNotExist:
                    logger.error(f"Subscription {subscription_id} not found for payment intent {payment_intent_id}")
            
            # Update local PaymentIntent record
            try:
                local_pi = PaymentIntent.objects.get(stripe_payment_intent_id=payment_intent_id)
                local_pi.status = payment_intent['status']
                local_pi.save()
            except PaymentIntent.DoesNotExist:
                logger.warning(f"Local PaymentIntent record not found for {payment_intent_id}")
            
            webhook_event.processed = True
            webhook_event.processed_at = timezone.now()
            webhook_event.save()
            
            return True
            
        except Exception as e:
            logger.error(f"Error handling payment_intent.succeeded: {e}")
            webhook_event.processing_error = str(e)
            webhook_event.save()
            return False
    
    @staticmethod
    def _handle_payment_intent_failed(event: Dict[str, Any], webhook_event: WebhookEvent) -> bool:
        """Handle failed payment intent"""
        try:
            payment_intent = event['data']['object']
            payment_intent_id = payment_intent['id']
            
            # Find related subscription
            subscription_id = payment_intent['metadata'].get('subscription_id')
            if subscription_id:
                try:
                    subscription = Subscription.objects.get(id=subscription_id)
                    subscription.status = 'failed'
                    subscription.save()
                    webhook_event.subscription = subscription
                    
                    logger.info(f"Marked subscription {subscription_id} as failed from payment intent {payment_intent_id}")
                    
                except Subscription.DoesNotExist:
                    logger.error(f"Subscription {subscription_id} not found for payment intent {payment_intent_id}")
            
            # Update local PaymentIntent record
            try:
                local_pi = PaymentIntent.objects.get(stripe_payment_intent_id=payment_intent_id)
                local_pi.status = payment_intent['status']
                local_pi.last_payment_error = payment_intent.get('last_payment_error')
                local_pi.save()
            except PaymentIntent.DoesNotExist:
                logger.warning(f"Local PaymentIntent record not found for {payment_intent_id}")
            
            webhook_event.processed = True
            webhook_event.processed_at = timezone.now()
            webhook_event.save()
            
            return True
            
        except Exception as e:
            logger.error(f"Error handling payment_intent.payment_failed: {e}")
            webhook_event.processing_error = str(e)
            webhook_event.save()
            return False
    
    @staticmethod
    def _handle_invoice_payment_succeeded(event: Dict[str, Any], webhook_event: WebhookEvent) -> bool:
        """Handle successful invoice payment (recurring billing)"""
        try:
            invoice = event['data']['object']
            subscription_id = invoice['subscription']
            
            # Find local subscription by Stripe subscription ID
            try:
                subscription = Subscription.objects.get(stripe_subscription_id=subscription_id)
                subscription.status = 'active'
                
                # Update next billing date
                if subscription.billing_period == 'annual':
                    from dateutil.relativedelta import relativedelta
                    subscription.next_billing_date = timezone.now() + relativedelta(years=1)
                else:
                    from dateutil.relativedelta import relativedelta
                    subscription.next_billing_date = timezone.now() + relativedelta(months=1)
                
                subscription.stripe_invoice_id = invoice['id']
                subscription.save()
                
                webhook_event.subscription = subscription
                
                logger.info(f"Updated subscription {subscription.id} from successful invoice payment")
                
            except Subscription.DoesNotExist:
                logger.error(f"Subscription not found for Stripe subscription {subscription_id}")
            
            webhook_event.processed = True
            webhook_event.processed_at = timezone.now()
            webhook_event.save()
            
            return True
            
        except Exception as e:
            logger.error(f"Error handling invoice.payment_succeeded: {e}")
            webhook_event.processing_error = str(e)
            webhook_event.save()
            return False
    
    @staticmethod
    def _handle_invoice_payment_failed(event: Dict[str, Any], webhook_event: WebhookEvent) -> bool:
        """Handle failed invoice payment"""
        try:
            invoice = event['data']['object']
            subscription_id = invoice['subscription']
            
            try:
                subscription = Subscription.objects.get(stripe_subscription_id=subscription_id)
                subscription.status = 'failed'
                subscription.save()
                
                webhook_event.subscription = subscription
                
                logger.info(f"Marked subscription {subscription.id} as failed from invoice payment failure")
                
            except Subscription.DoesNotExist:
                logger.error(f"Subscription not found for Stripe subscription {subscription_id}")
            
            webhook_event.processed = True
            webhook_event.processed_at = timezone.now()
            webhook_event.save()
            
            return True
            
        except Exception as e:
            logger.error(f"Error handling invoice.payment_failed: {e}")
            webhook_event.processing_error = str(e)
            webhook_event.save()
            return False
    
    @staticmethod
    def _handle_subscription_updated(event: Dict[str, Any], webhook_event: WebhookEvent) -> bool:
        """Handle subscription update"""
        try:
            stripe_subscription = event['data']['object']
            subscription_id = stripe_subscription['id']
            
            try:
                subscription = Subscription.objects.get(stripe_subscription_id=subscription_id)
                
                # Update status based on Stripe subscription status
                stripe_status = stripe_subscription['status']
                if stripe_status == 'active':
                    subscription.status = 'active'
                elif stripe_status == 'canceled':
                    subscription.status = 'cancelled'
                elif stripe_status == 'past_due':
                    subscription.status = 'failed'
                elif stripe_status == 'incomplete':
                    subscription.status = 'processing'
                
                subscription.save()
                webhook_event.subscription = subscription
                
                logger.info(f"Updated subscription {subscription.id} status to {subscription.status}")
                
            except Subscription.DoesNotExist:
                logger.error(f"Subscription not found for Stripe subscription {subscription_id}")
            
            webhook_event.processed = True
            webhook_event.processed_at = timezone.now()
            webhook_event.save()
            
            return True
            
        except Exception as e:
            logger.error(f"Error handling customer.subscription.updated: {e}")
            webhook_event.processing_error = str(e)
            webhook_event.save()
            return False
    
    @staticmethod
    def _handle_subscription_deleted(event: Dict[str, Any], webhook_event: WebhookEvent) -> bool:
        """Handle subscription deletion/cancellation"""
        try:
            stripe_subscription = event['data']['object']
            subscription_id = stripe_subscription['id']
            
            try:
                subscription = Subscription.objects.get(stripe_subscription_id=subscription_id)
                subscription.status = 'cancelled'
                subscription.end_date = timezone.now()
                subscription.save()
                
                webhook_event.subscription = subscription
                
                logger.info(f"Cancelled subscription {subscription.id}")
                
            except Subscription.DoesNotExist:
                logger.error(f"Subscription not found for Stripe subscription {subscription_id}")
            
            webhook_event.processed = True
            webhook_event.processed_at = timezone.now()
            webhook_event.save()
            
            return True
            
        except Exception as e:
            logger.error(f"Error handling customer.subscription.deleted: {e}")
            webhook_event.processing_error = str(e)
            webhook_event.save()
            return False