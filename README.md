
# Uganda SMS ChatGPT

A Twilio-based ChatGPT integration that enables SMS and voice-based conversations through OpenAI's API.

## Features
- 💬 SMS-based ChatGPT conversations
- 🎙️ Voice note transcription and response
- 🔐 Secure Twilio request validation
- 🌐 Health check endpoint
- 📝 Detailed logging

## Setting Up Twilio Webhooks

Start ngrok for local testing:
ngrok http 5000

Configure Twilio webhooks:

SMS Webhook: https://your-ngrok-url.ngrok.io/sms

MMS Webhook: https://your-ngrok-url.ngrok.io/voice-note

### Prerequisites
- Python 3.8+
- Twilio account with SMS-enabled number
- OpenAI API access

 **API Endpoints**:
- POST /sms - Handle incoming SMS
- POST /voice-note - Handle voice notes
- GET / - Health check
