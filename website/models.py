from django.db import models
from django.urls import reverse
from django.core.validators import URLValidator, EmailValidator


class SiteConfig(models.Model):
    """Site-wide configuration and company information"""
    
    company_name = models.CharField(max_length=100, default="VerionLabs")
    domain = models.CharField(max_length=100, default="verionlabs.com")
    email = models.EmailField(default="contact@verionlabs.com")
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(default="123 Innovation Drive, Tech Valley, CA 94000")
    description = models.TextField(
        default="VerionLabs provides innovative software solutions for modern businesses, specializing in cloud architecture, AI & machine learning, and custom web applications."
    )
    mission = models.TextField(
        default="We empower businesses with cutting-edge technology solutions that drive growth, efficiency, and innovation in the digital age."
    )
    
    # Social Media Links
    linkedin_url = models.URLField(blank=True, null=True, default="https://linkedin.com/company/verionlabs")
    github_url = models.URLField(blank=True, null=True, default="https://github.com/verionlabs")
    twitter_url = models.URLField(blank=True, null=True, default="https://twitter.com/verionlabs")
    
    # Hero Section
    hero_headline = models.CharField(max_length=200, default="Innovative Software Solutions for Modern Business")
    hero_subheadline = models.TextField(
        default="We transform ideas into powerful digital experiences that drive business growth and technological advancement."
    )
    hero_cta_text = models.CharField(max_length=50, default="Explore Our Services")
    
    # Mission Section
    mission_title = models.CharField(max_length=100, default="Our Mission")
    mission_content = models.TextField(
        default="At VerionLabs, we believe technology should be a catalyst for business success. We partner with companies from startups to enterprises, delivering custom software solutions that solve real-world challenges and unlock new opportunities for growth."
    )
    
    # Contact CTA Section
    contact_cta_title = models.CharField(max_length=100, default="Ready to Transform Your Business?")
    contact_cta_description = models.TextField(
        default="Let's discuss how our innovative solutions can help you achieve your goals and stay ahead of the competition."
    )
    contact_cta_button_text = models.CharField(max_length=50, default="Get Started Today")
    
    # About Section
    about_story_title = models.CharField(max_length=100, default="Our Story")
    about_vision_title = models.CharField(max_length=100, default="Our Vision")
    about_vision_content = models.TextField(
        default="To be the trusted technology partner that empowers businesses to thrive in the digital future, one innovative solution at a time."
    )
    
    # SEO Settings
    meta_keywords = models.TextField(
        default="software development, web applications, cloud architecture, AI, machine learning", 
        help_text="Comma-separated keywords"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Site Configuration"
        verbose_name_plural = "Site Configuration"
    
    def __str__(self):
        return f"{self.company_name} Configuration"
    
    def save(self, *args, **kwargs):
        # Ensure only one instance exists
        if not self.pk and SiteConfig.objects.exists():
            raise ValueError("Only one SiteConfig instance is allowed")
        super().save(*args, **kwargs)


class StoryParagraph(models.Model):
    """Paragraphs for the about story section"""
    
    site_config = models.ForeignKey(SiteConfig, on_delete=models.CASCADE, related_name='story_paragraphs')
    content = models.TextField()
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order']
        
    def __str__(self):
        return f"Story Paragraph {self.order}: {self.content[:50]}..."


class Service(models.Model):
    """Services offered by the company"""
    
    ICON_CHOICES = [
        ('cloud', 'Cloud'),
        ('brain', 'Brain/AI'),
        ('code', 'Code'),
        ('database', 'Database'),
        ('mobile', 'Mobile'),
        ('security', 'Security'),
        ('analytics', 'Analytics'),
        ('integration', 'Integration'),
    ]
    
    title = models.CharField(max_length=100)
    description = models.TextField(help_text="Brief description for cards")
    detailed_description = models.TextField(help_text="Detailed description for service pages")
    icon = models.CharField(max_length=20, choices=ICON_CHOICES, default='code')
    
    # Display settings
    featured = models.BooleanField(default=True, help_text="Show on homepage")
    order = models.PositiveIntegerField(default=0, help_text="Display order")
    
    # SEO
    slug = models.SlugField(unique=True, help_text="URL slug for this service")
    meta_description = models.TextField(blank=True, help_text="Meta description for SEO")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'title']
        
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('service_detail', kwargs={'slug': self.slug})


class ServiceTechnology(models.Model):
    """Technologies used in each service"""
    
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='technologies')
    name = models.CharField(max_length=50)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order', 'name']
        unique_together = ['service', 'name']
        
    def __str__(self):
        return f"{self.service.title} - {self.name}"


class TeamMember(models.Model):
    """Team members and their information"""
    
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    bio = models.TextField()
    image = models.ImageField(upload_to='team/', blank=True, null=True)
    image_url = models.URLField(blank=True, null=True, help_text="External image URL if not uploading")
    
    # Social Links
    linkedin_url = models.URLField(blank=True, null=True)
    github_url = models.URLField(blank=True, null=True)
    twitter_url = models.URLField(blank=True, null=True)
    
    # Display settings
    featured = models.BooleanField(default=True, help_text="Show on about page")
    order = models.PositiveIntegerField(default=0, help_text="Display order")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'name']
        
    def __str__(self):
        return f"{self.name} - {self.role}"
    
    def get_image_url(self):
        """Return image URL, preferring uploaded image over external URL"""
        if self.image:
            return self.image.url
        return self.image_url


class Demo(models.Model):
    """Project demos and portfolio items"""
    
    title = models.CharField(max_length=150)
    description = models.TextField()
    image = models.ImageField(upload_to='demos/', blank=True, null=True)
    image_url = models.URLField(blank=True, null=True, help_text="External image URL if not uploading")
    
    # Links
    live_demo_url = models.URLField(blank=True, null=True)
    github_url = models.URLField(blank=True, null=True)
    
    # Display settings
    featured = models.BooleanField(default=False, help_text="Show on homepage")
    order = models.PositiveIntegerField(default=0, help_text="Display order")
    
    # SEO
    slug = models.SlugField(unique=True, help_text="URL slug for this demo")
    meta_description = models.TextField(blank=True, help_text="Meta description for SEO")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'title']
        
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('demo_detail', kwargs={'slug': self.slug})
    
    def get_image_url(self):
        """Return image URL, preferring uploaded image over external URL"""
        if self.image:
            return self.image.url
        return self.image_url


class DemoTag(models.Model):
    """Tags for categorizing demos"""
    
    demo = models.ForeignKey(Demo, on_delete=models.CASCADE, related_name='tags')
    name = models.CharField(max_length=50)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order', 'name']
        unique_together = ['demo', 'name']
        
    def __str__(self):
        return f"{self.demo.title} - {self.name}"


class ContactInquiry(models.Model):
    """Contact form submissions"""
    
    STATUS_CHOICES = [
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('archived', 'Archived'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    
    # Management fields
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    notes = models.TextField(blank=True, help_text="Internal notes for follow-up")
    
    # Tracking
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Contact Inquiry"
        verbose_name_plural = "Contact Inquiries"
        
    def __str__(self):
        return f"{self.full_name} - {self.subject} ({self.status})"


class NavigationItem(models.Model):
    """Dynamic navigation menu items"""
    
    name = models.CharField(max_length=50)
    url = models.CharField(max_length=200, help_text="URL path or external URL")
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    is_external = models.BooleanField(default=False, help_text="Is this an external link?")
    
    class Meta:
        ordering = ['order', 'name']
        
    def __str__(self):
        return self.name


class DevelopmentBanner(models.Model):
    """Development progress banner configuration"""
    
    is_active = models.BooleanField(
        default=True, 
        help_text="Show the development banner on the website"
    )
    message = models.CharField(
        max_length=200, 
        default="Development in Progress - Opening Soon!",
        help_text="Banner message text"
    )
    background_color = models.CharField(
        max_length=20, 
        default="bg-blue-600",
        help_text="Tailwind CSS background color class"
    )
    text_color = models.CharField(
        max_length=20, 
        default="text-white",
        help_text="Tailwind CSS text color class"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Development Banner"
        verbose_name_plural = "Development Banner"
        
    def __str__(self):
        status = "Active" if self.is_active else "Inactive"
        return f"Development Banner ({status})"
    
    def save(self, *args, **kwargs):
        # Ensure only one instance exists
        if not self.pk and DevelopmentBanner.objects.exists():
            raise ValueError("Only one DevelopmentBanner instance is allowed")
        super().save(*args, **kwargs)
