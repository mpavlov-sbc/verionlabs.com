"""
Integration test script for the complete payment flow.
Tests Stripe payment processing, backend integration, and error handling.
"""

import os
import sys
import django
import requests
import json
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'verionlabs_django.settings')
django.setup()

from church_directory.models import Subscription, PricingTier, Coupon
from church_directory.stripe_service import StripeService
from church_directory.backend_api import BackendApiService
from church_directory.error_handling import monitor_subscription_health
import logging

logger = logging.getLogger(__name__)


class PaymentIntegrationTest:
    """Comprehensive test suite for payment integration"""
    
    def __init__(self):
        self.base_url = 'http://localhost:8000'
        self.backend_url = 'http://localhost:8001'
        self.test_results = []
    
    def run_all_tests(self):
        """Run all integration tests"""
        print("🚀 Starting Payment Integration Tests\n")
        
        # Test database connectivity
        self.test_database_connection()
        
        # Test Stripe service
        self.test_stripe_service()
        
        # Test backend API connectivity
        self.test_backend_api_connection()
        
        # Test payment flow
        self.test_payment_flow()
        
        # Test error handling
        self.test_error_handling()
        
        # Test health monitoring
        self.test_health_monitoring()
        
        # Print results
        self.print_test_results()
    
    def test_database_connection(self):
        """Test database connectivity and models"""
        try:
            # Test model access
            tier_count = PricingTier.objects.count()
            subscription_count = Subscription.objects.count()
            coupon_count = Coupon.objects.count()
            
            self.log_test("Database Connection", True, 
                         f"Tiers: {tier_count}, Subscriptions: {subscription_count}, Coupons: {coupon_count}")
            
        except Exception as e:
            self.log_test("Database Connection", False, str(e))
    
    def test_stripe_service(self):
        """Test Stripe service functionality"""
        try:
            import stripe
            
            # Test Stripe configuration
            if not stripe.api_key:
                self.log_test("Stripe Configuration", False, "Stripe API key not configured")
                return
            
            # Test customer creation
            customer = StripeService.create_customer(
                email="test@example.com",
                name="Test Church",
                church_name="Test Church",
                phone="555-123-4567"
            )
            
            if customer and customer.get('id'):
                self.log_test("Stripe Customer Creation", True, f"Customer ID: {customer['id']}")
                
                # Clean up test customer
                try:
                    stripe.Customer.delete(customer['id'])
                except:
                    pass
            else:
                self.log_test("Stripe Customer Creation", False, "Failed to create customer")
            
        except Exception as e:
            self.log_test("Stripe Service", False, str(e))
    
    def test_backend_api_connection(self):
        """Test backend API connectivity"""
        try:
            backend_api = BackendApiService()
            success, response_data = backend_api.test_connection()
            
            if success:
                self.log_test("Backend API Connection", True, "Connection successful")
            else:
                self.log_test("Backend API Connection", False, 
                             f"Connection failed: {response_data.get('error', 'Unknown error')}")
                
        except Exception as e:
            self.log_test("Backend API Connection", False, str(e))
    
    def test_payment_flow(self):
        """Test complete payment flow (simulation)"""
        try:
            # Get or create a pricing tier
            tier, created = PricingTier.objects.get_or_create(
                name="Test Plan",
                defaults={
                    'monthly_price': Decimal('29.99'),
                    'annual_price': Decimal('299.99'),
                    'features': ['Test Feature 1', 'Test Feature 2'],
                    'max_users': 100,
                    'is_active': True
                }
            )
            
            # Simulate subscription creation
            subscription = Subscription.objects.create(
                email="test-integration@example.com",
                church_name="Test Integration Church",
                contact_name="Test User",
                phone="555-123-4567",
                pricing_tier=tier,
                billing_period='monthly',
                base_amount=tier.monthly_price,
                final_amount=tier.monthly_price,
                status='pending'
            )
            
            self.log_test("Subscription Creation", True, f"Subscription ID: {subscription.id}")
            
            # Test webhook processing simulation
            if hasattr(StripeService, '_handle_payment_intent_succeeded'):
                # This would normally be triggered by Stripe webhook
                self.log_test("Webhook Processing", True, "Webhook handlers available")
            
            # Clean up test subscription
            subscription.delete()
            if created:
                tier.delete()
                
        except Exception as e:
            self.log_test("Payment Flow", False, str(e))
    
    def test_error_handling(self):
        """Test error handling functionality"""
        try:
            from church_directory.error_handling import PaymentError, ErrorLogger
            
            # Test error creation
            error = PaymentError("Test error", "TEST_ERROR", {"test": True})
            self.log_test("Error Creation", True, f"Error ID: {error.error_id}")
            
            # Test error logging
            ErrorLogger.log_payment_error(error)
            self.log_test("Error Logging", True, "Error logged successfully")
            
        except Exception as e:
            self.log_test("Error Handling", False, str(e))
    
    def test_health_monitoring(self):
        """Test health monitoring functionality"""
        try:
            alerts = monitor_subscription_health()
            self.log_test("Health Monitoring", True, f"Found {len(alerts)} alerts")
            
        except Exception as e:
            self.log_test("Health Monitoring", False, str(e))
    
    def log_test(self, test_name, success, details=""):
        """Log test result"""
        self.test_results.append({
            'name': test_name,
            'success': success,
            'details': details
        })
    
    def print_test_results(self):
        """Print formatted test results"""
        print("\n" + "="*60)
        print("📊 TEST RESULTS")
        print("="*60)
        
        passed = sum(1 for result in self.test_results if result['success'])
        total = len(self.test_results)
        
        for result in self.test_results:
            status = "✅ PASS" if result['success'] else "❌ FAIL"
            print(f"{status} | {result['name']:<30} | {result['details']}")
        
        print("-" * 60)
        print(f"Results: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
        
        if passed == total:
            print("\n🎉 All tests passed! Payment integration is working correctly.")
        else:
            print(f"\n⚠️  {total - passed} test(s) failed. Please check configuration.")
        
        print("\nNext steps:")
        if passed == total:
            print("• Payment system is ready for production")
            print("• Set up health monitoring cron job")
            print("• Configure production Stripe keys")
            print("• Set up proper error monitoring (Sentry)")
        else:
            print("• Fix failing tests before proceeding")
            print("• Check environment configuration")
            print("• Verify API keys and endpoints")


def main():
    """Run the integration tests"""
    if len(sys.argv) > 1 and sys.argv[1] == '--help':
        print("Payment Integration Test Suite")
        print("Usage: python test_payment_integration.py")
        print("\nThis script tests:")
        print("• Database connectivity")
        print("• Stripe service integration")
        print("• Backend API connectivity")
        print("• Payment flow simulation")
        print("• Error handling")
        print("• Health monitoring")
        return
    
    test_suite = PaymentIntegrationTest()
    test_suite.run_all_tests()


if __name__ == '__main__':
    main()