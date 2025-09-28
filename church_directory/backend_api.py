"""
Backend API Service for Church Directory Integration
Handles communication with the main church-directory backend for organization setup.
"""

import logging
import requests
from typing import Dict, Any, Optional, Tuple
from django.conf import settings
from church_directory.models import Subscription

logger = logging.getLogger(__name__)


class BackendApiService:
    """Service for communicating with the main church-directory backend"""
    
    def __init__(self):
        self.backend_url = getattr(settings, 'CHURCH_DIRECTORY_BACKEND_URL', 'http://localhost:8001')
        self.api_key = getattr(settings, 'CHURCH_DIRECTORY_API_KEY', '')
        self.timeout = 30
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests"""
        return {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}',
            'User-Agent': 'ChurchDirectoryMarketing/1.0',
        }
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Tuple[bool, Dict[str, Any]]:
        """Make a request to the backend API"""
        url = f"{self.backend_url.rstrip('/')}/{endpoint.lstrip('/')}"
        
        try:
            response = requests.request(
                method=method,
                url=url,
                json=data,
                headers=self._get_headers(),
                timeout=self.timeout
            )
            
            # Log the request
            logger.info(f"Backend API {method} {url} - Status: {response.status_code}")
            
            if response.status_code in [200, 201]:
                try:
                    return True, response.json()
                except ValueError:
                    # Response might not be JSON
                    logger.warning(f"Backend API returned non-JSON response: {response.text[:200]}")
                    return True, {'status': 'success', 'message': 'Request completed'}
            else:
                try:
                    error_data = response.json()
                except ValueError:
                    # Handle non-JSON error responses (like 404 HTML pages)
                    error_text = response.text[:500] if response.text else 'No error message'
                    error_data = {'error': f'HTTP {response.status_code}', 'details': error_text}
                
                logger.error(f"Backend API error {response.status_code}: {error_data}")
                return False, error_data
                
        except requests.exceptions.Timeout:
            logger.error(f"Backend API timeout for {method} {url}")
            return False, {'error': 'Backend API timeout'}
        except requests.exceptions.ConnectionError:
            logger.error(f"Backend API connection error for {method} {url}")
            return False, {'error': 'Backend API connection failed'}
        except requests.exceptions.RequestException as e:
            logger.error(f"Backend API request error for {method} {url}: {e}")
            return False, {'error': f'Request failed: {str(e)}'}
        except ValueError as e:
            logger.error(f"Backend API JSON decode error for {method} {url}: {e}")
            return False, {'error': f'Invalid JSON response: {str(e)}'}
        except Exception as e:
            logger.error(f"Unexpected error in backend API request: {e}")
            return False, {'error': f'Unexpected error: {str(e)}'}
    
    def create_organization(self, subscription: Subscription) -> Tuple[bool, Dict[str, Any]]:
        """Create a new organization in the main backend"""
        
        # Check if organization already exists for this subscription
        if subscription.backend_integration_status == 'completed':
            logger.info(f"Organization already created for subscription {subscription.id}")
            return True, {
                'organization_id': subscription.backend_organization_id,
                'tenant_slug': subscription.backend_tenant_slug,
                'message': 'Organization already exists'
            }
        
        # Log the backend URL being used for debugging
        logger.info(f"Creating organization for subscription {subscription.id} using backend URL: {self.backend_url}")
        
        # Prepare organization data
        organization_data = {
            'name': subscription.church_name,
            'contact_name': subscription.contact_name,
            'contact_email': subscription.email,
            'contact_phone': subscription.phone or '',
            'subscription_tier': subscription.pricing_tier.name,
            'billing_period': subscription.billing_period,
            'subscription_amount': float(subscription.final_amount),
            'stripe_customer_id': subscription.stripe_customer_id,
            'stripe_subscription_id': subscription.stripe_subscription_id,
            'marketing_subscription_id': str(subscription.id),
        }
        
        success, response_data = self._make_request('POST', '/api/public/organizations/create-from-marketing/', organization_data)
        
        if success:
            logger.info(f"Successfully created organization for subscription {subscription.id}")
            
            # Update subscription with backend info
            subscription.backend_organization_id = response_data.get('organization_id')
            subscription.backend_tenant_slug = response_data.get('tenant_slug')
            subscription.backend_integration_status = 'completed'
            subscription.backend_integration_data = response_data
            subscription.save()
            
            return True, response_data
        else:
            logger.error(f"Failed to create organization for subscription {subscription.id}: {response_data}")
            
            # Update subscription with error info
            subscription.backend_integration_status = 'failed'
            subscription.backend_integration_data = response_data
            subscription.save()
            
            return False, response_data
    
    def get_organization_status(self, organization_id: str) -> Tuple[bool, Dict[str, Any]]:
        """Get organization status from the backend"""
        success, response_data = self._make_request('GET', f'/api/organizations/{organization_id}/status/')
        return success, response_data
    
    def update_subscription_status(self, organization_id: str, status: str, subscription_data: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """Update subscription status in the backend"""
        data = {
            'status': status,
            'subscription_data': subscription_data
        }
        success, response_data = self._make_request('PATCH', f'/api/organizations/{organization_id}/subscription/', data)
        return success, response_data
    
    def test_connection(self) -> Tuple[bool, Dict[str, Any]]:
        """Test connection to the backend API"""
        success, response_data = self._make_request('GET', '/api/health/')
        return success, response_data
    
    def retry_organization_creation(self, subscription: Subscription) -> Tuple[bool, Dict[str, Any]]:
        """Retry organization creation for a failed subscription"""
        logger.info(f"Retrying organization creation for subscription {subscription.id}")
        
        # Reset backend integration status
        subscription.backend_integration_status = 'pending'
        subscription.save()
        
        return self.create_organization(subscription)
    
    def handle_subscription_cancellation(self, subscription: Subscription) -> Tuple[bool, Dict[str, Any]]:
        """Handle subscription cancellation in the backend"""
        if not subscription.backend_organization_id:
            logger.warning(f"No backend organization ID for subscription {subscription.id}")
            return False, {'error': 'No backend organization found'}
        
        data = {
            'action': 'cancel',
            'cancellation_reason': 'subscription_cancelled',
            'marketing_subscription_id': str(subscription.id)
        }
        
        success, response_data = self._make_request(
            'POST', 
            f'/api/organizations/{subscription.backend_organization_id}/cancel/',
            data
        )
        
        if success:
            subscription.backend_integration_status = 'cancelled'
            subscription.save()
        
        return success, response_data

    
    # TODO: Add automation on a server to retry failed subscriptiosn and add monitoring for such

    def retry_failed_integrations(self) -> Dict[str, int]:
        """Retry backend integration for all failed subscriptions"""
        from .models import Subscription
        
        failed_subscriptions = Subscription.objects.filter(
            backend_integration_status='failed',
            status='active' 
        )
        
        results = {'successful': 0, 'failed': 0, 'skipped': 0}
        
        for subscription in failed_subscriptions:
            try:
                logger.info(f"Retrying backend integration for subscription {subscription.id}")
                
                # Reset status to allow retry
                subscription.backend_integration_status = 'pending'
                subscription.save()
                
                success, response_data = self.create_organization(subscription)
                
                if success:
                    results['successful'] += 1
                    logger.info(f"Successfully retried backend integration for subscription {subscription.id}")
                else:
                    results['failed'] += 1
                    logger.error(f"Failed to retry backend integration for subscription {subscription.id}: {response_data}")
                    
            except Exception as e:
                results['failed'] += 1
                logger.error(f"Exception during retry for subscription {subscription.id}: {e}")
        
        logger.info(f"Backend integration retry completed: {results}")
        return results