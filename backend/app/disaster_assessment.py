from typing import Dict, List
from datetime import datetime
from loguru import logger

class DisasterRiskAssessor:
    def __init__(self):
        self.disaster_types = {
            "flood": {
                "thresholds": {"temp": 0, "rain": 50, "wind": 0, "humidity": 70},
                "level_1": 40,
                "level_2": 60,
                "level_3": 80,
                "icon": "🌊",
                "description": "Excessive rainfall causing water accumulation"
            },
            "cyclone": {
                "thresholds": {"temp": 25, "rain": 80, "wind": 120, "humidity": 80},
                "level_1": 50,
                "level_2": 70,
                "level_3": 90,
                "icon": "🌀",
                "description": "Severe storm with high-speed winds"
            },
            "heatwave": {
                "thresholds": {"temp": 40, "rain": 0, "wind": 0, "humidity": 30},
                "level_1": 50,
                "level_2": 70,
                "level_3": 90,
                "icon": "🌡️",
                "description": "Extreme temperatures posing health risks"
            },
            "drought": {
                "thresholds": {"temp": 35, "rain": 5, "wind": 0, "humidity": 20},
                "level_1": 40,
                "level_2": 60,
                "level_3": 80,
                "icon": "☀️",
                "description": "Prolonged period of abnormally low rainfall"
            },
            "storm": {
                "thresholds": {"temp": 20, "rain": 40, "wind": 80, "humidity": 60},
                "level_1": 45,
                "level_2": 65,
                "level_3": 85,
                "icon": "⛈️",
                "description": "Severe weather with strong winds and rain"
            }
        }
        
        self.recommendations = {
            "flood": [
                "🚨 Move to higher ground immediately",
                "📦 Prepare emergency supplies (water, food, medicine)",
                "🔌 Turn off electricity and gas",
                "📱 Keep mobile phones charged",
                "🏠 Do not walk or drive through flood waters",
                "🆘 Call emergency services if needed"
            ],
            "cyclone": [
                "🏃 Evacuate to designated cyclone shelter",
                "🔒 Secure all windows and doors",
                "🌳 Stay away from trees and power lines",
                "📱 Keep emergency contact numbers ready",
                "💊 Take important medicines with you",
                "📻 Keep battery-powered radio for updates"
            ],
            "heatwave": [
                "💧 Drink plenty of water every 20 minutes",
                "🏠 Stay indoors between 12 PM - 4 PM",
                "👕 Wear light-colored, loose clothing",
                "👴 Check on elderly and children",
                "❄️ Use wet towels to cool down",
                "🚫 Avoid strenuous outdoor activities"
            ],
            "drought": [
                "💧 Conserve water - limit daily usage",
                "🌾 Avoid planting water-intensive crops",
                "📊 Monitor water levels regularly",
                "🌿 Use drip irrigation if possible",
                "📱 Report water shortage to authorities",
                "♻️ Implement water recycling methods"
            ],
            "storm": [
                "🏠 Stay indoors and away from windows",
                "🔌 Unplug electronic devices",
                "🌳 Avoid open areas and tall trees",
                "🚗 Do not drive through flooded roads",
                "📱 Keep weather alerts on",
                "🛑 Secure outdoor furniture and objects"
            ]
        }
    
    def assess_risk(self, weather_data: Dict) -> Dict:
        """Assess disaster risks based on weather data"""
        current = weather_data.get("current", {})
        hourly = weather_data.get("hourly", {})
        
        temp = current.get("temperature_2m", 20)
        humidity = current.get("relative_humidity_2m", 60)
        rain = current.get("rain", 0)
        wind = current.get("wind_speed_10m", 0)
        
        # Get future forecast
        future_rain = sum(hourly.get("precipitation", [])[:24]) if hourly else rain
        
        risks = {}
        
        for disaster, config in self.disaster_types.items():
            thresholds = config["thresholds"]
            risk_score = 0
            
            # Temperature factor
            if temp >= thresholds["temp"] and thresholds["temp"] > 0:
                risk_score += 30 * min(1, (temp - thresholds["temp"]) / 10)
            
            # Rain factor
            if future_rain >= thresholds["rain"] and thresholds["rain"] > 0:
                risk_score += 40 * min(1, (future_rain - thresholds["rain"]) / 30)
            
            # Wind factor
            if wind >= thresholds["wind"] and thresholds["wind"] > 0:
                risk_score += 30 * min(1, (wind - thresholds["wind"]) / 40)
            
            # Humidity factor (for flood/cyclone)
            if thresholds.get("humidity", 0) > 0:
                if humidity >= thresholds["humidity"]:
                    risk_score += 10 * min(1, (humidity - thresholds["humidity"]) / 20)
            
            # Ensure risk score is within bounds
            risk_score = min(100, max(0, risk_score))
            
            # Determine risk level
            if risk_score >= config["level_3"]:
                level = "CRITICAL"
            elif risk_score >= config["level_2"]:
                level = "HIGH"
            elif risk_score >= config["level_1"]:
                level = "MODERATE"
            else:
                level = "LOW"
            
            risks[disaster] = {
                "risk_score": round(risk_score, 1),
                "risk_level": level,
                "icon": config["icon"],
                "description": config["description"],
                "evacuation_required": risk_score >= config["level_2"],
                "priority": "HIGH" if risk_score >= config["level_2"] else "NORMAL"
            }
        
        # Find highest risk
        highest_risk = max(risks.items(), key=lambda x: x[1]["risk_score"])
        
        return {
            "disaster_risks": risks,
            "highest_risk": {
                "type": highest_risk[0],
                "icon": highest_risk[1]["icon"],
                "risk_level": highest_risk[1]["risk_level"],
                "risk_score": highest_risk[1]["risk_score"]
            },
            "evacuation_required": highest_risk[1]["evacuation_required"],
            "recommendations": self.generate_recommendations(
                highest_risk[0], 
                risks[highest_risk[0]]
            ),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def generate_recommendations(self, disaster: str, risk: Dict) -> List[str]:
        """Generate actionable recommendations based on disaster type"""
        base_recs = self.recommendations.get(disaster, ["⚠️ Stay safe and monitor updates"])
        
        # Add severity-based recommendations
        if risk["risk_level"] in ["HIGH", "CRITICAL"]:
            base_recs.insert(0, "🔴 IMMEDIATE ACTION REQUIRED")
        
        if risk["evacuation_required"]:
            base_recs.insert(1, "🚨 EVACUATION ADVISORY: Follow local authority instructions")
        
        return base_recs[:6]  # Return top 6 recommendations

disaster_assessor = DisasterRiskAssessor()