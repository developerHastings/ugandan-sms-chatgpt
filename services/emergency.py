import requests
from twilio.rest import Client
from config import config

# Initialize Twilio client
twilio_client = Client(config.TWILIO_ACCOUNT_SID, config.TWILIO_AUTH_TOKEN)

class EmergencyDetector:
    def __init__(self):
        self.emergency_keywords = [
            "help", "emergency", "accident", "danger", "save me",
            "police", "ambulance", "fire", "hurt", "bleeding",
            "attack", "robbery", "fire", "burning", "unconscious",
            "heart attack", "stroke", "dying", "urgent", "critical"
        ]
        
        # Uganda-specific emergency phrases
        self.uganda_emergency_phrases = [
            "mpulira", "eddembe lyange", "nsaba eddembe", "nkulwa",
            "ntambula bulungi", "ndwadde", "omulwadde", "ensonga enkulu"
        ]
    
    def detect(self, text):
        text_lower = text.lower()
        
        # Check for emergency keywords
        for keyword in self.emergency_keywords:
            if keyword in text_lower:
                return True
        
        # Check for Uganda-specific emergency phrases
        for phrase in self.uganda_emergency_phrases:
            if phrase in text_lower:
                return True
        
        return False
    
    def handle_emergency(self, phone_number, message, location=None):
        """
        Handle emergency by contacting appropriate services based on content
        """
        # Analyze message to determine emergency type
        emergency_type = self.classify_emergency(message)
        
        # Send alerts to emergency contacts
        self.alert_emergency_contacts(phone_number, message, emergency_type)
        
        # Contact appropriate emergency services
        self.contact_emergency_services(phone_number, message, emergency_type)
        
        return emergency_type
    
    def classify_emergency(self, message):
        """Determine the type of emergency"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["police", "robbery", "attack", "crime"]):
            return "police"
        elif any(word in message_lower for word in ["medical", "hospital", "doctor", "hurt", "bleeding", "unconscious"]):
            return "medical"
        elif any(word in message_lower for word in ["fire", "burning", "smoke"]):
            return "fire"
        else:
            return "general"
    
    def alert_emergency_contacts(self, phone_number, message, emergency_type):
        """Send alerts to predefined emergency contacts"""
        alert_message = config.EMERGENCY_MESSAGE_TEMPLATE.format(
            user_number=phone_number,
            message=message,
            type=emergency_type
        )
        
        for contact in config.EMERGENCY_CONTACTS:
            if contact.strip():  # Skip empty contacts
                try:
                    twilio_client.messages.create(
                        body=alert_message,
                        from_=config.TWILIO_PHONE_NUMBER,
                        to=contact.strip()
                    )
                    print(f"Emergency alert sent to {contact}")
                except Exception as e:
                    print(f"Failed to send alert to {contact}: {str(e)}")
    
    def contact_emergency_services(self, phone_number, message, emergency_type):
        """Contact appropriate emergency services based on emergency type"""
        if emergency_type == "police" and "police" in config.EMERGENCY_SERVICES:
            # For police, we can initiate a call
            self.initiate_emergency_call(
                config.EMERGENCY_SERVICES["police"],
                f"Emergency alert from {phone_number}: {message}"
            )
        
        elif emergency_type == "medical" and "ambulance" in config.EMERGENCY_SERVICES:
            # For medical emergencies, contact ambulance service
            self.initiate_emergency_call(
                config.EMERGENCY_SERVICES["ambulance"],
                f"Medical emergency from {phone_number}: {message}"
            )
        
        elif emergency_type == "fire" and "fire" in config.EMERGENCY_SERVICES:
            # For fire emergencies
            self.initiate_emergency_call(
                config.EMERGENCY_SERVICES["fire"],
                f"Fire emergency from {phone_number}: {message}"
            )
        
        # Always contact Red Cross for any major emergency
        if emergency_type in ["medical", "general"] and "red_cross" in config.EMERGENCY_SERVICES:
            self.send_emergency_sms(
                config.EMERGENCY_SERVICES["red_cross"],
                f"Emergency alert from {phone_number}: {message}"
            )
    
    def initiate_emergency_call(self, to_number, message):
        """Initiate an emergency phone call"""
        try:
            # Create a call with Twilio
            call = twilio_client.calls.create(
                twiml=f'<Response><Say voice="alice">{message}</Say></Response>',
                to=to_number,
                from_=config.TWILIO_PHONE_NUMBER
            )
            print(f"Emergency call initiated to {to_number}: {call.sid}")
        except Exception as e:
            print(f"Failed to initiate call to {to_number}: {str(e)}")
    
    def send_emergency_sms(self, to_number, message):
        """Send emergency SMS"""
        try:
            twilio_client.messages.create(
                body=message,
                from_=config.TWILIO_PHONE_NUMBER,
                to=to_number
            )
            print(f"Emergency SMS sent to {to_number}")
        except Exception as e:
            print(f"Failed to send SMS to {to_number}: {str(e)}")

# Create singleton instance
emergency_detector = EmergencyDetector()

# Convenience functions
def detect_emergency(text):
    return emergency_detector.detect(text)

def handle_emergency(phone_number, message, location=None):
    return emergency_detector.handle_emergency(phone_number, message, location)