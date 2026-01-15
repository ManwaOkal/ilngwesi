# Community Tourism Relay System - Il Ngwesi Website

A modern booking website for the Community Tourism Relay (CTR) System, connecting tourists directly with community conservancies in Kenya.

## Features

- **Modern, Responsive Design**: Beautiful UI that works on all devices
- **Direct Booking System**: Book tours, homestays, and cultural experiences
- **Transparent Pricing**: Clear pricing with revenue sharing breakdown
- **M-Pesa Integration**: Secure payment via M-Pesa
- **Image Gallery**: Showcase of Il Ngwesi Conservancy experiences
- **Low-Tech Bridge**: Connects web bookings to SMS-based community system

## Project Structure

```
illngwesi_website/
├── index.html          # Main website HTML
├── styles.css          # Styling and responsive design
├── script.js           # Frontend JavaScript functionality
├── app.py              # Flask backend API (Bridge Server)
├── requirements.txt    # Python dependencies
├── images/             # Scraped images from Il Ngwesi website
└── README.md           # This file
```

## Setup Instructions

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Backend Server

```bash
python app.py
```

The API will be available at `http://localhost:5000`

### 3. Open the Website

Open `index.html` in a web browser, or serve it through the Flask app (it's already configured to serve static files).

## API Endpoints

### Booking Endpoints
- `POST /api/booking` - Create a new booking
- `GET /api/booking/<code>` - Get booking status
- `POST /api/sms/incoming` - Receive SMS from stewards
- `GET /api/availability` - Check availability

### M-Pesa Endpoints (Safaricom Daraja)
- `POST /api/mpesa/validation` - M-Pesa C2B validation callback
- `POST /api/mpesa/confirmation` - M-Pesa C2B confirmation callback
- `POST /api/mpesa/register-urls` - Register C2B URLs with Safaricom
- `GET /api/mpesa/test-token` - Test OAuth token generation

## Integration with Safaricom Services

### SMS Gateway
To enable SMS functionality, integrate with:
- Africa's Talking API
- Moya Messenger
- Direct Safaricom SMPP

Update the `send_sms_to_steward()` function in `app.py`.

### M-Pesa Integration (Daraja API)

The system includes full Safaricom Daraja API integration:

1. **Configure Credentials:**
   - Edit `safaricom_config.py` with your Consumer Key and Secret
   - Set your PayBill/Till Number
   - Configure callback URLs

2. **Register C2B URLs:**
   ```bash
   # After starting the server
   curl -X POST http://localhost:5000/api/mpesa/register-urls
   ```

3. **Test Integration:**
   ```bash
   curl http://localhost:5000/api/mpesa/test-token
   ```

4. **For Production:**
   - See `MPESA_SETUP.md` for detailed setup instructions
   - Update environment to 'production' in `safaricom_config.py`
   - Ensure HTTPS URLs for callbacks
   - Whitelist Safaricom IP addresses

### Email Service
Configure email sending service (SendGrid, Mailgun, etc.) in `send_email_confirmation()` function.

## Services Offered

- **Guided Wildlife Walks**: KES 500/person
- **Community Homestays**: KES 1,500/night
- **Cultural Evenings**: KES 750/person
- **Bush Breakfasts**: KES 1,200/person
- **Rhino Sanctuary Visits**: KES 800/person
- **Beading Workshops**: KES 600/person

## Revenue Sharing

- 40% - Local Guide
- 35% - Homestay Provider
- 20% - Conservancy Fund
- 5% - Tourism Steward Honorarium

## Development

### Frontend
- Pure HTML/CSS/JavaScript (no build process required)
- Responsive design with mobile-first approach
- Image gallery populated dynamically

### Backend
- Flask REST API
- SQLite database (can be upgraded to PostgreSQL)
- Ready for SMS and M-Pesa integration

## Next Steps

1. **Deploy Backend**: Deploy Flask app to Kenyan hosting (for low latency)
2. **Configure SMS**: Set up Africa's Talking or Safaricom SMS API
3. **Configure M-Pesa**: Complete Daraja API integration
4. **Set Up Email**: Configure email service for confirmations
5. **Test Flow**: Test complete booking → SMS → confirmation → payment flow

## License

Community-owned project for Il Ngwesi Conservancy.

## Contact

- Email: info@ilngwesi.com
- Phone: +254 (0) 741 770 540

