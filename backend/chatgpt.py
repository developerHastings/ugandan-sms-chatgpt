import requests
from .config import OPENAI_API_KEY

def query_chatgpt(message):
    print(f"Loaded OpenAI API Key starts with: {OPENAI_API_KEY[:8]}")
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": message}],
        "max_tokens": 500,
    }

    response = requests.post(url, json=data, headers=headers)
    response.raise_for_status()
    result = response.json()

    # Safety checks
    if result is None:
        raise ValueError("Empty response from OpenAI API")
    if 'choices' not in result or not result['choices']:
        raise ValueError(f"Unexpected response format: {result}")

    return result['choices'][0]['message']['content'].strip()