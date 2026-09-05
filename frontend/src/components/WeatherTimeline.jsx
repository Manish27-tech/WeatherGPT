import React, { useState, useEffect } from 'react';
import { Clock, Cloud, CloudRain, Sun, Moon, Wind } from 'lucide-react';

export function WeatherTimeline({ weatherData }) {
    const [currentHour, setCurrentHour] = useState(new Date().getHours());
    
    useEffect(() => {
        const interval = setInterval(() => {
            setCurrentHour(new Date().getHours());
        }, 60000);
        return () => clearInterval(interval);
    }, []);
    
    const hourly = weatherData?.hourly || {};
    const times = hourly.time || [];
    const temps = hourly.temperature_2m || [];
    const rain = hourly.precipitation || [];
    const humidity = hourly.relative_humidity_2m || [];
    const wind = hourly.wind_speed_10m || [];
    
    if (!times || times.length === 0) {
        return (
            <div className="timeline-empty">
                <p>No timeline data available</p>
            </div>
        );
    }
    
    return (
        <div className="timeline-3d">
            <div className="timeline-header">
                <Clock size={18} color="#4ecdc4" />
                <span>24-Hour Weather Timeline</span>
                <span className="timeline-live">● LIVE</span>
            </div>
            
            <div className="timeline-scroll">
                {times.slice(0, 24).map((time, i) => {
                    const hour = new Date(time).getHours();
                    const isCurrent = hour === currentHour;
                    const isPast = hour < currentHour;
                    const isNight = hour < 6 || hour > 18;
                    const temp = Math.round(temps[i] || 0);
                    const rainAmount = Math.round((rain[i] || 0) * 10) / 10;
                    const isRaining = rainAmount > 0.5;
                    const hum = Math.round(humidity[i] || 0);
                    const windSpeed = Math.round(wind[i] || 0);
                    
                    // Determine weather icon
                    let weatherIcon = '☀️';
                    if (isRaining) weatherIcon = '🌧️';
                    else if (isNight) weatherIcon = '🌙';
                    else if (hum > 70) weatherIcon = '⛅';
                    else if (windSpeed > 25) weatherIcon = '💨';
                    
                    return (
                        <div 
                            key={i} 
                            className={`timeline-item-3d ${isCurrent ? 'current' : ''} ${isPast ? 'past' : ''} ${isNight ? 'night' : ''}`}
                        >
                            <div className="timeline-time">
                                {hour === 0 ? '12AM' : hour < 12 ? `${hour}AM` : hour === 12 ? '12PM' : `${hour - 12}PM`}
                                {isCurrent && <span className="current-badge">●</span>}
                            </div>
                            <div className="timeline-weather">
                                <span className="timeline-icon">{weatherIcon}</span>
                                <span className="timeline-temp">{temp}°</span>
                            </div>
                            {isRaining && (
                                <div className="timeline-rain">
                                    <CloudRain size={10} /> {rainAmount}mm
                                </div>
                            )}
                            <div className="timeline-humidity">
                                💧 {hum}%
                            </div>
                        </div>
                    );
                })}
            </div>
            
            <div className="timeline-legend">
                <span><span className="legend-dot current-dot"></span> Current</span>
                <span><span className="legend-dot rain-dot"></span> Rain</span>
                <span><span className="legend-dot night-dot"></span> Night</span>
            </div>
        </div>
    );
}