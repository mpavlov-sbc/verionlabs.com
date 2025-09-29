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
        ('processing', 'Processing'),
        ('active', 'Active'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
        ('suspended', 'Suspended'),
        ('failed', 'Payment Failed'),
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
    trial_end_date = models.DateTimeField(null=True, blank=True)
    next_billing_date = models.DateTimeField(null=True, blank=True)
    
    # Payment information
    stripe_customer_id = models.CharField(max_length=100, blank=True)
    stripe_subscription_id = models.CharField(max_length=100, blank=True)
    stripe_payment_intent_id = models.CharField(max_length=100, blank=True)
    stripe_payment_method_id = models.CharField(max_length=100, blank=True)
    stripe_invoice_id = models.CharField(max_length=100, blank=True)
    
    # Integration with main backend
    backend_organization_id = models.CharField(max_length=100, blank=True, help_text="Organization ID in the main church directory backend")
    backend_tenant_slug = models.CharField(max_length=63, blank=True, help_text="Tenant slug for the organization in the main backend")
    backend_integration_status = models.CharField(max_length=20, default='not_started', choices=[
        ('not_started', 'Not Started'),
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ])
    backend_integration_error = models.TextField(blank=True, help_text="Error message if integration failed")
    
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
    
    # Basic site information
    site_title = models.CharField(max_length=200, default="Church Directory")
    site_description = models.TextField(
        default="The Complete Church Directory Solution for Modern Congregations"
    )
    company_name = models.CharField(max_length=100, default="VerionLabs")
    domain = models.CharField(max_length=100, default="directory.verionlabs.com")
    
    # Hero section
    hero_headline = models.CharField(
        max_length=200,
        default="Stay Connected with Your Church Family – Instantly & Securely"
    )
    hero_subline = models.TextField(
        default="Secure member directories that bring congregations closer together"
    )
    hero_cta_primary = models.CharField(max_length=50, default="Get Started Today")
    hero_cta_secondary = models.CharField(max_length=50, default="Learn More")
    
    # About page content
    about_headline = models.CharField(
        max_length=200,
        default="Building Stronger Church Communities"
    )
    about_subline = models.TextField(
        default="Church Directory was born from a simple belief: technology should bring people together, not drive them apart. We're passionate about helping churches foster genuine relationships and meaningful connections."
    )
    about_story_title = models.CharField(max_length=100, default="Our Story")
    about_values_title = models.CharField(max_length=100, default="Our Values")
    
    # Features section
    features_headline = models.CharField(
        max_length=200,
        default="Built Specifically for Churches"
    )
    features_subline = models.TextField(
        default="Every feature is designed with the unique needs, values, and privacy concerns of faith communities in mind."
    )
    
    # Pricing section
    pricing_headline = models.CharField(
        max_length=200,
        default="Simple, Transparent Pricing"
    )
    pricing_subline = models.TextField(
        default="Choose the plan that fits your congregation size. All plans include our core features with no hidden fees."
    )
    
    # Use cases section
    use_cases_headline = models.CharField(
        max_length=200,
        default="See It In Action"
    )
    use_cases_subline = models.TextField(
        default="Real scenarios from churches using Church Directory to strengthen their communities."
    )
    
    # CTA sections
    cta_headline = models.CharField(
        max_length=200,
        default="Ready to Connect Your Congregation?"
    )
    cta_subline = models.TextField(
        default="Join thousands of churches already using Church Directory to build stronger communities and streamline member management."
    )
    cta_button_primary = models.CharField(max_length=50, default="Start Free Trial")
    cta_button_secondary = models.CharField(max_length=50, default="Schedule Demo")
    
    # Contact information
    support_email = models.EmailField(default="support@verionlabs.com")
    sales_email = models.EmailField(default="sales@verionlabs.com")
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True)
    
    # Feature flags
    show_pricing = models.BooleanField(default=True)
    show_testimonials = models.BooleanField(default=True)
    show_use_cases = models.BooleanField(default=True)
    show_team = models.BooleanField(default=True)
    maintenance_mode = models.BooleanField(default=False)
    
    # Social media and app links
    app_store_url = models.URLField(blank=True)
    google_play_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    facebook_url = models.URLField(blank=True)
    
    # Footer links
    help_center_url = models.URLField(
        blank=True,
        help_text="URL for Help Center page (external link)"
    )
    privacy_policy_url = models.URLField(
        blank=True,
        help_text="URL for Privacy Policy page (external link)"
    )
    terms_of_service_url = models.URLField(
        blank=True,
        help_text="URL for Terms of Service page (external link)"
    )
    
    # SEO Settings
    meta_keywords = models.TextField(
        default="church directory, member management, church software, congregation management", 
        help_text="Comma-separated keywords"
    )
    
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


class Feature(models.Model):
    """Features displayed on the homepage and features page"""
    
    ICON_CHOICES = [
        ('users', 'Users'),
        ('shield', 'Shield'),
        ('users-group', 'User Group'),
        ('clipboard', 'Clipboard'),
        ('mobile', 'Mobile'),
        ('cog', 'Settings'),
        ('chart', 'Chart'),
        ('bell', 'Bell'),
        ('heart', 'Heart'),
        ('lock', 'Lock'),
    ]
    
    title = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=20, choices=ICON_CHOICES, default='users')
    
    # Display settings
    featured_on_homepage = models.BooleanField(default=True, help_text="Show on homepage")
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0, help_text="Display order")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'title']
        verbose_name = "Feature"
        verbose_name_plural = "Features"
        
    def __str__(self):
        return self.title


class Value(models.Model):
    """Company values displayed on the about page"""
    
    ICON_CHOICES = [
        ('heart', 'Heart'),
        ('shield', 'Shield'),
        ('check', 'Check'),
        ('users', 'Users'),
        ('info', 'Info'),
        ('star', 'Star'),
        ('cross', 'Cross'),
        ('hands', 'Hands'),
    ]
    
    title = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=20, choices=ICON_CHOICES, default='heart')
    
    # Display settings
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0, help_text="Display order")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'title']
        verbose_name = "Value"
        verbose_name_plural = "Values"
        
    def __str__(self):
        return self.title


class UseCase(models.Model):
    """Use cases/testimonials displayed on the homepage"""
    
    persona_name = models.CharField(max_length=100, help_text="e.g., 'Pastor Mike', 'Sarah'")
    persona_role = models.CharField(max_length=100, help_text="e.g., 'The Ministry Leader', 'The Caring Congregant'")
    quote = models.TextField(help_text="The testimonial quote")
    
    # Display settings
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0, help_text="Display order")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'persona_name']
        verbose_name = "Use Case"
        verbose_name_plural = "Use Cases"
        
    def __str__(self):
        return f"{self.persona_name} - {self.persona_role}"


class AboutStoryParagraph(models.Model):
    """Paragraphs for the about story section"""
    
    content = models.TextField()
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order']
        verbose_name = "About Story Paragraph"
        verbose_name_plural = "About Story Paragraphs"
        
    def __str__(self):
        return f"Story Paragraph {self.order}: {self.content[:50]}..."


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
        verbose_name = "Team Member"
        verbose_name_plural = "Team Members"
    
    def __str__(self):
        return f"{self.name} - {self.title}"


class PaymentIntent(models.Model):
    """Track Stripe Payment Intents and Checkout Sessions for better payment flow management"""
    
    STATUS_CHOICES = [
        # Payment Intent statuses
        ('requires_payment_method', 'Requires Payment Method'),
        ('requires_confirmation', 'Requires Confirmation'),
        ('requires_action', 'Requires Action'),
        ('processing', 'Processing'),
        ('requires_capture', 'Requires Capture'),
        ('canceled', 'Canceled'),
        ('succeeded', 'Succeeded'),
        
        # Checkout Session statuses
        ('pending', 'Pending'), # Checkout session created but not completed
        ('completed', 'Completed'), # Checkout session completed successfully
        ('expired', 'Expired'), # Checkout session expired
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    stripe_payment_intent_id = models.CharField(
        max_length=100, 
        unique=True,
        help_text="Stripe Payment Intent ID or Checkout Session ID"
    )
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name='payment_intents')
    
    # Payment details
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='usd')
    status = models.CharField(max_length=30, choices=STATUS_CHOICES)
    
    # Client secret for frontend (or checkout URL for sessions)
    client_secret = models.CharField(
        max_length=500, 
        blank=True,
        help_text="Payment Intent client secret or Checkout Session URL"
    )
    
    # Metadata
    stripe_metadata = models.JSONField(default=dict, blank=True)
    last_payment_error = models.JSONField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Payment Intent"
        verbose_name_plural = "Payment Intents"
    
    def __str__(self):
        return f"Payment Intent {self.stripe_payment_intent_id} - ${self.amount} ({self.status})"
    
    @property
    def is_checkout_session(self):
        """Check if this record represents a Checkout Session rather than Payment Intent"""
        return self.stripe_payment_intent_id.startswith('cs_')


class WebhookEvent(models.Model):
    """Track Stripe webhook events for debugging and audit trail"""
    
    EVENT_TYPES = [
        ('payment_intent.succeeded', 'Payment Intent Succeeded'),
        ('payment_intent.payment_failed', 'Payment Intent Failed'),
        ('invoice.payment_succeeded', 'Invoice Payment Succeeded'),
        ('invoice.payment_failed', 'Invoice Payment Failed'),
        ('customer.subscription.created', 'Subscription Created'),
        ('customer.subscription.updated', 'Subscription Updated'),
        ('customer.subscription.deleted', 'Subscription Deleted'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    stripe_event_id = models.CharField(max_length=100, unique=True)
    event_type = models.CharField(max_length=50)
    processed = models.BooleanField(default=False)
    processing_error = models.TextField(blank=True)
    
    # Full event data from Stripe
    event_data = models.JSONField()
    
    # Related subscription if applicable
    subscription = models.ForeignKey(
        Subscription, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='webhook_events'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Webhook Event"
        verbose_name_plural = "Webhook Events"
    
    def __str__(self):
        status = "Processed" if self.processed else "Pending"
        return f"{self.event_type} - {self.stripe_event_id} ({status})"


class MobileAuthToken(models.Model):
    """Temporary tokens for mobile-to-web authentication bridge"""
    token = models.CharField(max_length=100, unique=True, db_index=True)
    organization_schema = models.CharField(max_length=100)
    user_id = models.CharField(max_length=50)
    username = models.CharField(max_length=150)
    organization_name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Mobile Auth Token"
        verbose_name_plural = "Mobile Auth Tokens"
    
    def __str__(self):
        return f"Token for {self.username} ({self.organization_name})"
    
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    def is_valid(self):
        return not self.used and not self.is_expired()
