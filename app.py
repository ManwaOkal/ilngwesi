#!/usr/bin/env python3
"""
Bridge Server API for Community Tourism Relay System
This handles web bookings and converts them to SMS for community stewards
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3
import os
from datetime import datetime
import uuid
import json

# Import Safaricom API integration
try:
    from safaricom_api import safaricom_api
    SAFARICOM_ENABLED = True
except ImportError:
    SAFARICOM_ENABLED = False
    print("Warning: Safaricom API integration not available. Install dependencies and configure safaricom_config.py")

app = Flask(__name__, static_folder='.')
CORS(app)  # Enable CORS for frontend

# Database setup
DB_NAME = 'ctr_database.db'

def init_db():
    """Initialize the database with required tables"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Create bookings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            booking_code TEXT UNIQUE NOT NULL,
            tourist_name TEXT NOT NULL,
            tourist_contact TEXT NOT NULL,
            tourist_email TEXT NOT NULL,
            arrival_date DATE NOT NULL,
            num_visitors INTEGER NOT NULL,
            requested_services TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            steward_contact TEXT,
            confirmed_services TEXT,
            amount_paid DECIMAL,
            payment_status TEXT DEFAULT 'pending',
            special_requests TEXT,
            total_amount DECIMAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create communities table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS communities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            community_name TEXT NOT NULL,
            steward_name TEXT NOT NULL,
            steward_phone TEXT NOT NULL,
            services_offered TEXT,
            pricing_json TEXT,
            solar_hub_location TEXT,
            notice_board_locations TEXT
        )
    ''')
    
    # Create transactions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            booking_code TEXT NOT NULL,
            mpesa_code TEXT,
            amount DECIMAL NOT NULL,
            distribution_json TEXT,
            status TEXT DEFAULT 'pending',
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (booking_code) REFERENCES bookings(booking_code)
        )
    ''')
    
    # Insert default community if not exists
    cursor.execute('''
        SELECT COUNT(*) FROM communities WHERE community_name = 'Il Ngwesi'
    ''')
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
            INSERT INTO communities (community_name, steward_name, steward_phone, services_offered)
            VALUES (?, ?, ?, ?)
        ''', (
            'Il Ngwesi',
            'Joseph',
            '+254741770540',  # Update with actual steward phone
            json.dumps([
                'guided_walk', 'homestay', 'cultural_evening', 
                'bush_breakfast', 'rhino_sanctuary', 'beading_workshop'
            ])
        ))
    
    conn.commit()
    conn.close()

# Initialize database on startup
init_db()

def generate_booking_code():
    """Generate a unique booking code"""
    date_str = datetime.now().strftime("%Y%m%d")
    unique_id = str(uuid.uuid4())[:8].upper()
    return f"V{date_str}-{unique_id}"

def send_sms_to_steward(phone, message):
    """
    Send SMS to steward via SMS gateway
    In production, integrate with Africa's Talking, Moya Messenger, or Safaricom API
    """
    # TODO: Implement actual SMS sending
    # For now, just log it
    print(f"[SMS TO STEWARD {phone}]")
    print(message)
    print("-" * 50)
    return True

def send_email_confirmation(email, booking_code, booking_details):
    """
    Send email confirmation to tourist
    In production, use SendGrid, Mailgun, or similar service
    """
    # TODO: Implement actual email sending
    print(f"[EMAIL TO {email}]")
    print(f"Booking Code: {booking_code}")
    print(f"Details: {booking_details}")
    print("-" * 50)
    return True

@app.route('/')
def index():
    """Serve the main HTML file"""
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    """Serve static files"""
    return send_from_directory('.', path)

@app.route('/api/booking', methods=['POST'])
def create_booking():
    """Create a new booking from web portal"""
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['touristName', 'touristEmail', 'touristPhone', 
                          'arrivalDate', 'numVisitors', 'services', 'totalAmount', 'paymentMethod']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Validate payment method specific fields
        payment_method = data.get('paymentMethod', 'mpesa')
        if payment_method == 'card':
            card_fields = ['cardNumber', 'cardExpiry', 'cardCVC', 'cardName']
            for field in card_fields:
                if field not in data or not data[field]:
                    return jsonify({'error': f'Missing required card field: {field}'}), 400
        
        # Generate booking code
        booking_code = generate_booking_code()
        
        # Get community steward info
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('SELECT steward_name, steward_phone FROM communities WHERE community_name = ?', 
                      ('Il Ngwesi',))
        community = cursor.fetchone()
        
        if not community:
            conn.close()
            return jsonify({'error': 'Community not found'}), 500
        
        steward_name, steward_phone = community
        
        # Prepare payment info
        payment_info = {
            'method': payment_method,
            'status': 'pending'
        }
        
        if payment_method == 'card':
            # Store only last 4 digits for security
            card_number = data.get('cardNumber', '').replace(' ', '')
            payment_info['card_last4'] = card_number[-4:] if len(card_number) >= 4 else ''
            payment_info['card_expiry'] = data.get('cardExpiry', '')
            payment_info['card_name'] = data.get('cardName', '')
        elif payment_method == 'paypal':
            payment_info['paypal_ready'] = True
        
        # Insert booking into database
        cursor.execute('''
            INSERT INTO bookings (
                booking_code, tourist_name, tourist_contact, tourist_email,
                arrival_date, num_visitors, requested_services, steward_contact,
                total_amount, special_requests, status, payment_status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            booking_code,
            data['touristName'],
            data['touristPhone'],
            data['touristEmail'],
            data['arrivalDate'],
            data['numVisitors'],
            json.dumps(data['services']),
            steward_phone,
            data['totalAmount'],
            data.get('specialRequests', ''),
            'pending',
            json.dumps(payment_info)
        ))
        
        conn.commit()
        conn.close()
        
        # Prepare SMS message for steward
        services_map = {
            'guided_walk': 'Guided Walk',
            'homestay': 'Homestay',
            'cultural_evening': 'Cultural Evening',
            'bush_breakfast': 'Bush Breakfast',
            'rhino_sanctuary': 'Rhino Sanctuary',
            'beading_workshop': 'Beading Workshop'
        }
        
        services_list = ', '.join([services_map.get(s, s) for s in data['services']])
        
        sms_message = f"""VISITOR ALERT
Date: {data['arrivalDate']}
Visitors: {data['numVisitors']} {'person' if data['numVisitors'] == 1 else 'people'}
Requested: {services_list}
Contact: {data['touristPhone']}
Email: {data['touristEmail']}
Reply: CONFIRM {booking_code} [YES/NO for each service]
Code: {booking_code}"""
        
        if data.get('specialRequests'):
            sms_message += f"\nNotes: {data['specialRequests']}"
        
        # Send SMS to steward
        send_sms_to_steward(steward_phone, sms_message)
        
        # Send email confirmation to tourist
        email_message = f"""
Thank you for your booking request with Il Ngwesi Conservancy!

Your booking code is: {booking_code}

Booking Details:
- Arrival Date: {data['arrivalDate']}
- Number of Visitors: {data['numVisitors']}
- Services Requested: {services_list}
- Total Amount: KES {data['totalAmount']:,.2f}

What happens next:
1. Our Tourism Steward will receive your booking via SMS
2. Within 4 hours, you'll receive confirmation of availability
3. You'll receive M-Pesa payment instructions
4. After payment, you'll get final confirmation and arrival details

We'll contact you soon!

Il Ngwesi Conservancy
People of Wildlife
"""
        send_email_confirmation(data['touristEmail'], booking_code, email_message)
        
        return jsonify({
            'success': True,
            'booking_code': booking_code,
            'message': 'Booking request submitted successfully'
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/booking/<booking_code>', methods=['GET'])
def get_booking(booking_code):
    """Get booking status by code"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT booking_code, tourist_name, arrival_date, num_visitors,
                   requested_services, status, payment_status, total_amount,
                   confirmed_services, created_at
            FROM bookings
            WHERE booking_code = ?
        ''', (booking_code,))
        
        booking = cursor.fetchone()
        conn.close()
        
        if not booking:
            return jsonify({'error': 'Booking not found'}), 404
        
        return jsonify({
            'booking_code': booking[0],
            'tourist_name': booking[1],
            'arrival_date': booking[2],
            'num_visitors': booking[3],
            'requested_services': json.loads(booking[4]),
            'status': booking[5],
            'payment_status': booking[6],
            'total_amount': float(booking[7]),
            'confirmed_services': json.loads(booking[8]) if booking[8] else None,
            'created_at': booking[9]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sms/incoming', methods=['POST'])
def receive_sms():
    """
    Receive SMS from stewards (webhook endpoint)
    Format: "CONFIRM V20240314-001 WALK YES HOME YES"
    """
    try:
        data = request.json
        phone = data.get('from')
        message = data.get('message', '').strip().upper()
        
        # Parse confirmation message
        if message.startswith('CONFIRM'):
            parts = message.split()
            if len(parts) >= 2:
                booking_code = parts[1]
                
                # Update booking status
                conn = sqlite3.connect(DB_NAME)
                cursor = conn.cursor()
                
                # Parse confirmed services from message
                # This is simplified - in production, parse more carefully
                confirmed_services = []
                if 'WALK YES' in message or 'GUIDED_WALK YES' in message:
                    confirmed_services.append('guided_walk')
                if 'HOME YES' in message or 'HOMESTAY YES' in message:
                    confirmed_services.append('homestay')
                # Add more parsing logic as needed
                
                cursor.execute('''
                    UPDATE bookings
                    SET status = 'confirmed',
                        confirmed_services = ?
                    WHERE booking_code = ?
                ''', (json.dumps(confirmed_services), booking_code))
                
                conn.commit()
                conn.close()
                
                # Send confirmation email/SMS to tourist
                # TODO: Implement notification to tourist
                
                return jsonify({'success': True, 'message': 'Booking confirmed'}), 200
        
        return jsonify({'success': False, 'message': 'Invalid SMS format'}), 400
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/mpesa/validation', methods=['POST'])
def mpesa_validation():
    """
    M-Pesa C2B Validation URL
    Called when external validation is enabled on the PayBill/Till
    Must respond within 8 seconds
    """
    try:
        data = request.json
        print(f"[M-PESA VALIDATION] Received: {json.dumps(data, indent=2)}")
        
        # Extract payment details
        transaction_type = data.get('TransactionType')
        trans_amount = float(data.get('TransAmount', 0))
        bill_ref_number = data.get('BillRefNumber', '')  # Booking code
        msisdn = data.get('MSISDN', '')
        
        # Validate the transaction
        # Check if booking exists and amount matches
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT booking_code, total_amount, payment_status
            FROM bookings
            WHERE booking_code = ?
        ''', (bill_ref_number,))
        
        booking = cursor.fetchone()
        conn.close()
        
        if booking:
            booking_code, expected_amount, payment_status = booking
            
            # Check if already paid
            if payment_status == 'paid':
                return jsonify({
                    "ResultCode": "C2B00016",
                    "ResultDesc": "Rejected - Payment already received"
                }), 200
            
            # Validate amount (allow small variance for rounding)
            if abs(trans_amount - expected_amount) > 1.0:
                return jsonify({
                    "ResultCode": "C2B00013",
                    "ResultDesc": "Rejected - Invalid Amount"
                }), 200
            
            # Accept the transaction
            return jsonify({
                "ResultCode": "0",
                "ResultDesc": "Accepted"
            }), 200
        else:
            # Booking not found
            return jsonify({
                "ResultCode": "C2B00012",
                "ResultDesc": "Rejected - Invalid Account Number"
            }), 200
            
    except Exception as e:
        print(f"[M-PESA VALIDATION ERROR] {e}")
        # On error, accept the transaction (safer default)
        return jsonify({
            "ResultCode": "0",
            "ResultDesc": "Accepted"
        }), 200

@app.route('/api/mpesa/confirmation', methods=['POST'])
def mpesa_confirmation():
    """
    M-Pesa C2B Confirmation URL
    Called after successful payment completion
    """
    try:
        data = request.json
        print(f"[M-PESA CONFIRMATION] Received: {json.dumps(data, indent=2)}")
        
        # Extract payment details
        trans_id = data.get('TransID')
        trans_time = data.get('TransTime')
        trans_amount = float(data.get('TransAmount', 0))
        business_short_code = data.get('BusinessShortCode')
        bill_ref_number = data.get('BillRefNumber', '')  # Booking code
        msisdn = data.get('MSISDN', '')
        first_name = data.get('FirstName', '')
        middle_name = data.get('MiddleName', '')
        last_name = data.get('LastName', '')
        org_account_balance = data.get('OrgAccountBalance', '0.00')
        
        # Update booking payment status
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        # Check if booking exists
        cursor.execute('''
            SELECT booking_code, tourist_name, tourist_email, total_amount, payment_status
            FROM bookings
            WHERE booking_code = ?
        ''', (bill_ref_number,))
        
        booking = cursor.fetchone()
        
        if booking:
            booking_code, tourist_name, tourist_email, expected_amount, payment_status = booking
            
            # Update payment status
            cursor.execute('''
                UPDATE bookings
                SET payment_status = 'paid',
                    amount_paid = ?
                WHERE booking_code = ?
            ''', (trans_amount, booking_code))
            
            # Record transaction
            cursor.execute('''
                INSERT INTO transactions (booking_code, mpesa_code, amount, status, distribution_json)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                booking_code,
                trans_id,
                trans_amount,
                'completed',
                json.dumps({
                    'trans_id': trans_id,
                    'trans_time': trans_time,
                    'msisdn': msisdn,
                    'customer_name': f"{first_name} {middle_name} {last_name}".strip(),
                    'org_balance': org_account_balance
                })
            ))
            
            conn.commit()
            conn.close()
            
            # TODO: Send confirmation email/SMS to tourist
            # TODO: Notify steward of payment
            # TODO: Implement automatic fund distribution
            
            print(f"[M-PESA CONFIRMATION] Payment processed for booking {booking_code}")
            
        else:
            conn.close()
            print(f"[M-PESA CONFIRMATION] Warning: Booking {bill_ref_number} not found")
        
        # Always return success to M-Pesa
        return jsonify({
            "ResultCode": "0",
            "ResultDesc": "Accepted"
        }), 200
        
    except Exception as e:
        print(f"[M-PESA CONFIRMATION ERROR] {e}")
        # Always return success to M-Pesa (we'll handle errors internally)
        return jsonify({
            "ResultCode": "0",
            "ResultDesc": "Accepted"
        }), 200

@app.route('/api/mpesa/callback', methods=['POST'])
def mpesa_callback():
    """Legacy callback endpoint (redirects to confirmation)"""
    return mpesa_confirmation()

@app.route('/api/availability', methods=['GET'])
def check_availability():
    """Check community availability (placeholder)"""
    # In production, this would query steward or maintain availability calendar
    return jsonify({
        'available': True,
        'message': 'Contact steward for current availability'
    }), 200

@app.route('/api/mpesa/register-urls', methods=['POST'])
def register_mpesa_urls():
    """
    Register C2B Validation and Confirmation URLs with Safaricom
    This is typically a one-time setup
    """
    if not SAFARICOM_ENABLED:
        return jsonify({
            'error': 'Safaricom API integration not configured'
        }), 500
    
    try:
        result = safaricom_api.register_c2b_urls()
        return jsonify({
            'success': True,
            'message': 'C2B URLs registered successfully',
            'data': result
        }), 200
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

@app.route('/api/mpesa/test-token', methods=['GET'])
def test_mpesa_token():
    """Test endpoint to verify Safaricom API token generation"""
    if not SAFARICOM_ENABLED:
        return jsonify({
            'error': 'Safaricom API integration not configured'
        }), 500
    
    try:
        token = safaricom_api.get_access_token()
        return jsonify({
            'success': True,
            'access_token': token[:20] + '...' if token else None,
            'message': 'Token generated successfully'
        }), 200
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

@app.route('/api/mpesa/stk-push', methods=['POST'])
def initiate_stk_push():
    """
    Initiate STK Push (Lipa na M-Pesa Online)
    Sends push notification to customer's phone for payment
    """
    if not SAFARICOM_ENABLED:
        return jsonify({'error': 'Safaricom API integration not configured'}), 500
    
    try:
        data = request.json
        booking_code = data.get('booking_code')
        phone_number = data.get('phone_number')
        
        if not booking_code or not phone_number:
            return jsonify({'error': 'Missing booking_code or phone_number'}), 400
        
        # Get booking details
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT total_amount, payment_status, tourist_name
            FROM bookings
            WHERE booking_code = ?
        ''', (booking_code,))
        
        booking = cursor.fetchone()
        conn.close()
        
        if not booking:
            return jsonify({'error': 'Booking not found'}), 404
        
        total_amount, payment_status, tourist_name = booking
        
        if payment_status == 'paid':
            return jsonify({'error': 'Booking already paid'}), 400
        
        # Format phone number (ensure it starts with 254)
        if not phone_number.startswith('254'):
            phone_number = '254' + phone_number.lstrip('0')
        
        # Generate callback URL
        callback_url = request.host_url.rstrip('/') + '/api/mpesa/stk-callback'
        
        # Initiate STK Push
        result = safaricom_api.initiate_stk_push(
            phone_number=phone_number,
            amount=total_amount,
            account_reference=booking_code,
            callback_url=callback_url,
            description=f"Payment for booking {booking_code}"
        )
        
        # Store checkout request ID
        checkout_request_id = result.get('CheckoutRequestID')
        if checkout_request_id:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE bookings
                SET payment_status = 'pending_stk'
                WHERE booking_code = ?
            ''', (booking_code,))
            conn.commit()
            conn.close()
        
        return jsonify({
            'success': True,
            'checkout_request_id': checkout_request_id,
            'customer_message': result.get('CustomerMessage', ''),
            'message': 'STK Push initiated. Please check your phone.'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/mpesa/stk-callback', methods=['POST'])
def stk_push_callback():
    """
    STK Push callback endpoint
    Receives payment result from Safaricom
    """
    try:
        data = request.json
        print(f"[STK PUSH CALLBACK] Received: {json.dumps(data, indent=2)}")
        
        body = data.get('Body', {})
        stk_callback = body.get('stkCallback', {})
        
        checkout_request_id = stk_callback.get('CheckoutRequestID')
        result_code = stk_callback.get('ResultCode')
        result_desc = stk_callback.get('ResultDesc')
        
        callback_metadata = stk_callback.get('CallbackMetadata', {})
        items = callback_metadata.get('Item', [])
        
        # Extract payment details
        mpesa_receipt_number = None
        amount = None
        phone_number = None
        
        for item in items:
            name = item.get('Name')
            value = item.get('Value')
            if name == 'MpesaReceiptNumber':
                mpesa_receipt_number = value
            elif name == 'Amount':
                amount = value
            elif name == 'PhoneNumber':
                phone_number = value
        
        if result_code == 0 and mpesa_receipt_number:
            # Payment successful
            # Find booking by checkout request ID or phone number
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            
            # Try to find booking by phone number
            cursor.execute('''
                SELECT booking_code, total_amount
                FROM bookings
                WHERE tourist_contact LIKE ? AND payment_status = 'pending_stk'
                ORDER BY created_at DESC
                LIMIT 1
            ''', (f'%{phone_number[-9:]}%',))
            
            booking = cursor.fetchone()
            
            if booking:
                booking_code, expected_amount = booking
                
                # Update booking
                cursor.execute('''
                    UPDATE bookings
                    SET payment_status = 'paid',
                        amount_paid = ?
                    WHERE booking_code = ?
                ''', (amount / 100 if amount else expected_amount, booking_code))
                
                # Record transaction
                cursor.execute('''
                    INSERT INTO transactions (booking_code, mpesa_code, amount, status, distribution_json)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    booking_code,
                    mpesa_receipt_number,
                    amount / 100 if amount else expected_amount,
                    'completed',
                    json.dumps({
                        'checkout_request_id': checkout_request_id,
                        'phone_number': phone_number,
                        'result_code': result_code
                    })
                ))
                
                conn.commit()
                conn.close()
                
                print(f"[STK PUSH] Payment successful for booking {booking_code}")
            else:
                conn.close()
                print(f"[STK PUSH] Warning: Booking not found for phone {phone_number}")
        
        # Always return success to Safaricom
        return jsonify({'ResultCode': 0, 'ResultDesc': 'Success'}), 200
        
    except Exception as e:
        print(f"[STK PUSH CALLBACK ERROR] {e}")
        return jsonify({'ResultCode': 0, 'ResultDesc': 'Success'}), 200

if __name__ == '__main__':
    print("Starting Community Tourism Relay Bridge Server...")
    print("API endpoints available at http://localhost:5000/api/")
    
    if SAFARICOM_ENABLED:
        print("\nSafaricom Daraja API integration: ENABLED")
        print("To register C2B URLs, POST to /api/mpesa/register-urls")
    else:
        print("\nSafaricom Daraja API integration: DISABLED")
        print("Configure safaricom_config.py to enable M-Pesa integration")
    
    app.run(debug=True, port=5000)

