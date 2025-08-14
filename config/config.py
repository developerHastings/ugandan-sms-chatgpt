from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env file

class Config:
    def __init__(self):
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        self.TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
        self.TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
        self.TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
        self.SERVER_PORT = int(os.getenv("PORT", "5000"))

# Create a single instance of the configuration
config = Config()