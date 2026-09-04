from typing import Dict, List
import json
import httpx
from loguru import logger

class LanguageService:
    """
    Multi-language support for Indian languages
    Uses Bhashini API for translation
    """
    
    def __init__(self):
        # Common weather terms in Indian languages
        self.weather_terms = {
            "en": {
                "temperature": "Temperature",
                "humidity": "Humidity",
                "wind": "Wind Speed",
                "rain": "Rainfall",
                "forecast": "Forecast",
                "risk": "Risk",
                "advisory": "Advisory",
                "warning": "Warning",
                "safe": "Safe",
                "danger": "Danger"
            },
            "hi": {
                "temperature": "तापमान",
                "humidity": "आर्द्रता",
                "wind": "हवा की गति",
                "rain": "वर्षा",
                "forecast": "पूर्वानुमान",
                "risk": "जोखिम",
                "advisory": "सलाह",
                "warning": "चेतावनी",
                "safe": "सुरक्षित",
                "danger": "खतरा"
            },
            "pa": {
                "temperature": "ਤਾਪਮਾਨ",
                "humidity": "ਨਮੀ",
                "wind": "ਹਵਾ ਦੀ ਗਤੀ",
                "rain": "ਬਾਰਿਸ਼",
                "forecast": "ਪੂਰਵ-ਅਨੁਮਾਨ",
                "risk": "ਜੋਖਮ",
                "advisory": "ਸਲਾਹ",
                "warning": "ਚੇਤਾਵਨੀ",
                "safe": "ਸੁਰੱਖਿਅਤ",
                "danger": "ਖਤਰਾ"
            },
            "ta": {
                "temperature": "வெப்பநிலை",
                "humidity": "ஈரப்பதம்",
                "wind": "காற்றின் வேகம்",
                "rain": "மழைப்பொழிவு",
                "forecast": "முன்னறிவிப்பு",
                "risk": "இடர்",
                "advisory": "ஆலோசனை",
                "warning": "எச்சரிக்கை",
                "safe": "பாதுகாப்பான",
                "danger": "ஆபத்தான"
            },
            "te": {
                "temperature": "ఉష్ణోగ్రత",
                "humidity": "తేమ",
                "wind": "గాలి వేగం",
                "rain": "వర్షపాతం",
                "forecast": "సూచన",
                "risk": "ప్రమాదం",
                "advisory": "సలహా",
                "warning": "హెచ్చరిక",
                "safe": "సురక్షిత",
                "danger": "ప్రమాదకర"
            },
            "bn": {
                "temperature": "তাপমাত্রা",
                "humidity": "আর্দ্রতা",
                "wind": "বাতাসের গতি",
                "rain": "বৃষ্টিপাত",
                "forecast": "পূর্বাভাস",
                "risk": "ঝুঁকি",
                "advisory": "পরামর্শ",
                "warning": "সতর্কতা",
                "safe": "নিরাপদ",
                "danger": "বিপদ"
            },
            "mr": {
                "temperature": "तापमान",
                "humidity": "आर्द्रता",
                "wind": "वाऱ्याचा वेग",
                "rain": "पाऊस",
                "forecast": "पूर्वसूचना",
                "risk": "धोका",
                "advisory": "सल्ला",
                "warning": "चेतावणी",
                "safe": "सुरक्षित",
                "danger": "धोकादायक"
            },
            "gu": {
                "temperature": "તાપમાન",
                "humidity": "ભેજ",
                "wind": "પવનની ગતિ",
                "rain": "વરસાદ",
                "forecast": "આગાહી",
                "risk": "જોખમ",
                "advisory": "સલાહ",
                "warning": "ચેતવણી",
                "safe": "સુરક્ષિત",
                "danger": "ખતરો"
            },
            "kn": {
                "temperature": "ತಾಪಮಾನ",
                "humidity": "ಆರ್ದ್ರತೆ",
                "wind": "ಗಾಳಿಯ ವೇಗ",
                "rain": "ಮಳೆ",
                "forecast": "ಮುನ್ಸೂಚನೆ",
                "risk": "ಅಪಾಯ",
                "advisory": "ಸಲಹೆ",
                "warning": "ಎಚ್ಚರಿಕೆ",
                "safe": "ಸುರಕ್ಷಿತ",
                "danger": "ಅಪಾಯಕಾರಿ"
            },
            "ml": {
                "temperature": "താപനില",
                "humidity": "ഈർപ്പം",
                "wind": "കാറ്റിന്റെ വേഗം",
                "rain": "മഴ",
                "forecast": "പ്രവചനം",
                "risk": "അപകടസാധ്യത",
                "advisory": "ഉപദേശം",
                "warning": "മുന്നറിയിപ്പ്",
                "safe": "സുരക്ഷിത",
                "danger": "അപകടകരം"
            }
        }
        
        self.supported_languages = list(self.weather_terms.keys())
    
    def translate_weather_data(self, data: Dict, lang: str = "en") -> Dict:
        """
        Translate weather data to target language
        """
        if lang not in self.weather_terms:
            lang = "en"
        
        terms = self.weather_terms[lang]
        translated = {}
        
        # Translate current weather
        current = data.get("current", {})
        translated_current = {}
        
        # Weather condition mapping
        condition_map = {
            "temperature_2m": terms["temperature"],
            "relative_humidity_2m": terms["humidity"],
            "wind_speed_10m": terms["wind"],
            "precipitation": terms["rain"]
        }
        
        for key, value in current.items():
            if key in condition_map:
                translated_current[condition_map[key]] = value
            else:
                translated_current[key] = value
        
        # Translate risk levels
        risk_map = {
            "LOW": terms["safe"],
            "MODERATE": "मध्यम" if lang == "hi" else "MODERATE",  # Fallback
            "HIGH": terms["danger"]
        }
        
        risk_level = data.get("risk", "LOW")
        translated_risk = risk_map.get(risk_level, risk_level)
        
        # Build translated response
        translated = {
            "language": lang,
            "language_name": self._get_language_name(lang),
            "current": translated_current,
            "risk": translated_risk,
            "risk_level": risk_level,
            "message": self._translate_message(data.get("message", ""), lang),
            "actions": [
                self._translate_message(action, lang) 
                for action in data.get("actions", [])
            ]
        }
        
        return translated
    
    def _get_language_name(self, lang: str) -> str:
        """Get language name in the language itself"""
        names = {
            "en": "English",
            "hi": "हिन्दी",
            "pa": "ਪੰਜਾਬੀ",
            "ta": "தமிழ்",
            "te": "తెలుగు",
            "bn": "বাংলা",
            "mr": "मराठी",
            "gu": "ગુજરાતી",
            "kn": "ಕನ್ನಡ",
            "ml": "മലയാളം"
        }
        return names.get(lang, "English")
    
    def _translate_message(self, message: str, lang: str) -> str:
        """Translate message using Bhashini API"""
        if lang == "en":
            return message
        
        try:
            # Simplified translation - in production, use Bhashini API
            # For demo, we'll do basic translation of common terms
            translated = message
            
            # Common translations
            replacements = {
                "Temperature": self.weather_terms[lang]["temperature"],
                "Humidity": self.weather_terms[lang]["humidity"],
                "Wind Speed": self.weather_terms[lang]["wind"],
                "Rainfall": self.weather_terms[lang]["rain"],
                "Forecast": self.weather_terms[lang]["forecast"],
                "Risk": self.weather_terms[lang]["risk"],
                "Advisory": self.weather_terms[lang]["advisory"],
                "Warning": self.weather_terms[lang]["warning"],
                "Safe": self.weather_terms[lang]["safe"],
                "Danger": self.weather_terms[lang]["danger"]
            }
            
            for eng, trans in replacements.items():
                translated = translated.replace(eng, trans)
            
            return translated
            
        except Exception as e:
            logger.error(f"Translation error: {e}")
            return message
    
    async def bhashini_translate(self, text: str, lang: str) -> str:
        """
        Use Bhashini API for translation (Production)
        """
        if lang == "en":
            return text
        
        try:
            # Bhashini API endpoint
            url = "https://api.bhashini.gov.in/v1/translate"
            
            payload = {
                "text": text,
                "source_language": "en",
                "target_language": lang
            }
            
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.post(url, json=payload)
                if response.status_code == 200:
                    data = response.json()
                    return data.get("translation", text)
                return text
        except Exception as e:
            logger.error(f"Bhashini API error: {e}")
            return text

# Global instance
language_service = LanguageService()