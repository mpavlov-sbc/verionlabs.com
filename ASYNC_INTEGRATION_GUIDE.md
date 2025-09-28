# Asynchronous Backend Integration Guide

## Overview

The Church Directory marketing website now supports **asynchronous backend integration** using Celery. This means that when customers complete payments, the Stripe webhook responds immediately while backend organization creation happens in the background.

## Benefits

### ✅ **Fast Webhook Response**
- Webhooks respond in <1 second instead of 10-30 seconds
- Reduced risk of Stripe webhook timeouts
- Better user experience

### ✅ **Resilient Integration**
- Automatic retries with exponential backoff
- Failed integrations don't affect payment success
- Independent monitoring and alerting

### ✅ **Better Monitoring**
- Separate tracking of payment vs backend integration
- Detailed logging for troubleshooting
- Health check endpoints

## Architecture

```
Payment Success → Webhook → Subscription Activated → Celery Task Queued
                     ↓                                       ↓
            Fast Response (200 OK)              Background Organization Creation
```

## Configuration

### Environment Variables

Add to your `.env` file:

```bash
# Celery Configuration
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# Backend Integration
BACKEND_INTEGRATION_ENABLED=true
BACKEND_INTEGRATION_ASYNC=true
```

### Docker Services

The setup includes:
- `web_debug` - Main Django application
- `celery_worker` - Background task processor
- `celery_beat` - Scheduled task scheduler
- `redis` - Message broker for Celery

## Task Types

### 1. **Organization Creation** (`create_backend_organization_task`)
- **Trigger**: After successful payment
- **Retries**: 5 attempts with 60s intervals
- **Purpose**: Create organization and admin user in backend

### 2. **Failed Integration Retry** (`retry_failed_backend_integrations`)
- **Schedule**: Every hour
- **Purpose**: Automatically retry failed integrations
- **Scope**: All active subscriptions with failed status

### 3. **Health Monitoring** (`health_check_backend_integrations`)
- **Schedule**: Every 30 minutes  
- **Purpose**: Monitor integration success rates
- **Alerts**: Warns if failure rate >10%

## Operations

### Development

```bash
# Start all services
docker compose -f docker-compose.debug.yml up -d

# View logs
docker compose -f docker-compose.debug.yml logs celery_worker
docker compose -f docker-compose.debug.yml logs celery_beat

# Check Redis
docker compose -f docker-compose.debug.yml exec redis redis-cli ping
```

### Production

```bash
# Deploy with automated script (recommended)
./deploy-production-async.sh

# Manual deployment
docker compose -f docker-compose.prod.yml up -d --build
docker compose -f docker-compose.prod.yml exec web python manage.py migrate
docker compose -f docker-compose.prod.yml exec web python manage.py migrate django_celery_beat
docker compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput

# Monitor Celery workers
docker compose -f docker-compose.prod.yml exec celery_worker celery -A verionlabs_django inspect active

# Check task queue status
docker compose -f docker-compose.prod.yml exec celery_worker celery -A verionlabs_django inspect reserved

# View service status
docker compose -f docker-compose.prod.yml ps
```

### Manual Operations

```bash
# Retry specific subscription
python manage.py shell
>>> from church_directory.tasks import create_backend_organization_task
>>> create_backend_organization_task.delay('subscription-uuid-here')

# Bulk retry all failed integrations  
python manage.py retry_backend_integrations

# Check integration status
python manage.py shell
>>> from church_directory.models import Subscription
>>> Subscription.objects.filter(backend_integration_status='failed').count()
```

## Monitoring

### Admin Interface

1. Go to `/admin/church_directory/subscription/`
2. Filter by `backend_integration_status` 
3. Use bulk actions to retry failed integrations
4. View detailed error messages in individual subscription records

### Logs

```bash
# Webhook processing
grep "checkout.session.completed" logs/

# Backend integration
grep "Backend integration" logs/

# Task execution
grep "create_backend_organization_task" logs/
```

### Health Checks

- **Payment Health**: Subscription activation success rate
- **Integration Health**: Backend organization creation success rate  
- **Task Health**: Celery worker status and queue lengths

## Troubleshooting

### Common Issues

#### 1. **Redis Connection Failed**
```bash
# Check Redis is running
docker compose ps redis

# Test connection
docker compose exec redis redis-cli ping
```

#### 2. **Tasks Not Processing**
```bash  
# Check worker status
docker compose logs celery_worker

# Restart worker
docker compose restart celery_worker
```

#### 3. **High Failure Rate**
```bash
# Check recent failures
python manage.py shell
>>> from church_directory.models import Subscription  
>>> failed = Subscription.objects.filter(backend_integration_status='failed')
>>> for s in failed[:5]: print(f"{s.id}: {s.backend_integration_error}")
```

### Rollback to Synchronous

If needed, you can temporarily disable async processing:

```bash
# In .env file
BACKEND_INTEGRATION_ASYNC=false
```

This will fall back to synchronous processing within the webhook.

## Performance Metrics

### Target Metrics
- **Webhook Response Time**: <2 seconds (was 10-30s)
- **Integration Success Rate**: >95%
- **Task Processing Time**: <60 seconds average
- **Recovery Time**: Failed integrations retry within 1 hour

### Monitoring Dashboard

Consider setting up monitoring for:
- Celery queue lengths
- Task success/failure rates  
- Worker health status
- Redis memory usage
- Backend API response times