server {
    listen 80;
    server_name verionlabs.com www.verionlabs.com;
    
    # Rate limiting
    limit_req zone=web burst=20 nodelay;

    # Client settings
    client_max_body_size 75M;
    
    # Static files
    location /static/ {
        alias /app/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, no-transform";
        
        # Security headers for static files
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
    }
    
    # Media files
    location /media/ {
        alias /app/media/;
        expires 30d;
        add_header Cache-Control "public, no-transform";
    }
    
    # Health check endpoint
    location /health/ {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }

    # Main application - exclude /directory/ path
    location / {
        # Block access to /directory/ path on main domain
        location /directory/ {
            return 404;
        }
        
        proxy_pass http://django_web;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeout settings
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # Buffer settings
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
        proxy_busy_buffers_size 8k;
    }
}

# HTTPS redirect (for production with SSL)
# server {
#     listen 443 ssl http2;
#     server_name verionlabs.com www.verionlabs.com;
#     
#     # SSL configuration
#     ssl_certificate /etc/letsencrypt/live/verionlabs.com/fullchain.pem;
#     ssl_certificate_key /etc/letsencrypt/live/verionlabs.com/privkey.pem;
#     
#     # Include SSL settings
#     include /etc/nginx/ssl-params.conf;
#     
#     # Same location blocks as HTTP version above
#     # ... (copy all location blocks from above)
# }