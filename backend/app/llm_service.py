import os
import json
from typing import Dict, List, Any
from loguru import logger
from datetime import datetime, timedelta

# Try importing Groq
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    logger.warning("⚠️ Groq not installed. Run: pip install groq")

class LLMService:
    def __init__(self):
        # Load environment variables
        from dotenv import load_dotenv
        load_dotenv()
        
        self.groq_api_key = os.getenv("GROQ_API_KEY", "")
        self.enabled = False
        self.provider = None
        self.client = None
        
        if self.groq_api_key:
            logger.info(f"✅ Found GROQ_API_KEY: {self.groq_api_key[:15]}...")
        else:
            logger.warning("❌ No GROQ_API_KEY found")
        
        # Try to initialize Groq
        if self.groq_api_key and self.groq_api_key.startswith("gsk_"):
            try:
                if GROQ_AVAILABLE:
                    self.client = Groq(api_key=self.groq_api_key)
                    self.enabled = True
                    self.provider = "groq"
                    logger.info("🚀 Groq LLM initialized successfully!")
                    self._test_connection()
                else:
                    logger.warning("⚠️ Groq library not installed")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Groq: {e}")
        
        if not self.enabled:
            logger.warning("⚠️ Using advanced rule-based fallback.")
    
    def _test_connection(self):
        """Test Groq connection with an available model"""
        try:
            test_response = self.client.chat.completions.create(
                messages=[{"role": "user", "content": "Hello"}],
                model="qwen/qwen3.8-27b",
                max_tokens=10,
            )
            logger.info("✅ Groq connection test successful!")
        except Exception as e:
            logger.warning(f"⚠️ Groq test failed: {e}")
    
    def generate_weather_response(self, question: str, weather_data: Dict, role: str) -> Dict:
        """Generate a context-aware response using available LLM"""
        if self.enabled and self.provider == "groq":
            return self._generate_with_groq(question, weather_data, role)
        else:
            return self._generate_fallback_response(question, weather_data, role)
    
    def _generate_with_groq(self, question: str, weather_data: Dict, role: str) -> Dict:
        """Generate response using Groq's LLM with available models"""
        try:
            # Extract ALL weather data
            current = weather_data.get("current", {})
            hourly = weather_data.get("hourly", {})
            daily = weather_data.get("daily", {})
            
            # Current weather
            temp = current.get("temperature_2m", "N/A")
            humidity = current.get("relative_humidity_2m", "N/A")
            rain = current.get("rain", 0)
            wind = current.get("wind_speed_10m", "N/A")
            weather_code = current.get("weather_code", 0)
            
            # Extract hourly forecast for next 24 hours
            hourly_times = hourly.get("time", [])[:24]
            hourly_temps = hourly.get("temperature_2m", [])[:24]
            hourly_rain = hourly.get("precipitation", [])[:24]
            hourly_humidity = hourly.get("relative_humidity_2m", [])[:24]
            hourly_wind = hourly.get("wind_speed_10m", [])[:24]
            
            # Extract daily forecast
            daily_temps_max = daily.get("temperature_2m_max", [])
            daily_temps_min = daily.get("temperature_2m_min", [])
            daily_rain = daily.get("precipitation_sum", [])
            daily_rain_prob = daily.get("precipitation_probability_max", [])
            
            # Build forecast summary
            forecast_summary = self._build_forecast_summary(
                hourly_times, hourly_temps, hourly_rain, hourly_humidity, hourly_wind
            )
            
            # Build daily forecast
            daily_forecast = self._build_daily_forecast(
                daily_temps_max, daily_temps_min, daily_rain, daily_rain_prob
            )
            
            # Build the prompt with FULL weather data
            prompt = f"""You are WeatherGPT, a specialized weather assistant for farmers, travelers, and urban users.

CURRENT WEATHER:
- Temperature: {temp}°C
- Humidity: {humidity}%
- Rainfall: {rain}mm
- Wind Speed: {wind} km/h
- Weather Code: {weather_code}

HOURLY FORECAST (Next 12 Hours):
{forecast_summary}

DAILY FORECAST (Next 3 Days):
{daily_forecast}

User Role: {role}
User Question: {question}

Based on the weather data and forecast provided, give a specific, actionable response.
- If the question asks about future weather (tomorrow, next few hours), use the forecast data.
- Include specific timings if rain is expected.
- Provide practical recommendations.
- Keep response concise and helpful (2-4 sentences).
"""
            
            logger.info("Calling Groq API with forecast data...")
            
            # Use best English models
            models_to_try = [
                "qwen/qwen3.8-27b",
                "qwen/qwen3.6-27b",
                "groq/compound",
                "openai/gpt-oss-20b",
            ]
            
            for model in models_to_try:
                try:
                    chat_completion = self.client.chat.completions.create(
                        messages=[
                            {"role": "system", "content": "You are a helpful weather assistant. Always respond in English based on the provided data."},
                            {"role": "user", "content": prompt}
                        ],
                        model=model,
                        temperature=0.7,
                        max_tokens=400,
                    )
                    
                    answer = chat_completion.choices[0].message.content.strip()
                    logger.info(f"✅ Groq response with {model}")
                    
                    # Calculate risk
                    risk = self._calculate_risk(weather_data)
                    actions = self._extract_actions(weather_data, role)
                    
                    return {
                        "answer": answer,
                        "evidence": [
                            f"🌡️ Current Temperature: {temp}°C",
                            f"💧 Current Humidity: {humidity}%",
                            f"🌧️ Current Rainfall: {rain}mm",
                            f"💨 Wind: {wind} km/h",
                        ],
                        "actions": actions,
                        "risk": risk,
                        "confidence": "High - Generated by Groq AI with forecast data",
                        "source": f"WeatherGPT + Groq ({model})",
                        "llm_used": True,
                        "provider": "groq",
                    }
                    
                except Exception as e:
                    logger.warning(f"❌ Model {model} failed: {e}")
                    continue
            
            # If all models fail
            return self._generate_fallback_response(question, weather_data, role)
            
        except Exception as e:
            logger.error(f"Groq generation failed: {e}")
            return self._generate_fallback_response(question, weather_data, role)
    
    def _build_forecast_summary(self, times: List[str], temps: List[float], 
                                 rain: List[float], humidity: List[float], 
                                 wind: List[float]) -> str:
        """Build a readable forecast summary for next 12 hours"""
        if not times or len(times) < 6:
            return "No detailed forecast available."
        
        summary = []
        rain_hours = []
        
        # Show next 12 hours
        for i in range(min(12, len(times))):
            try:
                hour = datetime.fromisoformat(times[i]).hour
                temp_val = temps[i] if i < len(temps) else "N/A"
                rain_val = rain[i] if i < len(rain) else 0
                
                # Track rain hours
                if rain_val > 0.5:
                    rain_hours.append(f"{hour}:00 ({rain_val}mm)")
                
                if rain_val > 0.5:
                    summary.append(f"  • Hour {hour}:00 → 🌧️ {rain_val}mm rain, {temp_val}°C")
                else:
                    summary.append(f"  • Hour {hour}:00 → ☀️ {temp_val}°C, no rain")
            except:
                continue
        
        if not summary:
            return "No forecast data available."
        
        result = "\n".join(summary)
        
        # Add rain summary
        if rain_hours:
            result += f"\n\n⚠️ RAIN ALERT: Expected at {', '.join(rain_hours[:5])}"
        else:
            result += "\n\n☀️ No significant rain expected in the next 12 hours."
        
        return result
    
    def _build_daily_forecast(self, max_temps: List[float], min_temps: List[float], 
                               rain: List[float], rain_prob: List[float]) -> str:
        """Build daily forecast summary"""
        if not max_temps:
            return "No daily forecast available."
        
        days = ["Today", "Tomorrow", "Day after tomorrow"]
        result = []
        
        for i in range(min(3, len(max_temps))):
            day_name = days[i] if i < len(days) else f"Day {i+1}"
            max_t = max_temps[i] if i < len(max_temps) else "N/A"
            min_t = min_temps[i] if i < len(min_temps) else "N/A"
            rain_amt = rain[i] if i < len(rain) else 0
            prob = rain_prob[i] if i < len(rain_prob) else 0
            
            rain_emoji = "🌧️" if rain_amt > 5 else "☀️" if rain_amt < 0.5 else "🌤️"
            result.append(f"  • {day_name}: {rain_emoji} Max {max_t}°C / Min {min_t}°C, Rain {rain_amt}mm ({prob}% chance)")
        
        return "\n".join(result) if result else "No daily forecast available."
    
    def _get_weather_description(self, code: int) -> str:
        """Get weather description from code"""
        weather_codes = {
            0: "Clear sky ☀️",
            1: "Mainly clear 🌤️",
            2: "Partly cloudy ⛅",
            3: "Overcast ☁️",
            45: "Fog 🌫️",
            48: "Depositing rime fog 🌫️",
            51: "Light drizzle 🌦️",
            53: "Moderate drizzle 🌧️",
            55: "Dense drizzle 🌧️",
            61: "Slight rain 🌧️",
            63: "Moderate rain 🌧️",
            65: "Heavy rain 🌧️",
            71: "Slight snow ❄️",
            73: "Moderate snow ❄️",
            75: "Heavy snow ❄️",
            80: "Rain showers 🌧️",
            81: "Moderate rain showers 🌧️",
            82: "Violent rain showers ⛈️",
            95: "Thunderstorm ⛈️",
            96: "Thunderstorm with hail ⛈️",
            99: "Heavy thunderstorm with hail ⛈️"
        }
        return weather_codes.get(code, "Unknown")
    
    def _extract_actions(self, weather_data: Dict, role: str) -> List[str]:
        """Extract actions based on weather data"""
        current = weather_data.get("current", {})
        temp = current.get("temperature_2m", 0)
        humidity = current.get("relative_humidity_2m", 0)
        rain = current.get("rain", 0)
        wind = current.get("wind_speed_10m", 0)
        
        actions = []
        
        if temp > 35:
            actions.append("🌡️ Stay hydrated and avoid direct sunlight")
        if temp < 10:
            actions.append("🧥 Dress warmly and limit outdoor exposure")
        if humidity > 80:
            actions.append("💨 Use ventilation and stay in cool areas")
        if rain > 5:
            actions.append("🌧️ Avoid flooded areas and carry rain gear")
        if wind > 40:
            actions.append("💨 Secure loose objects and stay indoors")
        
        if role == "farmer":
            if rain < 1:
                actions.append("🌾 Favorable for irrigation and field work")
            if humidity > 70:
                actions.append("🌾 Monitor for fungal diseases")
            if temp > 30:
                actions.append("🌾 Irrigate early morning or late evening")
        
        elif role == "traveler":
            if rain > 1:
                actions.append("🧳 Carry rain protection")
            if wind > 30:
                actions.append("✈️ Check for travel disruptions")
        
        elif role == "disaster":
            if rain > 5 or wind > 40:
                actions.append("🚨 Prepare emergency supplies and evacuation plan")
        
        elif role == "urban":
            if rain > 1:
                actions.append("🚗 Expect traffic delays")
        
        return actions if actions else ["✅ No immediate actions required"]
    
    def _calculate_risk(self, weather_data: Dict) -> str:
        """Calculate risk level from weather data"""
        current = weather_data.get("current", {})
        temp = current.get("temperature_2m", 0)
        rain = current.get("rain", 0)
        wind = current.get("wind_speed_10m", 0)
        weather_code = current.get("weather_code", 0)
        
        if weather_code in [95, 96, 99]:
            return "HIGH"
        if temp > 38 or rain > 10 or wind > 50:
            return "HIGH"
        elif temp > 32 or rain > 3 or wind > 35:
            return "MODERATE"
        return "LOW"
    
    def _generate_fallback_response(self, question: str, weather_data: Dict, role: str) -> Dict:
        """Advanced rule-based fallback response"""
        current = weather_data.get("current", {})
        hourly = weather_data.get("hourly", {})
        
        temp = current.get("temperature_2m", 0)
        humidity = current.get("relative_humidity_2m", 0)
        rain = current.get("rain", 0)
        wind = current.get("wind_speed_10m", 0)
        
        # Check if question is about future rain
        question_lower = question.lower()
        is_future = any(w in question_lower for w in ["tomorrow", "next", "future", "later", "today", "hours", "week"])
        is_rain = any(w in question_lower for w in ["rain", "rainfall", "precipitation", "wet"])
        
        answer_parts = []
        actions = []
        risk = "LOW"
        
        # If asking about rain in future - use hourly data
        if is_rain and is_future:
            times = hourly.get("time", [])
            rains = hourly.get("precipitation", [])
            
            # Find rain in next 24 hours
            rain_times = []
            for i in range(min(24, len(times))):
                if rains and i < len(rains) and rains[i] and rains[i] > 0.5:
                    try:
                        hour = datetime.fromisoformat(times[i]).hour
                        rain_times.append(f"{hour}:00 ({rains[i]}mm)")
                    except:
                        pass
            
            if rain_times:
                answer_parts.append(f"🌧️ Rain expected at: {', '.join(rain_times[:6])}")
                actions.append("Carry umbrella during these hours")
                risk = "MODERATE"
            else:
                answer_parts.append("☀️ No significant rain expected in the next 24 hours.")
                risk = "LOW"
        
        # General weather description
        if not answer_parts:
            answer_parts.append(f"🌤️ Current: {temp}°C, {humidity}% humidity")
            if rain > 0:
                answer_parts.append(f"🌧️ {rain}mm rain")
            if wind > 10:
                answer_parts.append(f"💨 {wind} km/h wind")
        
        full_answer = " ".join(answer_parts)
        if not full_answer:
            full_answer = "Current conditions are normal."
        
        return {
            "answer": full_answer,
            "evidence": [
                f"Temperature: {temp}°C",
                f"Humidity: {humidity}%",
                f"Rainfall: {rain}mm",
                f"Wind: {wind} km/h"
            ],
            "actions": actions if actions else ["✅ No immediate actions required"],
            "risk": risk,
            "confidence": "Moderate - Rule-based",
            "source": "WeatherGPT Rule Engine",
            "llm_used": False,
            "fallback_mode": True
        }

# Global instance
llm_service = LLMService()