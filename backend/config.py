from dotenv import load_dotenv
import os

# Load from backend/.env
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))  

# Verify critical variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("Missing OPENAI_API_KEY in .env")

# Africa's Talking Configuration - UPDATED WITH SHORTCODE SUPPORT
AFRICASTALKING_USERNAME = os.getenv("AFRICASTALKING_USERNAME")
AFRICASTALKING_API_KEY = os.getenv("AFRICASTALKING_API_KEY")
AFRICASTALKING_SENDER_ID = os.getenv("AFRICASTALKING_SENDER_ID", "SMStoAI")
AFRICASTALKING_VOICE_CALLER_ID = os.getenv("AFRICASTALKING_VOICE_CALLER_ID", "")
AFRICASTALKING_SHORTCODE = os.getenv("AFRICASTALKING_SHORTCODE", "*284*426#")  # NEW: Your USSD shortcode

# Validate Africa's Talking credentials
if not AFRICASTALKING_USERNAME:
    raise ValueError("Missing AFRICASTALKING_USERNAME in .env")
if not AFRICASTALKING_API_KEY:
    raise ValueError("Missing AFRICASTALKING_API_KEY in .env")

# Africa's Talking settings - UPDATED FOR PRODUCTION
AFRICASTALKING_SANDBOX = os.getenv("AFRICASTALKING_SANDBOX", "False").lower() == "true"  # Changed default to False

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

# Log configuration status - UPDATED WITH SHORTCODE INFO
print("=" * 50)
print("UGANDA AI SMS CHATBOT CONFIGURATION")
print("=" * 50)
print(f"   Africa's Talking Configuration:")
print(f"   Username: {AFRICASTALKING_USERNAME}")
print(f"   Sender ID: {AFRICASTALKING_SENDER_ID}")
print(f"   Shortcode: {AFRICASTALKING_SHORTCODE}")
print(f"   Sandbox Mode: {AFRICASTALKING_SANDBOX}")
print(f"   Voice Caller ID: {AFRICASTALKING_VOICE_CALLER_ID or 'Not set'}")
print(f"   Service Settings:")
print(f"   Default Language: {DEFAULT_LANGUAGE}")
print(f"   Supported Languages: {', '.join(SUPPORTED_LANGUAGES)}")
print(f"   Voice Response Enabled: {VOICE_RESPONSE_ENABLED}")
print(f"🔧 Server Configuration:")
print(f"   Port: {SERVER_PORT}")
print(f"   OpenAI API Key: {'✓ Loaded' if OPENAI_API_KEY else '✗ Missing'}")
print("=" * 50)

# Check if we're using shortcode (production ready)
if AFRICASTALKING_SHORTCODE and AFRICASTALKING_SHORTCODE.startswith('*'):
    print("🚀 PRODUCTION READY: Shortcode detected - Service is live!")
    if AFRICASTALKING_SANDBOX:
        print("  WARNING: Sandbox mode is True but you have a production shortcode")
        print("   Consider setting AFRICASTALKING_SANDBOX=False")
else:
    print("🔧 DEVELOPMENT MODE: Using alphanumeric sender ID")

# Optional: Warn if Twilio credentials are still present (for migration)
if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN:
    print("  Twilio credentials detected - Africa's Talking is now primary service")

print("Configuration loaded successfully!")