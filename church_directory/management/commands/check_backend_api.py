"""
Management command to test backend API connection and retry failed integrations.
"""

from django.core.management.base import BaseCommand
from django.conf import settings
from church_directory.backend_api import BackendApiService
from church_directory.models import Subscription


class Command(BaseCommand):
    help = 'Test backend API connection and optionally retry failed integrations'

    def add_arguments(self, parser):
        parser.add_argument(
            '--retry-failed',
            action='store_true',
            help='Retry failed backend integrations'
        )
        parser.add_argument(
            '--test-connection',
            action='store_true',
            help='Test backend API connection'
        )

    def handle(self, *args, **options):
        backend_api = BackendApiService()
        
        self.stdout.write(f"Backend URL: {backend_api.backend_url}")
        self.stdout.write(f"API Key configured: {'Yes' if backend_api.api_key else 'No'}")
        
        if options['test_connection']:
            self.stdout.write("Testing backend API connection...")
            success, response = backend_api.test_connection()
            
            if success:
                self.stdout.write(
                    self.style.SUCCESS(f'Backend API connection successful: {response}')
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f'Backend API connection failed: {response}')
                )
        
        if options['retry_failed']:
            self.stdout.write("Looking for failed backend integrations...")
            
            failed_subs = Subscription.objects.filter(
                backend_integration_status='failed',
                status='active'
            )
            
            if not failed_subs:
                self.stdout.write("No failed integrations found.")
                return
            
            self.stdout.write(f"Found {failed_subs.count()} failed integrations. Retrying...")
            
            results = backend_api.retry_failed_integrations()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f"Retry completed - Successful: {results['successful']}, "
                    f"Failed: {results['failed']}, Skipped: {results['skipped']}"
                )
            )
        
        if not options['test_connection'] and not options['retry_failed']:
            # Show status summary
            self.stdout.write("Backend integration status summary:")
            
            status_counts = {}
            for status_choice in ['completed', 'failed', 'pending']:
                count = Subscription.objects.filter(
                    backend_integration_status=status_choice,
                    status='active'
                ).count()
                status_counts[status_choice] = count
                self.stdout.write(f"  {status_choice.title()}: {count}")
            
            self.stdout.write("\nUse --test-connection to test API connectivity")
            self.stdout.write("Use --retry-failed to retry failed integrations")