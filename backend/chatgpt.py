import logging
from openai import OpenAI
from config import OPENAI_API_KEY
from user_preferences import get_user_preference

logger = logging.getLogger(__name__)

# Initialize OpenAI client with error handling
try:
    client = OpenAI(api_key=OPENAI_API_KEY)
    logger.info("OpenAI client initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize OpenAI client: {str(e)}")
    raise ValueError(f"OpenAI client initialization failed: {str(e)}")

def query_chatgpt(message, phone_number=None, context=None, user_role=None):
    """
    Enhanced ChatGPT query with user context and language support
    """
    try:
        logger.info(f"Querying ChatGPT for {phone_number or 'unknown user'}")
        
        # Get user preferences if phone number provided
        language = "en"
        user_context = ""
        
        if phone_number:
            language = get_user_preference(phone_number, "language", "en")
            user_role = get_user_preference(phone_number, "user_role", user_role)
        
        # Prepare system message with context
        system_messages = []
        
        # Add user role context if available
        if user_role:
            role_contexts = {
                "boda_rider": "You are assisting a boda boda (motorcycle taxi) rider in Uganda. Provide practical, actionable advice for transportation business. Focus on safety, earnings, customer management, and local Ugandan context.",
                "shopkeeper": "You are assisting a small shopkeeper in Uganda. Help with inventory, pricing, customer service, and business growth. Use Ugandan shillings and local market context.",
                "farmer": "You are assisting a farmer in Uganda. Provide agricultural advice, weather considerations, market prices, and farming best practices suitable for Ugandan climate.",
                "student": "You are assisting a student in Uganda. Help with studies, career advice, and educational resources. Be encouraging and practical.",
                "market_trader": "You are assisting a market trader in Uganda. Focus on sales, pricing, customer relations, and market dynamics in places like Owino or Nakasero market.",
                "health_patient": "You are assisting a healthcare patient in Uganda. Provide health information, reminder support, and general wellness advice. Always recommend consulting healthcare professionals.",
                "default": "You are a helpful AI assistant for users in Uganda. Provide practical, culturally appropriate advice and information relevant to the Ugandan context."
            }
            user_context = role_contexts.get(user_role, role_contexts["default"])
            system_messages.append({"role": "system", "content": user_context})
        
        # Add language guidance if not English
        if language != "en":
            language_names = {
                "sw": "Swahili",
                "lg": "Luganda", 
                "fr": "French"
            }
            lang_name = language_names.get(language, "the local language")
            system_messages.append({
                "role": "system", 
                "content": f"Respond in {lang_name} if appropriate and when the user communicates in that language. Use simple, clear language suitable for SMS."
            })
        
        # Add general context for Uganda
        system_messages.append({
            "role": "system",
            "content": "You are assisting users in Uganda. Use Ugandan shillings (UGX) for financial amounts. Be culturally sensitive and practical. Keep responses concise for SMS limitations."
        })
        
        # Build messages array
        messages = system_messages + [{"role": "user", "content": message}]
        
        logger.debug(f"Sending request to OpenAI API with {len(messages)} messages")
        
        # Use new OpenAI client
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=350,  # Reduced for SMS compatibility
            temperature=0.7,
            timeout=30
        )
        
        # Extract response
        bot_response = response.choices[0].message.content.strip()
        logger.info(f"ChatGPT response generated: {bot_response[:100]}...")
        
        return bot_response

    except Exception as openai_error:
        if "timeout" in str(openai_error).lower():
            logger.error("OpenAI API request timed out")
            return "Sorry, the request took too long. Please try again."
        else:
            logger.error(f"OpenAI API request failed: {str(openai_error)}")
            return "Sorry, I'm having trouble connecting right now. Please try again later."
    except Exception as e:
        logger.error(f"Error in query_chatgpt: {str(e)}", exc_info=True)
        return "Sorry, I encountered an error processing your request. Please try again."