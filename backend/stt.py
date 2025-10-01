import logging
from openai import OpenAI
from config import OPENAI_API_KEY

logger = logging.getLogger(__name__)

# Initialize OpenAI client with error handling
try:
    client = OpenAI(api_key=OPENAI_API_KEY)
    logger.info("OpenAI STT client initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize OpenAI STT client: {str(e)}")
    client = None

def speech_to_text(audio_file_path):
    """Convert speech to text using OpenAI Whisper API"""
    if client is None:
        logger.error("OpenAI STT client not initialized")
        return None
        
    try:
        with open(audio_file_path, 'rb') as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
        return transcript.text
    except Exception as e:
        logger.error(f"Error in speech to text conversion: {str(e)}")
        return None
