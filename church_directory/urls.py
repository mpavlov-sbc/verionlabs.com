from django.urls import path
from . import views

app_name = 'church_directory'

urlpatterns = [
    # Main pages
    path('', views.home, name='home'),
    path('pricing/', views.pricing, name='pricing'),
    path('features/', views.features, name='features'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    
    # Subscription flow
    path('checkout/', views.checkout, name='checkout'),
    path('payment-success/<uuid:subscription_id>/', views.payment_success, name='payment_success'),
    path('payment-cancel/', views.payment_cancel, name='payment_cancel'),
    path('payment-failed/', views.payment_failed, name='payment_failed'),
    path('payment-failed/<uuid:subscription_id>/', views.payment_failed, name='payment_failed_with_id'),
    
    # Subscription Management
    path('subscription-dashboard/', views.subscription_dashboard, name='subscription_dashboard'),
    
    # AJAX API endpoints
    path('api/apply-coupon/', views.apply_coupon_ajax, name='apply_coupon_ajax'),
    path('api/subscription-status/', views.SubscriptionStatusView.as_view(), name='subscription_status'),
    path('api/subscription/<uuid:subscription_id>/status/', views.subscription_status, name='subscription_status_detail'),
    path('api/subscription/<uuid:subscription_id>/cancel/', views.cancel_subscription, name='cancel_subscription'),
    path('api/subscription/<uuid:subscription_id>/retry-integration/', views.retry_backend_integration, name='retry_backend_integration'),
    
    # Stripe webhooks
    path('webhooks/stripe/', views.stripe_webhook, name='stripe_webhook'),
]