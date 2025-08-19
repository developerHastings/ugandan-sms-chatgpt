class MenuSystem:
    def __init__(self):
        self.user_states = {}  # Track user menu states
    
    def handle(self, phone_number, message):
        message = message.strip().lower()
        
        # Get current user state
        current_state = self.user_states.get(phone_number, "main")
        
        # Handle based on state
        if message == "0":
            self.user_states[phone_number] = "main"
            return self.get_main_menu()
        
        elif current_state == "main":
            return self.handle_main_menu(phone_number, message)
        
        elif current_state == "health":
            return self.handle_health_menu(phone_number, message)
        
        elif current_state == "agriculture":
            return self.handle_agriculture_menu(phone_number, message)
        
        return None  # Not a menu command
    
    def get_main_menu(self):
        return (
            "📱 Main Menu:\n"
            "1. Health Information\n"
            "2. Agriculture Advice\n"
            "3. Education Resources\n"
            "4. Emergency Services\n"
            "5. Give Feedback\n"
            "\nSend 0 anytime to return to main menu"
        )
    
    def handle_main_menu(self, phone_number, message):
        if message == "1":
            self.user_states[phone_number] = "health"
            return (
                "🏥 Health Services:\n"
                "1. Disease Information\n"
                "2. Hospital Locations\n"
                "3. Medication Advice\n"
                "4. Emergency Contacts"
            )
        
        elif message == "2":
            self.user_states[phone_number] = "agriculture"
            return (
                "🌱 Agriculture Advice:\n"
                "1. Crop Farming\n"
                "2. Livestock\n"
                "3. Weather Information\n"
                "4. Market Prices"
            )
        
        elif message == "4":
            return "🚨 Emergency numbers: Police-999, Ambulance-911, Fire-112"
        
        elif message == "5":
            return "💬 Please share your feedback about this service"
        
        return None
    
    def handle_health_menu(self, phone_number, message):
        if message == "1":
            return "Please describe the symptoms you're concerned about"
        elif message == "2":
            return "Please share your location to find nearby hospitals"
        return "Invalid option. Send 0 to return to main menu"
    
    def handle_agriculture_menu(self, phone_number, message):
        if message == "1":
            return "Which crop are you interested in? (coffee, bananas, maize, etc.)"
        elif message == "2":
            return "Which livestock are you interested in? (cows, goats, chickens, etc.)"
        return "Invalid option. Send 0 to return to main menu"

# Create singleton instance
menu_system = MenuSystem()