from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Service, Demo


class StaticViewSitemap(Sitemap):
    """Sitemap for static pages"""
    priority = 0.5
    changefreq = 'weekly'

    def items(self):
        return ['website:home', 'website:services', 'website:about', 'website:demos', 'website:contact']

    def location(self, item):
        return reverse(item)


class ServiceSitemap(Sitemap):
    """Sitemap for service detail pages"""
    changefreq = "monthly"
    priority = 0.7

    def items(self):
        return Service.objects.filter(featured=True)

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return obj.get_absolute_url()


class DemoSitemap(Sitemap):
    """Sitemap for demo detail pages"""
    changefreq = "monthly" 
    priority = 0.6

    def items(self):
        return Demo.objects.all()

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return obj.get_absolute_url()