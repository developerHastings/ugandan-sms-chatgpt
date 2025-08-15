import requests
from .config import OPENAI_API_KEY

def speech_to_text(audio_file_path):
    url = "https://api.openai.com/v1/audio/transcriptions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }
    with open(audio_file_path, 'rb') as audio_file:
        files = {
            "file": audio_file,
            "model": (None, "whisper-1"),
        }
        response = requests.post(url, headers=headers, files=files)
    response.raise_for_status()
    return response.json()['text']
