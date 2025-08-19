import os
import logging
from flask import Flask, request, Response
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
from twilio.request_validator import RequestValidator
import requests
import tempfile

from config import config
from services import query_chatgpt, speech_to_text

app = Flask(__name__)

# Initialize Twilio client using config
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
    return "ChatGPT Twilio Bot is running!", 200

@app.route("/sms", methods=["POST"])
def sms_reply():
    if not validate_twilio_request(request):
        return Response("Invalid Twilio signature", status=403)
    
    try:
        incoming_msg = request.form.get("Body", "").strip()
        from_number = request.form.get("From", "")
        
        if not incoming_msg:
            return Response("Empty message body", status=400)
        
        logger.info(f"SMS from {from_number}: {incoming_msg}")
        bot_response = query_chatgpt(incoming_msg)
        
        resp = MessagingResponse()
        resp.message(bot_response)
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
        bot_response = query_chatgpt(transcript)
        
        # Send response
        twilio_client.messages.create(
            body=bot_response,
            from_=config.TWILIO_PHONE_NUMBER,
            to=from_number
        )
        
        os.unlink(tmp_path)
        return Response("Voice note processed", status=200)
        
    except Exception as e:
        logger.error(f"Voice Note Error: {str(e)}")
        return Response("Processing error", status=500)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=config.SERVER_PORT, debug=config.DEBUG)