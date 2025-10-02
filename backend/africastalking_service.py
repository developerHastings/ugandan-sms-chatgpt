import africastalking
from flask import Response
import logging
import tempfile
import os
import requests
from config import (
    AFRICASTALKING_USERNAME, 
    AFRICASTALKING_API_KEY, 
    AFRICASTALKING_SENDER_ID,
    AFRICASTALKING_SANDBOX,
    AFRICASTALKING_SHORTCODE,
    AFRICASTALKING_VOICE_CALLER_ID
)

logger = logging.getLogger(__name__)

class AfricaTalkingService:
    def __init__(self, username, api_key, sender_id):
        # Initialize Africa's Talking SDK for v2.0.1 - FIXED VERSION
        try:
            # Initialize the SDK with credentials (CORRECT for v2.0.1)
            africastalking.initialize(username, api_key)
            
            # Get the services
            self.sms = africastalking.SMS
            self.voice = africastalking.Voice
            self.sender_id = sender_id
            self.shortcode = AFRICASTALKING_SHORTCODE
            self.username = username
            self.api_key = api_key
            self.voice_caller_id = AFRICASTALKING_VOICE_CALLER_ID
            self.sandbox_mode = AFRICASTALKING_SANDBOX
            
            logger.info("Africa's Talking service initialized successfully")
            logger.info(f"Username: {username}, Sender ID: {sender_id}, Shortcode: {self.shortcode}")
            logger.info(f"Sandbox mode: {self.sandbox_mode}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Africa's Talking SDK: {str(e)}")
            raise e
        
    def send_sms(self, to, message, enqueue=True):
        """Send SMS via Africa's Talking SDK"""
        try:
            # ALWAYS use shortcode for production - remove fallback to sender_id
            sender = self.shortcode  # Use shortcode directly
            
            # Send SMS using Africa's Talking SDK
            response = self.sms.send(message, [to], sender)
            
            logger.info(f"SMS sent to {to} via {sender}. Response: {response}")
            return response
            
        except Exception as e:
            logger.error(f"Error sending SMS to {to}: {str(e)}")
            # Fallback to direct API call if SDK fails
            return self._send_sms_direct(to, message, enqueue)
    
    def _send_sms_direct(self, to, message, enqueue=True):
        """Fallback method using direct API call"""
        try:
            # Determine endpoint based on sandbox mode
            if self.sandbox_mode:
                url = "https://api.sandbox.africastalking.com/version1/messaging"
                logger.warning("Using SANDBOX API endpoint")
            else:
                url = "https://api.africastalking.com/version1/messaging"
                logger.info("Using PRODUCTION API endpoint")
            
            headers = {
                'ApiKey': self.api_key,
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json'
            }
            
            # ALWAYS use shortcode
            from_param = self.shortcode  # Use shortcode directly
            
            data = {
                'username': self.username,
                'to': to,
                'message': message,
                'from': from_param,
                'enqueue': '1' if enqueue else '0'
            }
            
            response = requests.post(url, data=data, headers=headers, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Direct API SMS sent to {to} via {from_param}: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Direct API SMS also failed for {to}: {str(e)}")
            raise e
    
    def send_bulk_sms(self, recipients, message, enqueue=True):
        """Send SMS to multiple recipients"""
        try:
            # ALWAYS use shortcode
            sender = self.shortcode  # Use shortcode directly
            
            response = self.sms.send(message, recipients, sender)
            
            logger.info(f"Bulk SMS sent to {len(recipients)} recipients via {sender}. Response: {response}")
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
            # Use voice caller ID if available, otherwise use shortcode
            caller_id = self.voice_caller_id if self.voice_caller_id else self.shortcode
            
            # Create call using Africa's Talking voice API
            call_options = {
                'from': caller_id,
                'to': to
            }
            
            # For Africa's Talking, we need to create an external XML response
            # that will be fetched when the call is initiated
            response = self.voice.call(call_options)
            logger.info(f"Voice call initiated to {to} from {caller_id}: {response}")
            
            # Note: Africa's Talking voice calls require a callback URL
            # that returns XML with the TTS instructions
            return response
            
        except Exception as e:
            logger.error(f"Error making voice call to {to}: {str(e)}")
            return False
    
    def get_voice_call_xml(self, text, language="en"):
        """Generate XML response for voice calls"""
        voice = "woman"  # Africa's Talking supports 'man' or 'woman'
        
        # Add language-specific greeting if needed
        greetings = {
            "en": "Hello! ",
            "sw": "Habari! ",
            "lg": "Nkulamusizza! ",
            "fr": "Bonjour! "
        }
        
        greeting = greetings.get(language, "")
        full_message = f"{greeting}{text}"
        
        xml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="{voice}" playBeep="true">
        {full_message}
    </Say>
    <Say voice="{voice}">
        Thank you for using SMStoAI. Goodbye!
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
            to_number = request_data.get('to', '')
            
            if not from_number or not text:
                logger.error("Invalid incoming SMS data")
                return None
            
            logger.info(f"Received SMS from {from_number} to {to_number}: {text}")
            
            return {
                'from_number': from_number,
                'text': text,
                'message_id': message_id,
                'to_number': to_number
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
            call_session_state = request_data.get('callSessionState', '')
            
            logger.info(f"Received voice call from {from_number}, session: {session_id}, state: {call_session_state}")
            
            return {
                'from_number': from_number,
                'session_id': session_id,
                'direction': direction,
                'call_session_state': call_session_state
            }
            
        except Exception as e:
            logger.error(f"Error processing voice call: {str(e)}")
            return None
    
    def check_balance(self):
        """Check Africa's Talking account balance"""
        try:
            if self.sandbox_mode:
                logger.info("Balance check in sandbox - using mock balance")
                return {"balance": "UGX 50,000.00", "currency": "UGX"}
            else:
                logger.info("Production balance check - implement via Africa's Talking API")
                return {"balance": "Check via Africa's Talking dashboard", "currency": "UGX"}
                
        except Exception as e:
            logger.error(f"Error checking balance: {str(e)}")
            return None
    
    def validate_phone_number(self, phone_number):
        """Validate Ugandan phone number format"""
        try:
            original_number = phone_number
            
            # Basic validation for Ugandan numbers
            if not phone_number.startswith('+256'):
                # Try to format as Ugandan number
                if phone_number.startswith('0'):
                    phone_number = '+256' + phone_number[1:]
                elif phone_number.startswith('256'):
                    phone_number = '+' + phone_number
                else:
                    logger.warning(f"Invalid Uganda number format: {original_number}")
                    return None
            
            # Remove any spaces or dashes
            phone_number = phone_number.replace(' ', '').replace('-', '')
            
            # Check length: +256 XXX XXX XXX (13 characters)
            if len(phone_number) == 13 and phone_number.startswith('+256'):
                logger.debug(f"Validated phone number: {original_number} -> {phone_number}")
                return phone_number
            else:
                logger.warning(f"Invalid Uganda number length: {phone_number}")
                return None
                
        except Exception as e:
            logger.error(f"Error validating phone number {phone_number}: {str(e)}")
            return None
    
    def get_service_info(self):
        """Get information about the Africa's Talking service status"""
        return {
            "username": self.username,
            "sender_id": self.sender_id,
            "shortcode": self.shortcode,
            "sandbox_mode": self.sandbox_mode,
            "production_ready": bool(self.shortcode and self.shortcode.startswith('*')),
            "voice_enabled": bool(self.voice_caller_id),
            "sdk_version": "2.0.1"
        }

# Create global instance with error handling
try:
    at_service = AfricaTalkingService(
        username=AFRICASTALKING_USERNAME,
        api_key=AFRICASTALKING_API_KEY,
        sender_id=AFRICASTALKING_SENDER_ID
    )
    logger.info("Africa's Talking service instance created successfully")
except Exception as e:
    at_service = None
    logger.error(f"Failed to create Africa's Talking service instance: {str(e)}")