"""
Safaricom Daraja API Integration
Handles OAuth token generation and C2B API calls
"""

import requests
import base64
import os
from datetime import datetime, timedelta
import json
from safaricom_config import (
    CONSUMER_KEY, CONSUMER_SECRET, OAUTH_URL,
    C2B_REGISTER_URL, C2B_SIMULATE_URL,
    VALIDATION_URL, CONFIRMATION_URL,
    RESPONSE_TYPE, SHORT_CODE, ENVIRONMENT,
    INITIATOR_NAME, INITIATOR_PASSWORD
)

# Import BASE_URL and other endpoints from config
from safaricom_config import BASE_URL, STK_PASSKEY

class SafaricomAPI:
    """Wrapper class for Safaricom Daraja APIs"""
    
    def __init__(self):
        self.access_token = None
        self.token_expiry = None
    
    def get_access_token(self):
        """
        Generate OAuth access token from Authorization API
        Token expires in 3600 seconds (1 hour)
        """
        # Check if token is still valid
        if self.access_token and self.token_expiry:
            if datetime.now() < self.token_expiry:
                return self.access_token
        
        # Generate new token
        try:
            # Create Basic Auth header
            credentials = f"{CONSUMER_KEY}:{CONSUMER_SECRET}"
            encoded_credentials = base64.b64encode(credentials.encode()).decode()
            
            headers = {
                'Authorization': f'Basic {encoded_credentials}'
            }
            
            response = requests.get(OAUTH_URL, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            self.access_token = data.get('access_token')
            expires_in = data.get('expires_in', 3600)
            
            # Set expiry time (subtract 60 seconds for safety margin)
            self.token_expiry = datetime.now() + timedelta(seconds=expires_in - 60)
            
            return self.access_token
            
        except requests.exceptions.RequestException as e:
            print(f"Error generating access token: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response: {e.response.text}")
            raise
    
    def register_c2b_urls(self):
        """
        Register C2B Validation and Confirmation URLs
        This is a one-time setup (or when URLs need to be changed)
        """
        try:
            access_token = self.get_access_token()
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                "ShortCode": SHORT_CODE,
                "ResponseType": RESPONSE_TYPE,
                "ConfirmationURL": CONFIRMATION_URL,
                "ValidationURL": VALIDATION_URL
            }
            
            response = requests.post(
                C2B_REGISTER_URL,
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            print(f"C2B URLs registered successfully: {result}")
            return result
            
        except requests.exceptions.RequestException as e:
            print(f"Error registering C2B URLs: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response: {e.response.text}")
            raise
    
    def simulate_c2b_payment(self, phone_number, amount, account_reference, command_id="CustomerPayBillOnline"):
        """
        Simulate C2B payment (Sandbox only)
        
        Args:
            phone_number: Customer phone number (format: 254712345678)
            amount: Payment amount
            account_reference: Account reference (booking code)
            command_id: "CustomerPayBillOnline" or "CustomerBuyGoodsOnline"
        """
        if ENVIRONMENT != 'sandbox':
            raise ValueError("Simulation is only available in sandbox environment")
        
        try:
            access_token = self.get_access_token()
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                "ShortCode": int(SHORT_CODE),
                "CommandID": command_id,
                "Amount": int(amount),
                "Msisdn": int(phone_number),
                "BillRefNumber": account_reference if command_id == "CustomerPayBillOnline" else ""
            }
            
            response = requests.post(
                C2B_SIMULATE_URL,
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            print(f"C2B payment simulated: {result}")
            return result
            
        except requests.exceptions.RequestException as e:
            print(f"Error simulating C2B payment: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response: {e.response.text}")
            raise
    
    def initiate_stk_push(self, phone_number, amount, account_reference, callback_url, description="Payment"):
        """
        Initiate STK Push (Lipa na M-Pesa Online)
        Sends a push notification to customer's phone to complete payment
        
        Args:
            phone_number: Customer phone number (format: 254712345678)
            amount: Payment amount
            account_reference: Account reference (booking code)
            callback_url: URL to receive payment result
            description: Transaction description
        """
        try:
            access_token = self.get_access_token()
            
            # Generate password (Base64 encoded string of BusinessShortCode + PassKey + Timestamp)
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            
            password_string = f"{SHORT_CODE}{STK_PASSKEY}{timestamp}"
            password = base64.b64encode(password_string.encode()).decode()
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                "BusinessShortCode": SHORT_CODE,
                "Password": password,
                "Timestamp": timestamp,
                "TransactionType": "CustomerPayBillOnline",
                "Amount": int(amount),
                "PartyA": int(phone_number),
                "PartyB": int(SHORT_CODE),
                "PhoneNumber": int(phone_number),
                "CallBackURL": callback_url,
                "AccountReference": account_reference,
                "TransactionDesc": description
            }
            
            stk_url = f"{BASE_URL}/mpesa/stkpush/v1/processrequest"
            response = requests.post(stk_url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            print(f"STK Push initiated: {result}")
            return result
            
        except requests.exceptions.RequestException as e:
            print(f"Error initiating STK Push: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response: {e.response.text}")
            raise
    
    def query_stk_push_status(self, checkout_request_id):
        """
        Query the status of an STK Push transaction
        
        Args:
            checkout_request_id: CheckoutRequestID from STK Push response
        """
        try:
            access_token = self.get_access_token()
            
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            
            password_string = f"{SHORT_CODE}{STK_PASSKEY}{timestamp}"
            password = base64.b64encode(password_string.encode()).decode()
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                "BusinessShortCode": SHORT_CODE,
                "Password": password,
                "Timestamp": timestamp,
                "CheckoutRequestID": checkout_request_id
            }
            
            query_url = f"{BASE_URL}/mpesa/stkpushquery/v1/query"
            response = requests.post(query_url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            return result
            
        except requests.exceptions.RequestException as e:
            print(f"Error querying STK Push status: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response: {e.response.text}")
            raise
    
    def initiate_b2c_payment(self, phone_number, amount, remarks, occasion="", result_url="", timeout_url=""):
        """
        Initiate B2C payment (Business to Customer)
        Used for distributing funds to guides, homestays, etc.
        
        Args:
            phone_number: Recipient phone number
            amount: Amount to send
            remarks: Payment remarks
            occasion: Optional occasion
            result_url: Callback URL for result
            timeout_url: Callback URL for timeout
        """
        try:
            access_token = self.get_access_token()
            
            # Generate security credential (encrypted initiator password)
            # In production, this should use M-Pesa public certificate
            # For now, using a placeholder - you need to implement proper encryption
            security_credential = self._generate_security_credential()
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                "InitiatorName": INITIATOR_NAME,
                "SecurityCredential": security_credential,
                "CommandID": "SalaryPayment",  # or "BusinessPayment", "PromotionPayment"
                "Amount": int(amount),
                "PartyA": int(SHORT_CODE),
                "PartyB": int(phone_number),
                "Remarks": remarks,
                "QueueTimeOutURL": timeout_url or result_url,
                "ResultURL": result_url,
                "Occasion": occasion
            }
            
            b2c_url = f"{BASE_URL}/mpesa/b2c/v1/paymentrequest"
            response = requests.post(b2c_url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            print(f"B2C payment initiated: {result}")
            return result
            
        except requests.exceptions.RequestException as e:
            print(f"Error initiating B2C payment: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response: {e.response.text}")
            raise
    
    def _generate_security_credential(self):
        """
        Generate security credential by encrypting initiator password with M-Pesa public key
        This is a placeholder - implement proper RSA encryption with M-Pesa certificate
        """
        # TODO: Implement proper RSA encryption with M-Pesa public certificate
        # For now, return a placeholder
        # In production, you must use the M-Pesa public certificate to encrypt the password
        return "PLACEHOLDER_SECURITY_CREDENTIAL"
    
    def query_transaction_status(self, transaction_id, identifier_type="4", result_url="", timeout_url=""):
        """
        Query the status of an M-Pesa transaction
        
        Args:
            transaction_id: M-Pesa transaction ID
            identifier_type: Identifier type (4 for organization)
            result_url: Callback URL for result
            timeout_url: Callback URL for timeout
        """
        try:
            access_token = self.get_access_token()
            security_credential = self._generate_security_credential()
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                "Initiator": INITIATOR_NAME,
                "SecurityCredential": security_credential,
                "CommandID": "TransactionStatusQuery",
                "TransactionID": transaction_id,
                "PartyA": int(SHORT_CODE),
                "IdentifierType": identifier_type,
                "ResultURL": result_url,
                "QueueTimeOutURL": timeout_url or result_url,
                "Remarks": "Transaction status query",
                "Occasion": ""
            }
            
            status_url = f"{BASE_URL}/mpesa/transactionstatus/v1/query"
            response = requests.post(status_url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            return result
            
        except requests.exceptions.RequestException as e:
            print(f"Error querying transaction status: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response: {e.response.text}")
            raise

# Global instance
safaricom_api = SafaricomAPI()

