import os
from flask import Flask, request, Response, jsonify
import logging
import tempfile
import requests
import json

from .chatgpt import query_chatgpt
from .stt import speech_to_text
from .tts import text_to_speech
from .africastalking_service import AfricaTalkingService, at_service
from .user_preferences import (
    get_user_preference, 
    set_user_preference, 
    set_user_role, 
    set_user_language,
    get_user_role
)
from .config import (
    AFRICASTALKING_USERNAME, 
    AFRICASTALKING_API_KEY, 
    AFRICASTALKING_SENDER_ID, 
    SERVER_PORT,
    DEFAULT_LANGUAGE, 
    SUPPORTED_LANGUAGES,
    VOICE_RESPONSE_ENABLED
)

app = Flask(__name__)

# Create logs directory if it doesn't exist (do this before logging setup)
logs_dir = os.path.join(os.path.dirname(__file__), 'logs')
os.makedirs(logs_dir, exist_ok=True)

# Configure logging
log_file = os.path.join(logs_dir, 'app.log')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Log startup info
logger.info("=== Uganda AI SMS Chatbot Starting ===")

@app.route("/")
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "Uganda AI SMS Chatbot",
        "version": "2.0",
        "features": ["SMS", "Voice", "Multi-language", "Africa's Talking"]
    })

@app.route("/africastalking/sms", methods=["POST"])
def africastalking_sms():
    """Handle incoming SMS from Africa's Talking"""
    try:
        # Africa's Talking sends data as form data
        from_number = request.form.get('from', '').strip()
        text = request.form.get('text', '').strip()
        message_id = request.form.get('id', '')
        
        if not from_number or not text:
            logger.error("Missing from number or text in Africa's Talking SMS")
            return Response("Invalid request", status=400)
        
        logger.info(f"Africa's Talking SMS from {from_number}: {text}")
        
        # Validate and format phone number
        formatted_number = at_service.validate_phone_number(from_number)
        if not formatted_number:
            logger.error(f"Invalid phone number format: {from_number}")
            return Response("Invalid phone number", status=400)
        
        # Check for voice preference
        voice_response = False
        language = get_user_preference(formatted_number, "language", DEFAULT_LANGUAGE)
        
        # Check for voice command (e.g., "voice:lg Hello")
        original_message = text
        if text.lower().startswith(('voice:', 'audio:', 'speak:')):
            voice_response = True
            parts = text.split(':', 2)
            if len(parts) > 1:
                if len(parts) > 2 and parts[1] in SUPPORTED_LANGUAGES:
                    language = parts[1]
                    text = parts[2].strip()
                    set_user_language(formatted_number, language)
                else:
                    text = parts[1].strip()
        
        # Check for role setting (e.g., "role:shopkeeper")
        if text.lower().startswith('role:'):
            role_part = text.split(':', 1)
            if len(role_part) > 1:
                role = role_part[1].strip().lower()
                set_user_role(formatted_number, role)
                response_msg = f"Role set to: {role}. How can I assist you today?"
                at_service.send_sms(formatted_number, response_msg)
                return Response("Role updated", status=200)
        
        # Check for language setting (e.g., "language:sw")
        if text.lower().startswith('language:'):
            lang_part = text.split(':', 1)
            if len(lang_part) > 1:
                new_lang = lang_part[1].strip().lower()
                if new_lang in SUPPORTED_LANGUAGES:
                    set_user_language(formatted_number, new_lang)
                    lang_names = {"en": "English", "sw": "Swahili", "lg": "Luganda", "fr": "French"}
                    response_msg = f"Language set to: {lang_names.get(new_lang, new_lang)}"
                    at_service.send_sms(formatted_number, response_msg)
                    return Response("Language updated", status=200)
                else:
                    at_service.send_sms(formatted_number, f"Supported languages: {', '.join(SUPPORTED_LANGUAGES)}")
                    return Response("Invalid language", status=200)
        
        # Set response preference
        set_user_preference(formatted_number, "prefers_voice", str(voice_response))
        
        # Get user role for context
        user_role = get_user_role(formatted_number)
        
        # Process with ChatGPT
        bot_response = query_chatgpt(text, formatted_number, user_role=user_role)
        if not bot_response:
            bot_response = "Sorry, I couldn't process your request. Please try again."
        
        # Send response based on preference
        if voice_response and VOICE_RESPONSE_ENABLED:
            # Send voice call with TTS
            success = at_service.send_voice_message(formatted_number, bot_response, language)
            if success:
                logger.info(f"Voice response sent to {formatted_number}")
                return Response("Voice message sent", status=200)
            else:
                # Fallback to SMS
                logger.warning(f"Voice response failed, falling back to SMS for {formatted_number}")
                at_service.send_sms(formatted_number, bot_response)
        else:
            # Send SMS
            at_service.send_sms(formatted_number, bot_response)
        
        logger.info(f"SMS response sent to {formatted_number}")
        return Response("SMS processed", status=200)
        
    except Exception as e:
        logger.error(f"Error handling Africa's Talking SMS: {str(e)}", exc_info=True)
        return Response("Error processing message", status=500)

@app.route("/africastalking/voice", methods=["POST"])
def africastalking_voice():
    """Handle incoming voice calls from Africa's Talking"""
    try:
        # Africa's Talking voice call data
        from_number = request.form.get('callerNumber', '').strip()
        session_id = request.form.get('sessionId', '')
        direction = request.form.get('direction', 'incoming')
        
        if not from_number:
            logger.error("Missing caller number in voice request")
            return Response("Invalid request", status=400)
        
        logger.info(f"Processing voice call from {from_number}, session: {session_id}")
        
        # Validate phone number
        formatted_number = at_service.validate_phone_number(from_number)
        if not formatted_number:
            logger.error(f"Invalid phone number format: {from_number}")
            return Response("Invalid phone number", status=400)
        
        # Get user's language preference
        language = get_user_preference(formatted_number, "language", DEFAULT_LANGUAGE)
        
        # Africa's Talking expects XML response for voice calls
        welcome_message = "Welcome to SMStoAI Voice Assistant. Please speak your message after the beep. You can ask me anything in English, Luganda, or Swahili."
        
        response_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="woman" playBeep="false">
        {welcome_message}
    </Say>
    <Record 
        action="/africastalking/voice/transcribe" 
        finishOnKey="#" 
        maxLength="60" 
        playBeep="true" 
        trimSilence="true"
        callbackUrl="/africastalking/voice/callback"
    />
</Response>"""
        
        return Response(response_xml, mimetype='application/xml')
        
    except Exception as e:
        logger.error(f"Error handling Africa's Talking voice: {str(e)}", exc_info=True)
        error_xml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="woman">Sorry, we encountered an error. Please try again later.</Say>
    <Hangup/>
</Response>"""
        return Response(error_xml, mimetype='application/xml')

@app.route("/africastalking/voice/transcribe", methods=["POST"])
def voice_transcribe():
    """Transcribe voice recording and respond"""
    try:
        from_number = request.form.get('callerNumber', '').strip()
        session_id = request.form.get('sessionId', '')
        recording_url = request.form.get('recordingUrl', '')
        duration = request.form.get('durationInSeconds', '0')
        
        if not from_number or not recording_url:
            logger.error("Missing caller number or recording URL")
            return Response("Invalid request", status=400)
        
        logger.info(f"Transcribing voice message from {from_number}, duration: {duration}s")
        
        # Validate phone number
        formatted_number = at_service.validate_phone_number(from_number)
        if not formatted_number:
            logger.error(f"Invalid phone number format: {from_number}")
            return Response("Invalid phone number", status=400)
        
        # Download recording
        response = requests.get(recording_url, stream=True, timeout=30)
        response.raise_for_status()
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    tmp_file.write(chunk)
            audio_path = tmp_file.name
        
        try:
            # Transcribe audio
            transcript = speech_to_text(audio_path)
            logger.info(f"Transcribed voice message from {formatted_number}: {transcript}")
            
            if not transcript or transcript.strip() == "":
                transcript = "I couldn't understand the audio message. Please try again."
                # Send error response via SMS
                at_service.send_sms(formatted_number, transcript)
                return Response("Empty transcription", status=200)
            
            # Get user role and language
            user_role = get_user_role(formatted_number)
            language = get_user_preference(formatted_number, "language", DEFAULT_LANGUAGE)
            
            # Process with ChatGPT
            bot_response = query_chatgpt(transcript, formatted_number, user_role=user_role)
            if not bot_response:
                bot_response = "Sorry, I couldn't process your voice message. Please try again."
            
            # Send response via SMS (more reliable than voice callbacks)
            at_service.send_sms(formatted_number, f"Voice message response: {bot_response}")
            
            logger.info(f"Voice message processed and SMS response sent to {formatted_number}")
            
        finally:
            # Cleanup
            try:
                os.remove(audio_path)
            except OSError as e:
                logger.error(f"Error deleting temp file: {e}")
        
        # Return empty response (we sent SMS instead of voice callback)
        return Response("Voice message processed", status=200)
        
    except Exception as e:
        logger.error(f"Error transcribing voice: {str(e)}", exc_info=True)
        # Try to send error via SMS
        try:
            from_number = request.form.get('callerNumber', '')
            if from_number:
                formatted_number = at_service.validate_phone_number(from_number)
                if formatted_number:
                    at_service.send_sms(formatted_number, "Sorry, there was an error processing your voice message. Please try again.")
        except Exception as sms_error:
            logger.error(f"Could not send error SMS: {sms_error}")
        
        return Response("Error processing voice", status=500)

@app.route("/africastalking/voice/callback", methods=["POST"])
def voice_callback():
    """Handle voice call events (call status updates)"""
    try:
        session_id = request.form.get('sessionId', '')
        status = request.form.get('status', '')
        from_number = request.form.get('callerNumber', '')
        
        logger.info(f"Voice callback - Session: {session_id}, Status: {status}, From: {from_number}")
        
        return Response("Callback received", status=200)
        
    except Exception as e:
        logger.error(f"Error in voice callback: {str(e)}")
        return Response("Error", status=500)

@app.route("/africastalking/delivery", methods=["POST"])
def delivery_report():
    """Handle delivery reports from Africa's Talking"""
    try:
        status = request.form.get('status', '')
        message_id = request.form.get('id', '')
        number = request.form.get('number', '')
        failure_reason = request.form.get('failureReason', '')
        
        logger.info(f"Delivery report: Message {message_id} to {number} - Status: {status}, Reason: {failure_reason}")
        
        # You could update message status in database here
        if status == 'Success':
            logger.debug(f"Message {message_id} delivered successfully to {number}")
        else:
            logger.warning(f"Message {message_id} failed to deliver to {number}: {failure_reason}")
        
        return Response("Delivery report received", status=200)
        
    except Exception as e:
        logger.error(f"Error processing delivery report: {str(e)}")
        return Response("Error", status=500)

@app.route("/voice-note", methods=["POST"])
def voice_note():
    """Handle incoming media messages (voice notes) via Africa's Talking"""
    try:
        # Africa's Talking media message format
        from_number = request.form.get('from', '').strip()
        media_url = request.form.get('mediaUrl', '')
        text = request.form.get('text', '')
        
        if not from_number or not media_url:
            logger.error("Missing from number or media URL in voice note")
            return Response("Invalid request", status=400)
        
        logger.info(f"Processing voice note from {from_number}")
        
        # Validate phone number
        formatted_number = at_service.validate_phone_number(from_number)
        if not formatted_number:
            logger.error(f"Invalid phone number format: {from_number}")
            return Response("Invalid phone number", status=400)
        
        # Download media file
        response = requests.get(media_url, stream=True, timeout=30)
        response.raise_for_status()
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".ogg") as tmp_file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    tmp_file.write(chunk)
            audio_path = tmp_file.name
        
        try:
            # Transcribe audio
            transcript = speech_to_text(audio_path)
            logger.info(f"Transcribed voice note from {formatted_number}: {transcript}")
            
            if not transcript:
                transcript = "I couldn't understand the voice note. Please try again or send as text."
            
            # Get user role
            user_role = get_user_role(formatted_number)
            
            # Process with ChatGPT
            bot_response = query_chatgpt(transcript, formatted_number, user_role=user_role)
            if not bot_response:
                bot_response = "Sorry, I couldn't process your voice note. Please try again."
            
            # Send response via SMS
            at_service.send_sms(formatted_number, f"Voice note response: {bot_response}")
            
            logger.info(f"Voice note processed and response sent to {formatted_number}")
            
        finally:
            # Cleanup
            try:
                os.remove(audio_path)
            except OSError as e:
                logger.error(f"Error deleting temp file: {e}")
        
        return Response("Voice note processed", status=200)
        
    except Exception as e:
        logger.error(f"Error handling voice note: {str(e)}", exc_info=True)
        return Response("Error processing voice note", status=500)

@app.route("/user/setrole", methods=["POST"])
def set_user_role_endpoint():
    """API endpoint to set user role"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        phone_number = data.get('phone_number', '').strip()
        role = data.get('role', '').strip().lower()
        
        if not phone_number or not role:
            return jsonify({"error": "Phone number and role are required"}), 400
        
        formatted_number = at_service.validate_phone_number(phone_number)
        if not formatted_number:
            return jsonify({"error": "Invalid phone number format"}), 400
        
        set_user_role(formatted_number, role)
        return jsonify({"message": f"Role set to {role} for {formatted_number}"}), 200
        
    except Exception as e:
        logger.error(f"Error setting user role: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route("/user/info/<phone_number>", methods=["GET"])
def get_user_info(phone_number):
    """Get user preferences and role"""
    try:
        formatted_number = at_service.validate_phone_number(phone_number)
        if not formatted_number:
            return jsonify({"error": "Invalid phone number format"}), 400
        
        role = get_user_role(formatted_number)
        language = get_user_preference(formatted_number, "language", DEFAULT_LANGUAGE)
        prefers_voice = get_user_preference(formatted_number, "prefers_voice", "false")
        
        return jsonify({
            "phone_number": formatted_number,
            "role": role,
            "language": language,
            "prefers_voice": prefers_voice.lower() == "true"
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting user info: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    logger.info("Starting Uganda AI SMS Chatbot with Africa's Talking integration")
    logger.info(f"Server running on port {SERVER_PORT}")
    logger.info(f"Supported languages: {SUPPORTED_LANGUAGES}")
    logger.info(f"Voice response enabled: {VOICE_RESPONSE_ENABLED}")
    
    app.run(host="0.0.0.0", port=SERVER_PORT, debug=False)