"""
Management command to retry failed backend integrations for active subscriptions.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from church_directory.models import Subscription
from church_directory.backend_api import BackendApiService
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Retry failed backend integrations for active subscriptions'

    def add_arguments(self, parser):
        parser.add_argument(
            '--subscription-id',
            type=int,
            help='Retry specific subscription ID',
        )
        parser.add_argument(
            '--max-age-hours',
            type=int,
            default=24,
            help='Maximum age in hours for subscriptions to retry (default: 24)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be processed without making changes',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        max_age_hours = options['max_age_hours']
        subscription_id = options.get('subscription_id')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))
        
        # Filter subscriptions for retry
        if subscription_id:
            subscriptions = Subscription.objects.filter(
                id=subscription_id,
                status='active'
            )
            if not subscriptions.exists():
                self.stdout.write(
                    self.style.ERROR(f'No active subscription found with ID {subscription_id}')
                )
                return
        else:
            # Find subscriptions that need backend integration
            cutoff_time = timezone.now() - timedelta(hours=max_age_hours)
            subscriptions = Subscription.objects.filter(
                status='active',
                backend_integration_status__in=['failed', 'pending', ''],
                created_at__gte=cutoff_time
            )
        
        total_count = subscriptions.count()
        
        if total_count == 0:
            self.stdout.write(self.style.SUCCESS('No subscriptions need backend integration retry'))
            return
        
        self.stdout.write(
            self.style.SUCCESS(f'Found {total_count} subscriptions to process')
        )
        
        if dry_run:
            for subscription in subscriptions:
                self.stdout.write(
                    f'Would retry: Subscription {subscription.id} - {subscription.church_name} '
                    f'(Status: {subscription.backend_integration_status or "not set"})'
                )
            return
        
        # Process subscriptions
        backend_api = BackendApiService()
        success_count = 0
        error_count = 0
        
        for subscription in subscriptions:
            self.stdout.write(
                f'Processing subscription {subscription.id} - {subscription.church_name}...'
            )
            
            try:
                # Test backend connection first
                connection_ok, _ = backend_api.test_connection()
                if not connection_ok:
                    self.stdout.write(
                        self.style.ERROR('Backend API connection failed - stopping')
                    )
                    break
                
                # Attempt to create organization
                success, response_data = backend_api.retry_organization_creation(subscription)
                
                if success:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'✓ Successfully integrated subscription {subscription.id} '
                            f'(Organization ID: {response_data.get("organization_id")})'
                        )
                    )
                    success_count += 1
                else:
                    self.stdout.write(
                        self.style.ERROR(
                            f'✗ Failed to integrate subscription {subscription.id}: '
                            f'{response_data.get("error", "Unknown error")}'
                        )
                    )
                    error_count += 1
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'✗ Unexpected error for subscription {subscription.id}: {e}'
                    )
                )
                error_count += 1
                logger.exception(f'Error retrying backend integration for subscription {subscription.id}')
        
        # Summary
        self.stdout.write(
            self.style.SUCCESS(
                f'Completed: {success_count} successful, {error_count} failed, {total_count} total'
            )
        )
        
        if error_count > 0:
            self.stdout.write(
                self.style.WARNING(
                    'Some integrations failed. Check logs for details.'
                )
            )