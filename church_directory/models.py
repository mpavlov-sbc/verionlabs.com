from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
from django.utils import timezone
import uuid


class PricingTier(models.Model):
    """Pricing tiers for church directory subscriptions"""
    name = models.CharField(max_length=100, help_text="e.g., 'Starter', 'Growth', 'Premium'")
    description = models.TextField(help_text="Brief description of the tier")
    max_users = models.PositiveIntegerField(
        help_text="Maximum number of users allowed (0 for unlimited)"
    )
    monthly_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Monthly subscription price in USD"
    )
    annual_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Annual subscription price in USD (optional)"
    )
    features = models.JSONField(
        default=list,
        help_text="List of features included in this tier"
    )
    is_popular = models.BooleanField(
        default=False,
        help_text="Mark as popular choice (for highlighting in pricing table)"
    )
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['sort_order', 'monthly_price']
        verbose_name = "Pricing Tier"
        verbose_name_plural = "Pricing Tiers"

    def __str__(self):
        users_text = f"{self.max_users} users" if self.max_users > 0 else "Unlimited users"
        return f"{self.name} - {users_text} - ${self.monthly_price}/month"

    @property
    def users_display(self):
        return f"Up to {self.max_users}" if self.max_users > 0 else "Unlimited"

    @property
    def annual_discount_percent(self):
        if self.annual_price and self.monthly_price:
            monthly_yearly = self.monthly_price * 12
            discount = ((monthly_yearly - self.annual_price) / monthly_yearly) * 100
            return round(discount)
        return 0


class Coupon(models.Model):
    """Discount coupons for subscriptions"""
    DISCOUNT_TYPES = [
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount'),
    ]
    
    code = models.CharField(
        max_length=50,
        unique=True,
        help_text="Coupon code (e.g., 'WELCOME20')"
    )
    name = models.CharField(
        max_length=100,
        help_text="Internal name for the coupon"
    )
    description = models.TextField(
        blank=True,
        help_text="Description of the coupon offer"
    )
    discount_type = models.CharField(
        max_length=20,
        choices=DISCOUNT_TYPES,
        default='percentage'
    )
    discount_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Percentage (0-100) or fixed amount in USD"
    )
    max_uses = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Maximum number of times this coupon can be used (blank for unlimited)"
    )
    used_count = models.PositiveIntegerField(default=0)
    minimum_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Minimum purchase amount required"
    )
    valid_from = models.DateTimeField(default=timezone.now)
    valid_until = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Leave blank for no expiration"
    )
    applicable_tiers = models.ManyToManyField(
        PricingTier,
        blank=True,
        help_text="Leave blank to apply to all tiers"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Coupon"
        verbose_name_plural = "Coupons"

    def __str__(self):
        if self.discount_type == 'percentage':
            return f"{self.code} - {self.discount_value}% off"
        return f"{self.code} - ${self.discount_value} off"

    def is_valid(self):
        """Check if coupon is currently valid"""
        now = timezone.now()
        
        # Check if active
        if not self.is_active:
            return False, "Coupon is not active"
        
        # Check date validity
        if self.valid_from and now < self.valid_from:
            return False, "Coupon is not yet valid"
        
        if self.valid_until and now > self.valid_until:
            return False, "Coupon has expired"
        
        # Check usage limit
        if self.max_uses and self.used_count >= self.max_uses:
            return False, "Coupon usage limit exceeded"
        
        return True, "Valid"

    def calculate_discount(self, amount):
        """Calculate discount amount for given price"""
        if self.discount_type == 'percentage':
            return (amount * self.discount_value) / 100
        else:
            return min(self.discount_value, amount)

    def can_apply_to_tier(self, tier):
        """Check if coupon can be applied to a specific tier"""
        if not self.applicable_tiers.exists():
            return True  # No restrictions
        return self.applicable_tiers.filter(id=tier.id).exists()


class Subscription(models.Model):
    """Customer subscriptions"""
    BILLING_PERIODS = [
        ('monthly', 'Monthly'),
        ('annual', 'Annual'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
        ('suspended', 'Suspended'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Customer information
    email = models.EmailField()
    church_name = models.CharField(max_length=200)
    contact_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, blank=True)
    
    # Subscription details
    pricing_tier = models.ForeignKey(PricingTier, on_delete=models.PROTECT)
    billing_period = models.CharField(max_length=20, choices=BILLING_PERIODS, default='monthly')
    
    # Pricing
    base_amount = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    final_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Coupon information
    coupon_used = models.ForeignKey(
        Coupon,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    # Status and dates
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    
    # Payment information
    stripe_customer_id = models.CharField(max_length=100, blank=True)
    stripe_subscription_id = models.CharField(max_length=100, blank=True)
    stripe_payment_intent_id = models.CharField(max_length=100, blank=True)
    
    # Metadata
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Subscription"
        verbose_name_plural = "Subscriptions"

    def __str__(self):
        return f"{self.church_name} - {self.pricing_tier.name} ({self.status})"

    @property
    def is_active(self):
        return self.status == 'active'

    def calculate_pricing(self, coupon=None):
        """Calculate final pricing with optional coupon"""
        if self.billing_period == 'annual' and self.pricing_tier.annual_price:
            base_amount = self.pricing_tier.annual_price
        else:
            base_amount = self.pricing_tier.monthly_price
        
        discount_amount = 0
        if coupon:
            is_valid, message = coupon.is_valid()
            if is_valid and coupon.can_apply_to_tier(self.pricing_tier):
                if coupon.minimum_amount and base_amount < coupon.minimum_amount:
                    pass  # Don't apply discount
                else:
                    discount_amount = coupon.calculate_discount(base_amount)
        
        final_amount = base_amount - discount_amount
        
        return {
            'base_amount': base_amount,
            'discount_amount': discount_amount,
            'final_amount': max(final_amount, 0)  # Ensure non-negative
        }


class Lead(models.Model):
    """Marketing leads from the website"""
    email = models.EmailField()
    church_name = models.CharField(max_length=200, blank=True)
    contact_name = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    message = models.TextField(blank=True)
    source = models.CharField(
        max_length=50,
        default='website',
        help_text="Source of the lead (e.g., 'pricing_page', 'contact_form')"
    )
    interested_tier = models.ForeignKey(
        PricingTier,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    is_contacted = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Lead"
        verbose_name_plural = "Leads"

    def __str__(self):
        name = self.contact_name or self.email
        church = f" ({self.church_name})" if self.church_name else ""
        return f"{name}{church}"


class WebsiteConfig(models.Model):
    """Configuration for the Church Directory marketing website"""
    site_title = models.CharField(max_length=200, default="Church Directory")
    site_description = models.TextField(
        default="The Complete Church Directory Solution for Modern Congregations"
    )
    hero_headline = models.CharField(
        max_length=200,
        default="Stay Connected with Your Church Family – Instantly & Securely"
    )
    hero_subline = models.TextField(
        default="Secure member directories that bring congregations closer together"
    )
    
    # Contact information
    support_email = models.EmailField(default="support@verionlabs.com")
    sales_email = models.EmailField(default="sales@verionlabs.com")
    
    # Feature flags
    show_pricing = models.BooleanField(default=True)
    show_testimonials = models.BooleanField(default=True)
    maintenance_mode = models.BooleanField(default=False)
    
    # Social media links
    app_store_url = models.URLField(blank=True)
    google_play_url = models.URLField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Website Configuration"
        verbose_name_plural = "Website Configuration"

    def __str__(self):
        return self.site_title

    def save(self, *args, **kwargs):
        # Ensure only one configuration object exists
        if not self.pk and WebsiteConfig.objects.exists():
            raise ValueError("Only one WebsiteConfig instance is allowed")
        super().save(*args, **kwargs)


class TeamMember(models.Model):
    """Team members displayed on the About page."""
    
    name = models.CharField(max_length=100)
    title = models.CharField(max_length=100)
    bio = models.TextField(help_text="Brief description of the team member")
    
    # Avatar options
    avatar_initials = models.CharField(max_length=3, help_text="2-3 initials for avatar (e.g., 'MP')")
    avatar_color = models.CharField(
        max_length=50, 
        default="bg-gradient-to-br from-blue-400 to-blue-600",
        help_text="Tailwind CSS classes for avatar background (e.g., 'bg-gradient-to-br from-blue-400 to-blue-600')"
    )
    
    # Display options
    is_active = models.BooleanField(default=True, help_text="Show this team member on the website")
    display_order = models.PositiveIntegerField(default=0, help_text="Order in which to display (lower numbers first)")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['display_order', 'name']
        verbose_name = "Team Member"
        verbose_name_plural = "Team Members"
    
    def __str__(self):
        return f"{self.name} - {self.title}"
