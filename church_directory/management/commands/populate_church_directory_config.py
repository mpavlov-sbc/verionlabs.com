from django.core.management.base import BaseCommand
from church_directory.models import (
    WebsiteConfig, Feature, Value, UseCase, AboutStoryParagraph, TeamMember
)


class Command(BaseCommand):
    help = 'Populate church directory with default configuration data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creating default church directory configuration...'))

        # Create website configuration
        config, created = WebsiteConfig.objects.get_or_create(
            id=1,
            defaults={
                'site_title': 'Church Directory',
                'site_description': 'The Complete Church Directory Solution for Modern Congregations',
                'company_name': 'VerionLabs',
                'domain': 'directory.verionlabs.com',
                'hero_headline': 'Stay Connected with Your Church Family – Instantly & Securely',
                'hero_subline': 'Secure member directories that bring congregations closer together',
                'hero_cta_primary': 'Get Started Today',
                'hero_cta_secondary': 'Learn More',
                'about_headline': 'Building Stronger Church Communities',
                'about_subline': 'Church Directory was born from a simple belief: technology should bring people together, not drive them apart. We\'re passionate about helping churches foster genuine relationships and meaningful connections.',
                'about_story_title': 'Our Story',
                'about_values_title': 'Our Values',
                'features_headline': 'Built Specifically for Churches',
                'features_subline': 'Every feature is designed with the unique needs, values, and privacy concerns of faith communities in mind.',
                'pricing_headline': 'Simple, Transparent Pricing',
                'pricing_subline': 'Choose the plan that fits your congregation size. All plans include our core features with no hidden fees.',
                'use_cases_headline': 'See It In Action',
                'use_cases_subline': 'Real scenarios from churches using Church Directory to strengthen their communities.',
                'cta_headline': 'Ready to Connect Your Congregation?',
                'cta_subline': 'Join thousands of churches already using Church Directory to build stronger communities and streamline member management.',
                'cta_button_primary': 'Start Free Trial',
                'cta_button_secondary': 'Schedule Demo',
                'support_email': 'support@verionlabs.com',
                'sales_email': 'sales@verionlabs.com',
                'show_pricing': True,
                'show_testimonials': True,
                'show_use_cases': True,
                'show_team': True,
                'maintenance_mode': False,
                'meta_keywords': 'church directory, member management, church software, congregation management',
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('✓ Created website configuration'))
        else:
            self.stdout.write('ℹ Website configuration already exists')

        # Create default features
        features_data = [
            {'title': 'Complete Member Directory', 'description': 'Browse a comprehensive directory of all church members with photos, contact details, and family connections.', 'icon': 'users', 'order': 1},
            {'title': 'Enterprise-Grade Security', 'description': 'Your member data is protected with military-grade encryption and sophisticated privacy controls.', 'icon': 'shield', 'order': 2},
            {'title': 'Group Management', 'description': 'Organize ministry groups, small groups, and committees with detailed member rosters and information.', 'icon': 'users-group', 'order': 3},
            {'title': 'Self-Service Updates', 'description': 'Members update their own information, reducing administrative burden by up to 80%.', 'icon': 'clipboard', 'order': 4},
            {'title': 'Mobile App Access', 'description': 'Works seamlessly across iOS and Android devices with offline access to key information.', 'icon': 'mobile', 'order': 5},
            {'title': 'Admin Dashboard', 'description': 'Comprehensive administrative tools for managing members, groups, and communications efficiently.', 'icon': 'cog', 'order': 6},
        ]

        created_features = 0
        for feature_data in features_data:
            feature, created = Feature.objects.get_or_create(
                title=feature_data['title'],
                defaults=feature_data
            )
            if created:
                created_features += 1
        
        self.stdout.write(self.style.SUCCESS(f'✓ Created {created_features} new features ({len(features_data)} total)'))

        # Create default values
        values_data = [
            {'title': 'Faith-Centered', 'description': 'We understand that churches are more than organizations—they\'re families united by faith. Our tools reflect this understanding in every interaction.', 'icon': 'heart', 'order': 1},
            {'title': 'Privacy First', 'description': 'We treat your member data with the highest respect and security, ensuring that sensitive information stays protected while enabling meaningful connections.', 'icon': 'shield', 'order': 2},
            {'title': 'Simplicity', 'description': 'Technology should make life easier, not more complicated. We prioritize intuitive design that anyone in your congregation can use with confidence.', 'icon': 'check', 'order': 3},
            {'title': 'Community', 'description': 'Every feature is designed to strengthen relationships and foster deeper connections within your church family.', 'icon': 'users', 'order': 4},
            {'title': 'Support', 'description': 'We\'re not just a software provider—we\'re partners in your ministry, committed to your success every step of the way.', 'icon': 'info', 'order': 5},
            {'title': 'Excellence', 'description': 'We continuously improve our platform to serve churches better, always striving for the highest quality and reliability.', 'icon': 'star', 'order': 6},
        ]

        created_values = 0
        for value_data in values_data:
            value, created = Value.objects.get_or_create(
                title=value_data['title'],
                defaults=value_data
            )
            if created:
                created_values += 1
        
        self.stdout.write(self.style.SUCCESS(f'✓ Created {created_values} new values ({len(values_data)} total)'))

        # Create default use cases
        use_cases_data = [
            {'persona_name': 'Pastor Mike', 'persona_role': 'The Ministry Leader', 'quote': 'I needed to quickly contact all 15 members about a location change for Thursday\'s meeting. Instead of making individual calls, I selected my Bible study group and sent a notification in under 30 seconds. Every member received the update instantly.', 'order': 1},
            {'persona_name': 'Sarah', 'persona_role': 'The Caring Congregant', 'quote': 'When I heard the Johnson family was going through a difficult time, I quickly found their contact information and coordinated with other small group members to organize a week\'s worth of meal deliveries.', 'order': 2},
            {'persona_name': 'Lisa', 'persona_role': 'The Church Administrator', 'quote': 'I used to spend 6 hours every month updating the printed directory. Now members update their own profiles, and I\'ve reclaimed those hours for more meaningful ministry work.', 'order': 3},
        ]

        created_use_cases = 0
        for use_case_data in use_cases_data:
            use_case, created = UseCase.objects.get_or_create(
                persona_name=use_case_data['persona_name'],
                persona_role=use_case_data['persona_role'],
                defaults=use_case_data
            )
            if created:
                created_use_cases += 1
        
        self.stdout.write(self.style.SUCCESS(f'✓ Created {created_use_cases} new use cases ({len(use_cases_data)} total)'))

        # Create default story paragraphs
        story_paragraphs_data = [
            {'content': 'Church Directory began when our founder, a longtime church member, watched his congregation struggle with outdated printed directories and scattered contact lists. Members couldn\'t reach each other for prayer support, ministry leaders spent hours managing group communications manually, and new families felt disconnected from the church community.', 'order': 1},
            {'content': 'We realized that while there were plenty of generic contact management tools available, none were designed specifically for the unique needs of faith communities. Churches needed something that respected privacy, fostered genuine relationships, and made it easy for members to connect and support one another.', 'order': 2},
            {'content': 'That\'s why we built Church Directory from the ground up with churches in mind. Every feature, from our security protocols to our user interface, was designed by people who understand church culture and the importance of building authentic Christian community in the digital age.', 'order': 3},
        ]

        created_paragraphs = 0
        for paragraph_data in story_paragraphs_data:
            paragraph, created = AboutStoryParagraph.objects.get_or_create(
                order=paragraph_data['order'],
                defaults=paragraph_data
            )
            if created:
                created_paragraphs += 1
        
        self.stdout.write(self.style.SUCCESS(f'✓ Created {created_paragraphs} new story paragraphs ({len(story_paragraphs_data)} total)'))

        # Create default team members
        team_members_data = [
            {'name': 'Michael Pavlov', 'title': 'Founder & CEO', 'bio': 'Passionate about helping churches leverage technology to build stronger communities and deepen relationships.', 'avatar_initials': 'MP', 'avatar_color': 'bg-gradient-to-br from-blue-400 to-blue-600', 'display_order': 1},
            {'name': 'Sarah Johnson', 'title': 'Head of Product', 'bio': 'Dedicated to creating intuitive experiences that make church management simple and effective.', 'avatar_initials': 'SJ', 'avatar_color': 'bg-gradient-to-br from-green-400 to-green-600', 'display_order': 2},
            {'name': 'David Chen', 'title': 'Lead Developer', 'bio': 'Expert in building secure, scalable solutions that churches can depend on for their most important data.', 'avatar_initials': 'DC', 'avatar_color': 'bg-gradient-to-br from-purple-400 to-purple-600', 'display_order': 3},
        ]

        created_team_members = 0
        for member_data in team_members_data:
            member, created = TeamMember.objects.get_or_create(
                name=member_data['name'],
                defaults=member_data
            )
            if created:
                created_team_members += 1
        
        self.stdout.write(self.style.SUCCESS(f'✓ Created {created_team_members} new team members ({len(team_members_data)} total)'))

        self.stdout.write(self.style.SUCCESS('\n🎉 Default church directory configuration created successfully!'))
        self.stdout.write('You can now customize the content through the Django admin interface.')