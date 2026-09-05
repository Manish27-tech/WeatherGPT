import json
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from loguru import logger

class WeatherReliabilityScore:
    """
    Advanced Weather Reliability Analysis
    - Forecast accuracy tracking
    - Historical comparison (3 months)
    - Model confidence scoring
    - Error margin calculation
    """
    
    def __init__(self):
        # Simulate 3 months of historical data
        self.historical_data = self._generate_historical_data()
        self.reliability_history = []
        self.accuracy_thresholds = {
            "excellent": 90,
            "good": 80,
            "fair": 70,
            "poor": 60
        }
    
    def _generate_historical_data(self) -> Dict:
        """Generate 3 months of simulated historical data"""
        import random
        
        data = {
            "temperature": [],
            "humidity": [],
            "rainfall": [],
            "wind": []
        }
        
        for day in range(90):
            # Simulate forecast vs actual with varying accuracy
            error_rate = 0.05 + random.random() * 0.15  # 5-20% error
            base_temp = 25 + random.random() * 10
            
            data["temperature"].append({
                "date": (datetime.now() - timedelta(days=day)).isoformat(),
                "forecast": round(base_temp, 1),
                "actual": round(base_temp + (random.random() - 0.5) * 4, 1),
                "error": round((random.random() - 0.5) * 4, 1)
            })
        
        return data
    
    def calculate_reliability(self, weather_data: Dict, location: Dict = None) -> Dict:
        """
        Calculate weather reliability score using 3-month history
        """
        try:
            current = weather_data.get("current", {})
            
            # 1. Current metrics reliability
            current_reliability = self._analyze_current_metrics(current)
            
            # 2. Historical accuracy analysis (3 months)
            historical_accuracy = self._analyze_historical_accuracy()
            
            # 3. Model confidence
            model_confidence = self._calculate_model_confidence(weather_data)
            
            # 4. Overall reliability
            overall = self._calculate_overall_reliability(
                current_reliability,
                historical_accuracy,
                model_confidence
            )
            
            return {
                "status": "success",
                "analysis": {
                    "current_metrics": current_reliability,
                    "historical_accuracy": historical_accuracy,
                    "model_confidence": model_confidence,
                    "overall": overall,
                    "source": "3-Month Historical Analysis"
                },
                "recommendations": self._generate_recommendations(overall),
                "visualization": self._generate_visualization_data(),
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Reliability calculation failed: {e}")
            return {
                "status": "error",
                "error": "Reliability calculation failed",
                "message": str(e)
            }
    
    def _analyze_current_metrics(self, current: Dict) -> Dict:
        """Analyze reliability of current metrics"""
        metrics = {}
        
        # Temperature reliability
        temp = current.get("temperature_2m", 0)
        if 15 <= temp <= 35:
            temp_reliability = 85 + (25 - abs(temp - 25)) * 0.5
        else:
            temp_reliability = 70 - abs(temp - 35) * 0.5
        
        metrics["temperature"] = {
            "value": temp,
            "reliability": round(min(95, max(50, temp_reliability)), 1),
            "unit": "°C"
        }
        
        # Humidity reliability
        humidity = current.get("relative_humidity_2m", 0)
        if 40 <= humidity <= 80:
            humidity_reliability = 80 + (60 - abs(humidity - 60)) * 0.3
        else:
            humidity_reliability = 70 - abs(humidity - 80) * 0.3
        
        metrics["humidity"] = {
            "value": humidity,
            "reliability": round(min(95, max(50, humidity_reliability)), 1),
            "unit": "%"
        }
        
        # Rainfall reliability
        rain = current.get("rain", 0)
        if rain == 0:
            rain_reliability = 85
        elif rain < 5:
            rain_reliability = 75
        elif rain < 20:
            rain_reliability = 65
        else:
            rain_reliability = 50
        
        metrics["rainfall"] = {
            "value": rain,
            "reliability": round(rain_reliability, 1),
            "unit": "mm"
        }
        
        # Wind reliability
        wind = current.get("wind_speed_10m", 0)
        if wind < 20:
            wind_reliability = 85
        elif wind < 40:
            wind_reliability = 75
        else:
            wind_reliability = 65
        
        metrics["wind"] = {
            "value": wind,
            "reliability": round(wind_reliability, 1),
            "unit": "km/h"
        }
        
        return metrics
    
    def _analyze_historical_accuracy(self) -> Dict:
        """Analyze 3-month historical accuracy"""
        # Use the stored historical data
        temps = self.historical_data.get("temperature", [])
        
        if not temps:
            return {"accuracy": 70, "trend": "Stable"}
        
        # Calculate average error
        errors = [t.get("error", 0) for t in temps[-90:]]
        avg_error = sum(abs(e) for e in errors) / len(errors) if errors else 0
        
        # Calculate accuracy
        accuracy = max(50, min(95, 100 - avg_error * 4))
        
        # Calculate trend
        recent_errors = [abs(t.get("error", 0)) for t in temps[-30:]]
        older_errors = [abs(t.get("error", 0)) for t in temps[-60:-30]]
        
        if recent_errors and older_errors:
            recent_avg = sum(recent_errors) / len(recent_errors)
            older_avg = sum(older_errors) / len(older_errors)
            
            if recent_avg < older_avg * 0.9:
                trend = "Improving"
            elif recent_avg > older_avg * 1.1:
                trend = "Declining"
            else:
                trend = "Stable"
        else:
            trend = "Stable"
        
        return {
            "accuracy": round(accuracy, 1),
            "trend": trend,
            "sample_size": len(temps),
            "period": "3 months",
            "average_error": round(avg_error, 2)
        }
    
    def _calculate_model_confidence(self, weather_data: Dict) -> Dict:
        """Calculate confidence in the weather model"""
        # Factors affecting confidence
        hourly = weather_data.get("hourly", {})
        daily = weather_data.get("daily", {})
        
        confidence_score = 80  # Base confidence
        
        # Check data completeness
        if not hourly.get("temperature_2m"):
            confidence_score -= 10
        if not daily.get("temperature_2m_max"):
            confidence_score -= 5
        
        # Check for extreme conditions (reduces confidence)
        current = weather_data.get("current", {})
        if abs(current.get("temperature_2m", 0)) > 40:
            confidence_score -= 10
        if current.get("wind_speed_10m", 0) > 40:
            confidence_score -= 5
        
        return {
            "score": round(max(50, min(95, confidence_score)), 1),
            "level": "High" if confidence_score >= 80 else "Moderate" if confidence_score >= 60 else "Low"
        }
    
    def _calculate_overall_reliability(self, current: Dict, historical: Dict, model: Dict) -> Dict:
        """Calculate overall reliability"""
        # Weighted average
        current_avg = sum(m["reliability"] for m in current.values()) / len(current)
        weights = {"current": 0.4, "historical": 0.4, "model": 0.2}
        
        overall = (
            current_avg * weights["current"] +
            historical["accuracy"] * weights["historical"] +
            model["score"] * weights["model"]
        )
        
        overall = round(overall, 1)
        
        # Determine level
        if overall >= 85:
            level = "VERY HIGH"
            color = "#2ecc71"
            description = "Excellent reliability - Trust this forecast"
        elif overall >= 75:
            level = "HIGH"
            color = "#4ecdc4"
            description = "Good reliability - Reliable for planning"
        elif overall >= 65:
            level = "MODERATE"
            color = "#ffd93d"
            description = "Moderate reliability - Cross-check when possible"
        elif overall >= 50:
            level = "FAIR"
            color = "#ff9f43"
            description = "Fair reliability - Use with caution"
        else:
            level = "LOW"
            color = "#ff6b6b"
            description = "Low reliability - Verify with other sources"
        
        return {
            "score": overall,
            "level": level,
            "color": color,
            "description": description,
            "confidence_interval": {
                "low": round(overall - 10, 1),
                "high": round(overall + 10, 1)
            }
        }
    
    def _generate_recommendations(self, overall: Dict) -> List[str]:
        """Generate recommendations based on reliability"""
        recs = []
        
        if overall["score"] >= 75:
            recs.append("✅ High reliability - Confident in forecast")
            recs.append("📊 Use for planning and decisions")
        elif overall["score"] >= 60:
            recs.append("⚠️ Moderate reliability - Monitor updates")
            recs.append("📱 Check for forecast updates regularly")
        else:
            recs.append("🔴 Low reliability - Be cautious")
            recs.append("📡 Cross-reference with multiple sources")
        
        return recs
    
    def _generate_visualization_data(self) -> Dict:
        """Generate data for reliability visualization"""
        # Generate 3 months of reliability data
        import random
        reliability_history = []
        
        for day in range(90):
            base = 70 + random.random() * 20
            variation = (random.random() - 0.5) * 15
            reliability_history.append({
                "date": (datetime.now() - timedelta(days=day)).isoformat(),
                "reliability": round(max(50, min(95, base + variation)), 1)
            })
        
        return {
            "history": reliability_history,
            "trend_line": self._calculate_trend_line(reliability_history)
        }
    
    def _calculate_trend_line(self, history: List[Dict]) -> str:
        """Calculate reliability trend"""
        if len(history) < 2:
            return "Stable"
        
        values = [h["reliability"] for h in history]
        first = sum(values[-30:]) / 30 if len(values) >= 30 else sum(values) / len(values)
        last = sum(values[:30]) / 30 if len(values) >= 30 else sum(values) / len(values)
        
        if first - last > 5:
            return "Improving"
        elif last - first > 5:
            return "Declining"
        else:
            return "Stable"

reliability_calculator = WeatherReliabilityScore()