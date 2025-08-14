import requests
from config.config import OPENAI_API_KEY

def query_chatgpt(message):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-4o-mini",  # or "gpt-4" if available
        "messages": [{"role": "user", "content": message}],
        "max_tokens": 500,
    }
    response = requests.post(url, json=data, headers=headers)
    response.raise_for_status()
    return response.json()['choices'][0]['message']['content'].strip()
