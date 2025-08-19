import json
import os
from datetime import datetime

class FeedbackHandler:
    def __init__(self, storage_path="data/feedback"):
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)
    
    def save(self, phone_number, feedback_text):
        timestamp = datetime.now().isoformat()
        file_path = os.path.join(self.storage_path, f"{date.today().isoformat()}.json")
        
        # Load today's feedback
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                data = json.load(f)
        else:
            data = {"date": date.today().isoformat(), "feedbacks": []}
        
        # Add new feedback
        data["feedbacks"].append({
            "timestamp": timestamp,
            "phone_number": phone_number,
            "feedback": feedback_text
        })
        
        # Save updated feedback
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)

# Create singleton instance
feedback_handler = FeedbackHandler()

# Convenience function
def handle_feedback(phone_number, feedback_text):
    feedback_handler.save(phone_number, feedback_text)