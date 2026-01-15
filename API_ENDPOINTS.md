# API Endpoints Documentation

Complete list of API endpoints for the Community Tourism Relay System.

## Base URL
- **Development**: `http://localhost:5000`
- **Production**: `https://your-domain.com`

## Booking Endpoints

### Create Booking
**POST** `/api/booking`

Create a new booking request.

**Request Body:**
```json
{
  "touristName": "John Doe",
  "touristEmail": "john@example.com",
  "touristPhone": "+254712345678",
  "arrivalDate": "2024-03-15",
  "numVisitors": 2,
  "services": ["guided_walk", "homestay"],
  "totalAmount": 4000,
  "specialRequests": "Vegetarian meals please"
}
```

**Response:**
```json
{
  "success": true,
  "booking_code": "V20240314-001",
  "message": "Booking request submitted successfully"
}
```

### Get Booking Status
**GET** `/api/booking/<booking_code>`

Retrieve booking details and status.

**Response:**
```json
{
  "booking_code": "V20240314-001",
  "tourist_name": "John Doe",
  "arrival_date": "2024-03-15",
  "num_visitors": 2,
  "requested_services": ["guided_walk", "homestay"],
  "status": "confirmed",
  "payment_status": "paid",
  "total_amount": 4000.0,
  "confirmed_services": ["guided_walk", "homestay"],
  "created_at": "2024-03-14 10:30:00"
}
```

### Receive SMS from Steward
**POST** `/api/sms/incoming`

Receive SMS confirmation from Tourism Steward.

**Request Body:**
```json
{
  "from": "+254741770540",
  "message": "CONFIRM V20240314-001 WALK YES HOME YES"
}
```

## M-Pesa Endpoints

### Register C2B URLs
**POST** `/api/mpesa/register-urls`

Register validation and confirmation URLs with Safaricom (one-time setup).

**Response:**
```json
{
  "success": true,
  "message": "C2B URLs registered successfully",
  "data": {
    "ResponseCode": "0",
    "ResponseDescription": "Success"
  }
}
```

### C2B Validation Callback
**POST** `/api/mpesa/validation`

Called by Safaricom to validate payments before processing.

**Request Body (from Safaricom):**
```json
{
  "TransactionType": "Pay Bill",
  "TransAmount": "4000.00",
  "BusinessShortCode": "600984",
  "BillRefNumber": "V20240314-001",
  "MSISDN": "2547*****126"
}
```

**Response:**
```json
{
  "ResultCode": "0",
  "ResultDesc": "Accepted"
}
```

### C2B Confirmation Callback
**POST** `/api/mpesa/confirmation`

Called by Safaricom after successful payment.

**Request Body (from Safaricom):**
```json
{
  "TransactionType": "Pay Bill",
  "TransID": "RKL51ZDR4F",
  "TransTime": "20240314121325",
  "TransAmount": "4000.00",
  "BusinessShortCode": "600984",
  "BillRefNumber": "V20240314-001",
  "MSISDN": "2547*****126",
  "FirstName": "JOHN",
  "LastName": "DOE"
}
```

### Initiate STK Push (Lipa na M-Pesa Online)
**POST** `/api/mpesa/stk-push`

Send push notification to customer's phone for payment.

**Request Body:**
```json
{
  "booking_code": "V20240314-001",
  "phone_number": "254712345678"
}
```

**Response:**
```json
{
  "success": true,
  "checkout_request_id": "ws_CO_14032024121325",
  "customer_message": "Success. Request accepted for processing",
  "message": "STK Push initiated. Please check your phone."
}
```

### STK Push Callback
**POST** `/api/mpesa/stk-callback`

Receives STK Push payment result from Safaricom.

**Request Body (from Safaricom):**
```json
{
  "Body": {
    "stkCallback": {
      "CheckoutRequestID": "ws_CO_14032024121325",
      "ResultCode": 0,
      "ResultDesc": "The service request is processed successfully.",
      "CallbackMetadata": {
        "Item": [
          {"Name": "Amount", "Value": 4000},
          {"Name": "MpesaReceiptNumber", "Value": "RKL51ZDR4F"},
          {"Name": "PhoneNumber", "Value": 254712345678}
        ]
      }
    }
  }
}
```

### Test Token Generation
**GET** `/api/mpesa/test-token`

Test Safaricom OAuth token generation.

**Response:**
```json
{
  "success": true,
  "access_token": "c9SQxWWhmdVRlyh0zh8gZDTkubVF...",
  "message": "Token generated successfully"
}
```

## Availability Endpoint

### Check Availability
**GET** `/api/availability`

Check community availability (placeholder).

**Response:**
```json
{
  "available": true,
  "message": "Contact steward for current availability"
}
```

## Payment Flow Options

### Option 1: C2B Payment (Customer initiated)
1. Customer pays via M-Pesa App/USSD to PayBill/Till Number
2. Include booking code in account reference
3. System receives validation → confirmation callbacks
4. Booking status updated automatically

### Option 2: STK Push (System initiated)
1. Customer submits booking
2. System calls `/api/mpesa/stk-push`
3. Customer receives push notification on phone
4. Customer enters PIN to complete payment
5. System receives callback with payment result

## Error Responses

All endpoints return standard HTTP status codes:

- **200**: Success
- **400**: Bad Request (missing/invalid parameters)
- **404**: Resource not found
- **500**: Internal server error

**Error Response Format:**
```json
{
  "error": "Error message description"
}
```

## Authentication

Most endpoints don't require authentication (for simplicity). In production, consider adding:
- API key authentication
- Rate limiting
- IP whitelisting for callbacks

## Testing

### Sandbox Testing
1. Use test credentials from Daraja Portal
2. Use test phone number: `254708374149`
3. Use ngrok for local callback testing: `ngrok http 5000`

### Production
1. Update `safaricom_config.py` with production credentials
2. Ensure HTTPS for all callback URLs
3. Whitelist Safaricom IP addresses
4. Register URLs once via `/api/mpesa/register-urls`

