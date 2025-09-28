from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    PricingTier, Coupon, Subscription, Lead, WebsiteConfig, TeamMember,
    Feature, Value, UseCase, AboutStoryParagraph
)


@admin.register(PricingTier)
class PricingTierAdmin(admin.ModelAdmin):
    list_display = ['name', 'max_users_display', 'monthly_price', 'annual_price', 'is_popular', 'is_active', 'sort_order']
    list_filter = ['is_active', 'is_popular', 'created_at']
    list_editable = ['is_popular', 'is_active', 'sort_order']
    search_fields = ['name', 'description']
    ordering = ['sort_order', 'monthly_price']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'max_users', 'sort_order')
        }),
        ('Pricing', {
            'fields': ('monthly_price', 'annual_price')
        }),
        ('Features', {
            'fields': ('features',),
            'description': 'Enter features as a JSON list, e.g., ["Feature 1", "Feature 2"]'
        }),
        ('Settings', {
            'fields': ('is_popular', 'is_active')
        })
    )
    
    def max_users_display(self, obj):
        if obj.max_users == 0:
            return mark_safe('<span style="color: green;"><strong>Unlimited</strong></span>')
        return f"{obj.max_users:,} users"
    max_users_display.short_description = 'User Limit'
    max_users_display.admin_order_field = 'max_users'
    
    def get_queryset(self, request):
        return super().get_queryset(request).order_by('sort_order', 'monthly_price')


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'discount_display', 'usage_display', 'validity_status', 'is_active']
    list_filter = ['discount_type', 'is_active', 'valid_from', 'valid_until', 'created_at']
    list_editable = ['is_active']
    search_fields = ['code', 'name', 'description']
    readonly_fields = ['used_count', 'created_at', 'updated_at']
    filter_horizontal = ['applicable_tiers']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('code', 'name', 'description')
        }),
        ('Discount Settings', {
            'fields': ('discount_type', 'discount_value', 'minimum_amount')
        }),
        ('Usage Limits', {
            'fields': ('max_uses', 'used_count')
        }),
        ('Validity Period', {
            'fields': ('valid_from', 'valid_until')
        }),
        ('Applicable Plans', {
            'fields': ('applicable_tiers',),
            'description': 'Leave empty to apply to all pricing tiers'
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def discount_display(self, obj):
        if obj.discount_type == 'percentage':
            return f"{obj.discount_value}% off"
        return f"${obj.discount_value} off"
    discount_display.short_description = 'Discount'
    
    def usage_display(self, obj):
        if obj.max_uses:
            percentage = (obj.used_count / obj.max_uses) * 100
            color = 'red' if percentage > 90 else 'orange' if percentage > 75 else 'green'
            return mark_safe(f'<span style="color: {color};">{obj.used_count}/{obj.max_uses}</span>')
        return f"{obj.used_count}/∞"
    usage_display.short_description = 'Usage'
    
    def validity_status(self, obj):
        is_valid, message = obj.is_valid()
        if is_valid:
            return mark_safe('<span style="color: green;">✓ Valid</span>')
        return mark_safe(f'<span style="color: red;">✗ {message}</span>')
    validity_status.short_description = 'Status'


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['church_name', 'contact_name', 'pricing_tier', 'billing_period', 'final_amount', 'status', 'backend_integration_status_display', 'created_at']
    list_filter = ['status', 'billing_period', 'pricing_tier', 'backend_integration_status', 'created_at']
    list_editable = ['status']
    search_fields = ['church_name', 'contact_name', 'email', 'backend_tenant_slug']
    readonly_fields = ['id', 'created_at', 'updated_at', 'stripe_customer_id', 'stripe_subscription_id', 'stripe_payment_intent_id']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Subscription ID', {
            'fields': ('id',),
            'classes': ('collapse',)
        }),
        ('Customer Information', {
            'fields': ('church_name', 'contact_name', 'email', 'phone')
        }),
        ('Subscription Details', {
            'fields': ('pricing_tier', 'billing_period', 'status')
        }),
        ('Pricing', {
            'fields': ('base_amount', 'discount_amount', 'final_amount', 'coupon_used')
        }),
        ('Dates', {
            'fields': ('start_date', 'end_date')
        }),
        ('Backend Integration', {
            'fields': ('backend_integration_status', 'backend_organization_id', 'backend_tenant_slug', 'backend_integration_error'),
            'description': 'Status of integration with the main church directory backend'
        }),
        ('Payment Information', {
            'fields': ('stripe_customer_id', 'stripe_subscription_id', 'stripe_payment_intent_id'),
            'classes': ('collapse',)
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    actions = ['mark_active', 'mark_cancelled', 'retry_backend_integration', 'retry_failed_backend_integrations']
    
    def backend_integration_status_display(self, obj):
        """Display backend integration status with color coding"""
        status = obj.backend_integration_status
        status_colors = {
            'not_started': 'gray',
            'pending': 'orange', 
            'processing': 'blue',
            'completed': 'green',
            'failed': 'red',
        }
        color = status_colors.get(status, 'gray')
        display_text = status.replace('_', ' ').title()
        
        if status == 'failed' and obj.backend_integration_error:
            # Show error message on hover
            return mark_safe(f'<span style="color: {color};" title="{obj.backend_integration_error[:100]}">✗ {display_text}</span>')
        elif status == 'completed':
            return mark_safe(f'<span style="color: {color};">✓ {display_text}</span>')
        else:
            return mark_safe(f'<span style="color: {color};">{display_text}</span>')
    
    backend_integration_status_display.short_description = 'Backend Status'
    backend_integration_status_display.admin_order_field = 'backend_integration_status'
    
    def mark_active(self, request, queryset):
        updated = queryset.update(status='active')
        self.message_user(request, f'{updated} subscriptions marked as active.')
    mark_active.short_description = "Mark selected subscriptions as active"
    
    def mark_cancelled(self, request, queryset):
        updated = queryset.update(status='cancelled')
        self.message_user(request, f'{updated} subscriptions marked as cancelled.')
    mark_cancelled.short_description = "Mark selected subscriptions as cancelled"
    
    def retry_backend_integration(self, request, queryset):
        """Retry backend integration for selected subscriptions"""
        from .backend_api import BackendApiService
        
        backend_api = BackendApiService()
        successful = 0
        failed = 0
        skipped = 0
        
        for subscription in queryset:
            if subscription.backend_integration_status == 'completed':
                skipped += 1
                continue
                
            try:
                success, response_data = backend_api.retry_organization_creation(subscription)
                if success:
                    successful += 1
                else:
                    failed += 1
            except Exception as e:
                failed += 1
                # Update subscription with error info if not already set
                subscription.backend_integration_error = str(e)
                subscription.save()
        
        message = f'Backend integration retry completed: {successful} successful, {failed} failed'
        if skipped > 0:
            message += f', {skipped} skipped (already completed)'
            
        self.message_user(request, message)
    
    retry_backend_integration.short_description = "Retry backend integration for selected subscriptions"
    
    def retry_failed_backend_integrations(self, request, queryset):
        """Retry backend integration for all failed subscriptions in the system"""
        from .backend_api import BackendApiService
        
        backend_api = BackendApiService()
        results = backend_api.retry_failed_integrations()
        
        message = f'Bulk retry completed: {results["successful"]} successful, {results["failed"]} failed'
        if results['skipped'] > 0:
            message += f', {results["skipped"]} skipped'
            
        self.message_user(request, message)
    
    retry_failed_backend_integrations.short_description = "Retry ALL failed backend integrations (system-wide)"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('pricing_tier', 'coupon_used')


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ['contact_info', 'church_name', 'source', 'interested_tier', 'is_contacted', 'created_at']
    list_filter = ['is_contacted', 'source', 'interested_tier', 'created_at']
    list_editable = ['is_contacted']
    search_fields = ['email', 'contact_name', 'church_name']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Contact Information', {
            'fields': ('email', 'contact_name', 'church_name', 'phone')
        }),
        ('Lead Details', {
            'fields': ('message', 'source', 'interested_tier')
        }),
        ('Follow-up', {
            'fields': ('is_contacted', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    actions = ['mark_contacted', 'mark_not_contacted']
    
    def contact_info(self, obj):
        name = obj.contact_name or 'Unknown'
        return f"{name} ({obj.email})"
    contact_info.short_description = 'Contact'
    
    def mark_contacted(self, request, queryset):
        updated = queryset.update(is_contacted=True)
        self.message_user(request, f'{updated} leads marked as contacted.')
    mark_contacted.short_description = "Mark selected leads as contacted"
    
    def mark_not_contacted(self, request, queryset):
        updated = queryset.update(is_contacted=False)
        self.message_user(request, f'{updated} leads marked as not contacted.')
    mark_not_contacted.short_description = "Mark selected leads as not contacted"


@admin.register(WebsiteConfig)
class WebsiteConfigAdmin(admin.ModelAdmin):
    list_display = ['site_title', 'maintenance_mode', 'show_pricing', 'show_testimonials', 'show_team']
    
    fieldsets = (
        ('Basic Site Information', {
            'fields': ('site_title', 'site_description', 'company_name', 'domain')
        }),
        ('Hero Section', {
            'fields': ('hero_headline', 'hero_subline', 'hero_cta_primary', 'hero_cta_secondary')
        }),
        ('About Page Content', {
            'fields': ('about_headline', 'about_subline', 'about_story_title', 'about_values_title')
        }),
        ('Section Headlines', {
            'fields': (
                'features_headline', 'features_subline',
                'pricing_headline', 'pricing_subline',
                'use_cases_headline', 'use_cases_subline'
            )
        }),
        ('Call-to-Action Section', {
            'fields': ('cta_headline', 'cta_subline', 'cta_button_primary', 'cta_button_secondary')
        }),
        ('Contact Information', {
            'fields': ('support_email', 'sales_email', 'phone', 'address')
        }),
        ('Feature Toggles', {
            'fields': ('show_pricing', 'show_testimonials', 'show_use_cases', 'show_team', 'maintenance_mode')
        }),
        ('Social Media & App Links', {
            'fields': ('app_store_url', 'google_play_url', 'linkedin_url', 'twitter_url', 'facebook_url')
        }),
        ('Footer Links', {
            'fields': ('help_center_url', 'privacy_policy_url', 'terms_of_service_url')
        }),
        ('SEO Settings', {
            'fields': ('meta_keywords',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def has_add_permission(self, request):
        # Only allow one configuration instance
        return not WebsiteConfig.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Don't allow deleting the configuration
        return False


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ['name', 'title', 'avatar_preview', 'is_active', 'display_order', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'title', 'bio']
    list_editable = ['is_active', 'display_order']
    ordering = ['display_order', 'name']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'title', 'bio')
        }),
        ('Avatar Settings', {
            'fields': ('avatar_initials', 'avatar_color'),
            'description': 'Configure the avatar display for this team member'
        }),
        ('Display Options', {
            'fields': ('is_active', 'display_order')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def avatar_preview(self, obj):
        """Show a preview of how the avatar will look"""
        return format_html(
            '<div class="w-8 h-8 {} rounded-full flex items-center justify-center text-white text-xs font-bold">{}</div>',
            obj.avatar_color,
            obj.avatar_initials
        )
    avatar_preview.short_description = "Avatar Preview"
    
    class Media:
        css = {
            'all': ('https://cdn.tailwindcss.com/3.3.0/tailwind.min.css',)
        }


@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    list_display = ['title', 'icon', 'featured_on_homepage', 'is_active', 'order']
    list_filter = ['featured_on_homepage', 'is_active', 'icon']
    list_editable = ['featured_on_homepage', 'is_active', 'order']
    search_fields = ['title', 'description']
    ordering = ['order', 'title']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'icon')
        }),
        ('Display Settings', {
            'fields': ('featured_on_homepage', 'is_active', 'order')
        })
    )


@admin.register(Value)
class ValueAdmin(admin.ModelAdmin):
    list_display = ['title', 'icon', 'is_active', 'order']
    list_filter = ['is_active', 'icon']
    list_editable = ['is_active', 'order']
    search_fields = ['title', 'description']
    ordering = ['order', 'title']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'icon')
        }),
        ('Display Settings', {
            'fields': ('is_active', 'order')
        })
    )


@admin.register(UseCase)
class UseCaseAdmin(admin.ModelAdmin):
    list_display = ['persona_name', 'persona_role', 'is_active', 'order']
    list_filter = ['is_active']
    list_editable = ['is_active', 'order']
    search_fields = ['persona_name', 'persona_role', 'quote']
    ordering = ['order', 'persona_name']
    
    fieldsets = (
        ('Persona Information', {
            'fields': ('persona_name', 'persona_role')
        }),
        ('Testimonial', {
            'fields': ('quote',)
        }),
        ('Display Settings', {
            'fields': ('is_active', 'order')
        })
    )


@admin.register(AboutStoryParagraph)
class AboutStoryParagraphAdmin(admin.ModelAdmin):
    list_display = ['paragraph_preview', 'order', 'is_active']
    list_filter = ['is_active']
    list_editable = ['order', 'is_active']
    ordering = ['order']
    
    fieldsets = (
        ('Content', {
            'fields': ('content',)
        }),
        ('Display Settings', {
            'fields': ('order', 'is_active')
        })
    )
    
    def paragraph_preview(self, obj):
        return f"Paragraph {obj.order}: {obj.content[:100]}..."
    paragraph_preview.short_description = 'Preview'


# Customize admin site header
admin.site.site_header = "Church Directory Admin"
admin.site.site_title = "Church Directory"
admin.site.index_title = "Church Directory Administration"
