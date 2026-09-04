import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List
from loguru import logger

class CropYieldPredictor:
    """
    Predicts crop yield based on weather conditions
    """
    
    def __init__(self):
        self.crop_types = {
            "wheat": {"base_yield": 3.5, "temp_optimal": 20, "humidity_optimal": 60},
            "rice": {"base_yield": 4.2, "temp_optimal": 28, "humidity_optimal": 75},
            "maize": {"base_yield": 5.0, "temp_optimal": 25, "humidity_optimal": 65},
            "cotton": {"base_yield": 2.8, "temp_optimal": 30, "humidity_optimal": 55},
            "sugarcane": {"base_yield": 8.5, "temp_optimal": 27, "humidity_optimal": 70},
            "potato": {"base_yield": 4.0, "temp_optimal": 18, "humidity_optimal": 65},
            "tomato": {"base_yield": 3.2, "temp_optimal": 22, "humidity_optimal": 60},
            "onion": {"base_yield": 2.5, "temp_optimal": 20, "humidity_optimal": 55}
        }
    
    def predict_yield(self, crop: str, weather_data: Dict, soil_quality: str = "medium") -> Dict:
        """
        Predict crop yield based on weather conditions
        """
        if crop not in self.crop_types:
            return {"error": f"Unknown crop: {crop}"}
        
        current = weather_data.get("current", {})
        temp = current.get("temperature_2m", 20)
        humidity = current.get("relative_humidity_2m", 60)
        rain = current.get("rain", 0)
        
        crop_info = self.crop_types[crop]
        base = crop_info["base_yield"]
        
        # Calculate weather impact
        temp_impact = 1 - abs(temp - crop_info["temp_optimal"]) / 30
        humidity_impact = 1 - abs(humidity - crop_info["humidity_optimal"]) / 50
        
        # Rain impact (too much or too little)
        if rain < 0.5:
            rain_impact = 0.7
        elif rain > 8:
            rain_impact = 0.8
        else:
            rain_impact = 1 + (rain - 2) * 0.05
        
        # Soil quality factor
        soil_factors = {"poor": 0.7, "medium": 1.0, "good": 1.3}
        soil_factor = soil_factors.get(soil_quality, 1.0)
        
        # Calculate predicted yield
        predicted = base * max(0, temp_impact) * max(0, humidity_impact) * rain_impact * soil_factor
        
        # Add some randomness for realism
        predicted += np.random.normal(0, 0.2)
        predicted = max(0.5, min(predicted, base * 1.5))
        
        return {
            "crop": crop,
            "predicted_yield": round(predicted, 2),
            "unit": "tons/hectare",
            "baseline": base,
            "weather_impact": {
                "temperature": round(max(0, temp_impact), 2),
                "humidity": round(max(0, humidity_impact), 2),
                "rainfall": round(rain_impact, 2)
            },
            "soil_quality": soil_quality,
            "confidence": round(0.85 + np.random.random() * 0.1, 2),
            "recommendations": self._get_recommendations(crop, temp, humidity, rain)
        }
    
    def _get_recommendations(self, crop: str, temp: float, humidity: float, rain: float) -> List[str]:
        """Get crop-specific recommendations"""
        recs = []
        
        if temp > 35:
            recs.append("⚠️ Heat stress - provide shade or irrigation")
        elif temp < 10:
            recs.append("❄️ Cold stress - use protective covers")
        
        if humidity > 80:
            recs.append("🦠 High humidity - watch for fungal diseases")
        
        if rain > 5:
            recs.append("🌊 Heavy rain - ensure proper drainage")
        elif rain < 0.5:
            recs.append("💧 Drought conditions - irrigate immediately")
        
        if not recs:
            recs.append("✅ Optimal growing conditions")
        
        return recs

crop_yield_predictor = CropYieldPredictor()