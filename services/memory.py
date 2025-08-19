import json
import os
from datetime import datetime

class ConversationMemory:
    def __init__(self, storage_path="data/conversations"):
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)
    
    def get_context(self, phone_number, max_messages=5):
        file_path = os.path.join(self.storage_path, f"{phone_number}.json")
        
        if not os.path.exists(file_path):
            return []
        
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                return data.get("messages", [])[-max_messages:]
        except:
            return []
    
    def save(self, phone_number, user_message, bot_response):
        file_path = os.path.join(self.storage_path, f"{phone_number}.json")
        
        # Load existing data
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                data = json.load(f)
        else:
            data = {"phone_number": phone_number, "messages": []}
        
        # Add new messages
        timestamp = datetime.now().isoformat()
        data["messages"].append({
            "timestamp": timestamp,
            "user": user_message,
            "bot": bot_response
        })
        
        # Keep only last 20 messages
        data["messages"] = data["messages"][-20:]
        
        # Save back to file
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)

# Create singleton instance
conversation_memory = ConversationMemory()