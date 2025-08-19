import json
import os
from datetime import datetime, date

class AnalyticsTracker:
    def __init__(self, storage_path="data/analytics"):
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)
    
    def track(self, phone_number, event_type, details=None):
        today = date.today().isoformat()
        file_path = os.path.join(self.storage_path, f"{today}.json")
        
        # Load today's analytics
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                data = json.load(f)
        else:
            data = {
                "date": today,
                "total_messages": 0,
                "unique_users": set(),
                "message_types": {"sms": 0, "voice_note": 0},
                "events": []
            }
        
        # Update analytics
        data["total_messages"] += 1
        data["unique_users"].add(phone_number)
        
        if event_type in data["message_types"]:
            data["message_types"][event_type] += 1
        
        data["events"].append({
            "timestamp": datetime.now().isoformat(),
            "phone_number": phone_number,
            "type": event_type,
            "details": details or {}
        })
        
        # Convert set to list for JSON serialization
        data["unique_users"] = list(data["unique_users"])
        
        # Save updated analytics
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def get_analytics(self, days=7):
        results = []
        for i in range(days):
            day = date.fromordinal(date.today().toordinal() - i)
            file_path = os.path.join(self.storage_path, f"{day.isoformat()}.json")
            
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    results.append(data)
        
        return {
            "period": f"Last {days} days",
            "total_messages": sum(day["total_messages"] for day in results),
            "unique_users": len(set(uid for day in results for uid in day["unique_users"])),
            "daily_breakdown": results
        }

# Create singleton instance
analytics_tracker = AnalyticsTracker()

# Convenience function
def track_usage(phone_number, event_type):
    analytics_tracker.track(phone_number, event_type)