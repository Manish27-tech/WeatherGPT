import httpx
import math
from datetime import datetime
from typing import Dict, List, Optional
from loguru import logger

class WeatherComparison:
    """
    Advanced Multi-City Weather Comparison
    - Compare up to 5 cities
    - Statistical analysis
    - Difference metrics
    - Best time to visit recommendations
    """
    
    def __init__(self):
        self.max_cities = 5
    
    async def compare_cities(self, cities: List[Dict]) -> Dict:
        """
        Compare weather across multiple cities
        """
        try:
            results = []
            
            for city in cities:
                weather_data = await self._get_city_weather(
                    city["latitude"], 
                    city["longitude"]
                )
                
                if weather_data:
                    results.append({
                        "name": city.get("name", f"{city['latitude']}, {city['longitude']}"),
                        "latitude": city["latitude"],
                        "longitude": city["longitude"],
                        "weather": weather_data,
                        "metrics": self._calculate_metrics(weather_data)
                    })
            
            # Perform comparative analysis
            comparison = self._perform_comparison(results)
            
            return {
                "status": "success",
                "cities_compared": len(results),
                "results": results,
                "comparison": comparison,
                "insights": self._generate_insights(results, comparison),
                "visualization_data": self._generate_visualization_data(results),
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Weather comparison failed: {e}")
            return {
                "status": "error",
                "error": "Comparison failed",
                "message": str(e)
            }
    
    async def _get_city_weather(self, lat: float, lon: float) -> Optional[Dict]:
        """Get weather for a city"""
        try:
            from .weather import get_weather
            weather = await get_weather(lat, lon)
            current = weather.get("current", {})
            
            return {
                "temperature": current.get("temperature_2m", 0),
                "humidity": current.get("relative_humidity_2m", 0),
                "rainfall": current.get("rain", 0),
                "wind": current.get("wind_speed_10m", 0),
                "weather_code": current.get("weather_code", 0),
                "pressure": current.get("pressure_msl", 1013),
                "visibility": current.get("visibility", 10),
                "uv_index": current.get("uv_index", 5)
            }
        except Exception as e:
            logger.error(f"Failed to get weather for {lat}, {lon}: {e}")
            return None
    
    def _calculate_metrics(self, weather: Dict) -> Dict:
        """Calculate weather metrics"""
        temp = weather.get("temperature", 0)
        humidity = weather.get("humidity", 0)
        wind = weather.get("wind", 0)
        
        # Comfort Index (0-100)
        comfort = 100 - abs(temp - 22) * 3 - max(0, humidity - 60) * 0.5 - wind * 0.5
        comfort = max(0, min(100, comfort))
        
        # Weather Score (0-100)
        weather_score = 100
        if temp > 35 or temp < 10:
            weather_score -= 20
        if humidity > 80:
            weather_score -= 10
        if wind > 30:
            weather_score -= 10
        if weather.get("rainfall", 0) > 2:
            weather_score -= 15
        
        return {
            "comfort_index": round(comfort, 1),
            "weather_score": round(max(0, min(100, weather_score)), 1),
            "heat_index": self._calculate_heat_index(temp, humidity),
            "feels_like": self._calculate_feels_like(temp, humidity, wind)
        }
    
    def _calculate_heat_index(self, temp: float, humidity: float) -> float:
        """Calculate heat index"""
        if temp < 27:
            return temp
        
        hi = temp + 0.5 * (humidity - 40)
        return round(hi, 1)
    
    def _calculate_feels_like(self, temp: float, humidity: float, wind: float) -> float:
        """Calculate feels like temperature"""
        feels = temp
        
        # Humidity adjustment
        if humidity > 60:
            feels += (humidity - 60) * 0.1
        
        # Wind chill (if cold)
        if temp < 10 and wind > 5:
            feels -= (wind - 5) * 0.3
        
        return round(feels, 1)
    
    def _perform_comparison(self, results: List[Dict]) -> Dict:
        """Perform comparative analysis"""
        if len(results) < 2:
            return {"message": "Need at least 2 cities for comparison"}
        
        temps = [r["weather"]["temperature"] for r in results]
        humidities = [r["weather"]["humidity"] for r in results]
        winds = [r["weather"]["wind"] for r in results]
        scores = [r["metrics"]["weather_score"] for r in results]
        
        return {
            "statistics": {
                "temperature": {
                    "highest": max(temps),
                    "lowest": min(temps),
                    "average": round(sum(temps) / len(temps), 1),
                    "difference": round(max(temps) - min(temps), 1)
                },
                "humidity": {
                    "highest": max(humidities),
                    "lowest": min(humidities),
                    "average": round(sum(humidities) / len(humidities), 1)
                },
                "wind": {
                    "highest": max(winds),
                    "lowest": min(winds),
                    "average": round(sum(winds) / len(winds), 1)
                },
                "weather_score": {
                    "best": max(scores),
                    "worst": min(scores),
                    "average": round(sum(scores) / len(scores), 1)
                }
            },
            "ranking": {
                "best_weather": results[scores.index(max(scores))]["name"],
                "worst_weather": results[scores.index(min(scores))]["name"],
                "most_extreme": results[temps.index(max(temps))]["name"] if max(temps) - min(temps) > 5 else None
            }
        }
    
    def _generate_insights(self, results: List[Dict], comparison: Dict) -> List[str]:
        """Generate actionable insights"""
        insights = []
        
        if len(results) < 2:
            return ["Add more cities for comparison insights"]
        
        # Best weather recommendation
        best = comparison.get("ranking", {}).get("best_weather")
        if best:
            insights.append(f"🏆 Best weather: {best}")
        
        # Temperature insight
        stats = comparison.get("statistics", {})
        if stats.get("temperature", {}).get("difference", 0) > 10:
            insights.append("🌡️ Large temperature variation between cities")
        
        # Humidity insight
        if stats.get("humidity", {}).get("difference", 0) > 30:
            insights.append("💧 Significant humidity differences - plan accordingly")
        
        # Worst weather
        worst = comparison.get("ranking", {}).get("worst_weather")
        if worst:
            insights.append(f"⚠️ Consider avoiding: {worst}")
        
        return insights
    
    def _generate_visualization_data(self, results: List[Dict]) -> Dict:
        """Generate data for visualization"""
        return {
            "labels": [r["name"] for r in results],
            "datasets": {
                "temperature": [r["weather"]["temperature"] for r in results],
                "humidity": [r["weather"]["humidity"] for r in results],
                "wind": [r["weather"]["wind"] for r in results],
                "score": [r["metrics"]["weather_score"] for r in results]
            }
        }

weather_comparison = WeatherComparison()