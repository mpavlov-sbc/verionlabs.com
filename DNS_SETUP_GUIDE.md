# DNS Configuration Guide for VerionLabs Website
# Server IP: 209.38.156.33

## DNS Records to Configure

You need to configure the following DNS records in your domain registrar's DNS management panel:

### For verionlabs.com domain:

| Type | Name/Host | Value/Target | TTL |
|------|-----------|--------------|-----|
| A    | @         | 209.38.156.33 | 300 |
| A    | www       | 209.38.156.33 | 300 |
| A    | directory | 209.38.156.33 | 300 |

### Alternative CNAME setup (if you prefer):

| Type  | Name/Host | Value/Target      | TTL |
|-------|-----------|-------------------|-----|
| A     | @         | 209.38.156.33     | 300 |
| CNAME | www       | verionlabs.com    | 300 |
| CNAME | directory | verionlabs.com    | 300 |

## Step-by-Step Instructions

### 1. Access Your Domain Registrar
- Log into your domain registrar (GoDaddy, Namecheap, Cloudflare, etc.)
- Navigate to DNS Management or DNS Settings for verionlabs.com

### 2. Add/Update DNS Records

**Record 1: Root Domain**
- Type: A
- Name/Host: @ (or leave blank, or verionlabs.com)
- Value: 209.38.156.33
- TTL: 300 (5 minutes)

**Record 2: WWW Subdomain**
- Type: A
- Name/Host: www
- Value: 209.38.156.33
- TTL: 300

**Record 3: Directory Subdomain**
- Type: A
- Name/Host: directory
- Value: 209.38.156.33
- TTL: 300

### 3. Remove Conflicting Records
Make sure to remove any existing A or CNAME records that might conflict with these domains.

## DNS Propagation

- DNS changes typically take 5-60 minutes to propagate
- Use TTL of 300 seconds (5 minutes) for faster updates during setup
- You can increase TTL to 3600 (1 hour) or higher once everything is working

## Test DNS Resolution

Use these commands to test if DNS is working:

```bash
# Test main domain
nslookup verionlabs.com
dig verionlabs.com

# Test www subdomain
nslookup www.verionlabs.com
dig www.verionlabs.com

# Test directory subdomain
nslookup directory.verionlabs.com
dig directory.verionlabs.com

# All should return: 209.38.156.33
```

## Online DNS Testing Tools

- https://www.whatsmydns.net/
- https://dnschecker.org/
- https://www.dnswatch.info/

Enter your domain names and check if they resolve to 209.38.156.33 globally.

## Common DNS Registrars Instructions

### Cloudflare
1. Go to cloudflare.com → Your domain → DNS
2. Add A records as shown above
3. Make sure proxy status is "DNS only" (gray cloud, not orange)

### GoDaddy
1. Go to GoDaddy → My Products → DNS
2. Add A records in the DNS Management section

### Namecheap
1. Go to Domain List → Manage → Advanced DNS
2. Add A records in the Host Records section

### Google Domains
1. Go to domains.google.com → Your domain → DNS
2. Add A records in the Custom Records section

## After DNS is Configured

Once DNS is propagated (test with nslookup), you can:

1. **Test HTTP access:**
   ```bash
   curl -I http://verionlabs.com
   curl -I http://www.verionlabs.com
   curl -I http://directory.verionlabs.com
   ```

2. **Install SSL certificates:**
   ```bash
   cd /opt/verionlabs-website
   sudo ./setup-ssl.sh
   ```

3. **Test HTTPS access:**
   ```bash
   curl -I https://verionlabs.com
   curl -I https://www.verionlabs.com
   curl -I https://directory.verionlabs.com
   ```

## Troubleshooting

**If domains don't resolve:**
- Wait longer (DNS can take up to 24-48 hours in rare cases)
- Check for typos in DNS records
- Make sure you're editing the right domain zone
- Contact your registrar support if needed

**If SSL fails:**
- Make sure DNS is fully propagated first
- Ensure ports 80 and 443 are open on your server
- Check that nginx is not running outside Docker