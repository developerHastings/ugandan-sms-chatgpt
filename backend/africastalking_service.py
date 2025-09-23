import africastalking
from flask import Response
import logging
import tempfile
import os

logger = logging.getLogger(__name__)

class AfricaTalkingService:
    def __init__(self, username, api_key, sender_id):
        # Initialize Africa's Talking SDK
        africastalking.initialize(username, api_key)
        self.sms = africastalking.SMS
        self.voice = africastalking.Voice
        self.sender_id = sender_id
        self.username = username
        
    def send_sms(self, to, message, voice_url=None):
        """Send SMS via Africa's Talking"""
        try:
            # Prepare SMS options
            options = {
                'to': [to],
                'message': message,
                'from_': self.sender_id
            }
            
            # Send SMS
            response = self.sms.send(options)
            logger.info(f"SMS sent to {to}: {response}")
            return response
            
        except Exception as e:
            logger.error(f"Error sending SMS: {str(e)}")
            raise e
    
    def send_voice_message(self, to, text_message, language="en"):
        """Convert text to speech and make voice call"""
        try:
            from backend.tts import text_to_speech  # Import your TTS function
            
            # Generate audio file from text
            audio_file = text_to_speech(text_message, language=language)
            if not audio_file:
                logger.error("Failed to generate audio file")
                return False
            
            # Upload audio to accessible URL (you'll need to host this file)
            # For now, we'll use Africa's Talking TTS - more practical for production
            call_response = self.make_tts_call(to, text_message, language)
            
            # Clean up temp file
            try:
                os.remove(audio_file)
            except OSError:
                pass
                
            return call_response
            
        except Exception as e:
            logger.error(f"Error sending voice message: {str(e)}")
            return False
    
    def make_tts_call(self, to, text, language="en"):
        """Make a voice call using Africa's Talking TTS"""
        try:
            # Map languages to appropriate voices
            voice_mapping = {
                "en": "en-US-SaraNeural",
                "sw": "sw-KE-ZuriNeural",  # Swahili (Kenya)
                "lg": "en-US-AriaNeural",  # Luganda not directly supported, use English
                "fr": "fr-FR-DeniseNeural"
            }
            
            voice = voice_mapping.get(language, "en-US-SaraNeural")
            
            # Create call
            call_options = {
                'callFrom': self.username,  # Your Africa's Talking voice number
                'callTo': to,
                'text': text
            }
            
            response = self.voice.call(call_options)
            logger.info(f"Voice call initiated to {to}: {response}")
            return response
            
        except Exception as e:
            logger.error(f"Error making voice call: {str(e)}")
            return False
    
    def handle_incoming_sms(self, request_data):
        """Process incoming SMS from Africa's Talking"""
        try:
            # Africa's Talking SMS delivery format
            from_number = request_data.get('from', '').strip()
            text = request_data.get('text', '').strip()
            message_id = request_data.get('id', '')
            
            if not from_number or not text:
                logger.error("Invalid incoming SMS data")
                return Response("Invalid request", status=400)
            
            logger.info(f"Received SMS from {from_number}: {text}")
            
            return {
                'from_number': from_number,
                'text': text,
                'message_id': message_id
            }
            
        except Exception as e:
            logger.error(f"Error processing incoming SMS: {str(e)}")
            raise e
    
    def handle_voice_call(self, request_data):
        """Process incoming voice call from Africa's Talking"""
        try:
            # Africa's Talking voice call format
            from_number = request_data.get('callerNumber', '').strip()
            session_id = request_data.get('sessionId', '')
            direction = request_data.get('direction', '')  # Incoming or Outgoing
            
            logger.info(f"Received voice call from {from_number}, session: {session_id}")
            
            return {
                'from_number': from_number,
                'session_id': session_id,
                'direction': direction
            }
            
        except Exception as e:
            logger.error(f"Error processing voice call: {str(e)}")
            raise e