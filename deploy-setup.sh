#!/bin/bash

# Digital Ocean Droplet Setup Script for VerionLabs Website
# Run this script on a fresh Ubuntu 22.04 LTS droplet
# Usage: wget -O - https://raw.githubusercontent.com/your-repo/setup.sh | bash

set -e  # Exit on any error

echo "=== VerionLabs Website Deployment Setup ==="
echo "Setting up a fresh Digital Ocean droplet for production..."

# Update system packages
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install essential packages
echo "🛠️  Installing essential packages..."
sudo apt install -y \
    curl \
    wget \
    git \
    vim \
    htop \
    ufw \
    fail2ban \
    certbot \
    python3-certbot-nginx \
    unzip

# Install Docker
echo "🐳 Installing Docker..."
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
echo "📦 Installing Docker Compose..."
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Configure UFW Firewall
echo "🔥 Configuring firewall..."
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable

# Configure fail2ban
echo "🛡️  Configuring fail2ban..."
sudo systemctl enable fail2ban
sudo systemctl start fail2ban

# Create application directory
echo "📁 Creating application directory..."
sudo mkdir -p /opt/verionlabs-website
sudo chown $USER:$USER /opt/verionlabs-website
cd /opt/verionlabs-website

# Clone the repository
echo "📥 Cloning website repository..."
git clone https://github.com/mpavlov-sbc/verionlabs.com .

# Set up environment files
echo "⚙️  Setting up environment configuration..."

# Generate secure secret key
DJANGO_SECRET_KEY=$(python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')

echo "🔐 Configuring production environment..."
echo "Please provide the following information:"

read -p "Domain name (e.g., verionlabs.com): " DOMAIN_NAME
read -p "Directory subdomain (e.g., directory.verionlabs.com): " DIRECTORY_DOMAIN
read -p "Admin email for SSL certificates: " ADMIN_EMAIL
read -s -p "Database password: " DB_PASSWORD
echo ""

# Create production environment file with collected information
cat > .env.production << EOF
# Django environment variables for PRODUCTION
SECRET_KEY=$DJANGO_SECRET_KEY
DEBUG=False
ALLOWED_HOSTS=$DOMAIN_NAME,www.$DOMAIN_NAME,$DIRECTORY_DOMAIN,web,localhost,127.0.0.1

# Database Configuration (PostgreSQL for Docker)
DB_ENGINE=django.db.backends.postgresql
DB_NAME=website_production_db
DB_USER=website_prod_user
DB_PASSWORD=$DB_PASSWORD
DB_HOST=db
DB_PORT=5432

# Email settings for production
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@$DOMAIN_NAME

# Contact form recipients
CONTACT_EMAIL_RECIPIENTS=contact@$DOMAIN_NAME

# Stripe Configuration (Update with production keys)
STRIPE_PUBLISHABLE_KEY=pk_live_your_publishable_key_here
STRIPE_SECRET_KEY=sk_live_your_secret_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here

# Backend Integration Configuration
BACKEND_INTEGRATION_ENABLED=True
CHURCH_DIRECTORY_BACKEND_URL=https://api.your-church-directory-domain.com
CHURCH_DIRECTORY_API_KEY=your-production-api-key-change-this

# Payment Processing Settings (PRODUCTION URLs)
PAYMENT_SUCCESS_URL=https://$DOMAIN_NAME/payment-success/
PAYMENT_CANCEL_URL=https://$DOMAIN_NAME/payment-cancel/

# Security Settings
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
EOF

# Update nginx configuration with actual domains
echo "🌐 Configuring nginx for your domains..."
sed -i "s/verionlabs.com/$DOMAIN_NAME/g" nginx/sites-available/verionlabs.com
sed -i "s/directory.verionlabs.com/$DIRECTORY_DOMAIN/g" nginx/sites-available/directory.verionlabs.com
sed -i "s/www.verionlabs.com/www.$DOMAIN_NAME/g" nginx/sites-available/verionlabs.com

# Update docker-compose with actual database password
sed -i "s/your-production-db-password/$DB_PASSWORD/g" docker-compose.prod.yml

# Stop any existing nginx service that might conflict
echo "🔧 Stopping existing nginx service (if running)..."
sudo systemctl stop nginx 2>/dev/null || true
sudo systemctl disable nginx 2>/dev/null || true

# Start the application
echo "🚀 Starting the application..."
docker-compose -f docker-compose.prod.yml up -d --build

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 30

# Run database migrations
echo "📊 Setting up database..."
docker-compose -f docker-compose.prod.yml exec -T web python manage.py migrate

# Collect static files
echo "🎨 Collecting static files..."
docker-compose -f docker-compose.prod.yml exec -T web python manage.py collectstatic --noinput

# Set up SSL certificates
echo "🔒 Setting up SSL certificates..."
sudo ./setup-ssl.sh

# Create a systemd service for auto-start
echo "⚡ Creating systemd service..."
sudo tee /etc/systemd/system/verionlabs-website.service > /dev/null << EOF
[Unit]
Description=VerionLabs Website
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/verionlabs-website
ExecStart=/usr/local/bin/docker-compose -f docker-compose.prod.yml up -d
ExecStop=/usr/local/bin/docker-compose -f docker-compose.prod.yml down
TimeoutStartSec=0
User=$USER

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable verionlabs-website.service

# Final status check
echo "✅ Checking final status..."
docker-compose -f docker-compose.prod.yml ps

echo ""
echo "=== 🎉 DEPLOYMENT COMPLETE! ==="
echo ""
echo "Your VerionLabs website should now be running at:"
echo "  🌐 Main site: https://$DOMAIN_NAME"
echo "  📁 Directory: https://$DIRECTORY_DOMAIN"
echo ""
echo "Next steps:"
echo "  1. Update your DNS records to point to this server's IP"
echo "  2. Update Stripe keys in .env.production with your live keys"
echo "  3. Configure email settings in .env.production"
echo "  4. Create a Django superuser: docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser"
echo ""
echo "Management commands:"
echo "  📊 View logs: docker-compose -f docker-compose.prod.yml logs -f"
echo "  🔄 Restart: docker-compose -f docker-compose.prod.yml restart"
echo "  ⬇️  Stop: docker-compose -f docker-compose.prod.yml down"
echo "  ⬆️  Start: docker-compose -f docker-compose.prod.yml up -d"
echo ""
echo "Files locations:"
echo "  📁 App: /opt/verionlabs-website"
echo "  💾 Backups: /opt/verionlabs-website/backups"
echo "  📝 Logs: /var/log/verionlabs-backup.log"
echo ""
echo "Security features enabled:"
echo "  🔥 UFW Firewall (ports 22, 80, 443)"
echo "  🛡️  Fail2ban (SSH protection)"
echo "  🔒 SSL certificates (auto-renewal)"
echo "  💾 Daily database backups"
echo ""