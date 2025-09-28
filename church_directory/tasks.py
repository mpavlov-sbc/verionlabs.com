"""
Celery tasks for asynchronous processing in Church Directory marketing site.
"""
import logging
from celery import shared_task
from django.utils import timezone
from .models import Subscription
from .backend_api import BackendApiService

logger = logging.getLogger(__name__)


@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 5, 'countdown': 60})
def create_backend_organization_task(self, subscription_id):
    """
    Create organization in backend API asynchronously.
    
    This task runs in the background after a successful payment to create
    the organization and admin user in the main church directory backend.
    
    Args:
        subscription_id: UUID string of the subscription to process
        
    Returns:
        dict: Success status and organization details
    """
    try:
        logger.info(f"Starting async backend integration for subscription {subscription_id}")
        
        # Get subscription with error handling
        try:
            subscription = Subscription.objects.get(id=subscription_id)
        except Subscription.DoesNotExist:
            logger.error(f"Subscription {subscription_id} not found for backend integration")
            return {'success': False, 'error': 'Subscription not found'}
        
        # Check if already completed to avoid duplicate processing
        if subscription.backend_integration_status == 'completed':
            logger.info(f"Backend integration already completed for subscription {subscription_id}")
            return {
                'success': True, 
                'message': 'Already completed',
                'organization_id': subscription.backend_organization_id
            }
        
        # Create organization via backend API
        backend_api = BackendApiService()
        success, response_data = backend_api.create_organization(subscription)
        
        if success:
            logger.info(f"Successfully created backend organization for subscription {subscription_id}")
            return {
                'success': True,
                'organization_id': response_data.get('organization_id'),
                'tenant_slug': response_data.get('tenant_slug')
            }
        else:
            error_msg = f"Backend API failed for subscription {subscription_id}: {response_data}"
            logger.error(error_msg)
            
            # Update subscription status to failed
            subscription.backend_integration_status = 'failed'
            subscription.backend_integration_error = str(response_data)
            subscription.save()
            
            # Raise exception to trigger Celery retry
            raise Exception(f"Backend API error: {response_data}")
            
    except Exception as e:
        logger.error(f"Error in async backend integration for subscription {subscription_id}: {e}")
        
        # Update subscription on final failure
        if self.request.retries >= self.max_retries:
            try:
                subscription = Subscription.objects.get(id=subscription_id)
                subscription.backend_integration_status = 'failed'
                subscription.backend_integration_error = str(e)
                subscription.save()
                logger.error(f"Backend integration permanently failed for subscription {subscription_id} after {self.max_retries} retries")
            except Exception as update_error:
                logger.error(f"Failed to update subscription status after permanent failure: {update_error}")
        
        # Re-raise to trigger Celery retry mechanism
        raise


@shared_task
def retry_failed_backend_integrations():
    """
    Periodic task to retry failed backend integrations.
    
    This can be scheduled to run every hour/day to catch and retry
    any backend integrations that failed due to temporary issues.
    """
    logger.info("Starting periodic retry of failed backend integrations")
    
    # Find subscriptions with failed backend integration
    failed_subscriptions = Subscription.objects.filter(
        status='active',  # Only active subscriptions
        backend_integration_status='failed'
    )
    
    retry_count = 0
    for subscription in failed_subscriptions:
        logger.info(f"Retrying backend integration for subscription {subscription.id}")
        
        # Schedule the task (this will use the retry mechanism)
        create_backend_organization_task.delay(str(subscription.id))
        retry_count += 1
    
    logger.info(f"Scheduled {retry_count} backend integration retries")
    return {'retries_scheduled': retry_count}


@shared_task
def health_check_backend_integrations():
    """
    Health check task to monitor backend integration status.
    
    This can be used to generate alerts or metrics about
    backend integration success rates.
    """
    from django.db.models import Count, Q
    
    # Get integration statistics
    stats = Subscription.objects.aggregate(
        total=Count('id'),
        completed=Count('id', filter=Q(backend_integration_status='completed')),
        failed=Count('id', filter=Q(backend_integration_status='failed')),
        pending=Count('id', filter=Q(backend_integration_status='pending')),
        not_started=Count('id', filter=Q(backend_integration_status='not_started'))
    )
    
    logger.info(f"Backend integration health check: {stats}")
    
    # Alert if failure rate is high
    if stats['total'] > 0:
        failure_rate = stats['failed'] / stats['total']
        if failure_rate > 0.1:  # More than 10% failure rate
            logger.warning(f"High backend integration failure rate: {failure_rate:.2%}")
    
    return stats