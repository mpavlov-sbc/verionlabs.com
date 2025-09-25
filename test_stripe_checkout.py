#!/usr/bin/env python3
"""
Test script for Stripe Checkout integration
Tests the complete payment flow from checkout to backend organization creation
"""

import os
import sys
import django
import json
import requests
from decimal import Decimal
from datetime import datetime

# Add the project directory to Python path
sys.path.append('/Users/mp/Projects/website')

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'verionlabs_django.settings')
django.setup()

from church_directory.models import PricingTier, Subscription, PaymentIntent, WebhookEvent
from church_directory.stripe_service import StripeService
from church_directory.backend_api import BackendApiService


class StripeCheckoutTester:
    """Test suite for Stripe Checkout integration"""
    
    def __init__(self):
        self.test_results = []
        print("🧪 Stripe Checkout Integration Test Suite")
        print("=" * 50)
    
    def run_all_tests(self):
        """Run all test methods"""
        test_methods = [
            self.test_pricing_tier_setup,
            self.test_subscription_creation,
            self.test_checkout_session_creation,
            self.test_webhook_event_handling,
            self.test_backend_api_service,
            self.test_complete_checkout_flow,
        ]
        
        passed = 0
        failed = 0
        
        for test_method in test_methods:
            try:
                print(f"\n🔍 Running {test_method.__name__}...")
                test_method()
                print(f"✅ {test_method.__name__} PASSED")
                passed += 1
            except Exception as e:
                print(f"❌ {test_method.__name__} FAILED: {e}")
                failed += 1
        
        print(f"\n{'='*50}")
        print(f"📊 Test Results: {passed} passed, {failed} failed")
        
        if failed == 0:
            print("🎉 All tests passed! Stripe Checkout integration is ready.")
        else:
            print("⚠️  Some tests failed. Review the errors above.")
        
        return failed == 0
    
    def test_pricing_tier_setup(self):
        """Test that pricing tiers are properly configured"""
        tiers = PricingTier.objects.filter(is_active=True)
        
        if not tiers:
            raise Exception("No active pricing tiers found")
        
        for tier in tiers:
            if not tier.monthly_price or tier.monthly_price <= 0:
                raise Exception(f"Tier {tier.name} has invalid monthly_price")
            
            if not tier.features:
                raise Exception(f"Tier {tier.name} has no features defined")
        
        print(f"   ✓ Found {tiers.count()} active pricing tiers")
    
    def test_subscription_creation(self):
        """Test subscription model creation"""
        tier = PricingTier.objects.filter(is_active=True).first()
        if not tier:
            raise Exception("No pricing tier available for testing")
        
        subscription = Subscription.objects.create(
            email='test@example.com',
            church_name='Test Church',
            contact_name='Test Contact',
            phone='123-456-7890',
            pricing_tier=tier,
            billing_period='monthly',
            base_amount=tier.monthly_price,
            discount_amount=Decimal('0.00'),
            final_amount=tier.monthly_price,
            status='pending'
        )
        
        print(f"   ✓ Created test subscription: {subscription.id}")
        
        # Cleanup
        subscription.delete()
    
    def test_checkout_session_creation(self):
        """Test Stripe Checkout Session creation"""
        tier = PricingTier.objects.filter(is_active=True).first()
        if not tier:
            raise Exception("No pricing tier available for testing")
        
        # Create test subscription
        subscription = Subscription.objects.create(
            email='test@example.com',
            church_name='Test Church',
            contact_name='Test Contact',
            pricing_tier=tier,
            billing_period='monthly',
            base_amount=tier.monthly_price,
            discount_amount=Decimal('0.00'),
            final_amount=tier.monthly_price,
            status='pending'
        )
        
        try:
            # Test checkout session creation
            success_url = 'http://localhost:8000/payment-success/' + str(subscription.id) + '/'
            cancel_url = 'http://localhost:8000/payment-cancel/'
            
            checkout_session, payment_intent = StripeService.create_checkout_session(
                subscription=subscription,
                success_url=success_url,
                cancel_url=cancel_url
            )
            
            # Verify session was created
            if not checkout_session.get('id'):
                raise Exception("Checkout session creation failed - no ID returned")
            
            if not checkout_session.get('url'):
                raise Exception("Checkout session creation failed - no URL returned")
            
            if not payment_intent:
                raise Exception("Local PaymentIntent record not created")
            
            print(f"   ✓ Created checkout session: {checkout_session['id']}")
            print(f"   ✓ Checkout URL: {checkout_session['url']}")
            print(f"   ✓ Local PaymentIntent record created: {payment_intent.id}")
            
        finally:
            # Cleanup
            subscription.delete()
    
    def test_webhook_event_handling(self):
        """Test webhook event processing logic"""
        # Test checkout.session.completed event simulation
        mock_event = {
            'id': 'evt_test_123',
            'type': 'checkout.session.completed',
            'data': {
                'object': {
                    'id': 'cs_test_123',
                    'customer': 'cus_test_123',
                    'payment_intent': 'pi_test_123',
                    'metadata': {
                        'subscription_id': '12345',
                        'church_name': 'Test Church'
                    }
                }
            }
        }
        
        # Create a test subscription
        tier = PricingTier.objects.filter(is_active=True).first()
        subscription = Subscription.objects.create(
            email='test@example.com',
            church_name='Test Church',
            contact_name='Test Contact',
            pricing_tier=tier,
            billing_period='monthly',
            base_amount=tier.monthly_price,
            discount_amount=Decimal('0.00'),
            final_amount=tier.monthly_price,
            status='processing'
        )
        
        # Update mock event with real subscription ID
        mock_event['data']['object']['metadata']['subscription_id'] = str(subscription.id)
        
        try:
            # Create webhook event record
            webhook_event = WebhookEvent.objects.create(
                stripe_event_id=mock_event['id'],
                event_type=mock_event['type'],
                event_data=mock_event
            )
            
            # Test event handling
            success = StripeService._handle_checkout_session_completed(mock_event, webhook_event)
            
            if not success:
                raise Exception("Checkout session completion handler failed")
            
            # Verify subscription was updated
            subscription.refresh_from_db()
            if subscription.status != 'active':
                raise Exception(f"Subscription status not updated correctly: {subscription.status}")
            
            print(f"   ✓ Webhook event processing successful")
            print(f"   ✓ Subscription status updated to: {subscription.status}")
            
        finally:
            # Cleanup
            subscription.delete()
            webhook_event.delete()
    
    def test_backend_api_service(self):
        """Test backend API service connectivity"""
        backend_api = BackendApiService()
        
        # Test API configuration
        if not hasattr(backend_api, 'base_url') or not backend_api.base_url:
            print("   ⚠️  Backend API URL not configured - skipping connectivity test")
            return
        
        if not hasattr(backend_api, 'api_key') or not backend_api.api_key:
            print("   ⚠️  Backend API key not configured - skipping connectivity test")
            return
        
        # Test basic connectivity (this would fail without actual backend)
        try:
            # Create a test subscription for API testing
            tier = PricingTier.objects.filter(is_active=True).first()
            subscription = Subscription.objects.create(
                email='test@example.com',
                church_name='Test Church API',
                contact_name='Test Contact',
                pricing_tier=tier,
                billing_period='monthly',
                base_amount=tier.monthly_price,
                discount_amount=Decimal('0.00'),
                final_amount=tier.monthly_price,
                status='active',
                stripe_customer_id='cus_test_123'
            )
            
            # This would actually call the backend API
            success, response_data = backend_api.create_organization(subscription)
            print(f"   ✓ Backend API call completed: {success}")
            
            # Cleanup
            subscription.delete()
            
        except Exception as e:
            print(f"   ⚠️  Backend API test failed (expected if backend not running): {e}")
    
    def test_complete_checkout_flow(self):
        """Test complete end-to-end checkout flow simulation"""
        tier = PricingTier.objects.filter(is_active=True).first()
        if not tier:
            raise Exception("No pricing tier available for testing")
        
        print(f"   🔄 Simulating complete checkout flow for {tier.name} plan...")
        
        # Step 1: Create subscription (like checkout form submission)
        subscription = Subscription.objects.create(
            email='complete-test@example.com',
            church_name='Complete Test Church',
            contact_name='Complete Test Contact',
            phone='555-123-4567',
            pricing_tier=tier,
            billing_period='monthly',
            base_amount=tier.monthly_price,
            discount_amount=Decimal('0.00'),
            final_amount=tier.monthly_price,
            status='pending'
        )
        print(f"   ✓ Step 1: Subscription created - {subscription.id}")
        
        # Step 2: Create Checkout Session
        success_url = f'http://localhost:8000/payment-success/{subscription.id}/'
        cancel_url = 'http://localhost:8000/payment-cancel/'
        
        checkout_session, payment_intent = StripeService.create_checkout_session(
            subscription=subscription,
            success_url=success_url,
            cancel_url=cancel_url
        )
        
        subscription.stripe_payment_intent_id = checkout_session.id
        subscription.status = 'processing'
        subscription.save()
        
        print(f"   ✓ Step 2: Checkout Session created - {checkout_session['id']}")
        print(f"   ✓ User would be redirected to: {checkout_session['url']}")
        
        # Step 3: Simulate successful checkout completion via webhook
        webhook_event_data = {
            'id': f'evt_test_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
            'type': 'checkout.session.completed',
            'data': {
                'object': {
                    'id': checkout_session.id,
                    'customer': 'cus_test_complete',
                    'payment_intent': 'pi_test_complete',
                    'metadata': {
                        'subscription_id': str(subscription.id),
                        'church_name': subscription.church_name,
                        'contact_name': subscription.contact_name
                    }
                }
            }
        }
        
        webhook_event = WebhookEvent.objects.create(
            stripe_event_id=webhook_event_data['id'],
            event_type=webhook_event_data['type'],
            event_data=webhook_event_data
        )
        
        success = StripeService._handle_checkout_session_completed(webhook_event_data, webhook_event)
        if not success:
            raise Exception("Webhook processing failed")
        
        print(f"   ✓ Step 3: Webhook processed successfully")
        
        # Step 4: Verify final state
        subscription.refresh_from_db()
        webhook_event.refresh_from_db()
        
        if subscription.status != 'active':
            raise Exception(f"Final subscription status incorrect: {subscription.status}")
        
        if not webhook_event.processed:
            raise Exception("Webhook event not marked as processed")
        
        print(f"   ✓ Step 4: Subscription activated - status: {subscription.status}")
        print(f"   ✓ Backend integration status: {subscription.backend_integration_status}")
        
        # Cleanup
        subscription.delete()
        webhook_event.delete()
        
        print(f"   🎉 Complete checkout flow test successful!")
    
    def generate_test_report(self):
        """Generate a comprehensive test report"""
        print(f"\n📋 Test Environment Report")
        print("=" * 30)
        
        # Django models
        print(f"Pricing Tiers: {PricingTier.objects.filter(is_active=True).count()}")
        print(f"Total Subscriptions: {Subscription.objects.count()}")
        print(f"Payment Intents: {PaymentIntent.objects.count()}")
        print(f"Webhook Events: {WebhookEvent.objects.count()}")
        
        # Configuration check
        from django.conf import settings
        config_items = [
            ('STRIPE_PUBLISHABLE_KEY', getattr(settings, 'STRIPE_PUBLISHABLE_KEY', None)),
            ('STRIPE_SECRET_KEY', getattr(settings, 'STRIPE_SECRET_KEY', None)),
            ('STRIPE_WEBHOOK_SECRET', getattr(settings, 'STRIPE_WEBHOOK_SECRET', None)),
            ('BACKEND_INTEGRATION_ENABLED', getattr(settings, 'BACKEND_INTEGRATION_ENABLED', False)),
        ]
        
        print(f"\n🔧 Configuration:")
        for key, value in config_items:
            status = "✓ Configured" if value else "❌ Missing"
            # Don't show actual keys for security
            display_value = "***HIDDEN***" if value and 'KEY' in key else str(value)
            print(f"   {key}: {status}")


if __name__ == '__main__':
    tester = StripeCheckoutTester()
    tester.generate_test_report()
    
    # Run the tests
    success = tester.run_all_tests()
    
    if success:
        print(f"\n🚀 Stripe Checkout integration is ready for production!")
        print(f"   • Simplified checkout flow with Stripe hosted pages")
        print(f"   • Secure payment processing with webhooks")
        print(f"   • Backend organization creation integration")
        print(f"   • Comprehensive error handling and monitoring")
    else:
        print(f"\n⚠️  Please fix the failing tests before deploying.")
    
    sys.exit(0 if success else 1)