# M-Pesa Integration Setup Guide

This guide will help you set up Safaricom Daraja API integration for the Community Tourism Relay System.

## Prerequisites

1. **Daraja Developer Account**
   - Sign up at https://developer.safaricom.co.ke
   - Create a sandbox app to get API credentials

2. **M-Pesa Business Account**
   - PayBill or Till Number
   - Business Administrator access to M-PESA Organization Portal

## Step 1: Get API Credentials

1. Log in to [Daraja Developer Portal](https://developer.safaricom.co.ke)
2. Go to **My Apps** section
3. Create a new app or select existing app
4. Copy your **Consumer Key** and **Consumer Secret**

## Step 2: Configure the System

1. Open `safaricom_config.py`
2. Update the following values:

```python
CONSUMER_KEY = 'your_consumer_key_here'
CONSUMER_SECRET = 'your_consumer_secret_here'
SHORT_CODE = '600984'  # Your PayBill or Till Number
```

3. Update callback URLs (for production, use HTTPS):

```python
VALIDATION_URL = 'https://your-domain.com/api/mpesa/validation'
CONFIRMATION_URL = 'https://your-domain.com/api/mpesa/confirmation'
```

## Step 3: Test on Localhost (Sandbox)

For local testing, you need to expose your local server to the internet:

### Option 1: Using Ngrok

```bash
# Install ngrok: https://ngrok.com/download
ngrok http 5000

# Copy the HTTPS URL (e.g., https://abc123.ngrok.io)
# Update safaricom_config.py:
VALIDATION_URL = 'https://abc123.ngrok.io/api/mpesa/validation'
CONFIRMATION_URL = 'https://abc123.ngrok.io/api/mpesa/confirmation'
```

### Option 2: Using LocalTunnel

```bash
npm install -g localtunnel
lt --port 5000

# Copy the URL and update safaricom_config.py
```

## Step 4: Register C2B URLs

Once your server is running and accessible:

```bash
# Start the Flask server
python app.py

# In another terminal, register URLs:
curl -X POST http://localhost:5000/api/mpesa/register-urls \
  -H "Content-Type: application/json"
```

Or use the API endpoint directly from your application.

## Step 5: Test Payment Flow

### Sandbox Testing

1. Use test phone number: `254708374149`
2. Simulate payment using Daraja Simulator or Postman
3. Check your server logs for validation and confirmation callbacks

### Test Token Generation

```bash
curl http://localhost:5000/api/mpesa/test-token
```

## Step 6: Go Live (Production)

1. **Complete M-PESA Portal Setup:**
   - Log in to https://org.ke.m-pesa.com
   - Create Business Manager and API users
   - Set API user passwords

2. **Request Production Credentials:**
   - Email: m-pesabusiness@safaricom.co.ke
   - Include: Short code, organization name, admin username

3. **Update Configuration:**
   ```python
   ENVIRONMENT = 'production'
   CONSUMER_KEY = 'production_consumer_key'
   CONSUMER_SECRET = 'production_consumer_secret'
   ```

4. **Register Production URLs:**
   - URLs must be HTTPS
   - Whitelist Safaricom IPs (see app.py for list)
   - Register URLs once (can be changed via portal)

5. **Test Production Flow:**
   - Use real M-Pesa App or USSD
   - Pay to your PayBill/Till Number
   - Include booking code in account reference

## IP Whitelisting

For production, whitelist these Safaricom IPs to accept callbacks:

```
196.201.214.200
196.201.214.206
196.201.213.114
196.201.214.207
196.201.214.208
196.201.213.44
196.201.212.127
196.201.212.138
196.201.212.129
196.201.212.136
196.201.212.74
196.201.212.69
```

## Payment Flow

1. **Customer initiates payment** via M-Pesa App/USSD
2. **Validation URL** receives request (if enabled)
   - Must respond within 8 seconds
   - Returns `{"ResultCode": "0", "ResultDesc": "Accepted"}` to accept
3. **M-Pesa processes payment**
4. **Confirmation URL** receives payment notification
   - Update booking status
   - Record transaction
   - Notify tourist and steward

## Account Reference Format

When customers pay, they should include the booking code in the account reference:
- **PayBill**: Account number = Booking code (e.g., `V20240314-001`)
- **Till Number**: No account reference needed (booking code tracked separately)

## Troubleshooting

### Token Expiry
- Tokens expire after 3600 seconds (1 hour)
- System automatically refreshes tokens

### URLs Not Receiving Callbacks
- Verify URLs are publicly accessible
- Check HTTPS certificate (production)
- Ensure server is running and accessible
- Check firewall/security group settings

### Validation Errors
- Ensure validation URL responds within 8 seconds
- Return proper JSON format
- Check booking code format matches

### Common Error Codes
- `400.003.01`: Invalid Access Token - Regenerate token
- `500.003.1001`: URLs already registered - Delete via portal first
- `404.003.01`: Resource not found - Check endpoint URL

## Support

- **Daraja Chatbot**: Available on developer portal
- **Email**: apisupport@safaricom.co.ke
- **Incident Management**: https://developer.safaricom.co.ke/incident-management

## Security Notes

1. **Never commit credentials** to version control
2. Use environment variables for sensitive data
3. Enable HTTPS in production
4. Validate all incoming callbacks
5. Implement rate limiting
6. Log all transactions for audit

## Next Steps

After M-Pesa integration:
1. Set up automatic fund distribution (B2C API)
2. Implement SMS notifications (Africa's Talking)
3. Set up email confirmations (SendGrid/Mailgun)
4. Create admin dashboard for transaction monitoring

