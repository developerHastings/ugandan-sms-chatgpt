import json
import os

class LocalKnowledge:
    def __init__(self, knowledge_file="data/uganda_knowledge.json"):
        self.knowledge_file = knowledge_file
        self.knowledge = self._load_knowledge()
    
    def _load_knowledge(self):
        if os.path.exists(self.knowledge_file):
            with open(self.knowledge_file, 'r') as f:
                return json.load(f)
        return {
            "health_centers": {
                "kampala": ["Mulago Hospital", "Case Clinic", "Nakasero Hospital"],
                "entebbe": ["Entebbe Hospital", "Victoria Medical Center"]
            },
            "emergency_numbers": {
                "police": "999",
                "ambulance": "911",
                "fire": "112"
            },
            "agriculture_tips": {
                "coffee": "Plant coffee in well-drained soil with partial shade",
                "bananas": "Matooke requires regular watering and fertile soil"
            }
        }
    
    def enhance(self, query, response):
        query_lower = query.lower()
        
        if any(term in query_lower for term in ["hospital", "clinic", "health center"]):
            return response + f"\n\n🏥 Nearby hospitals: {', '.join(self.knowledge['health_centers']['kampala'])}"
        
        elif "emergency" in query_lower:
            numbers = self.knowledge['emergency_numbers']
            return response + f"\n\n🚨 Emergency numbers: Police-{numbers['police']}, Ambulance-{numbers['ambulance']}, Fire-{numbers['fire']}"
        
        elif any(term in query_lower for term in ["crop", "farming", "agriculture"]):
            # Add relevant farming tips
            tips = []
            for crop, tip in self.knowledge['agriculture_tips'].items():
                if crop in query_lower:
                    tips.append(f"{crop.capitalize()}: {tip}")
            
            if tips:
                return response + f"\n\n🌱 Farming tips:\n" + "\n".join(tips)
        
        return response

# Create singleton instance
local_knowledge = LocalKnowledge()