import os
from flask import Flask, request, Response
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
import requests
import tempfile

from config.config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER, SERVER_PORT
from services.chatgpt import query_chatgpt
from services.stt import speech_to_text

app = Flask(__name__)
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

@app.route("/sms", methods=["POST"])
def sms_reply():
    incoming_msg = request.form.get("Body")
    from_number = request.form.get("From")

    try:
        bot_response = query_chatgpt(incoming_msg)

        resp = MessagingResponse()
        resp.message(bot_response)
        return str(resp)

    except Exception as e:
        print(f"Error handling SMS: {e}")
        return Response("Error processing message", status=500)

@app.route("/voice-note", methods=["POST"])
def voice_note():
    from_number = request.form.get("From")
    media_url = request.form.get("MediaUrl0")  # Twilio sends media links here

    if not media_url:
        return Response("No media file uploaded", status=400)

    try:
        # Download the audio file temporarily
        response = requests.get(media_url, stream=True)
        response.raise_for_status()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".ogg") as tmp_file:
            for chunk in response.iter_content(chunk_size=8192):
                tmp_file.write(chunk)
            tmp_file_path = tmp_file.name

        # Transcribe audio to text
        transcript = speech_to_text(tmp_file_path)

        # Query ChatGPT with the transcript
        bot_response = query_chatgpt(transcript)

        # Send SMS reply with ChatGPT response
        twilio_client.messages.create(
            body=bot_response,
            from_=TWILIO_PHONE_NUMBER,
            to=from_number
        )

        # Cleanup temporary file
        os.remove(tmp_file_path)
        return Response("Voice note processed and SMS response sent", status=200)

    except Exception as e:
        print(f"Error handling voice note: {e}")
        return Response("Error processing voice note", status=500)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=SERVER_PORT)
