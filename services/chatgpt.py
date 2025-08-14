import requests
import logging
from config import config

logger = logging.getLogger(__name__)

def query_chatgpt(message):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {config.OPENAI_API_KEY}",  # FIXED: use config instance
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-4o",
        "messages": [{"role": "user", "content": message}],
        "max_tokens": 500,
    }
    
    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content'].strip()
    
    except Exception as e:
        logger.error(f"ChatGPT Error: {str(e)}")
        return "I'm having trouble thinking right now. Please try again later."