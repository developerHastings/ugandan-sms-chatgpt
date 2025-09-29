import tempfile
import os
import logging
from openai import OpenAI
from .config import OPENAI_API_KEY

logger = logging.getLogger(__name__)

# Initialize OpenAI client with error handling
try:
    client = OpenAI(api_key=OPENAI_API_KEY)
    logger.info("OpenAI TTS client initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize OpenAI TTS client: {str(e)}")
    client = None

def text_to_speech(text, language="en", voice="alloy"):
    """
    Convert text to speech using OpenAI's TTS API
    Supports multiple languages and voices
    """
    if client is None:
        logger.error("OpenAI TTS client not initialized")
        return None
        
    # Map languages to appropriate voices if needed
    voice_mapping = {
        "en": "alloy",
        "sw": "echo",  # Swahili
        "lg": "ash",  # Luganda
        "fr": "nova"   # French
    }
    
    # Use appropriate voice for the language
    selected_voice = voice_mapping.get(language, voice)
    
    try:
        response = client.audio.speech.create(
            model="tts-1",
            voice=selected_voice,
            input=text
        )
        
        # Create temporary file for audio
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
            response.stream_to_file(tmp_file.name)
            return tmp_file.name
            
    except Exception as e:
        logger.error(f"Error in TTS conversion: {str(e)}")
        return None
