from typing import Dict, List
from datetime import datetime

class CropRecommendation:
    def __init__(self):
        self.crop_data = {
            "wheat": {
                "temp_min": 15,
                "temp_max": 25,
                "rainfall_min": 50,
                "rainfall_max": 100,
                "soil_types": ["loam", "clay"],
                "growing_season": ["winter", "spring"],
                "emoji": "🌾",
                "description": "Staple grain, rich in carbohydrates"
            },
            "rice": {
                "temp_min": 20,
                "temp_max": 35,
                "rainfall_min": 150,
                "rainfall_max": 300,
                "soil_types": ["clay", "loamy"],
                "growing_season": ["summer", "monsoon"],
                "emoji": "🍚",
                "description": "Major staple food, requires plenty of water"
            },
            "maize": {
                "temp_min": 20,
                "temp_max": 30,
                "rainfall_min": 60,
                "rainfall_max": 120,
                "soil_types": ["loam", "sandy"],
                "growing_season": ["summer"],
                "emoji": "🌽",
                "description": "Versatile crop for food and feed"
            },
            "cotton": {
                "temp_min": 25,
                "temp_max": 35,
                "rainfall_min": 50,
                "rainfall_max": 80,
                "soil_types": ["black", "alluvial"],
                "growing_season": ["summer", "monsoon"],
                "emoji": "🌿",
                "description": "Cash crop for textile industry"
            },
            "potato": {
                "temp_min": 15,
                "temp_max": 25,
                "rainfall_min": 50,
                "rainfall_max": 100,
                "soil_types": ["loam", "sandy"],
                "growing_season": ["winter"],
                "emoji": "🥔",
                "description": "Staple vegetable, good for temperate regions"
            },
            "tomato": {
                "temp_min": 18,
                "temp_max": 28,
                "rainfall_min": 60,
                "rainfall_max": 100,
                "soil_types": ["loam", "sandy"],
                "growing_season": ["spring", "summer"],
                "emoji": "🍅",
                "description": "Popular vegetable, high demand"
            },
            "sugarcane": {
                "temp_min": 22,
                "temp_max": 32,
                "rainfall_min": 100,
                "rainfall_max": 200,
                "soil_types": ["loam", "clay"],
                "growing_season": ["summer"],
                "emoji": "🌿",
                "description": "Cash crop for sugar production"
            },
            "onion": {
                "temp_min": 15,
                "temp_max": 25,
                "rainfall_min": 40,
                "rainfall_max": 80,
                "soil_types": ["loam", "sandy"],
                "growing_season": ["winter", "spring"],
                "emoji": "🧅",
                "description": "Essential vegetable for cooking"
            }
        }
    
    def recommend_crops(self, weather_data: Dict, soil_type: str = "loam") -> Dict:
        """Recommend best crops based on weather conditions"""
        current = weather_data.get("current", {})
        hourly = weather_data.get("hourly", {})
        
        temp = current.get("temperature_2m", 20)
        humidity = current.get("relative_humidity_2m", 60)
        rain = current.get("rain", 0)
        
        # Get average rainfall from hourly data
        rainfall = sum(hourly.get("precipitation", [])[:24]) if hourly else rain
        
        recommendations = []
        
        for crop, requirements in self.crop_data.items():
            # Calculate match scores
            temp_suitable = requirements["temp_min"] <= temp <= requirements["temp_max"]
            rain_suitable = requirements["rainfall_min"] <= rainfall <= requirements["rainfall_max"]
            soil_suitable = soil_type.lower() in requirements["soil_types"]
            
            # Calculate match percentage
            match_score = 0
            
            if temp_suitable:
                match_score += 40
            else:
                # Partial temperature match
                if requirements["temp_min"] <= temp <= requirements["temp_max"] + 5:
                    match_score += 20
                if requirements["temp_min"] - 5 <= temp <= requirements["temp_max"]:
                    match_score += 10
            
            if rain_suitable:
                match_score += 35
            else:
                # Partial rainfall match
                if rainfall >= requirements["rainfall_min"] * 0.7:
                    match_score += 15
            
            if soil_suitable:
                match_score += 25
            else:
                # Check if soil type is somewhat suitable
                for soil in requirements["soil_types"]:
                    if soil in soil_type or soil_type in soil:
                        match_score += 10
                        break
            
            recommendations.append({
                "crop": crop,
                "match_score": round(match_score, 1),
                "temp_suitable": temp_suitable,
                "rainfall_suitable": rain_suitable,
                "soil_suitable": soil_suitable,
                "emoji": requirements["emoji"],
                "description": requirements["description"],
                "temp_range": f"{requirements['temp_min']}°C - {requirements['temp_max']}°C",
                "rainfall_range": f"{requirements['rainfall_min']}mm - {requirements['rainfall_max']}mm",
                "soil_types": requirements["soil_types"],
                "growing_season": requirements["growing_season"]
            })
        
        # Sort by match score (highest first)
        recommendations.sort(key=lambda x: x["match_score"], reverse=True)
        
        return {
            "current_weather": {
                "temperature": temp,
                "humidity": humidity,
                "rainfall": rainfall,
                "soil_type": soil_type
            },
            "recommendations": recommendations[:3],  # Top 3 recommendations
            "best_match": recommendations[0] if recommendations else None,
            "timestamp": datetime.utcnow().isoformat()
        }

crop_recommender = CropRecommendation()