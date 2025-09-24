import africastalking
from flask import Response
import logging
import tempfile
import os
import requests
from .config import (
    AFRICASTALKING_USERNAME, 
    AFRICASTALKING_API_KEY, 
    AFRICASTALKING_SENDER_ID,
    AFRICASTALKING_SANDBOX
)

logger = logging.getLogger(__name__)

class AfricaTalkingService:
    def __init__(self, username, api_key, sender_id):
        # Initialize Africa's Talking SDK
        africastalking.initialize(username, api_key)
        self.sms = africastalking.SMS
        self.voice = africastalking.Voice
        self.sender_id = sender_id
        self.username = username
        self.api_key = api_key
        
        logger.info(f"Africa's Talking service initialized with sender: {sender_id}")
        
    def send_sms(self, to, message, enqueue=True):
        """Send SMS via Africa's Talking SDK"""
        try:
            # Format recipient as list (required by API)
            recipients = [to]
            
            # Use sender_id if available, otherwise use shortcode
            sender = self.sender_id
            
            # Send SMS using Africa's Talking SDK
            response = self.sms.send(message, recipients, sender)
            
            logger.info(f"SMS sent to {to}. Response: {response}")
            return response
            
        except Exception as e:
            logger.error(f"Error sending SMS to {to}: {str(e)}")
            # Fallback to direct API call if SDK fails
            return self._send_sms_direct(to, message, enqueue)
    
    def _send_sms_direct(self, to, message, enqueue=True):
        """Fallback method using direct API call"""
        try:
            # Determine endpoint based on sandbox mode
            if AFRICASTALKING_SANDBOX:
                url = "https://api.sandbox.africastalking.com/version1/messaging"
            else:
                url = "https://api.africastalking.com/version1/messaging"
            
            headers = {
                'ApiKey': self.api_key,
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json'
            }
            
            data = {
                'username': self.username,
                'to': to,
                'message': message,
                'from': self.sender_id,
                'enqueue': '1' if enqueue else '0'
            }
            
            response = requests.post(url, data=data, headers=headers, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Direct API SMS sent to {to}: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Direct API SMS also failed for {to}: {str(e)}")
            raise e
    
    def send_bulk_sms(self, recipients, message, enqueue=True):
        """Send SMS to multiple recipients"""
        try:
            sender = self.sender_id
            response = self.sms.send(message, recipients, sender)
            
            logger.info(f"Bulk SMS sent to {len(recipients)} recipients. Response: {response}")
            return response
            
        except Exception as e:
            logger.error(f"Error sending bulk SMS: {str(e)}")
            return None
    
    def send_voice_message(self, to, text_message, language="en"):
        """Convert text to speech and make voice call using Africa's Talking"""
        try:
            # For Africa's Talking, we'll use their built-in TTS for voice calls
            return self.make_tts_call(to, text_message, language)
            
        except Exception as e:
            logger.error(f"Error sending voice message to {to}: {str(e)}")
            return False
    
    def make_tts_call(self, to, text, language="en"):
        """Make a voice call using Africa's Talking TTS"""
        try:
            # Map languages to appropriate TTS voices
            voice_mapping = {
                "en": "woman",
                "sw": "woman",  # Swahili - use woman voice
                "lg": "woman",  # Luganda - use woman voice  
                "fr": "woman"   # French - use woman voice
            }
            
            voice = voice_mapping.get(language, "woman")
            
            # Create call using Africa's Talking voice API
            call_options = {
                'from': self.sender_id if len(self.sender_id) <= 11 else 'SMStoAI',
                'to': to
            }
            
            # For Africa's Talking, we need to create an external XML response
            # that will be fetched when the call is initiated
            response = self.voice.call(call_options)
            logger.info(f"Voice call initiated to {to}: {response}")
            
            # Note: Africa's Talking voice calls require a callback URL
            # that returns XML with the TTS instructions
            return response
            
        except Exception as e:
            logger.error(f"Error making voice call to {to}: {str(e)}")
            return False
    
    def get_voice_call_xml(self, text, language="en"):
        """Generate XML response for voice calls"""
        voice = "woman"  # Africa's Talking supports 'man' or 'woman'
        
        xml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="{voice}" playBeep="true">
        {text}
    </Say>
    <Hangup/>
</Response>"""
        
        return xml_response
    
    def handle_incoming_sms(self, request_data):
        """Process incoming SMS from Africa's Talking"""
        try:
            # Africa's Talking SMS delivery format
            from_number = request_data.get('from', '').strip()
            text = request_data.get('text', '').strip()
            message_id = request_data.get('id', '')
            
            if not from_number or not text:
                logger.error("Invalid incoming SMS data")
                return None
            
            logger.info(f"Received SMS from {from_number}: {text}")
            
            return {
                'from_number': from_number,
                'text': text,
                'message_id': message_id
            }
            
        except Exception as e:
            logger.error(f"Error processing incoming SMS: {str(e)}")
            return None
    
    def handle_voice_call(self, request_data):
        """Process incoming voice call from Africa's Talking"""
        try:
            # Africa's Talking voice call format
            from_number = request_data.get('callerNumber', '').strip()
            session_id = request_data.get('sessionId', '')
            direction = request_data.get('direction', 'incoming')
            
            logger.info(f"Received voice call from {from_number}, session: {session_id}")
            
            return {
                'from_number': from_number,
                'session_id': session_id,
                'direction': direction
            }
            
        except Exception as e:
            logger.error(f"Error processing voice call: {str(e)}")
            return None
    
    def check_balance(self):
        """Check Africa's Talking account balance"""
        try:
            # Note: Balance checking might require premium subscription
            # This is a placeholder for future implementation
            logger.info("Balance check requested - feature requires premium account")
            return None
            
        except Exception as e:
            logger.error(f"Error checking balance: {str(e)}")
            return None
    
    def validate_phone_number(self, phone_number):
        """Validate Ugandan phone number format"""
        try:
            # Basic validation for Ugandan numbers
            if not phone_number.startswith('+256'):
                # Try to format as Ugandan number
                if phone_number.startswith('0'):
                    phone_number = '+256' + phone_number[1:]
                elif phone_number.startswith('256'):
                    phone_number = '+' + phone_number
                else:
                    return None
            
            # Remove any spaces or dashes
            phone_number = phone_number.replace(' ', '').replace('-', '')
            
            # Check length: +256 XXX XXX XXX (13 characters)
            if len(phone_number) == 13 and phone_number.startswith('+256'):
                return phone_number
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error validating phone number {phone_number}: {str(e)}")
            return None

# Create global instance
at_service = AfricaTalkingService(
    username=AFRICASTALKING_USERNAME,
    api_key=AFRICASTALKING_API_KEY,
    sender_id=AFRICASTALKING_SENDER_ID
)