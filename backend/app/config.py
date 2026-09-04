from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    app_name: str = "WeatherGPT"
    environment: str = "development"
    frontend_origin: str = "http://localhost:5173"
    database_url: str = "postgresql+psycopg://weather:weather@localhost:5432/weather"
    redis_url: str = "redis://localhost:6379/0"
    open_meteo_url: str = "https://api.open-meteo.com/v1/forecast"
    open_meteo_geocoding_url: str = "https://geocoding-api.open-meteo.com/v1/search"
    mqtt_enabled: bool = False
    mqtt_broker: str = "localhost"
    mqtt_port: int = 1883
    mqtt_topic: str = "weathergpt/alerts"
    
    # Advanced settings
    rate_limit_requests: int = 100
    rate_limit_period: int = 60
    cache_ttl: int = 300
    max_history_days: int = 7
    alert_check_interval: int = 300
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()