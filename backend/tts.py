import requests
import tempfile
import os
from .config import OPENAI_API_KEY

def text_to_speech(text, language="en", voice="alloy"):
    """
    Convert text to speech using OpenAI's TTS API
    Supports multiple languages and voices
    """
    url = "https://api.openai.com/v1/audio/speech"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Map languages to appropriate voices if needed
    voice_mapping = {
        "en": "alloy",
        "sw": "echo",  # Swahili
        "lg": "ash",  # Luganda
        "fr": "nova"   # French
    }
    
    # Use appropriate voice for the language
    selected_voice = voice_mapping.get(language, voice)
    
    data = {
        "model": "tts-1",
        "input": text,
        "voice": selected_voice,
        "response_format": "mp3"
    }
    
    try:
        response = requests.post(url, json=data, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Create temporary file for audio
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
            tmp_file.write(response.content)
            return tmp_file.name
            
    except requests.RequestException as e:
        print(f"Error in TTS conversion: {str(e)}")
        return None