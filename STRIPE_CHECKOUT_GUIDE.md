# Stripe Checkout Integration Guide

## Overview

The church directory marketing website now uses **Stripe Checkout** instead of Stripe Elements for payment processing. This provides a more reliable, secure, and maintainable payment solution.

## Architecture Changes

### Before (Stripe Elements)
- Custom payment form with complex JavaScript
- Client-side payment intent confirmation
- Multiple frontend-backend API calls
- Complex error handling and 3D Secure flow
- Custom payment UI that needed maintenance

### After (Stripe Checkout)
- Simple redirect to Stripe's hosted checkout page
- All payment processing handled by Stripe
- Single redirect back to success/cancel pages
- Built-in security, compliance, and mobile optimization
- No payment UI maintenance required

## Implementation Details

### 1. Checkout Flow

```python
# User submits checkout form
# ↓
# Server creates Stripe Checkout Session
checkout_session = StripeService.create_checkout_session(
    subscription=subscription,
    success_url=success_url,
    cancel_url=cancel_url
)
# ↓
# User redirected to checkout_session.url
# ↓ (User completes payment on Stripe)
# Stripe processes payment and sends webhook
# ↓
# Webhook handler activates subscription & creates organization
```

### 2. Key Components

#### StripeService Updates
- `create_checkout_session()` - Creates hosted checkout
- `retrieve_checkout_session()` - Gets session status
- `_handle_checkout_session_completed()` - Webhook handler
- `_handle_checkout_session_expired()` - Expiration handler

#### View Changes
- Simplified `checkout()` view
- Removed `PaymentProcessView` (no longer needed)
- Updated `payment_cancel()` with session handling
- Direct redirect to Stripe Checkout URL

#### Template Simplification
- Removed complex Stripe Elements JavaScript
- Simple form submission that redirects to Stripe
- Clean loading states and success messaging
- No payment card UI components needed

#### Model Updates
- `PaymentIntent` model now handles both Payment Intents and Checkout Sessions
- Added checkout-specific status choices (`pending`, `completed`, `expired`)
- `is_checkout_session` property to identify session records
- Extended field lengths for checkout URLs

### 3. Webhook Events

New webhook events handled:
- `checkout.session.completed` - Payment successful
- `checkout.session.expired` - Session expired without payment

Existing events still supported:
- `payment_intent.succeeded` (for direct API usage)
- `invoice.payment_succeeded` (for recurring billing)

### 4. Error Handling

Simplified error handling:
- Checkout creation errors handled server-side
- Payment errors handled by Stripe's UI
- Session expiration handled automatically
- Webhook failures logged and retryable

## Configuration

### Environment Variables
```bash
# Same Stripe keys as before
STRIPE_PUBLISHABLE_KEY=pk_...
STRIPE_SECRET_KEY=sk_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Backend integration (unchanged)
BACKEND_INTEGRATION_ENABLED=True
CHURCH_DIRECTORY_BACKEND_URL=http://localhost:8001
CHURCH_DIRECTORY_API_KEY=your_api_key
```

### Webhook Endpoints
```bash
# Update your Stripe webhook endpoint to listen for:
checkout.session.completed
checkout.session.expired
```

## Testing

### Run Integration Tests
```bash
cd /Users/mp/Projects/website
python3 test_stripe_checkout.py
```

### Manual Testing Flow
1. Visit `/checkout/?tier=1&billing=monthly`
2. Fill out church information form
3. Click "Continue to Secure Checkout"
4. Complete payment on Stripe's hosted page
5. Verify redirect to success page
6. Check backend organization creation

### Test Webhook Events
```bash
# Use Stripe CLI to forward webhooks
stripe listen --forward-to localhost:8000/webhooks/stripe/
```

## Benefits of Stripe Checkout

### Reliability
- ✅ Stripe handles all payment edge cases
- ✅ Built-in 3D Secure support
- ✅ Automatic retry logic for failed payments
- ✅ PCI compliance handled by Stripe

### User Experience
- ✅ Mobile-optimized checkout flow
- ✅ Multiple payment methods (cards, wallets, BNPL)
- ✅ Automatic address validation
- ✅ Multi-language support

### Developer Experience
- ✅ 90% less frontend payment code
- ✅ No complex JavaScript debugging
- ✅ No payment form maintenance
- ✅ Simplified error handling

### Security
- ✅ Payment data never touches your servers
- ✅ Automatic fraud detection
- ✅ Strong customer authentication
- ✅ SSL/TLS handled by Stripe

## Migration Notes

### Removed Components
- `payment_process.html` template (no longer used)
- Stripe Elements JavaScript code
- `PaymentProcessView` class
- Complex payment confirmation logic
- Manual 3D Secure handling

### Preserved Components
- All existing database models
- Webhook processing infrastructure
- Backend organization creation
- Subscription management
- Admin dashboard functionality

### Backward Compatibility
- Existing subscriptions continue to work
- Webhook events from both systems handled
- Same database schema (with additions)
- Same admin interface

## Deployment Checklist

- [ ] Update Stripe webhook endpoints to include checkout events
- [ ] Test checkout flow in Stripe test mode
- [ ] Verify backend organization creation still works
- [ ] Update any monitoring/alerting for new error patterns
- [ ] Run migration for PaymentIntent model changes
- [ ] Deploy and test production webhook endpoints

## Troubleshooting

### Common Issues

**Checkout Session Creation Fails**
- Check Stripe API keys in settings
- Verify line_items formatting
- Check success/cancel URL accessibility

**Webhooks Not Processing**
- Verify webhook secret in settings
- Check webhook event types in Stripe dashboard
- Ensure checkout.session.completed event enabled

**Backend Integration Fails**
- Check backend API configuration
- Verify subscription has required fields
- Test backend API connectivity manually

### Monitoring

Key metrics to monitor:
- Checkout session creation success rate
- Webhook processing success rate
- Backend integration success rate
- Payment completion rate

### Logs

Important log entries:
```
INFO: Created Checkout Session cs_xxx for subscription xxx
INFO: Webhook event checkout.session.completed processed
INFO: Successfully created backend organization for subscription xxx
ERROR: Failed to create Checkout Session: [error details]
```

## Support

For issues with this integration:
1. Check the test script output: `python3 test_stripe_checkout.py`
2. Review Stripe dashboard for payment events
3. Check Django logs for webhook processing
4. Verify backend API connectivity

The Stripe Checkout integration provides a more robust, secure, and maintainable payment solution for the church directory system.