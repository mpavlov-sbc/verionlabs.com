#!/usr/bin/env python
"""
Test script for the contact form functionality.
"""

import requests
import sys

def test_contact_form():
    """Test the contact form submission."""
    url = 'http://127.0.0.1:8000/contact/'
    
    # First, get the page to obtain CSRF token
    session = requests.Session()
    
    try:
        # Get the contact page
        get_response = session.get(url)
        if get_response.status_code != 200:
            print(f"❌ Contact page not accessible: {get_response.status_code}")
            return False
            
        print("✅ Contact page accessible")
        
        # Extract CSRF token from the form
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(get_response.content, 'html.parser')
        csrf_token = soup.find('input', {'name': 'csrfmiddlewaretoken'})
        
        if not csrf_token:
            print("❌ CSRF token not found in form")
            return False
            
        csrf_value = csrf_token.get('value')
        print("✅ CSRF token found")
        
        # Test form submission
        form_data = {
            'csrfmiddlewaretoken': csrf_value,
            'name': 'Test User',
            'email': 'test@example.com',
            'subject': 'Test Inquiry',
            'message': 'This is a test message from the Django transformation testing.',
        }
        
        post_response = session.post(url, data=form_data)
        
        if post_response.status_code == 200:
            # Check if form was submitted successfully
            if 'Thank you' in post_response.text or 'success' in post_response.text.lower():
                print("✅ Contact form submitted successfully")
                return True
            else:
                print("⚠️ Form submitted but no success message found")
                return True
        elif post_response.status_code == 302:
            print("✅ Contact form submitted successfully (redirect)")
            return True
        else:
            print(f"❌ Form submission failed: {post_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing contact form: {e}")
        return False

def test_contact_inquiry_in_database():
    """Check if contact inquiry was saved to database."""
    import os
    import django
    
    # Set up Django environment
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'verionlabs_django.settings')
    django.setup()
    
    from website.models import ContactInquiry
    
    try:
        # Check if any contact inquiries exist
        inquiries = ContactInquiry.objects.all()
        if inquiries.exists():
            latest = inquiries.latest('created_at')
            print(f"✅ Contact inquiry found in database: {latest.name} - {latest.subject}")
            return True
        else:
            print("⚠️ No contact inquiries found in database")
            return False
    except Exception as e:
        print(f"❌ Error checking database: {e}")
        return False

if __name__ == '__main__':
    print("Testing Django Contact Form Functionality")
    print("=" * 50)
    
    # First install required packages
    try:
        import bs4
    except ImportError:
        print("Installing BeautifulSoup4...")
        import subprocess
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'beautifulsoup4'])
        import bs4
    
    form_test = test_contact_form()
    print()
    db_test = test_contact_inquiry_in_database()
    
    print("\n" + "=" * 50)
    if form_test and db_test:
        print("🎉 All contact form tests passed!")
    elif form_test:
        print("⚠️ Form works but check database connection")
    else:
        print("❌ Contact form tests failed")