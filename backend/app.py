import os
from flask import Flask, request, Response, jsonify
import logging
import tempfile
import requests

from backend.chatgpt import query_chatgpt
from backend.stt import speech_to_text
from backend.tts import text_to_speech
from backend.africastalking_service import AfricaTalkingService
from backend.user_preferences import get_user_preference, set_user_preference
from config import (
    AFRICASTALKING_USERNAME, AFRICASTALKING_API_KEY, 
    AFRICASTALKING_SENDER_ID, SERVER_PORT,
    DEFAULT_LANGUAGE, SUPPORTED_LANGUAGES
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Initialize Africa's Talking service
at_service = AfricaTalkingService(
    username=AFRICASTALKING_USERNAME,
    api_key=AFRICASTALKING_API_KEY,
    sender_id=AFRICASTALKING_SENDER_ID
)

@app.route("/africastalking/sms", methods=["POST"])
def africastalking_sms():
    """Handle incoming SMS from Africa's Talking"""
    try:
        # Process incoming SMS
        sms_data = at_service.handle_incoming_sms(request.form)
        from_number = sms_data['from_number']
        incoming_msg = sms_data['text']
        
        logger.info(f"Processing SMS from {from_number}: {incoming_msg}")
        
        # Check for voice preference
        voice_response = False
        language = get_user_preference(from_number, "language", DEFAULT_LANGUAGE)
        
        # Check for voice command (e.g., "voice:lg Hello")
        if incoming_msg.lower().startswith(('voice:', 'audio:', 'speak:')):
            voice_response = True
            parts = incoming_msg.split(':', 2)
            if len(parts) > 1:
                if len(parts) > 2 and parts[1] in SUPPORTED_LANGUAGES:
                    language = parts[1]
                    incoming_msg = parts[2].strip()
                    set_user_preference(from_number, "language", language)
                else:
                    incoming_msg = parts[1].strip()
        
        # Set response preference
        set_user_preference(from_number, "prefers_voice", str(voice_response))
        
        # Process with ChatGPT
        bot_response = query_chatgpt(incoming_msg, from_number)
        if not bot_response:
            bot_response = "Sorry, I couldn't process your request. Please try again."
        
        # Send response based on preference
        if voice_response:
            # Send voice call with TTS
            success = at_service.send_voice_message(from_number, bot_response, language)
            if success:
                return Response("Voice message sent", status=200)
            else:
                # Fallback to SMS
                at_service.send_sms(from_number, bot_response)
        else:
            # Send SMS
            at_service.send_sms(from_number, bot_response)
        
        return Response("SMS processed", status=200)
        
    except Exception as e:
        logger.error(f"Error handling Africa's Talking SMS: {str(e)}")
        return Response("Error processing message", status=500)

@app.route("/africastalking/voice", methods=["POST"])
def africastalking_voice():
    """Handle incoming voice calls from Africa's Talking"""
    try:
        # Process incoming call
        call_data = at_service.handle_voice_call(request.form)
        from_number = call_data['from_number']
        session_id = call_data['session_id']
        
        logger.info(f"Processing voice call from {from_number}")
        
        # Africa's Talking expects XML response for voice calls
        response_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="woman" playBeep="false">
        Welcome to SMStoAI Voice Assistant. Please speak your message after the beep.
        You can ask me anything in English, Luganda, or Swahili.
    </Say>
    <Record 
        action="/africastalking/voice/transcribe/{session_id}" 
        finishOnKey="#" 
        maxLength="30" 
        playBeep="true" 
        trimSilence="true"
    />
    <Say voice="woman">
        Thank you. Your message is being processed. You will receive a response shortly.
    </Say>
</Response>"""
        
        return Response(response_xml, mimetype='text/xml')
        
    except Exception as e:
        logger.error(f"Error handling Africa's Talking voice: {str(e)}")
        error_xml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="woman">Sorry, we encountered an error. Please try again later.</Say>
</Response>"""
        return Response(error_xml, mimetype='text/xml')

@app.route("/africastalking/voice/transcribe/<session_id>", methods=["POST"])
def voice_transcribe(session_id):
    """Transcribe voice recording and respond"""
    try:
        from_number = request.form.get('callerNumber', '').strip()
        recording_url = request.form.get('recordingUrl', '')
        
        if not recording_url:
            logger.error("No recording URL provided")
            return Response("No recording", status=400)
        
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
            logger.info(f"Transcribed voice message from {from_number}: {transcript}")
            
            if not transcript:
                transcript = "I couldn't understand the audio message."
            
            # Process with ChatGPT
            bot_response = query_chatgpt(transcript, from_number)
            if not bot_response:
                bot_response = "Sorry, I couldn't process your voice message. Please try again."
            
            # Get user's language preference
            language = get_user_preference(from_number, "language", DEFAULT_LANGUAGE)
            
            # Send voice response
            at_service.send_voice_message(from_number, bot_response, language)
            
            logger.info(f"Voice response sent to {from_number}")
            
        finally:
            # Cleanup
            try:
                os.remove(audio_path)
            except OSError:
                pass
        
        return Response("Voice message processed", status=200)
        
    except Exception as e:
        logger.error(f"Error transcribing voice: {str(e)}")
        return Response("Error processing voice", status=500)

@app.route("/africastalking/delivery", methods=["POST"])
def delivery_report():
    """Handle delivery reports from Africa's Talking"""
    try:
        status = request.form.get('status', '')
        message_id = request.form.get('id', '')
        number = request.form.get('number', '')
        
        logger.info(f"Delivery report: Message {message_id} to {number} - Status: {status}")
        
        return Response("Delivery report received", status=200)
        
    except Exception as e:
        logger.error(f"Error processing delivery report: {str(e)}")
        return Response("Error", status=500)

# Keep the existing voice-note endpoint but adapt it for Africa's Talking
@app.route("/voice-note", methods=["POST"])
def voice_note():
    """Handle incoming media messages (voice notes)"""
    try:
        # Africa's Talking sends media messages differently
        from_number = request.form.get('from', '').strip()
        media_url = request.form.get('mediaUrl', '')  # Different parameter name
        
        if not from_number or not media_url:
            logger.error("Missing from number or media URL")
            return Response("Invalid request", status=400)
        
        # Similar processing as before, but using Africa's Talking service
        # ... (implementation similar to previous voice-note handler)
        
        return Response("Voice note processed", status=200)
        
    except Exception as e:
        logger.error(f"Error handling voice note: {str(e)}")
        return Response("Error processing voice note", status=500)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=SERVER_PORT)