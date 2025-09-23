import os
from flask import Flask, request, Response, jsonify
import logging
import tempfile
import requests
import tempfile
import logging
from werkzeug.utils import secure_filename

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

@app.route("/sms", methods=["POST"])
def sms_reply():
    """Handle incoming SMS messages and respond using ChatGPT."""
    try:
        # Validate incoming request
        if not request.form:
            logger.error("No form data received in SMS request")
            return Response("Invalid request format", status=400)

        incoming_msg = request.form.get("Body", "").strip()
        from_number = request.form.get("From", "").strip()

        if not incoming_msg:
            logger.warning(f"Empty message received from {from_number}")
            return Response("Message body cannot be empty", status=400)

        if not from_number:
            logger.error("No sender number provided")
            return Response("Sender number missing", status=400)

        logger.info(f"Received SMS from {from_number}: {incoming_msg}")

        # Process message with ChatGPT
        bot_response = query_chatgpt(incoming_msg)
        if not bot_response:
            bot_response = "Sorry, I couldn't process your request. Please try again."

        # Create Twilio response
        resp = MessagingResponse()
        resp.message(bot_response)
        
        logger.info(f"Responded to {from_number} with: {bot_response}")
        return str(resp)

    except Exception as e:
        logger.error(f"Error handling Africa's Talking SMS: {str(e)}")
        return Response("Error processing message", status=500)

@app.route("/africastalking/voice", methods=["POST"])
def africastalking_voice():
    """Handle incoming voice calls from Africa's Talking"""
    try:
        # Validate request
        from_number = request.form.get("From", "").strip()
        if not from_number:
            logger.error("No sender number in voice note request")
            return Response("Sender number missing", status=400)

        media_url = request.form.get("MediaUrl0")
        if not media_url:
            logger.error(f"No media URL in voice note from {from_number}")
            return Response("No media file uploaded", status=400)

        logger.info(f"Processing voice note from {from_number}")

        # Download the audio file with safety checks
        try:
            response = requests.get(media_url, stream=True, timeout=10)
            response.raise_for_status()
            
            # Create secure temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".ogg") as tmp_file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:  # filter out keep-alive chunks
                        tmp_file.write(chunk)
                tmp_file_path = tmp_file.name

            logger.info(f"Downloaded voice note to {tmp_file_path}")

        except requests.RequestException as e:
            logger.error(f"Failed to download media: {str(e)}")
            return Response("Failed to process media file", status=500)

        try:
            # Transcribe audio to text
            transcript = speech_to_text(tmp_file_path)
            if not transcript:
                logger.error("Empty transcription from voice note")
                raise ValueError("Could not transcribe voice note")

            logger.info(f"Transcribed voice note: {transcript}")

            # Query ChatGPT with the transcript
            bot_response = query_chatgpt(transcript)
            if not bot_response:
                logger.error("Empty response from ChatGPT")
                bot_response = "Sorry, I couldn't process your voice note. Please try again."

            # Send SMS reply with ChatGPT response
            twilio_client.messages.create(
                body=bot_response,
                from_=TWILIO_PHONE_NUMBER,
                to=from_number
            )

            logger.info(f"Sent SMS response to {from_number}")

            return Response("Voice note processed and SMS response sent", status=200)

        finally:
            # Cleanup temporary file
            try:
                os.remove(tmp_file_path)
                logger.info(f"Deleted temporary file {tmp_file_path}")
            except OSError as e:
                logger.error(f"Error deleting temp file: {str(e)}")

    except Exception as e:
        logger.error(f"Error handling voice note: {str(e)}")
        return Response("Error processing voice note", status=500)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=SERVER_PORT)
