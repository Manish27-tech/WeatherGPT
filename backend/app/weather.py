import httpx
import json
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from loguru import logger

from .config import settings
from .cache import cache_manager

class WeatherService:
    def __init__(self):
        self.cache_ttl = getattr(settings, 'cache_ttl', 300)

    async def get_weather(self, latitude: float, longitude: float, force_refresh: bool = False) -> dict:
        """Get weather data with caching and analytics"""
        cache_key = f"weather:{latitude:.4f}:{longitude:.4f}"
        
        if not force_refresh:
            cached = cache_manager.get(cache_key)
            if cached:
                logger.info(f"✅ Cache hit for {latitude}, {longitude}")
                return cached
        
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": ",".join([
                "temperature_2m", "relative_humidity_2m", "precipitation",
                "rain", "weather_code", "wind_speed_10m", "wind_gusts_10m"
            ]),
            "hourly": ",".join([
                "temperature_2m", "relative_humidity_2m", "precipitation_probability",
                "precipitation", "wind_speed_10m", "wind_gusts_10m", "weather_code"
            ]),
            "daily": ",".join([
                "temperature_2m_max", "temperature_2m_min",
                "precipitation_probability_max", "precipitation_sum",
                "wind_speed_10m_max"
            ]),
            "forecast_days": 3,
            "timezone": "auto",
        }
        
        async with httpx.AsyncClient(timeout=15) as client:
            try:
                r = await client.get(settings.open_meteo_url, params=params)
                r.raise_for_status()
                data = r.json()
                
                # Add derived metrics (trend, heat index, comfort, etc.)
                data = self._add_derived_metrics(data)
                
                # Cache the result
                cache_manager.set(cache_key, data, ttl=self.cache_ttl)
                logger.info(f"💾 Cached weather for {latitude}, {longitude}")
                return data
                
            except httpx.HTTPStatusError as e:
                logger.error(f"❌ Open-Meteo API error: {e}")
                raise
            except Exception as e:
                logger.error(f"❌ Weather fetch error: {e}")
                raise

    def _add_derived_metrics(self, data: dict) -> dict:
        """Add derived metrics like trend, heat index, comfort, etc."""
        current = data.get("current", {})
        hourly = data.get("hourly", {})
        derived = {}
        
        # --- Temperature Trend ---
        temps = hourly.get("temperature_2m", [])[:24]
        if len(temps) >= 3:
            derived["trend"] = self._calculate_trend(temps)
            derived["volatility"] = self._calculate_volatility(temps)
        else:
            derived["trend"] = "stable"
            derived["volatility"] = 0.0
        
        # --- Heat Index ---
        temp = current.get("temperature_2m", 0)
        humidity = current.get("relative_humidity_2m", 0)
        derived["heat_index"] = self._calculate_heat_index(temp, humidity)
        
        # --- Comfort Index ---
        derived["comfort_index"] = self._calculate_comfort_index(temp, humidity)
        
        # --- Risk Factors ---
        derived["risk_factors"] = self._analyze_risk_factors(data)
        
        data["derived"] = derived
        return data

    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate temperature trend (rising/falling/stable)"""
        if len(values) < 3:
            return "stable"
        
        recent_avg = np.mean(values[:6]) if len(values) >= 6 else np.mean(values[:3])
        older_avg = np.mean(values[6:12]) if len(values) >= 12 else np.mean(values[3:6])
        diff = recent_avg - older_avg
        
        if diff > 2:
            return "rising"
        elif diff < -2:
            return "falling"
        return "stable"

    def _calculate_volatility(self, values: List[float]) -> float:
        """Calculate temperature volatility (standard deviation)"""
        if len(values) < 2:
            return 0.0
        return float(np.std(values[:24]) if len(values) >= 24 else np.std(values))

    def _calculate_heat_index(self, temp: float, humidity: float) -> Optional[float]:
        """Calculate heat index (simplified)"""
        if temp < 27 or humidity < 40:
            return None
        hi = temp + 0.5 * (humidity - 40)
        return round(hi, 1)

    def _calculate_comfort_index(self, temp: float, humidity: float) -> str:
        """Calculate comfort level"""
        if 18 <= temp <= 25 and 40 <= humidity <= 60:
            return "comfortable"
        elif (temp > 30) or (humidity > 70):
            return "uncomfortable"
        return "moderate"

    def _analyze_risk_factors(self, data: dict) -> List[dict]:
        """Analyze multiple risk factors (heat, wind, rain)"""
        current = data.get("current", {})
        risks = []
        
        temp = current.get("temperature_2m", 0)
        if temp > 35:
            risks.append({"type": "heat", "level": "high", "value": temp})
        elif temp > 30:
            risks.append({"type": "heat", "level": "moderate", "value": temp})
        
        wind = current.get("wind_speed_10m", 0)
        if wind > 50:
            risks.append({"type": "wind", "level": "high", "value": wind})
        elif wind > 35:
            risks.append({"type": "wind", "level": "moderate", "value": wind})
        
        rain = current.get("rain", 0)
        if rain > 5:
            risks.append({"type": "rain", "level": "high", "value": rain})
        elif rain > 2:
            risks.append({"type": "rain", "level": "moderate", "value": rain})
        
        return risks


# Global instance
weather_service = WeatherService()

# Public API functions
async def get_weather(latitude: float, longitude: float, force_refresh: bool = False) -> dict:
    """Public function to get weather data"""
    return await weather_service.get_weather(latitude, longitude, force_refresh)

async def geocode_city(name: str) -> list[dict]:
    """Geocode city name to coordinates"""
    params = {"name": name, "count": 5, "language": "en", "format": "json"}
    async with httpx.AsyncClient(timeout=10) as client:
        try:
            r = await client.get(settings.open_meteo_geocoding_url, params=params)
            r.raise_for_status()
            return r.json().get("results", [])
        except Exception as e:
            logger.error(f"❌ Geocoding error: {e}")
            return []