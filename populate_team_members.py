#!/usr/bin/env python3
"""
Populate sample team members for Church Directory
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'verionlabs_django.settings')
django.setup()

from church_directory.models import TeamMember


def create_team_members():
    """Create sample team members"""
    
    # Clear existing team members
    TeamMember.objects.all().delete()
    
    team_members_data = [
        {
            'name': 'Michael Pavlov',
            'title': 'Founder & CEO',
            'bio': 'Michael brings over 15 years of experience in church leadership and technology, passionate about using innovation to strengthen faith communities.',
            'avatar_initials': 'MP',
            'avatar_color': 'bg-gradient-to-br from-blue-400 to-blue-600',
            'display_order': 1,
        },
        {
            'name': 'VerionLabs Team',
            'title': 'Development Team',
            'bio': 'Our skilled development team combines technical expertise with deep understanding of church needs to create exceptional solutions.',
            'avatar_initials': 'VL',
            'avatar_color': 'bg-gradient-to-br from-green-400 to-green-600',
            'display_order': 2,
        },
        {
            'name': 'Support Team',
            'title': 'Customer Success',
            'bio': 'Our dedicated support team is committed to helping every church succeed with personalized guidance and responsive assistance.',
            'avatar_initials': 'CS',
            'avatar_color': 'bg-gradient-to-br from-purple-400 to-purple-600',
            'display_order': 3,
        },
    ]
    
    created_members = []
    for member_data in team_members_data:
        member, created = TeamMember.objects.get_or_create(
            name=member_data['name'],
            defaults=member_data
        )
        if created:
            created_members.append(member)
            print(f"✓ Created team member: {member.name}")
        else:
            print(f"→ Team member already exists: {member.name}")
    
    print(f"\nTotal team members in database: {TeamMember.objects.count()}")
    print("Team member population completed!")


if __name__ == '__main__':
    create_team_members()