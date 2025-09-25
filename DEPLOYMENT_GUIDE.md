# Digital Ocean Droplet Setup Commands
# Quick reference for setting up VerionLabs website on a fresh Ubuntu 22.04 droplet

## Step 1: Initial Server Setup (run these manually)
```bash
# Connect to your droplet
ssh root@your-server-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install essential packages
sudo apt install -y git vim htop ufw fail2ban certbot python3-certbot-nginx

# Configure firewall
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw --force enable
```

## Step 2: Clone and Setup Application
```bash
# Create app directory
mkdir -p /opt/verionlabs-website
cd /opt/verionlabs-website

# Clone your repository
git clone https://github.com/mpavlov-sbc/verionlabs.com.git .

# Make setup script executable
chmod +x deploy-setup.sh

# Run the automated setup (interactive)
./deploy-setup.sh
```

## Step 3: Manual Configuration (after script)
```bash
# Update environment file with your actual credentials
nano .env.production

# Update Stripe keys, email settings, etc.

# Restart services after config changes
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d

# Create Django superuser
docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
```

## Step 4: DNS Configuration
1. Point your domains to the server IP:
   - `verionlabs.com` → Server IP
   - `www.verionlabs.com` → Server IP  
   - `directory.verionlabs.com` → Server IP

## Common Management Commands
```bash
# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Restart services
docker-compose -f docker-compose.prod.yml restart

# Update application
git pull
docker-compose -f docker-compose.prod.yml up -d --build

# Backup database
docker-compose -f docker-compose.prod.yml exec db pg_dump -U website_prod_user website_production_db > backup.sql

# Restore database
docker-compose -f docker-compose.prod.yml exec -T db psql -U website_prod_user website_production_db < backup.sql

# Shell access
docker-compose -f docker-compose.prod.yml exec web bash
docker-compose -f docker-compose.prod.yml exec db psql -U website_prod_user website_production_db

# Check status
docker-compose -f docker-compose.prod.yml ps
systemctl status verionlabs-website
```

## Security Checklist
- [ ] UFW firewall enabled
- [ ] Fail2ban configured
- [ ] SSL certificates installed
- [ ] Strong database passwords
- [ ] Django SECRET_KEY changed
- [ ] Debug mode disabled
- [ ] Admin user created
- [ ] Backup script scheduled

## Troubleshooting
```bash
# Check nginx config
docker-compose -f docker-compose.prod.yml exec nginx nginx -t

# Check SSL certificates
sudo certbot certificates

# View system logs
journalctl -u verionlabs-website -f

# Monitor resources
htop
df -h
docker system df
```