import os
import logging
from flask import Flask, request, Response
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
from twilio.request_validator import RequestValidator
import requests
import tempfile

from config import config
from services import (
    query_chatgpt, 
    speech_to_text,
    conversation_memory,
    language_detection,
    local_knowledge,
    menu_system,
    track_usage,
    handle_feedback,
    moderate_content,
    detect_emergency,
    handle_emergency  # Add this import
)

app = Flask(__name__)
twilio_client = Client(config.TWILIO_ACCOUNT_SID, config.TWILIO_AUTH_TOKEN)
validator = RequestValidator(config.TWILIO_AUTH_TOKEN)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def validate_twilio_request(request):
    signature = request.headers.get('X-Twilio-Signature', '')
    params = request.form.to_dict()
    url = request.url
    return validator.validate(url, params, signature)

@app.route("/")
def health_check():
    return "Uganda SMS ChatGPT is running!", 200

@app.route("/sms", methods=["POST"])
def sms_reply():
    if not validate_twilio_request(request):
        return Response("Invalid Twilio signature", status=403)
    
    try:
        incoming_msg = request.form.get("Body", "").strip()
        from_number = request.form.get("From", "")
        
        if not incoming_msg:
            return Response("Empty message body", status=400)
        
        # Track usage
        track_usage(from_number, "sms")
        
        # Check for emergency - UPDATED
        if detect_emergency(incoming_msg):
            emergency_type = handle_emergency(from_number, incoming_msg)
            return Response(f"Emergency detected! {emergency_type.capitalize()} services have been alerted.", status=200)
        
        # Moderate content
        if not moderate_content(incoming_msg):
            return Response("Message contains inappropriate content", status=200)
        
        # Handle menu options
        menu_response = menu_system.handle(from_number, incoming_msg)
        if menu_response:
            return str(MessagingResponse().message(menu_response))
        
        # Detect language
        lang = language_detection.detect(incoming_msg)
        
        # Get conversation context
        context = conversation_memory.get_context(from_number)
        
        # Generate response with local knowledge
        bot_response = query_chatgpt(incoming_msg, context, lang)
        enhanced_response = local_knowledge.enhance(incoming_msg, bot_response)
        
        # Save conversation
        conversation_memory.save(from_number, incoming_msg, enhanced_response)
        
        resp = MessagingResponse()
        resp.message(enhanced_response)
        return str(resp)
        
    except Exception as e:
        logger.error(f"SMS Error: {str(e)}")
        return Response("Server Error", status=500)

@app.route("/voice-note", methods=["POST"])
def voice_note():
    if not validate_twilio_request(request):
        return Response("Invalid Twilio signature", status=403)
    
    try:
        from_number = request.form.get("From")
        media_url = request.form.get("MediaUrl0")
        media_type = request.form.get("MediaContentType0", "")
        
        if not media_url:
            return Response("No media file", status=400)
        
        # Track usage
        track_usage(from_number, "voice_note")
        
        # Verify audio type
        if not media_type.startswith('audio/'):
            return Response("Invalid media type", status=415)
        
        # Download audio
        response = requests.get(media_url, stream=True)
        response.raise_for_status()
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".oga") as tmp_file:
            for chunk in response.iter_content(chunk_size=8192):
                tmp_file.write(chunk)
            tmp_path = tmp_file.name
        
        # Transcribe and process
        transcript = speech_to_text(tmp_path)
        logger.info(f"Voice note from {from_number}: {transcript}")
        
        # Check for emergency - UPDATED
        if detect_emergency(transcript):
            emergency_type = handle_emergency(from_number, transcript)
            return Response(f"Emergency detected in voice note! {emergency_type.capitalize()} services have been alerted.", status=200)
        
        # Moderate content
        if not moderate_content(transcript):
            return Response("Message contains inappropriate content", status=200)
        
        # Get conversation context
        context = conversation_memory.get_context(from_number)
        
        # Generate response
        bot_response = query_chatgpt(transcript, context, "english")
        enhanced_response = local_knowledge.enhance(transcript, bot_response)
        
        # Save conversation
        conversation_memory.save(from_number, transcript, enhanced_response)
        
        # Send response
        twilio_client.messages.create(
            body=enhanced_response,
            from_=config.TWILIO_PHONE_NUMBER,
            to=from_number
        )
        
        os.unlink(tmp_path)
        return Response("Voice note processed", status=200)
        
    except Exception as e:
        logger.error(f"Voice Note Error: {str(e)}")
        return Response("Processing error", status=500)

@app.route("/feedback", methods=["POST"])
def feedback():
    if not validate_twilio_request(request):
        return Response("Invalid Twilio signature", status=403)
    
    try:
        from_number = request.form.get("From")
        feedback_text = request.form.get("Body", "").strip()
        
        if not feedback_text:
            return Response("Empty feedback", status=400)
        
        handle_feedback.save(from_number, feedback_text)
        return Response("Thank you for your feedback!", status=200)
        
    except Exception as e:
        logger.error(f"Feedback Error: {str(e)}")
        return Response("Feedback processing error", status=500)

@app.route("/admin/analytics", methods=["GET"])
def admin_analytics():
    # Basic authentication check
    auth = request.headers.get("Authorization")
    if auth != f"Bearer {config.ADMIN_TOKEN}":
        return Response("Unauthorized", status=401)
    
    return track_usage.get_analytics()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=config.SERVER_PORT, debug=config.DEBUG)