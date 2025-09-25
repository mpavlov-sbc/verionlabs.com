#!/bin/bash

# SSL Setup Script for Production
# This script helps set up SSL certificates for both domains

echo "=== SSL Setup for VerionLabs Domains ==="

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run this script as root (use sudo)"
    exit 1
fi

# Install certbot if not already installed
if ! command -v certbot &> /dev/null; then
    echo "Installing certbot..."
    apt-get update
    apt-get install -y certbot python3-certbot-nginx
fi

# Stop nginx temporarily
echo "Stopping nginx temporarily for certificate generation..."
docker-compose -f docker-compose.prod.yml stop nginx

# Generate certificates for both domains
echo "Generating SSL certificate for verionlabs.com..."
certbot certonly --standalone -d verionlabs.com -d www.verionlabs.com \
    --email admin@verionlabs.com \
    --agree-tos \
    --non-interactive

echo "Generating SSL certificate for directory.verionlabs.com..."
certbot certonly --standalone -d directory.verionlabs.com \
    --email admin@verionlabs.com \
    --agree-tos \
    --non-interactive

# Generate DH parameters (this may take a while)
echo "Generating DH parameters (this may take several minutes)..."
if [ ! -f /etc/nginx/dhparam.pem ]; then
    openssl dhparam -out /etc/nginx/dhparam.pem 2048
fi

# Enable HTTPS configurations
echo "Enabling HTTPS configurations..."
sed -i 's/# server {/server {/g' /app/nginx/sites-available/verionlabs.com
sed -i 's/# }/}/g' /app/nginx/sites-available/verionlabs.com
sed -i 's/# ssl_/ssl_/g' /app/nginx/sites-available/verionlabs.com
sed -i 's/# include/include/g' /app/nginx/sites-available/verionlabs.com
sed -i 's/# \.\.\./    # Copy all location blocks from HTTP version/g' /app/nginx/sites-available/verionlabs.com

sed -i 's/# server {/server {/g' /app/nginx/sites-available/directory.verionlabs.com
sed -i 's/# }/}/g' /app/nginx/sites-available/directory.verionlabs.com
sed -i 's/# ssl_/ssl_/g' /app/nginx/sites-available/directory.verionlabs.com
sed -i 's/# include/include/g' /app/nginx/sites-available/directory.verionlabs.com
sed -i 's/# \.\.\./    # Copy all location blocks from HTTP version/g' /app/nginx/sites-available/directory.verionlabs.com

# Set up automatic renewal
echo "Setting up automatic certificate renewal..."
(crontab -l 2>/dev/null; echo "0 12 * * * /usr/bin/certbot renew --quiet --deploy-hook 'docker-compose -f $(pwd)/docker-compose.prod.yml restart nginx'") | crontab -

# Restart nginx
echo "Restarting nginx with SSL configuration..."
docker-compose -f docker-compose.prod.yml up -d nginx

echo "=== SSL Setup Complete ==="
echo "Your sites should now be available at:"
echo "  - https://verionlabs.com"
echo "  - https://www.verionlabs.com"
echo "  - https://directory.verionlabs.com"
echo ""
echo "Certificates will automatically renew every 12 hours via cron job."