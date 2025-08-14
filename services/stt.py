import requests
import logging
from config import config  # Import the config instance

logger = logging.getLogger(__name__)

def speech_to_text(audio_path):
    # Use config.OPENAI_API_KEY INSIDE the function
    headers = {"Authorization": f"Bearer {config.OPENAI_API_KEY}"}
    
    try:
        with open(audio_path, 'rb') as audio_file:
            files = {"file": audio_file}
            data = {"model": "whisper-1"}
            response = requests.post(
                "https://api.openai.com/v1/audio/transcriptions",
                headers=headers,
                files=files,
                data=data
            )
        
        response.raise_for_status()
        return response.json().get('text', '').strip()
    
    except Exception as e:
        logger.error(f"STT Error: {str(e)}")
        return ""