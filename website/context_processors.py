from .models import SiteConfig, NavigationItem, DevelopmentBanner


def site_config(request):
    """
    Context processor to make site configuration available in all templates
    """
    try:
        config = SiteConfig.objects.first()
    except SiteConfig.DoesNotExist:
        config = None
    
    try:
        development_banner = DevelopmentBanner.objects.first()
    except DevelopmentBanner.DoesNotExist:
        development_banner = None
    
    navigation_items = NavigationItem.objects.filter(is_active=True).order_by('order')
    
    return {
        'site_config': config,
        'navigation_items': navigation_items,
        'development_banner': development_banner,
    }