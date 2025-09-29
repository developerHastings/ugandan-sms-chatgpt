import json
import os
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Use absolute path for user preferences - create data directory in backend folder
USER_PREFS_FILE = os.path.join(os.path.dirname(__file__), "data", "user_preferences.json")

def ensure_data_directory():
    """Create data directory if it doesn't exist"""
    data_dir = os.path.dirname(USER_PREFS_FILE)
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        logger.info(f"Created data directory: {data_dir}")

def load_user_preferences() -> Dict[str, Any]:
    """Load user preferences from JSON file"""
    ensure_data_directory()
    
    if not os.path.exists(USER_PREFS_FILE):
        logger.info(f"Preferences file not found, creating new one: {USER_PREFS_FILE}")
        return {}
    
    try:
        with open(USER_PREFS_FILE, 'r', encoding='utf-8') as f:
            prefs = json.load(f)
            logger.debug(f"Loaded preferences for {len(prefs)} users")
            return prefs
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Error loading preferences file: {str(e)}")
        return {}

def save_user_preferences(prefs: Dict[str, Any]):
    """Save user preferences to JSON file with backup"""
    ensure_data_directory()
    
    try:
        # Create backup if file exists
        if os.path.exists(USER_PREFS_FILE):
            backup_file = USER_PREFS_FILE + ".bak"
            with open(USER_PREFS_FILE, 'r', encoding='utf-8') as original:
                with open(backup_file, 'w', encoding='utf-8') as backup:
                    backup.write(original.read())
        
        # Save new preferences
        with open(USER_PREFS_FILE, 'w', encoding='utf-8') as f:
            json.dump(prefs, f, indent=2, ensure_ascii=False)
        
        logger.debug(f"Saved preferences for {len(prefs)} users")
        
    except IOError as e:
        logger.error(f"Error saving preferences file: {str(e)}")
        raise

def get_user_preference(phone_number: str, preference_key: str, default: Any = None) -> Any:
    """
    Get a specific preference for a user
    
    Args:
        phone_number: User's phone number (key)
        preference_key: Specific preference to retrieve
        default: Default value if preference not found
    
    Returns:
        Preference value or default
    """
    if not phone_number:
        logger.warning("Empty phone number provided to get_user_preference")
        return default
    
    prefs = load_user_preferences()
    user_prefs = prefs.get(phone_number, {})
    
    value = user_prefs.get(preference_key, default)
    logger.debug(f"Retrieved preference '{preference_key}' for {phone_number}: {value}")
    
    return value

def set_user_preference(phone_number: str, preference_key: str, value: Any):
    """
    Set a preference for a user
    
    Args:
        phone_number: User's phone number (key)
        preference_key: Preference to set
        value: Value to set
    """
    if not phone_number:
        logger.warning("Empty phone number provided to set_user_preference")
        return
    
    prefs = load_user_preferences()
    
    if phone_number not in prefs:
        prefs[phone_number] = {}
        logger.info(f"Created new preferences entry for {phone_number}")
    
    prefs[phone_number][preference_key] = value
    save_user_preferences(prefs)
    
    logger.debug(f"Set preference '{preference_key}' for {phone_number}: {value}")

def get_all_user_preferences(phone_number: str) -> Dict[str, Any]:
    """Get all preferences for a user"""
    if not phone_number:
        return {}
    
    prefs = load_user_preferences()
    return prefs.get(phone_number, {})

def delete_user_preference(phone_number: str, preference_key: str) -> bool:
    """Delete a specific preference for a user"""
    if not phone_number:
        return False
    
    prefs = load_user_preferences()
    
    if phone_number in prefs and preference_key in prefs[phone_number]:
        del prefs[phone_number][preference_key]
        save_user_preferences(prefs)
        logger.info(f"Deleted preference '{preference_key}' for {phone_number}")
        return True
    
    return False

def get_user_role(phone_number: str) -> str:
    """Convenience method to get user role"""
    return get_user_preference(phone_number, "user_role", "default")

def set_user_role(phone_number: str, role: str):
    """Convenience method to set user role"""
    valid_roles = ["boda_rider", "shopkeeper", "farmer", "student", "market_trader", 
                  "health_patient", "factory_manager", "performer", "hustler", 
                  "family_manager", "investor", "community_connector", "default"]
    
    if role not in valid_roles:
        logger.warning(f"Invalid role attempted: {role}")
        role = "default"
    
    set_user_preference(phone_number, "user_role", role)

def get_user_language(phone_number: str) -> str:
    """Convenience method to get user language preference"""
    return get_user_preference(phone_number, "language", "en")

def set_user_language(phone_number: str, language: str):
    """Convenience method to set user language preference"""
    valid_languages = ["en", "sw", "lg", "fr"]
    
    if language not in valid_languages:
        logger.warning(f"Invalid language attempted: {language}")
        language = "en"
    
    set_user_preference(phone_number, "language", language)

# Initialize default structure if file doesn't exist
def initialize_defaults():
    """Initialize with default structure if needed"""
    if not os.path.exists(USER_PREFS_FILE):
        ensure_data_directory()
        default_prefs = {
            "metadata": {
                "version": "1.0",
                "created_by": "SMStoAI System",
                "user_count": 0
            },
            "users": {}
        }
        save_user_preferences(default_prefs)

# Run initialization when module is imported
initialize_defaults()