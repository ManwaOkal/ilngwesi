"""
Safaricom Daraja API Configuration
Update these values with your actual credentials from the Daraja Portal
"""

import os

# Environment: 'sandbox' or 'production'
ENVIRONMENT = os.getenv('SAFARICOM_ENV', 'sandbox')

# Daraja API Credentials (from Daraja Portal > My Apps)
CONSUMER_KEY = os.getenv('SAFARICOM_CONSUMER_KEY', 'your_consumer_key_here')
CONSUMER_SECRET = os.getenv('SAFARICOM_CONSUMER_SECRET', 'your_consumer_secret_here')

# M-Pesa Short Code (PayBill or Till Number)
SHORT_CODE = os.getenv('SAFARICOM_SHORT_CODE', '600984')  # Update with your short code

# API Endpoints
if ENVIRONMENT == 'sandbox':
    BASE_URL = 'https://sandbox.safaricom.co.ke'
    OAUTH_URL = f'{BASE_URL}/oauth/v1/generate?grant_type=client_credentials'
    C2B_REGISTER_URL = f'{BASE_URL}/mpesa/c2b/v2/registerurl'
    C2B_SIMULATE_URL = f'{BASE_URL}/mpesa/c2b/v2/simulate'
    STK_PUSH_URL = f'{BASE_URL}/mpesa/stkpush/v1/processrequest'
    STK_QUERY_URL = f'{BASE_URL}/mpesa/stkpushquery/v1/query'
    B2C_URL = f'{BASE_URL}/mpesa/b2c/v1/paymentrequest'
    TRANSACTION_STATUS_URL = f'{BASE_URL}/mpesa/transactionstatus/v1/query'
else:
    BASE_URL = 'https://api.safaricom.co.ke'
    OAUTH_URL = f'{BASE_URL}/oauth/v1/generate?grant_type=client_credentials'
    C2B_REGISTER_URL = f'{BASE_URL}/mpesa/c2b/v2/registerurl'
    STK_PUSH_URL = f'{BASE_URL}/mpesa/stkpush/v1/processrequest'
    STK_QUERY_URL = f'{BASE_URL}/mpesa/stkpushquery/v1/query'
    B2C_URL = f'{BASE_URL}/mpesa/b2c/v1/paymentrequest'
    TRANSACTION_STATUS_URL = f'{BASE_URL}/mpesa/transactionstatus/v1/query'

# STK Push Passkey (Sandbox default, production from Safaricom)
STK_PASSKEY = os.getenv('SAFARICOM_PASSKEY', 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919')

# Callback URLs (Update with your actual URLs)
# For local testing, use ngrok: ngrok http 5000
VALIDATION_URL = os.getenv('VALIDATION_URL', 'https://your-domain.com/api/mpesa/validation')
CONFIRMATION_URL = os.getenv('CONFIRMATION_URL', 'https://your-domain.com/api/mpesa/confirmation')

# Response Type for validation failures
RESPONSE_TYPE = 'Completed'  # Options: 'Completed' or 'Cancelled'

# M-Pesa API Certificates Path
# Download from: https://developer.safaricom.co.ke
MPESA_PUBLIC_KEY_PATH = os.getenv('MPESA_PUBLIC_KEY_PATH', 'certs/mpesa_public_cert.cer')

# Security Credentials (for B2C, B2B, etc.)
# Generate using M-Pesa public key certificate
INITIATOR_NAME = os.getenv('INITIATOR_NAME', 'testapi')
INITIATOR_PASSWORD = os.getenv('INITIATOR_PASSWORD', 'your_initiator_password')

