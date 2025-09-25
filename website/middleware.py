"""
Middleware for main website maintenance mode
"""
from django.shortcuts import render
from django.http import HttpResponse
from website.models import SiteConfig

class WebsiteMaintenanceModeMiddleware:
    """
    Middleware to handle maintenance mode for main website
    """
    def __init__(self, get_response):
        self.get_response = get_response
    def __call__(self, request):
        try:
            config = SiteConfig.objects.first()
            if config and config.maintenance_mode:
                # Allow admin access
                if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser):
                    pass
                elif request.path.startswith('/admin/'):
                    pass
                elif request.path.startswith('/static/') or request.path.startswith('/media/'):
                    pass
                else:
                    context = {
                        'site_config': config,
                        'site_title': config.company_name if config else 'VerionLabs',
                        'support_email': config.email if config else 'contact@verionlabs.com'
                    }
                    response = HttpResponse(
                        render(request, 'website/maintenance.html', context).content,
                        status=503
                    )
                    response['Retry-After'] = '300'
                    return response
        except:
            pass
        return self.get_response(request)
