# Environment Configuration Guide

## Overview
This guide explains how to configure the environment variables for the Stripe payment integration between the marketing website and the church directory backend.

## Files Structure
```
/Users/mp/Projects/website/
├── .env                    # Development environment for marketing site
├── .env.production        # Production environment for marketing site

/Users/mp/Projects/church-directory/backend/
├── .env.debug            # Development environment for backend
├── .env.production       # Production environment for backend
```

## Required Configuration Steps

### 1. Stripe Account Setup
1. Create a Stripe account at https://stripe.com
2. Get your API keys from the Stripe Dashboard:
   - **Test keys** (for development): `pk_test_...` and `sk_test_...`
   - **Live keys** (for production): `pk_live_...` and `sk_live_...`

### 2. Stripe Webhook Configuration
1. Go to Stripe Dashboard > Developers > Webhooks
2. Create a new webhook endpoint:
   - **Development URL**: `http://localhost:8000/webhooks/stripe/`
   - **Production URL**: `https://yourmarketingsite.com/webhooks/stripe/`
3. Select these events:
   - `checkout.session.completed`
   - `checkout.session.expired`
   - `payment_intent.succeeded` (optional, for fallback)
   - `invoice.payment_succeeded` (for recurring billing)
4. Copy the webhook secret (`whsec_...`)

### 3. Environment Variables to Update

#### Marketing Website (.env and .env.production)

**Development (.env):**
```bash
# Stripe Test Keys
STRIPE_PUBLISHABLE_KEY=pk_test_your_test_key_here
STRIPE_SECRET_KEY=sk_test_your_test_secret_here
STRIPE_WEBHOOK_SECRET=whsec_your_test_webhook_secret

# Backend Integration
CHURCH_DIRECTORY_BACKEND_URL=http://localhost:8001
CHURCH_DIRECTORY_API_KEY=dev-marketing-key-12345
```

**Production (.env.production):**
```bash
# Stripe Live Keys
STRIPE_PUBLISHABLE_KEY=pk_live_your_live_key_here
STRIPE_SECRET_KEY=sk_live_your_live_secret_here
STRIPE_WEBHOOK_SECRET=whsec_your_live_webhook_secret

# Backend Integration
CHURCH_DIRECTORY_BACKEND_URL=https://directory.salvationbc.com
CHURCH_DIRECTORY_API_KEY=your-secure-production-api-key
```

#### Backend (.env.debug and .env.production)

**Development (.env.debug):**
```bash
# API Configuration
BACKEND_API_ENABLED=True
MARKETING_INTEGRATION_API_KEY=dev-marketing-key-12345
CORS_ALLOWED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000
```

**Production (.env.production):**
```bash
# API Configuration
BACKEND_API_ENABLED=True
MARKETING_INTEGRATION_API_KEY=your-secure-production-api-key
CORS_ALLOWED_ORIGINS=https://yourmarketingsite.com
```

### 4. Security Considerations

#### API Keys
- **Never commit real API keys to version control**
- Use different API keys for development and production
- Rotate API keys regularly
- Restrict API key permissions in Stripe dashboard

#### Webhook Secrets
- Use different webhook secrets for each environment
- Keep webhook secrets secure and never expose them in client-side code
- Test webhook endpoints before going live

#### CORS Origins
- Only allow trusted domains in CORS_ALLOWED_ORIGINS
- Use HTTPS in production
- Restrict backend API access to known marketing site domains

#### API Key Authentication
- `CHURCH_DIRECTORY_API_KEY` (website) must match `MARKETING_INTEGRATION_API_KEY` (backend)
- Use different keys for development and production environments
- Keep API keys secure and rotate them regularly

### 5. Testing Your Configuration

#### Development Testing
```bash
# Navigate to website directory
cd /Users/mp/Projects/website

# Run the test script
python3 test_stripe_checkout.py

# Start the development server
python3 manage.py runserver 8000
```

#### Webhook Testing
```bash
# Install Stripe CLI
# Forward webhooks to local development
stripe listen --forward-to localhost:8000/webhooks/stripe/

# In another terminal, trigger test events
stripe trigger checkout.session.completed
```

### 6. Production Deployment

#### Before Deploying:
1. ✅ Update all production environment variables
2. ✅ Test Stripe webhooks with live endpoints
3. ✅ Verify backend API connectivity
4. ✅ Test complete payment flow in Stripe test mode
5. ✅ Switch to Stripe live mode when ready

#### Deployment Checklist:
- [ ] Production Stripe keys configured
- [ ] Webhook endpoints pointing to production URLs
- [ ] Backend API keys match between marketing site and backend
- [ ] CORS origins configured for production domains
- [ ] SSL certificates installed and working
- [ ] Database migrations applied
- [ ] Static files collected and served properly

### 7. Monitoring and Troubleshooting

#### Key Logs to Monitor:
- Stripe webhook processing logs
- Backend API integration logs
- Payment completion rates
- Organization creation success rates

#### Common Issues:
- **Webhook signature verification fails**: Check STRIPE_WEBHOOK_SECRET
- **Backend API calls fail**: Verify CHURCH_DIRECTORY_BACKEND_URL and CHURCH_DIRECTORY_API_KEY
- **CORS errors**: Check CORS_ALLOWED_ORIGINS configuration
- **Payment processing fails**: Check Stripe dashboard for errors

#### Debug Commands:
```bash
# Test backend API connectivity
curl -X GET "http://localhost:8001/api/health/" \
  -H "Authorization: Bearer test-api-key-for-development"

# Check webhook event processing
tail -f django.log | grep "webhook"

# Test Stripe configuration
python3 test_stripe_checkout.py
```

## Support

For issues with this configuration:
1. Check the STRIPE_CHECKOUT_GUIDE.md for implementation details
2. Run the test script to verify configuration
3. Check Django logs for specific error messages
4. Verify Stripe dashboard for payment event details

## Security Notice

🔐 **IMPORTANT**: 
- Never commit `.env` files containing real API keys
- Always use test keys for development
- Regularly rotate production API keys
- Monitor webhook endpoints for suspicious activity
- Use HTTPS in production for all API communications