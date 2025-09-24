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
    path('checkout/<int:tier_id>/', views.checkout, name='checkout'),
    path('payment/<uuid:subscription_id>/', views.payment_process, name='payment_process'),
    path('success/<uuid:subscription_id>/', views.payment_success, name='payment_success'),
    path('cancel/', views.payment_cancel, name='payment_cancel'),
    
    # API endpoints
    path('api/validate-coupon/', views.validate_coupon, name='validate_coupon'),
]