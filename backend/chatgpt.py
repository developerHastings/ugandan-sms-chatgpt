import requests
from .config import OPENAI_API_KEY

def query_chatgpt(message):
    """
    Query GPT-4-turbo with instructions to respond in Ugandan local languages when appropriate.
    Args:
        message (str): User input message
    Returns:
        str: AI response in Luganda/English mix or English
    """
    print(f"Loaded OpenAI API Key starts with: {OPENAI_API_KEY[:8]}")
    
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "gpt-4-turbo",
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a friendly assistant fluent in Ugandan languages including Luganda, Runyankole, and Acholi. "
                    "Follow these rules:\n"
                    "1. If the user speaks in a Ugandan language, respond in the same language mixed with English\n"
                    "2. Use Luganda for common phrases like greetings ('Webale nyo' for thank you)\n"
                    "3. For complex topics, mix English with local language explanations\n"
                    "4. Incorporate Ugandan cultural context and proverbs when appropriate\n"
                    "5. Keep responses clear and concise (max 500 tokens)"
                )
            },
            {
                "role": "user",
                "content": message
            }
        ],
        "max_tokens": 500,
        "temperature": 0.7  # Adds some creativity to responses
    }

    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        result = response.json()

        # Safety checks
        if result is None:
            raise ValueError("Empty response from OpenAI API")
        if 'choices' not in result or not result['choices']:
            raise ValueError(f"Unexpected response format: {result}")

        return result['choices'][0]['message']['content'].strip()
    
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        return "Nze sikisobola kukutteko olw'ensonga enkalu. Geragerako myo!"  # "I can't help right now due to a problem. Try again later!"
    
    except Exception as e:
        print(f"Error processing response: {e}")
        return "Wabula ensonga etereeze. Ddamu oyagale!"  # "An unexpected error occurred. Please try again!"
