from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView, ListView, DetailView
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import SiteConfig, Service, TeamMember, Demo, ContactInquiry, NavigationItem
from .forms import ContactForm


def get_site_context():
    """Get common site context data"""
    try:
        site_config = SiteConfig.objects.first()
        if not site_config:
            # Create default site config if none exists
            site_config = SiteConfig.objects.create()
    except Exception:
        site_config = None
    
    return {
        'site_config': site_config,
        'navigation_items': NavigationItem.objects.filter(is_active=True),
    }


class HomeView(TemplateView):
    template_name = 'website/index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_site_context())
        
        # Get featured content
        context['services'] = Service.objects.filter(featured=True)[:3]
        context['featured_demos'] = Demo.objects.filter(featured=True)[:3]
        
        return context


class ServicesView(TemplateView):
    template_name = 'website/services.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_site_context())
        
        context['services'] = Service.objects.all()
        
        # Process steps data
        context['process_steps'] = [
            {
                'title': 'Discovery',
                'description': 'We analyze your business needs, technical requirements, and project goals to create a comprehensive strategy.'
            },
            {
                'title': 'Design',
                'description': 'Our team designs the architecture, user experience, and technical specifications for your solution.'
            },
            {
                'title': 'Development',
                'description': 'We build your solution using best practices, modern technologies, and agile development methodologies.'
            },
            {
                'title': 'Deployment',
                'description': 'We deploy, test, and optimize your solution to ensure smooth operation and maximum performance.'
            }
        ]
        
        # Benefits data
        context['benefits'] = [
            {
                'title': 'Expert Team',
                'description': 'Our experienced developers and architects bring deep expertise across multiple technologies and industries.',
                'icon': 'brain'
            },
            {
                'title': 'Proven Process',
                'description': 'We follow industry best practices and agile methodologies to ensure successful project delivery.',
                'icon': 'code'
            },
            {
                'title': 'Scalable Solutions',
                'description': 'Our solutions are designed to grow with your business, ensuring long-term value and flexibility.',
                'icon': 'cloud'
            },
            {
                'title': 'Quality Assurance',
                'description': 'Rigorous testing and quality control processes ensure reliable, secure, and high-performing solutions.',
                'icon': 'code'
            },
            {
                'title': 'Ongoing Support',
                'description': 'We provide continuous support and maintenance to keep your systems running smoothly.',
                'icon': 'cloud'
            },
            {
                'title': 'Innovation Focus',
                'description': 'We stay at the forefront of technology trends to deliver cutting-edge solutions for our clients.',
                'icon': 'brain'
            }
        ]
        
        return context


class AboutView(TemplateView):
    template_name = 'website/about.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_site_context())
        
        # Get team members and story paragraphs
        context['team_members'] = TeamMember.objects.filter(featured=True)
        
        site_config = context.get('site_config')
        if site_config:
            context['story_paragraphs'] = site_config.story_paragraphs.all()
        
        # Company values data
        context['company_values'] = [
            {
                'title': 'Innovation',
                'description': 'We continuously explore new technologies and methodologies to deliver cutting-edge solutions that drive business growth.',
                'icon': 'brain'
            },
            {
                'title': 'Quality',
                'description': 'Every project we deliver meets the highest standards of quality, reliability, and performance through rigorous testing and best practices.',
                'icon': 'code'
            },
            {
                'title': 'Collaboration',
                'description': 'We work closely with our clients as partners, ensuring transparent communication and shared success throughout every project.',
                'icon': 'cloud'
            },
            {
                'title': 'Expertise',
                'description': 'Our team brings deep technical knowledge and industry experience to solve complex challenges with elegant solutions.',
                'icon': 'brain'
            },
            {
                'title': 'Scalability',
                'description': 'We design solutions that grow with your business, ensuring long-term value and adaptability to changing needs.',
                'icon': 'cloud'
            },
            {
                'title': 'Security',
                'description': 'Security is built into every solution we develop, protecting your data and ensuring compliance with industry standards.',
                'icon': 'code'
            }
        ]
        
        # Company statistics
        context['company_stats'] = [
            {'value': '50+', 'label': 'Projects Delivered'},
            {'value': '25+', 'label': 'Happy Clients'},
            {'value': '5+', 'label': 'Years Experience'},
            {'value': '99.9%', 'label': 'Uptime'},
        ]
        
        return context


class DemosView(ListView):
    model = Demo
    template_name = 'website/demos.html'
    context_object_name = 'demos'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_site_context())
        return context


class DemoDetailView(DetailView):
    model = Demo
    template_name = 'website/demo_detail.html'
    context_object_name = 'demo'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_site_context())
        return context


class ServiceDetailView(DetailView):
    model = Service
    template_name = 'website/service_detail.html'
    context_object_name = 'service'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_site_context())
        return context


class ContactView(TemplateView):
    template_name = 'website/contact.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_site_context())
        context['form'] = ContactForm()
        return context
    
    def post(self, request, *args, **kwargs):
        form = ContactForm(request.POST)
        if form.is_valid():
            # Save the contact inquiry
            contact_inquiry = form.save(commit=False)
            
            # Add tracking information
            contact_inquiry.ip_address = self.get_client_ip(request)
            contact_inquiry.user_agent = request.META.get('HTTP_USER_AGENT', '')
            contact_inquiry.save()
            
            # Send notification email (if configured)
            try:
                self.send_notification_email(contact_inquiry)
                messages.success(request, 'Thank you for your message! We\'ll get back to you within 24 hours.')
            except Exception as e:
                # Log the error but still show success to user
                messages.success(request, 'Thank you for your message! We\'ll get back to you soon.')
            
            return redirect('website:contact')
        else:
            context = self.get_context_data()
            context['form'] = form
            return render(request, self.template_name, context)
    
    def get_client_ip(self, request):
        """Get the client's IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def send_notification_email(self, inquiry):
        """Send notification email to admin"""
        subject = f'New Contact Inquiry: {inquiry.subject}'
        message = f"""
        New contact inquiry received:
        
        Name: {inquiry.full_name}
        Email: {inquiry.email}
        Subject: {inquiry.subject}
        
        Message:
        {inquiry.message}
        
        ---
        Submitted from: {inquiry.ip_address}
        User Agent: {inquiry.user_agent}
        Time: {inquiry.created_at}
        """
        
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [settings.CONTACT_EMAIL] if hasattr(settings, 'CONTACT_EMAIL') else [settings.DEFAULT_FROM_EMAIL]
        
        send_mail(subject, message, from_email, recipient_list, fail_silently=False)
