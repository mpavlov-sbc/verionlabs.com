#!/bin/bash

# Production Deployment Script for Church Directory Marketing Site
# This script handles Docker deployment with Celery services

set -e

echo "🚀 Starting Church Directory Marketing Site Production Deployment..."

# Configuration
COMPOSE_FILE="docker-compose.prod.yml"
ENV_FILE=".env.production"

# Check if environment file exists
if [ ! -f "$ENV_FILE" ]; then
    echo "❌ Error: $ENV_FILE not found!"
    echo "Please create the production environment file first."
    exit 1
fi

# Stop existing containers
echo "⏹️  Stopping existing containers..."
docker compose -f $COMPOSE_FILE down

# Build and start services
echo "🔨 Building and starting services..."
docker compose -f $COMPOSE_FILE up -d --build

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
sleep 10

# Run database migrations
echo "📊 Running database migrations..."
docker compose -f $COMPOSE_FILE exec web python manage.py migrate

# Create Celery beat tables
echo "⏰ Setting up Celery beat database tables..."
docker compose -f $COMPOSE_FILE exec web python manage.py migrate django_celery_beat

# Collect static files
echo "📁 Collecting static files..."
docker compose -f $COMPOSE_FILE exec web python manage.py collectstatic --noinput

# Create superuser (optional, only if needed)
echo "👤 Creating superuser (if needed)..."
docker compose -f $COMPOSE_FILE exec web python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@verionlabs.com', 'changeme123!')
    print('✅ Superuser created: admin / changeme123!')
else:
    print('ℹ️  Superuser already exists')
"

# Health checks
echo "🔍 Running health checks..."

# Check web service
if curl -f -s http://localhost:8002/admin/ > /dev/null; then
    echo "✅ Web service is responding"
else
    echo "❌ Web service health check failed"
fi

# Check Redis
if docker compose -f $COMPOSE_FILE exec redis redis-cli ping | grep -q "PONG"; then
    echo "✅ Redis is responding"
else
    echo "❌ Redis health check failed"
fi

# Check Celery worker
if docker compose -f $COMPOSE_FILE exec celery_worker celery -A verionlabs_django inspect ping | grep -q "pong"; then
    echo "✅ Celery worker is responding"
else
    echo "⚠️  Celery worker may not be ready yet"
fi

# Check database
if docker compose -f $COMPOSE_FILE exec web python manage.py check --database default > /dev/null 2>&1; then
    echo "✅ Database connection is working"
else
    echo "❌ Database health check failed"
fi

echo ""
echo "🎉 Deployment completed!"
echo ""
echo "📋 Service Status:"
docker compose -f $COMPOSE_FILE ps

echo ""
echo "🔗 Access Points:"
echo "   📱 Website: http://localhost:8002 (or your domain)"
echo "   🛠️  Admin: http://localhost:8002/admin/"
echo "   📊 Database: localhost:5434"
echo "   🔴 Redis: localhost:6381"
echo ""
echo "📊 Monitoring Commands:"
echo "   docker compose -f $COMPOSE_FILE logs web"
echo "   docker compose -f $COMPOSE_FILE logs celery_worker"
echo "   docker compose -f $COMPOSE_FILE logs celery_beat"
echo "   docker compose -f $COMPOSE_FILE exec celery_worker celery -A verionlabs_django inspect active"
echo ""
echo "🔧 Maintenance Commands:"
echo "   # Retry failed integrations"
echo "   docker compose -f $COMPOSE_FILE exec web python manage.py retry_backend_integrations"
echo ""
echo "   # Check Celery queue"  
echo "   docker compose -f $COMPOSE_FILE exec celery_worker celery -A verionlabs_django inspect reserved"
echo ""
echo "   # Restart Celery services"
echo "   docker compose -f $COMPOSE_FILE restart celery_worker celery_beat"

echo ""
echo "⚠️  Important Notes:"
echo "   • Change the default superuser password immediately"
echo "   • Monitor logs for any integration issues"
echo "   • Set up backup for Redis data volume"
echo "   • Configure SSL certificates for production"
echo ""
echo "✅ Deployment script completed successfully!"