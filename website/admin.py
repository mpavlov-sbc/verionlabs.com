from django.contrib import admin
from django.utils.html import format_html
from .models import (
    SiteConfig, StoryParagraph, Service, ServiceTechnology, 
    TeamMember, Demo, DemoTag, ContactInquiry, NavigationItem, DevelopmentBanner
)


class StoryParagraphInline(admin.TabularInline):
    """Inline editor for story paragraphs"""
    model = StoryParagraph
    extra = 1
    fields = ['content', 'order']
    ordering = ['order']


@admin.register(SiteConfig)
class SiteConfigAdmin(admin.ModelAdmin):
    """Admin interface for site configuration"""
    
    list_display = ['company_name', 'domain', 'email', 'updated_at']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [StoryParagraphInline]
    
    fieldsets = (
        ('Company Information', {
            'fields': ('company_name', 'domain', 'email', 'phone', 'address')
        }),
        ('Site Content', {
            'fields': ('description', 'mission')
        }),
        ('Hero Section', {
            'fields': ('hero_headline', 'hero_subheadline', 'hero_cta_text'),
            'classes': ['collapse']
        }),
        ('Mission Section', {
            'fields': ('mission_title', 'mission_content'),
            'classes': ['collapse']
        }),
        ('Contact CTA', {
            'fields': ('contact_cta_title', 'contact_cta_description', 'contact_cta_button_text'),
            'classes': ['collapse']
        }),
        ('About Page', {
            'fields': ('about_story_title', 'about_vision_title', 'about_vision_content'),
            'classes': ['collapse']
        }),
        ('Social Media', {
            'fields': ('linkedin_url', 'github_url', 'twitter_url'),
            'classes': ['collapse']
        }),
        ('SEO', {
            'fields': ('meta_keywords',),
            'classes': ['collapse']
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ['collapse']
        }),
    )
    
    def has_delete_permission(self, request, obj=None):
        # Prevent deletion of site config
        return False
    
    def has_add_permission(self, request):
        # Only allow one site config instance
        return not SiteConfig.objects.exists()


class ServiceTechnologyInline(admin.TabularInline):
    """Inline editor for service technologies"""
    model = ServiceTechnology
    extra = 1
    fields = ['name', 'order']
    ordering = ['order']


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    """Admin interface for services"""
    
    list_display = ['title', 'icon', 'featured', 'order']
    list_filter = ['featured', 'icon']
    list_editable = ['featured', 'order']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ServiceTechnologyInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'icon', 'description', 'detailed_description')
        }),
        ('Display Settings', {
            'fields': ('featured', 'order')
        }),
        ('SEO', {
            'fields': ('meta_description',),
            'classes': ['collapse']
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ['collapse']
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    """Admin interface for team members"""
    
    list_display = ['name', 'role', 'featured', 'order']
    list_filter = ['featured', 'role']
    list_editable = ['featured', 'order']
    search_fields = ['name', 'role', 'bio']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'role', 'bio')
        }),
        ('Images', {
            'fields': ('image', 'image_url'),
            'description': 'Upload an image or provide an external URL. Uploaded image takes priority.'
        }),
        ('Social Links', {
            'fields': ('linkedin_url', 'github_url', 'twitter_url'),
            'classes': ['collapse']
        }),
        ('Display Settings', {
            'fields': ('featured', 'order')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ['collapse']
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']


class DemoTagInline(admin.TabularInline):
    """Inline editor for demo tags"""
    model = DemoTag
    extra = 1
    fields = ['name', 'order']
    ordering = ['order']


@admin.register(Demo)
class DemoAdmin(admin.ModelAdmin):
    """Admin interface for demos"""
    
    list_display = ['title', 'featured', 'order', 'live_demo_url', 'github_url']
    list_filter = ['featured']
    list_editable = ['featured', 'order']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [DemoTagInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'description')
        }),
        ('Images', {
            'fields': ('image', 'image_url'),
            'description': 'Upload an image or provide an external URL. Uploaded image takes priority.'
        }),
        ('Links', {
            'fields': ('live_demo_url', 'github_url')
        }),
        ('Display Settings', {
            'fields': ('featured', 'order')
        }),
        ('SEO', {
            'fields': ('meta_description',),
            'classes': ['collapse']
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ['collapse']
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']


@admin.register(ContactInquiry)
class ContactInquiryAdmin(admin.ModelAdmin):
    """Admin interface for contact inquiries"""
    
    list_display = ['full_name', 'email', 'subject', 'status', 'priority', 'created_at']
    list_filter = ['status', 'priority', 'created_at']
    search_fields = ['full_name', 'email', 'subject', 'message']
    readonly_fields = ['full_name', 'email', 'subject', 'message', 'ip_address', 'user_agent', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Contact Information', {
            'fields': ('full_name', 'email', 'subject', 'message')
        }),
        ('Management', {
            'fields': ('status', 'priority', 'notes')
        }),
        ('Technical Information', {
            'fields': ('ip_address', 'user_agent'),
            'classes': ['collapse']
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ['collapse']
        }),
    )
    
    def has_add_permission(self, request):
        # Contact inquiries should only be created through the form
        return False


@admin.register(NavigationItem)
class NavigationItemAdmin(admin.ModelAdmin):
    """Admin interface for navigation items"""
    
    list_display = ['name', 'url', 'order', 'is_active', 'is_external']
    list_filter = ['is_active', 'is_external']
    list_editable = ['order', 'is_active']
    search_fields = ['name', 'url']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'url')
        }),
        ('Settings', {
            'fields': ('order', 'is_active', 'is_external')
        }),
    )


@admin.register(DevelopmentBanner)
class DevelopmentBannerAdmin(admin.ModelAdmin):
    """Admin interface for development banner"""
    
    list_display = ['message', 'is_active', 'background_color', 'text_color', 'updated_at']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Banner Content', {
            'fields': ('is_active', 'message')
        }),
        ('Styling', {
            'fields': ('background_color', 'text_color'),
            'description': 'Use Tailwind CSS classes like "bg-blue-600" or "text-white"'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ['collapse']
        }),
    )
    
    def has_delete_permission(self, request, obj=None):
        # Prevent deletion of banner config
        return False
    
    def has_add_permission(self, request):
        # Only allow one banner instance
        return not DevelopmentBanner.objects.exists()


# Customize admin site header and title
admin.site.site_header = "VerionLabs Administration"
admin.site.site_title = "VerionLabs Admin"
admin.site.index_title = "Welcome to VerionLabs Administration"
