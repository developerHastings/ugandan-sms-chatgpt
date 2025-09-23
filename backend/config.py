from dotenv import load_dotenv
import os

# Load from backend/.env
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))  

# Verify critical variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("Missing OPENAI_API_KEY in .env")

# Africa's Talking Configuration
AFRICASTALKING_USERNAME = os.getenv("AFRICASTALKING_USERNAME")
AFRICASTALKING_API_KEY = os.getenv("AFRICASTALKING_API_KEY")
AFRICASTALKING_SENDER_ID = os.getenv("AFRICASTALKING_SENDER_ID", "SMStoAI")  # Max 11 characters
AFRICASTALKING_VOICE_CALLER_ID = os.getenv("AFRICASTALKING_VOICE_CALLER_ID", "")

# Validate Africa's Talking credentials
if not AFRICASTALKING_USERNAME:
    raise ValueError("Missing AFRICASTALKING_USERNAME in .env")
if not AFRICASTALKING_API_KEY:
    raise ValueError("Missing AFRICASTALKING_API_KEY in .env")

# Africa's Talking settings
AFRICASTALKING_SANDBOX = os.getenv("AFRICASTALKING_SANDBOX", "True").lower() == "true"

# Voice and Language Configuration
DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "en")
SUPPORTED_LANGUAGES = os.getenv("SUPPORTED_LANGUAGES", "en,sw,lg,fr").split(",")
VOICE_RESPONSE_ENABLED = os.getenv("VOICE_RESPONSE_ENABLED", "True").lower() == "true"

# Server Configuration
SERVER_PORT = int(os.getenv("PORT", "5000"))

# Optional: Keep Twilio for transition period (comment out or remove later)
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

# Log configuration status
print("Configuration loaded successfully:")
print(f"- Africa's Talking Username: {AFRICASTALKING_USERNAME}")
print(f"- Africa's Talking Sender ID: {AFRICASTALKING_SENDER_ID}")
print(f"- Sandbox Mode: {AFRICASTALKING_SANDBOX}")
print(f"- Default Language: {DEFAULT_LANGUAGE}")
print(f"- Supported Languages: {SUPPORTED_LANGUAGES}")
print(f"- Voice Response Enabled: {VOICE_RESPONSE_ENABLED}")
print(f"- Server Port: {SERVER_PORT}")

# Optional: Warn if Twilio credentials are still present (for migration)
if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN:
    print("⚠️  Twilio credentials detected - remember to update endpoints for Africa's Talking")