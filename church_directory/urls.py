from django.urls import path
from . import views

app_name = 'church_directory'

urlpatterns = [
    # Main pages
    path('', views.home, name='home'),
    path('pricing/', views.pricing, name='pricing'),
    path('features/', views.features, name='features'),
    path('about/', views.about, name='about'),
    
    # API endpoints for syncing data to backend
    path('api/pricing-tiers/', views.api_pricing_tiers, name='api_pricing_tiers'),
    path('api/features/', views.api_features, name='api_features'),
    path('contact/', views.contact, name='contact'),
    
    # Subscription flow
    path('checkout/', views.checkout, name='checkout'),
    path('payment-success/<uuid:subscription_id>/', views.payment_success, name='payment_success'),
    path('payment-cancel/', views.payment_cancel, name='payment_cancel'),
    path('payment-failed/', views.payment_failed, name='payment_failed'),
    path('payment-failed/<uuid:subscription_id>/', views.payment_failed, name='payment_failed_with_id'),
    
    # Subscription Management  
    path('subscription-dashboard/', views.subscription_dashboard, name='subscription_dashboard'),
    path('subscription/<uuid:subscription_id>/', views.subscription_detail, name='subscription_detail'),
    
    # AJAX API endpoints
    path('api/apply-coupon/', views.apply_coupon_ajax, name='apply_coupon_ajax'),
    path('api/subscription/<uuid:subscription_id>/cancel/', views.cancel_subscription, name='cancel_subscription'),
    path('api/subscription/<uuid:subscription_id>/retry-integration/', views.retry_backend_integration, name='retry_backend_integration'),
    path('api/subscription/<uuid:subscription_id>/customer-portal/', views.create_customer_portal_session, name='create_customer_portal'),
    path('api/subscription/<uuid:subscription_id>/change-billing/', views.change_billing_cycle, name='change_billing_cycle'),
    path('api/organization-subscription-status/', views.organization_subscription_status_api, name='organization_subscription_status_api'),
    path('subscription-portal/', views.subscription_portal, name='subscription_portal'),
    path('subscription-login/', views.subscription_login, name='subscription_login'),
    path('subscription-auto-login/', views.subscription_auto_login, name='subscription_auto_login'),
    path('my-subscription/', views.subscription_dashboard_authenticated, name='subscription_dashboard_authenticated'),
    
    # Stripe webhooks
    path('webhooks/stripe/', views.stripe_webhook, name='stripe_webhook'),
]