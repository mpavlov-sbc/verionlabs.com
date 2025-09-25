from django.conf import settings
from .models import WebsiteConfig, Feature, Value, UseCase, AboutStoryParagraph, TeamMember, PricingTier


def church_directory_config(request):
    """
    Add church directory configuration to template context
    """
    try:
        config = WebsiteConfig.objects.first()
    except WebsiteConfig.DoesNotExist:
        config = None
    
    # Get active features for homepage
    featured_features = Feature.objects.filter(
        is_active=True, 
        featured_on_homepage=True
    ).order_by('order', 'title')[:6]  # Limit to 6 for layout
    
    # Get all active features for features page
    all_features = Feature.objects.filter(is_active=True).order_by('order', 'title')
    
    # Get active values for about page
    values = Value.objects.filter(is_active=True).order_by('order', 'title')
    
    # Get active use cases for homepage
    use_cases = UseCase.objects.filter(is_active=True).order_by('order', 'persona_name')[:3]  # Limit to 3 for layout
    
    # Get active story paragraphs for about page
    story_paragraphs = AboutStoryParagraph.objects.filter(is_active=True).order_by('order')
    
    # Get active team members for about page
    team_members = TeamMember.objects.filter(is_active=True).order_by('display_order', 'name')
    
    # Get featured pricing tiers for homepage
    featured_tiers = PricingTier.objects.filter(
        is_active=True
    ).order_by('sort_order', 'monthly_price')[:3]  # Show top 3 on homepage
    
    return {
        'church_config': config,
        'church_featured_features': featured_features,
        'church_all_features': all_features,
        'church_values': values,
        'church_use_cases': use_cases,
        'church_story_paragraphs': story_paragraphs,
        'church_team_members': team_members,
        'church_featured_tiers': featured_tiers,
    }