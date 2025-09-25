"""
Management command to monitor payment system health and send alerts.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from church_directory.error_handling import monitor_subscription_health
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Monitor payment system health and send alerts'

    def add_arguments(self, parser):
        parser.add_argument(
            '--send-email',
            action='store_true',
            help='Send email alerts for issues found',
        )

    def handle(self, *args, **options):
        self.stdout.write('Checking payment system health...')
        
        try:
            alerts = monitor_subscription_health()
            
            if alerts:
                self.stdout.write(
                    self.style.WARNING(f'Found {len(alerts)} issues:')
                )
                for alert in alerts:
                    self.stdout.write(f'  • {alert}')
                
                if options['send_email']:
                    self.send_alert_email(alerts)
                    self.stdout.write(self.style.SUCCESS('Alert emails sent'))
                
            else:
                self.stdout.write(
                    self.style.SUCCESS('No issues found - system is healthy')
                )
            
        except Exception as e:
            logger.exception(f'Error during health check: {e}')
            self.stdout.write(
                self.style.ERROR(f'Health check failed: {e}')
            )
    
    def send_alert_email(self, alerts):
        """Send alert email to administrators"""
        from django.core.mail import send_mail
        from django.conf import settings
        
        subject = 'Church Directory Payment System Alert'
        message = 'Payment system health check found the following issues:\n\n'
        message += '\n'.join(f'• {alert}' for alert in alerts)
        message += '\n\nPlease check the system and take appropriate action.'
        
        admin_emails = [admin[1] for admin in getattr(settings, 'ADMINS', [])]
        if admin_emails:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                admin_emails,
                fail_silently=False,
            )