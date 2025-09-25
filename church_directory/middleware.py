"""
Middleware for Church Directory app
"""
from django.shortcuts import render
from django.http import HttpResponse
from django.urls import reverse
from django.contrib.admin.views.decorators import staff_member_required
from .models import WebsiteConfig


class MaintenanceModeMiddleware:
    """
    Middleware to handle maintenance mode for church directory
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Check if maintenance mode is enabled
        try:
            config = WebsiteConfig.objects.first()
            if config and config.maintenance_mode:
                # Allow admin access
                if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser):
                    # Allow access to admin and staff users
                    pass
                elif request.path.startswith('/admin/'):
                    # Always allow admin login page
                    pass
                elif request.path.startswith('/directory/'):
                    # Return maintenance page for any church directory URLs
                    context = {
                        'church_config': config,
                        'site_title': config.site_title if config else 'Church Directory',
                        'support_email': config.support_email if config else 'support@verionlabs.com'
                    }
                    response = HttpResponse(
                        render(request, 'church_directory/maintenance.html', context).content,
                        status=503
                    )
                    response['Retry-After'] = '300'  # Suggest retry after 5 minutes
                    return response
        except:
            # If there's any error checking config, proceed normally
            pass
        
        response = self.get_response(request)
        return response