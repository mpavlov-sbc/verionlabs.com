#!/bin/bash

# SSL Setup Script for Production
# This script helps set up SSL certificates for both domains

echo "=== SSL Setup for VerionLabs Domains ==="

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run this script as root (use sudo)"
    exit 1
fi

# Get domain names from user
read -p "Enter your main domain (e.g., verionlabs.com): " DOMAIN_NAME
read -p "Enter your directory subdomain (e.g., directory.verionlabs.com): " DIRECTORY_DOMAIN
ADMIN_EMAIL="contact@verionlabs.com"
echo "Using admin email: $ADMIN_EMAIL"

# Install certbot if not already installed
if ! command -v certbot &> /dev/null; then
    echo "Installing certbot..."
    apt-get update
    apt-get install -y certbot
fi

# Stop nginx temporarily
echo "Stopping nginx temporarily for certificate generation..."
cd /opt/verionlabs-website
docker-compose -f docker-compose.prod.yml stop nginx

# Generate certificates for both domains
echo "Generating SSL certificate for $DOMAIN_NAME..."
certbot certonly --standalone \
    -d $DOMAIN_NAME \
    -d www.$DOMAIN_NAME \
    --email $ADMIN_EMAIL \
    --agree-tos \
    --non-interactive

echo "Generating SSL certificate for $DIRECTORY_DOMAIN..."
certbot certonly --standalone \
    -d $DIRECTORY_DOMAIN \
    --email $ADMIN_EMAIL \
    --agree-tos \
    --non-interactive

# Update docker-compose to mount SSL certificates
echo "Updating docker-compose to mount SSL certificates..."
sed -i '/# For SSL certificates/,/# - \/etc\/letsencrypt/ {
    s/# - \/etc\/letsencrypt/- \/etc\/letsencrypt/
}' docker-compose.prod.yml

# Enable HTTPS configurations in nginx files
echo "Enabling HTTPS configurations..."
# Update nginx configs to use actual domain names and enable SSL blocks
sed -i "s/verionlabs\.com/$DOMAIN_NAME/g" nginx/sites-available/verionlabs.com
sed -i "s/www\.verionlabs\.com/www.$DOMAIN_NAME/g" nginx/sites-available/verionlabs.com
sed -i "s/directory\.verionlabs\.com/$DIRECTORY_DOMAIN/g" nginx/sites-available/directory.verionlabs.com

# Uncomment SSL server blocks
sed -i '/# HTTPS redirect (for production with SSL)/,/# }/ {
    s/^# //
}' nginx/sites-available/verionlabs.com

sed -i '/# HTTPS redirect (for production with SSL)/,/# }/ {
    s/^# //
}' nginx/sites-available/directory.verionlabs.com

# Set up automatic renewal
echo "Setting up automatic certificate renewal..."
(crontab -l 2>/dev/null; echo "0 12 * * * /usr/bin/certbot renew --quiet --deploy-hook 'cd /opt/verionlabs-website && docker-compose -f docker-compose.prod.yml restart nginx'") | crontab -

# Restart nginx with SSL
echo "Restarting nginx with SSL configuration..."
docker-compose -f docker-compose.prod.yml up -d nginx

# Wait a moment and check status
sleep 5
docker-compose -f docker-compose.prod.yml ps

echo "=== SSL Setup Complete ==="
echo "Your sites should now be available at:"
echo "  - https://$DOMAIN_NAME"
echo "  - https://www.$DOMAIN_NAME"
echo "  - https://$DIRECTORY_DOMAIN"
echo ""
echo "Certificates will automatically renew every 12 hours via cron job."
echo ""
echo "To test SSL certificates:"
echo "  curl -I https://$DOMAIN_NAME"
echo "  curl -I https://$DIRECTORY_DOMAIN"