import httpx
from datetime import datetime
from loguru import logger
from typing import Dict

class LightningDetector:
    def __init__(self):
        self.lightning_api = "https://api.lightningmaps.org/v1/"
        self.thresholds = {
            "low": 30,
            "moderate": 50,
            "high": 70
        }
    
    async def detect_lightning(self, lat: float, lon: float, radius: int = 50) -> Dict:
        """Detect lightning risk based on weather conditions"""
        try:
            # For demo, calculate risk from weather data
            weather = await self._get_weather(lat, lon)
            current = weather.get("current", {})
            temp = current.get("temperature_2m", 0)
            humidity = current.get("relative_humidity_2m", 0)
            rain = current.get("rain", 0)
            wind = current.get("wind_speed_10m", 0)
            weather_code = current.get("weather_code", 0)
            
            # Calculate lightning risk
            lightning_risk = 0
            
            # Thunderstorm weather code (95-99)
            if 95 <= weather_code <= 99:
                lightning_risk = 90
            
            # Temperature factor
            if temp > 25:
                lightning_risk += (temp - 25) * 2
            
            # Humidity factor
            if humidity > 60:
                lightning_risk += (humidity - 60) * 1.5
            
            # Rain factor
            if rain > 1:
                lightning_risk += rain * 5
            
            # Wind factor (strong winds can indicate storms)
            if wind > 30:
                lightning_risk += 10
            
            # Cap at 100
            lightning_risk = min(100, max(0, lightning_risk))
            
            # Determine risk level
            if lightning_risk >= 70:
                level = "HIGH"
                color = "#ff6b6b"
                message = "⚠️ HIGH LIGHTNING RISK! Seek shelter immediately."
            elif lightning_risk >= 40:
                level = "MODERATE"
                color = "#ffd93d"
                message = "⚡ Moderate lightning risk. Stay alert."
            else:
                level = "LOW"
                color = "#4ecdc4"
                message = "✅ Low lightning risk."
            
            return {
                "lightning_risk": round(lightning_risk, 1),
                "risk_level": level,
                "color": color,
                "message": message,
                "radius": radius,
                "warning": lightning_risk > 50,
                "factors": {
                    "temperature": temp,
                    "humidity": humidity,
                    "rainfall": rain,
                    "wind_speed": wind,
                    "weather_code": weather_code
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Lightning detection failed: {e}")
            return {
                "lightning_risk": 0,
                "warning": False,
                "error": str(e)
            }
    
    async def _get_weather(self, lat: float, lon: float):
        """Get weather data for lightning detection"""
        from .weather import get_weather
        return await get_weather(lat, lon)

lightning_detector = LightningDetector()