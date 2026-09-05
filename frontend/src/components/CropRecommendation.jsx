import React, { useState, useEffect } from 'react';
import { Sprout, TrendingUp, TrendingDown, Minus, Calendar, Droplets, Thermometer, Wind } from 'lucide-react';

const API = import.meta.env.VITE_API_URL || "http://localhost:8000";

export function CropRecommendation({ lat, lon, soilType = "loam" }) {
    const [recommendations, setRecommendations] = useState(null);
    const [loading, setLoading] = useState(false);
    const [selectedSoil, setSelectedSoil] = useState(soilType);
    const [error, setError] = useState(null);
    
    useEffect(() => {
        if (lat && lon) {
            fetchRecommendations();
        }
    }, [lat, lon, selectedSoil]);
    
    async function fetchRecommendations() {
        setLoading(true);
        setError(null);
        try {
            const res = await fetch(`${API}/api/crop/recommend?latitude=${lat}&longitude=${lon}&soil_type=${selectedSoil}`);
            if (!res.ok) throw new Error('Failed to fetch recommendations');
            const data = await res.json();
            setRecommendations(data);
        } catch (e) {
            console.error('Crop recommendation failed:', e);
            setError('Could not fetch crop recommendations');
            // Fallback data for demo
            setRecommendations({
                current_weather: { temperature: 25, humidity: 60, rainfall: 0, soil_type: selectedSoil },
                recommendations: [
                    { crop: 'wheat', match_score: 85, emoji: '🌾', description: 'Staple grain', temp_range: '15-25°C', rainfall_range: '50-100mm' },
                    { crop: 'rice', match_score: 70, emoji: '🍚', description: 'Major staple', temp_range: '20-35°C', rainfall_range: '150-300mm' },
                    { crop: 'maize', match_score: 65, emoji: '🌽', description: 'Versatile crop', temp_range: '20-30°C', rainfall_range: '60-120mm' },
                ],
                best_match: { crop: 'wheat', match_score: 85, emoji: '🌾' }
            });
        }
        setLoading(false);
    }
    
    if (loading) {
        return <div className="crop-recommend-loading">🌾 Analyzing soil & weather...</div>;
    }
    
    if (error) {
        return <div className="crop-recommend-error">⚠️ {error}</div>;
    }
    
    if (!recommendations) {
        return <div className="crop-recommend-empty">Select a location to get recommendations</div>;
    }
    
    return (
        <div className="crop-recommendation-3d">
            <div className="recommend-header">
                <Sprout size={18} color="#4ecdc4" />
                <span>AI Crop Recommendations</span>
            </div>
            
            <div className="recommend-weather">
                <h5>🌤️ Current Conditions</h5>
                <div className="weather-params">
                    <div className="param-item">
                        <Thermometer size={14} />
                        <span>{Math.round(recommendations.current_weather.temperature)}°C</span>
                    </div>
                    <div className="param-item">
                        <Droplets size={14} />
                        <span>{Math.round(recommendations.current_weather.humidity)}%</span>
                    </div>
                    <div className="param-item">
                        <Wind size={14} />
                        <span>{recommendations.current_weather.rainfall}mm</span>
                    </div>
                    <div className="param-item">
                        <div className="soil-indicator">🌱 {selectedSoil}</div>
                    </div>
                </div>
            </div>
            
            <div className="soil-selector">
                <label>Soil Type:</label>
                <select value={selectedSoil} onChange={e => setSelectedSoil(e.target.value)}>
                    <option value="loam">Loam</option>
                    <option value="clay">Clay</option>
                    <option value="sandy">Sandy</option>
                    <option value="black">Black</option>
                    <option value="alluvial">Alluvial</option>
                </select>
            </div>
            
            <div className="recommend-list">
                <h5>🌾 Top Recommendations</h5>
                {recommendations.recommendations.map((crop, i) => (
                    <div key={i} className={`recommend-item ${i === 0 ? 'best' : ''}`}>
                        <div className="recommend-icon">{crop.emoji}</div>
                        <div className="recommend-details">
                            <div className="recommend-name">
                                {crop.crop.charAt(0).toUpperCase() + crop.crop.slice(1)}
                                {i === 0 && <span className="best-badge">⭐ Best Match</span>}
                            </div>
                            <div className="recommend-meta">
                                <span>📈 {crop.match_score}% match</span>
                                <span>🌡️ {crop.temp_range || '15-25°C'}</span>
                                <span>💧 {crop.rainfall_range || '50-100mm'}</span>
                            </div>
                            <div className="recommend-desc">{crop.description}</div>
                        </div>
                    </div>
                ))}
            </div>
            
            <div className="recommend-tip">
                <div className="tip-icon">💡</div>
                <div>
                    <span>Pro Tip</span>
                    <p>Based on current weather, <strong>{recommendations.best_match?.crop || 'wheat'}</strong> is the most suitable crop for your area.</p>
                </div>
            </div>
        </div>
    );
}