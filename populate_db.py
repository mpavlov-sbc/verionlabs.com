#!/usr/bin/env python
"""
Django database population script.
This script populates the database with initial data for the website.
"""

import os
import sys
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'verionlabs_django.settings')
django.setup()

from website.models import (
    SiteConfig, NavigationItem, Service, ServiceTechnology, 
    TeamMember, Demo, DemoTag, ContactInquiry
)

def create_navigation_items():
    """Create navigation menu items."""
    nav_items = [
        {'name': 'Home', 'url': 'website:home', 'order': 1, 'is_external': False},
        {'name': 'Services', 'url': 'website:services', 'order': 2, 'is_external': False},
        {'name': 'About', 'url': 'website:about', 'order': 3, 'is_external': False},
        {'name': 'Demos', 'url': 'website:demos', 'order': 4, 'is_external': False},
    ]
    
    for item_data in nav_items:
        nav_item, created = NavigationItem.objects.get_or_create(
            name=item_data['name'],
            defaults=item_data
        )
        if created:
            print(f"Created navigation item: {nav_item.name}")
        else:
            print(f"Navigation item already exists: {nav_item.name}")

def create_services():
    """Create service offerings."""
    services_data = [
        {
            'title': 'AI & Machine Learning Solutions',
            'slug': 'ai-machine-learning',
            'description': 'Harness the power of artificial intelligence to transform your business processes.',
            'detailed_description': '''Our AI and Machine Learning solutions help businesses automate complex processes, gain insights from data, and make intelligent decisions. We develop custom ML models, implement natural language processing systems, and create predictive analytics platforms.

Key offerings include:
• Custom ML model development
• Natural Language Processing (NLP)
• Computer Vision applications
• Predictive analytics
• AI-powered automation
• Data science consulting''',
            'icon': 'brain',
            'featured': True,
            'order': 1,
            'technologies': ['Python', 'TensorFlow', 'PyTorch', 'Scikit-learn', 'OpenAI API']
        },
        {
            'title': 'Cloud Infrastructure & DevOps',
            'slug': 'cloud-devops',
            'description': 'Scalable cloud solutions and automated deployment pipelines for modern applications.',
            'detailed_description': '''We design and implement robust cloud infrastructure solutions that scale with your business. Our DevOps expertise ensures smooth deployment processes, monitoring, and maintenance of your applications.

Key offerings include:
• Cloud architecture design (AWS, Azure, GCP)
• Containerization with Docker & Kubernetes
• CI/CD pipeline setup
• Infrastructure as Code (IaC)
• Monitoring and logging solutions
• Cloud migration services''',
            'icon': 'cloud',
            'featured': True,
            'order': 2,
            'technologies': ['AWS', 'Docker', 'Kubernetes', 'Terraform', 'Jenkins', 'Ansible']
        },
        {
            'title': 'Custom Software Development',
            'slug': 'custom-software',
            'description': 'Tailored software solutions built to meet your specific business requirements.',
            'detailed_description': '''Our team develops custom software applications that perfectly align with your business processes. From web applications to mobile apps and enterprise software, we deliver solutions that drive growth.

Key offerings include:
• Web application development
• Mobile app development (iOS/Android)
• Enterprise software solutions
• API development and integration
• Database design and optimization
• Software architecture consulting''',
            'icon': 'code',
            'featured': True,
            'order': 3,
            'technologies': ['React', 'Vue.js', 'Django', 'Node.js', 'React Native', 'PostgreSQL']
        }
    ]
    
    for service_data in services_data:
        technologies = service_data.pop('technologies', [])
        service, created = Service.objects.get_or_create(
            slug=service_data['slug'],
            defaults=service_data
        )
        
        if created:
            print(f"Created service: {service.title}")
            
            # Add technologies
            for tech_name in technologies:
                tech, _ = ServiceTechnology.objects.get_or_create(
                    service=service,
                    name=tech_name
                )
        else:
            print(f"Service already exists: {service.title}")

def create_team_members():
    """Create team member profiles."""
    team_data = [
        {
            'name': 'John Smith',
            'role': 'CEO & Founder',
            'bio': 'Experienced technology leader with 15+ years in software development and AI solutions.',
            'linkedin_url': 'https://linkedin.com/in/johnsmith',
            'order': 1,
            'featured': True
        },
        {
            'name': 'Sarah Johnson',
            'role': 'CTO',
            'bio': 'Machine Learning expert specializing in natural language processing and computer vision.',
            'linkedin_url': 'https://linkedin.com/in/sarahjohnson',
            'order': 2,
            'featured': True
        },
        {
            'name': 'Mike Chen',
            'role': 'Lead Developer',
            'bio': 'Full-stack developer with expertise in cloud architecture and DevOps practices.',
            'github_url': 'https://github.com/mikechen',
            'order': 3,
            'featured': True
        }
    ]
    
    for member_data in team_data:
        member, created = TeamMember.objects.get_or_create(
            name=member_data['name'],
            defaults=member_data
        )
        if created:
            print(f"Created team member: {member.name}")
        else:
            print(f"Team member already exists: {member.name}")

def create_demos():
    """Create demo projects."""
    demos_data = [
        {
            'title': 'AI-Powered Analytics Dashboard',
            'slug': 'ai-analytics-dashboard',
            'description': 'Interactive dashboard showcasing real-time data analytics with machine learning insights. Features real-time data visualization, predictive analytics, anomaly detection, interactive charts and graphs, and machine learning insights.',
            'live_demo_url': 'https://demo.verionlabs.com/analytics',
            'github_url': 'https://github.com/verionlabs/analytics-demo',
            'image_url': '/static/images/analytics_platform.jpg',
            'featured': True,
            'order': 1,
            'tags': ['AI', 'Analytics', 'Dashboard', 'Machine Learning']
        },
        {
            'title': 'Intelligent Chat Assistant',
            'slug': 'chat-assistant',
            'description': 'AI-powered chat bot demonstrating natural language processing capabilities. Features natural language understanding, context-aware responses, multi-turn conversations, intent recognition, and sentiment analysis.',
            'live_demo_url': 'https://demo.verionlabs.com/chatbot',
            'github_url': 'https://github.com/verionlabs/chatbot-demo',
            'image_url': '/static/images/chat_bot.jpg',
            'featured': True,
            'order': 2,
            'tags': ['AI', 'NLP', 'Chatbot', 'Conversation']
        },
        {
            'title': 'Cloud Infrastructure Monitor',
            'slug': 'cloud-monitor',
            'description': 'Real-time monitoring dashboard for cloud infrastructure and applications. Features infrastructure monitoring, application performance tracking, alert management, resource utilization metrics, and automated scaling insights.',
            'live_demo_url': 'https://demo.verionlabs.com/monitor',
            'github_url': 'https://github.com/verionlabs/monitor-demo',
            'image_url': '/static/images/cloud_migration.jpg',
            'featured': False,
            'order': 3,
            'tags': ['Cloud', 'Monitoring', 'DevOps', 'Infrastructure']
        }
    ]
    
    for demo_data in demos_data:
        tags = demo_data.pop('tags', [])
        demo, created = Demo.objects.get_or_create(
            slug=demo_data['slug'],
            defaults=demo_data
        )
        
        if created:
            print(f"Created demo: {demo.title}")
            
            # Add tags
            for tag_name in tags:
                tag, _ = DemoTag.objects.get_or_create(
                    demo=demo,
                    name=tag_name
                )
        else:
            print(f"Demo already exists: {demo.title}")

def main():
    """Main function to populate the database."""
    print("Starting database population...")
    
    create_navigation_items()
    print()
    
    create_services()
    print()
    
    create_team_members()
    print()
    
    create_demos()
    print()
    
    print("Database population completed!")

if __name__ == '__main__':
    main()