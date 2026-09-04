from typing import Any, Dict, List, Tuple, Optional
import numpy as np
from datetime import datetime, timedelta

class AdvisoryEngine:
    def __init__(self):
        self.weights = {
            "temperature": 0.25,
            "humidity": 0.20,
            "precipitation": 0.30,
            "wind": 0.15,
            "trend": 0.10
        }
        self.thresholds = {
            "temperature": {"low": 0, "moderate": 32, "high": 38},
            "humidity": {"low": 30, "moderate": 70, "high": 85},
            "precipitation": {"low": 0, "moderate": 2, "high": 5},
            "wind": {"low": 0, "moderate": 35, "high": 50}
        }
    
    def build_advisory(self, question: str, role: str, data: dict) -> dict:
        """Build comprehensive advisory with risk scoring"""
        current = data.get("current", {})
        derived = data.get("derived", {})
        
        # Extract metrics
        temp = current.get("temperature_2m", 0)
        humidity = current.get("relative_humidity_2m", 0)
        rain = current.get("rain", 0) or 0
        precip = current.get("precipitation", 0) or 0
        wind = current.get("wind_speed_10m", 0)
        gust = current.get("wind_gusts_10m", 0)
        code = current.get("weather_code", 0)
        
        # Derived metrics
        trend = derived.get("trend", "stable")
        heat_index = derived.get("heat_index")
        comfort = derived.get("comfort_index", "moderate")
        
        # Calculate risk scores
        risk_scores = self._calculate_risk_scores(temp, humidity, rain, wind)
        overall_risk = self._calculate_overall_risk(risk_scores)
        
        # Get role-specific analysis
        role_actions = self._get_role_actions(role, risk_scores, data)
        
        # Build evidence
        evidence = self._build_evidence(current, derived, risk_scores)
        
        # Generate natural language answer
        answer = self._generate_answer(role, overall_risk, risk_scores, role_actions, trend, comfort)
        
        # Get forecast timeline
        timeline = self._get_forecast_timeline(data)
        
        return {
            "answer": answer,
            "evidence": evidence,
            "actions": role_actions,
            "risk": overall_risk,
            "risk_scores": risk_scores,
            "confidence": self._calculate_confidence(risk_scores, data),
            "source": "Open-Meteo forecast API + Advanced Analytics Engine",
            "trend": trend,
            "comfort": comfort,
            "heat_index": heat_index,
            "timeline": timeline,
            "advisory_time": datetime.utcnow().isoformat()
        }
    
    def _calculate_risk_scores(self, temp: float, humidity: float, rain: float, wind: float) -> Dict[str, str]:
        """Calculate individual risk scores"""
        scores = {}
        
        # Temperature risk
        if temp >= self.thresholds["temperature"]["high"]:
            scores["temperature"] = "high"
        elif temp >= self.thresholds["temperature"]["moderate"]:
            scores["temperature"] = "moderate"
        else:
            scores["temperature"] = "low"
        
        # Humidity risk
        if humidity >= self.thresholds["humidity"]["high"]:
            scores["humidity"] = "high"
        elif humidity >= self.thresholds["humidity"]["moderate"]:
            scores["humidity"] = "moderate"
        else:
            scores["humidity"] = "low"
        
        # Precipitation risk
        if rain >= self.thresholds["precipitation"]["high"]:
            scores["precipitation"] = "high"
        elif rain >= self.thresholds["precipitation"]["moderate"]:
            scores["precipitation"] = "moderate"
        else:
            scores["precipitation"] = "low"
        
        # Wind risk
        if wind >= self.thresholds["wind"]["high"]:
            scores["wind"] = "high"
        elif wind >= self.thresholds["wind"]["moderate"]:
            scores["wind"] = "moderate"
        else:
            scores["wind"] = "low"
        
        return scores
    
    def _calculate_overall_risk(self, scores: Dict[str, str]) -> str:
        """Calculate overall risk level with weighted scoring"""
        risk_values = {"low": 0, "moderate": 1, "high": 2}
        weighted_sum = 0
        total_weight = 0
        
        for factor, level in scores.items():
            weight = self.weights.get(factor, 0.2)
            weighted_sum += risk_values[level] * weight
            total_weight += weight
        
        if total_weight > 0:
            avg_risk = weighted_sum / total_weight
            if avg_risk >= 1.5:
                return "HIGH"
            elif avg_risk >= 0.8:
                return "MODERATE"
            else:
                return "LOW"
        return "LOW"
    
    def _get_role_actions(self, role: str, scores: Dict[str, str], data: dict) -> List[str]:
        """Get role-specific actions with priority ordering"""
        actions = []
        current = data.get("current", {})
        temp = current.get("temperature_2m", 0)
        rain = current.get("rain", 0) or 0
        
        # Priority 1: Immediate safety actions
        if scores.get("wind") == "high":
            actions.append("⚠️ HIGH WIND WARNING: Secure loose objects, avoid outdoor activities")
        if scores.get("precipitation") == "high":
            actions.append("⚠️ HEAVY RAIN WARNING: Avoid flooded areas, delay travel")
        if scores.get("temperature") == "high":
            actions.append("⚠️ EXTREME HEAT: Stay hydrated, avoid peak sun hours (12-4 PM)")
        
        # Priority 2: Role-specific actions
        if role == "farmer":
            if rain >= 1:
                actions.append("🌾 Postpone pesticide/fungicide application - rain expected")
            if scores.get("humidity") in ["moderate", "high"]:
                actions.append("🌾 Monitor crops for fungal diseases - high humidity conditions")
            if scores.get("temperature") == "high":
                actions.append("🌾 Irrigate early morning or late evening to minimize evaporation")
            if rain < 1 and scores.get("humidity") == "low":
                actions.append("🌾 Favorable conditions for harvesting operations")
        
        elif role == "disaster":
            actions.append("🚨 Monitor official IMD warnings alongside this forecast")
            if scores.get("wind") in ["moderate", "high"]:
                actions.append("🚨 Prepare emergency shelter and communication systems")
            if scores.get("precipitation") in ["moderate", "high"]:
                actions.append("🚨 Check drainage systems and flood prevention measures")
        
        elif role == "urban":
            if scores.get("precipitation") in ["moderate", "high"]:
                actions.append("🏙️ Expect traffic delays - allow extra commute time")
            if scores.get("temperature") == "high":
                actions.append("🏙️ Use public transport to reduce heat exposure")
            if scores.get("wind") == "high":
                actions.append("🏙️ Secure rooftop items and balcony furniture")
        
        elif role == "traveler":
            if scores.get("precipitation") in ["moderate", "high"]:
                actions.append("🧳 Carry rain protection and check flight/rail delays")
            if scores.get("temperature") == "high":
                actions.append("🧳 Pack light clothing and stay hydrated")
            if scores.get("wind") == "high":
                actions.append("🧳 Avoid coastal/outdoor activities - high wind risk")
        
        # Priority 3: General recommendations
        if not actions:
            actions.append("✅ Current conditions favorable for normal activities")
        else:
            actions.append("📱 Stay updated with regular forecast checks")
        
        return actions
    
    def _build_evidence(self, current: dict, derived: dict, scores: Dict[str, str]) -> List[str]:
        """Build evidence list with score explanations"""
        evidence = []
        
        temp = current.get("temperature_2m")
        if temp is not None:
            evidence.append(f"🌡️ Temperature: {temp}°C ({scores.get('temperature', 'unknown')} risk)")
        
        humidity = current.get("relative_humidity_2m")
        if humidity is not None:
            evidence.append(f"💧 Humidity: {humidity}% ({scores.get('humidity', 'unknown')} risk)")
        
        rain = current.get("rain", 0)
        if rain:
            evidence.append(f"🌧️ Precipitation: {rain}mm ({scores.get('precipitation', 'unknown')} risk)")
        
        wind = current.get("wind_speed_10m")
        if wind is not None:
            evidence.append(f"💨 Wind: {wind}km/h ({scores.get('wind', 'unknown')} risk)")
        
        trend = derived.get("trend")
        if trend:
            evidence.append(f"📈 Trend: {trend}")
        
        heat_index = derived.get("heat_index")
        if heat_index:
            evidence.append(f"🌡️ Heat Index: {heat_index}°C")
        
        return evidence
    
    def _generate_answer(self, role: str, overall_risk: str, scores: Dict[str, str], 
                         actions: List[str], trend: str, comfort: str) -> str:
        """Generate comprehensive natural language answer"""
        role_names = {
            "farmer": "farmer",
            "disaster": "emergency manager",
            "urban": "city resident",
            "traveler": "traveler",
            "general": "user"
        }
        
        role_name = role_names.get(role, "user")
        risk_desc = overall_risk.lower()
        
        base = f"For {role_name}: Current conditions indicate {risk_desc} risk. "
        
        if overall_risk == "HIGH":
            base += "⚠️ Exercise caution and prioritize safety. "
        elif overall_risk == "MODERATE":
            base += "⚡ Monitor conditions and prepare for potential changes. "
        else:
            base += "✅ Conditions are generally favorable. "
        
        # Add trend information
        if trend == "rising":
            base += "Temperatures are rising - prepare for warming conditions. "
        elif trend == "falling":
            base += "Temperatures are cooling - dress accordingly. "
        
        # Add comfort information
        if comfort == "uncomfortable":
            base += "Conditions may be uncomfortable - take necessary precautions. "
        
        # Add specific risk factors
        risk_factors = [f for f, lvl in scores.items() if lvl in ["moderate", "high"]]
        if risk_factors:
            base += f"Key risk factors: {', '.join(risk_factors)}. "
        
        # Add actions summary
        if actions:
            base += f"Recommended actions: {actions[0]}"
        
        return base
    
    def _calculate_confidence(self, scores: Dict[str, str], data: dict) -> str:
        """Calculate confidence score for the advisory"""
        metrics_available = sum(1 for v in scores.values() if v is not None)
        if metrics_available >= 4:
            return "High confidence in current measurements"
        elif metrics_available >= 2:
            return "Moderate confidence - limited data points"
        return "Limited confidence - please cross-check with official sources"
    
    def _get_forecast_timeline(self, data: dict) -> List[dict]:
        """Extract forecast timeline for next 24 hours"""
        hourly = data.get("hourly", {})
        if not hourly:
            return []
        
        times = hourly.get("time", [])
        temps = hourly.get("temperature_2m", [])
        rains = hourly.get("precipitation", [])
        
        timeline = []
        for i in range(min(12, len(times))):
            if i < len(temps):
                timeline.append({
                    "time": times[i] if i < len(times) else None,
                    "temperature": temps[i] if i < len(temps) else None,
                    "precipitation": rains[i] if i < len(rains) else None
                })
        
        return timeline

advisory_engine = AdvisoryEngine()

# Public API functions
def build_advisory(question: str, role: str, data: dict) -> dict:
    return advisory_engine.build_advisory(question, role, data)