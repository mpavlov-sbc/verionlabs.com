#!/usr/bin/env python
"""
Populate initial data for Church Directory marketing website
"""
import os
import sys
import django
from decimal import Decimal
from datetime import datetime, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'verionlabs_django.settings')
django.setup()

from church_directory.models import PricingTier, Coupon, WebsiteConfig
from django.utils import timezone


def create_pricing_tiers():
    """Create the 4 pricing tiers"""
    print("Creating pricing tiers...")
    
    # Clear existing tiers
    PricingTier.objects.all().delete()
    
    tiers = [
        {
            'name': 'Starter',
            'description': 'Perfect for small churches getting started with digital directories',
            'max_users': 150,
            'monthly_price': Decimal('10.00'),
            'annual_price': Decimal('100.00'),
            'features': [
                'Up to 150 church members',
                'Complete member directory',
                'Contact information management',
                'Group organization',
                'Basic admin dashboard',
                'Mobile app access',
                'Email support'
            ],
            'is_popular': False,
            'sort_order': 1,
        },
        {
            'name': 'Growth',
            'description': 'Ideal for growing congregations with active ministry programs',
            'max_users': 500,
            'monthly_price': Decimal('25.00'),
            'annual_price': Decimal('250.00'),
            'features': [
                'Up to 500 church members',
                'Complete member directory',
                'Advanced contact management',
                'Ministry group organization',
                'Member photo uploads',
                'Push notifications',
                'Advanced admin dashboard',
                'Role-based permissions',
                'Priority email support'
            ],
            'is_popular': True,
            'sort_order': 2,
        },
        {
            'name': 'Community',
            'description': 'Designed for larger churches with extensive member engagement',
            'max_users': 2000,
            'monthly_price': Decimal('50.00'),
            'annual_price': Decimal('500.00'),
            'features': [
                'Up to 2,000 church members',
                'Complete member directory',
                'Advanced contact management',
                'Unlimited ministry groups',
                'Member photo uploads',
                'Custom announcements',
                'Advanced reporting',
                'Multi-admin support',
                'Role-based permissions',
                'Phone & email support'
            ],
            'is_popular': False,
            'sort_order': 3,
        },
        {
            'name': 'Enterprise',
            'description': 'For large churches and multi-campus organizations',
            'max_users': 0,  # Unlimited
            'monthly_price': Decimal('80.00'),
            'annual_price': Decimal('800.00'),
            'features': [
                'Unlimited church members',
                'Complete member directory',
                'Advanced contact management',
                'Unlimited ministry groups',
                'Member photo uploads',
                'Custom announcements',
                'Advanced reporting & analytics',
                'Multi-campus support',
                'Custom integrations',
                'Dedicated account manager',
                'Priority phone support',
                'Training & onboarding'
            ],
            'is_popular': False,
            'sort_order': 4,
        }
    ]
    
    created_tiers = []
    for tier_data in tiers:
        tier = PricingTier.objects.create(**tier_data)
        created_tiers.append(tier)
        print(f"Created tier: {tier}")
    
    return created_tiers


def create_sample_coupons():
    """Create sample discount coupons"""
    print("Creating sample coupons...")
    
    # Clear existing coupons
    Coupon.objects.all().delete()
    
    coupons = [
        {
            'code': 'WELCOME20',
            'name': 'New Customer Welcome',
            'description': '20% off your first subscription',
            'discount_type': 'percentage',
            'discount_value': Decimal('20.00'),
            'max_uses': None,  # Unlimited
            'minimum_amount': None,
            'valid_from': timezone.now(),
            'valid_until': timezone.now() + timedelta(days=365),
            'is_active': True,
        },
        {
            'code': 'LAUNCH50',
            'name': 'Launch Special',
            'description': '50% off for early adopters',
            'discount_type': 'percentage',
            'discount_value': Decimal('50.00'),
            'max_uses': 100,
            'minimum_amount': None,
            'valid_from': timezone.now(),
            'valid_until': timezone.now() + timedelta(days=90),
            'is_active': True,
        },
        {
            'code': 'SPRING10',
            'name': 'Spring Promotion',
            'description': '$10 off any annual plan',
            'discount_type': 'fixed',
            'discount_value': Decimal('10.00'),
            'max_uses': 50,
            'minimum_amount': Decimal('100.00'),
            'valid_from': timezone.now(),
            'valid_until': timezone.now() + timedelta(days=60),
            'is_active': True,
        },
        {
            'code': 'TESTEXPIRED',
            'name': 'Expired Test Coupon',
            'description': 'For testing expired coupons',
            'discount_type': 'percentage',
            'discount_value': Decimal('25.00'),
            'max_uses': None,
            'minimum_amount': None,
            'valid_from': timezone.now() - timedelta(days=30),
            'valid_until': timezone.now() - timedelta(days=1),
            'is_active': True,
        }
    ]
    
    created_coupons = []
    for coupon_data in coupons:
        coupon = Coupon.objects.create(**coupon_data)
        created_coupons.append(coupon)
        print(f"Created coupon: {coupon}")
    
    return created_coupons


def create_website_config():
    """Create website configuration"""
    print("Creating website configuration...")
    
    # Clear existing config
    WebsiteConfig.objects.all().delete()
    
    config = WebsiteConfig.objects.create(
        site_title="Church Directory",
        site_description="The Complete Church Directory Solution for Modern Congregations",
        hero_headline="Stay Connected with Your Church Family – Instantly & Securely",
        hero_subline="Secure member directories that bring congregations closer together",
        support_email="support@verionlabs.com",
        sales_email="sales@verionlabs.com",
        show_pricing=True,
        show_testimonials=True,
        maintenance_mode=False,
        app_store_url="https://apps.apple.com/app/church-directory",
        google_play_url="https://play.google.com/store/apps/details?id=com.verionlabs.churchdirectory"
    )
    
    print(f"Created website config: {config}")
    return config


def main():
    print("Populating Church Directory initial data...")
    print("=" * 50)
    
    # Create all data
    tiers = create_pricing_tiers()
    coupons = create_sample_coupons()
    config = create_website_config()
    
    print("=" * 50)
    print("Data population completed successfully!")
    print(f"Created {len(tiers)} pricing tiers")
    print(f"Created {len(coupons)} sample coupons")
    print("Created website configuration")
    
    print("\nPricing Tiers:")
    for tier in tiers:
        print(f"  - {tier.name}: {tier.users_display} users - ${tier.monthly_price}/month")
    
    print("\nActive Coupons:")
    for coupon in coupons:
        if coupon.is_valid()[0]:
            print(f"  - {coupon.code}: {coupon.description}")


if __name__ == '__main__':
    main()