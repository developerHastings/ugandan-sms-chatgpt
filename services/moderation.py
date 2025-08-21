class ContentModerator:
    def __init__(self):
        self.blocked_terms = [
            # Add inappropriate terms specific to your context
            "hate_speech_term1", "hate_speech_term2", 
            "explicit_term1", "explicit_term2"
        ]
    
    def moderate(self, text):
        text_lower = text.lower()
        
        # Check for blocked terms
        for term in self.blocked_terms:
            if term in text_lower:
                return False
        
        # Additional moderation checks can be added here
        return True

# Create singleton instance
content_moderator = ContentModerator()

# Convenience function
def moderate_content(text):
    return content_moderator.moderate(text)