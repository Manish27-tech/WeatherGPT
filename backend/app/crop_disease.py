from typing import Dict, List, Tuple
from datetime import datetime, timedelta
import json

class CropDiseasePredictor:
    """
    Predicts crop diseases based on weather conditions
    """
    
    def __init__(self):
        self.disease_models = {
            "late_blight": {
                "name": "Late Blight",
                "icon": "🍅",
                "temp_min": 18,
                "temp_max": 28,
                "humidity_min": 80,
                "rain_min": 2,
                "description": "Potato/Tomato disease caused by Phytophthora infestans",
                "treatment": "Apply fungicide within 24h, remove infected plants"
            },
            "powdery_mildew": {
                "name": "Powdery Mildew",
                "icon": "🌾",
                "temp_min": 20,
                "temp_max": 30,
                "humidity_min": 60,
                "rain_min": 0,
                "description": "Fungal disease affecting cereals, fruits, and vegetables",
                "treatment": "Apply sulfur-based fungicide, improve air circulation"
            },
            "rust": {
                "name": "Wheat Rust",
                "icon": "🌾",
                "temp_min": 15,
                "temp_max": 25,
                "humidity_min": 70,
                "rain_min": 1,
                "description": "Fungal disease causing severe yield loss in wheat",
                "treatment": "Use resistant varieties, apply fungicide early"
            },
            "downy_mildew": {
                "name": "Downy Mildew",
                "icon": "🌿",
                "temp_min": 18,
                "temp_max": 22,
                "humidity_min": 85,
                "rain_min": 3,
                "description": "Water mold affecting grapes, onions, and cucurbits",
                "treatment": "Improve drainage, apply copper-based fungicide"
            },
            "blight": {
                "name": "Bacterial Blight",
                "icon": "🌾",
                "temp_min": 25,
                "temp_max": 35,
                "humidity_min": 75,
                "rain_min": 1,
                "description": "Bacterial disease in rice, cotton, and pulses",
                "treatment": "Use disease-free seeds, apply copper sprays"
            }
        }
    
    def predict_disease(self, weather: Dict) -> Dict:
        """Predict disease risk based on weather conditions"""
        temp = weather.get("temperature", 20)
        humidity = weather.get("humidity", 60)
        rain = weather.get("rain", 0)
        
        disease_risks = []
        
        for disease_id, model in self.disease_models.items():
            risk = self._calculate_risk(model, temp, humidity, rain)
            if risk > 0:
                disease_risks.append({
                    "id": disease_id,
                    "name": model["name"],
                    "icon": model["icon"],
                    "risk": risk,
                    "level": self._risk_level(risk),
                    "description": model["description"],
                    "treatment": model["treatment"],
                    "conditions": {
                        "temperature": f"{model['temp_min']}-{model['temp_max']}°C",
                        "humidity": f"{model['humidity_min']}%+",
                        "rainfall": f"{model['rain_min']}mm+"
                    }
                })
        
        # Sort by risk (highest first)
        disease_risks.sort(key=lambda x: x["risk"], reverse=True)
        
        return {
            "current_weather": {
                "temperature": temp,
                "humidity": humidity,
                "rainfall": rain
            },
            "disease_risks": disease_risks[:3],
            "advisory": self._generate_advisory(disease_risks),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _calculate_risk(self, model: Dict, temp: float, humidity: float, rain: float) -> float:
        """Calculate disease risk score (0-100)"""
        risk = 0
        
        # Temperature factor
        if model["temp_min"] <= temp <= model["temp_max"]:
            risk += 50
        elif temp <= model["temp_min"] + 2:
            risk += 25
        elif temp >= model["temp_max"] - 2:
            risk += 25
        
        # Humidity factor
        if humidity >= model["humidity_min"]:
            risk += 40
        elif humidity >= model["humidity_min"] - 10:
            risk += 20
        
        # Rain factor
        if rain >= model["rain_min"]:
            risk += 10
        
        # Additional factors
        if model["rain_min"] > 0 and rain > model["rain_min"] * 2:
            risk += 10
        if humidity > 90 and temp > 25:
            risk += 10
        
        return min(100, risk)
    
    def _risk_level(self, risk: float) -> str:
        """Convert risk score to level"""
        if risk >= 70:
            return "HIGH"
        elif risk >= 40:
            return "MODERATE"
        else:
            return "LOW"
    
    def _generate_advisory(self, risks: List[Dict]) -> Dict:
        """Generate crop advisory"""
        high_risks = [r for r in risks if r["level"] == "HIGH"]
        moderate_risks = [r for r in risks if r["level"] == "MODERATE"]
        
        advisory = {
            "action_needed": len(high_risks) > 0,
            "severity": "HIGH" if high_risks else "MODERATE" if moderate_risks else "LOW",
            "message": "",
            "actions": []
        }
        
        if high_risks:
            advisory["message"] = f"⚠️ HIGH DISEASE RISK: {', '.join([r['name'] for r in high_risks])}"
            advisory["actions"] = [
                f"Apply preventive fungicide for {r['name']}" for r in high_risks
            ]
        elif moderate_risks:
            advisory["message"] = f"⚡ MODERATE DISEASE RISK: {', '.join([r['name'] for r in moderate_risks])}"
            advisory["actions"] = [
                f"Monitor crops for {r['name']} symptoms" for r in moderate_risks
            ]
        else:
            advisory["message"] = "✅ Low disease risk. Continue regular monitoring."
            advisory["actions"] = ["Regular field inspection recommended"]
        
        return advisory

crop_predictor = CropDiseasePredictor()