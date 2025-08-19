import json
import os

class LanguageDetection:
    def __init__(self, keywords_file="data/language_keywords.json"):
        self.keywords_file = keywords_file
        self.keywords = self._load_keywords()
    
    def _load_keywords(self):
        if os.path.exists(self.keywords_file):
            with open(self.keywords_file, 'r') as f:
                return json.load(f)
        return {
            "english": ["hello", "hi", "how are you", "what is", "tell me"],
            "luganda": ["mweraba", "gyebale", "nsanyuse", "oli otya", "webale"],
            "swahili": ["jambo", "habari", "asante", "sawa", "mambo"],
            "acholi": ["apwoyo", "itet", "ngo", "dyango", "aber"]
        }
    
    def detect(self, text):
        text_lower = text.lower()
        scores = {lang: 0 for lang in self.keywords}
        
        for lang, words in self.keywords.items():
            for word in words:
                if word in text_lower:
                    scores[lang] += 1
        
        # Return language with highest score, default to English
        return max(scores, key=scores.get, default="english")

# Create singleton instance
language_detection = LanguageDetection()