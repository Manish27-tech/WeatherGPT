import React, { useState, useEffect } from 'react';
import { MapPin, Search, Thermometer, Droplets, Wind, CloudRain, Eye, RefreshCw, AlertTriangle, TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { MapContainer, TileLayer, CircleMarker, Popup } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

const API = import.meta.env.VITE_API_URL || "http://localhost:8000";

// Fix for Leaflet default icons
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
    iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
    iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

export function WeatherComparison() {
    const [cities, setCities] = useState([]);
    const [searchQuery, setSearchQuery] = useState('');
    const [searchResults, setSearchResults] = useState([]);
    const [comparisonData, setComparisonData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [weatherData, setWeatherData] = useState({});
    const [error, setError] = useState(null);
    const [isComparing, setIsComparing] = useState(false);
    const mapCenter = cities.length > 0 ? [cities[0].latitude, cities[0].longitude] : [20.5937, 78.9629];

    const searchCity = async (query) => {
        if (query.length < 2) {
            setSearchResults([]);
            return;
        }
        try {
            const res = await fetch(`${API}/api/geocode?name=${query}`);
            const data = await res.json();
            setSearchResults(data.results || []);
        } catch (e) {
            console.error('Search failed:', e);
            setSearchResults([]);
        }
    };

    const addCity = async (city) => {
        if (cities.length >= 5) {
            alert('Maximum 5 cities allowed');
            return;
        }
        
        if (cities.some(c => c.name === city.name)) {
            alert(`${city.name} is already added`);
            return;
        }
        
        try {
            const res = await fetch(`${API}/api/weather?latitude=${city.latitude}&longitude=${city.longitude}`);
            if (res.ok) {
                const data = await res.json();
                setWeatherData(prev => ({
                    ...prev,
                    [city.name]: data.current || {}
                }));
            }
        } catch (e) {
            console.error('Failed to fetch weather:', e);
        }
        
        setCities([...cities, city]);
        setSearchQuery('');
        setSearchResults([]);
        setError(null);
        setComparisonData(null);
    };

    const removeCity = (index) => {
        const cityName = cities[index].name;
        setCities(cities.filter((_, i) => i !== index));
        const newData = { ...weatherData };
        delete newData[cityName];
        setWeatherData(newData);
        
        if (cities.length - 1 < 2) {
            setComparisonData(null);
        }
    };

    const compareWeather = async () => {
        if (cities.length < 2) {
            alert('Add at least 2 cities to compare');
            return;
        }
        
        setIsComparing(true);
        setLoading(true);
        setError(null);
        
        try {
            // First, fetch fresh weather data for all cities
            const weatherPromises = cities.map(async (city) => {
                const res = await fetch(`${API}/api/weather?latitude=${city.latitude}&longitude=${city.longitude}`);
                if (res.ok) {
                    const data = await res.json();
                    return { name: city.name, weather: data.current || {} };
                }
                return { name: city.name, weather: {} };
            });
            
            const weatherResults = await Promise.all(weatherPromises);
            const newWeatherData = {};
            weatherResults.forEach(w => {
                newWeatherData[w.name] = w.weather;
            });
            setWeatherData(newWeatherData);
            
            // Then compare
            const res = await fetch(`${API}/api/compare-weather`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(cities)
            });
            
            if (!res.ok) {
                throw new Error(`HTTP ${res.status}`);
            }
            
            const data = await res.json();
            console.log('Comparison data:', data);
            setComparisonData(data);
            
        } catch (e) {
            console.error('Comparison failed:', e);
            setError(e.message || 'Failed to compare weather');
        }
        
        setLoading(false);
        setIsComparing(false);
    };

    const clearAll = () => {
        setCities([]);
        setComparisonData(null);
        setWeatherData({});
        setError(null);
    };

    const colors = ['#4ecdc4', '#ff6b6b', '#ffd93d', '#74b9ff', '#a29bfe'];

    return (
        <div className="compare-container-3d">
            <div className="compare-header">
                <div className="compare-title">
                    <MapPin size={18} color="#4ecdc4" />
                    <span>Weather Comparison</span>
                </div>
                <span className="compare-count">{cities.length}/5 Cities</span>
            </div>

            {/* Interactive Map */}
            <div className="compare-map-container">
                <MapContainer 
                    center={mapCenter} 
                    zoom={cities.length > 0 ? 4 : 2} 
                    style={{ height: '200px', width: '100%', borderRadius: '12px' }}
                >
                    <TileLayer
                        attribution='© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                    />
                    {cities.map((city, index) => {
                        const color = colors[index % colors.length];
                        const data = weatherData?.[city.name] || {};
                        
                        return (
                            <CircleMarker
                                key={index}
                                center={[city.latitude, city.longitude]}
                                radius={12}
                                fillColor={color}
                                color={color}
                                weight={3}
                                opacity={0.9}
                                fillOpacity={0.8}
                            >
                                <Popup>
                                    <div className="compare-popup">
                                        <strong>📍 {city.name}</strong>
                                        <div className="popup-weather-details">
                                            <div className="popup-row">
                                                <Thermometer size={14} /> {data.temperature_2m || 'N/A'}°C
                                            </div>
                                            <div className="popup-row">
                                                <Droplets size={14} /> {data.relative_humidity_2m || 'N/A'}%
                                            </div>
                                            <div className="popup-row">
                                                <Wind size={14} /> {data.wind_speed_10m || 'N/A'} km/h
                                            </div>
                                            <div className="popup-row">
                                                <CloudRain size={14} /> {data.rain || 'N/A'} mm
                                            </div>
                                        </div>
                                    </div>
                                </Popup>
                            </CircleMarker>
                        );
                    })}
                </MapContainer>
                <div className="map-legend-compare">
                    {cities.map((city, i) => (
                        <span key={i}>
                            <span className="legend-dot" style={{background: colors[i % colors.length]}}></span>
                            {city.name}
                        </span>
                    ))}
                    {cities.length === 0 && <span>Add cities to see on map</span>}
                </div>
            </div>

            {/* Search Input */}
            <div className="compare-search">
                <input
                    type="text"
                    placeholder="Search city to add..."
                    value={searchQuery}
                    onChange={(e) => {
                        setSearchQuery(e.target.value);
                        searchCity(e.target.value);
                    }}
                    onKeyDown={(e) => {
                        if (e.key === 'Enter' && searchResults.length > 0) {
                            addCity(searchResults[0]);
                        }
                    }}
                />
                <button className="search-btn" onClick={() => searchCity(searchQuery)}>
                    <Search size={16} />
                </button>
                {searchResults.length > 0 && (
                    <div className="compare-search-results">
                        {searchResults.map((city) => (
                            <button key={`${city.latitude}${city.longitude}`} onClick={() => addCity(city)}>
                                <MapPin size={12} /> {city.name}, {city.country}
                            </button>
                        ))}
                    </div>
                )}
            </div>

            {/* City Chips */}
            <div className="compare-cities">
                {cities.map((city, index) => (
                    <div key={index} className="city-chip" style={{ borderColor: colors[index % colors.length] }}>
                        <span>{city.name}</span>
                        <button onClick={() => removeCity(index)}>×</button>
                    </div>
                ))}
                {cities.length === 0 && (
                    <span className="empty-hint">Add cities to compare</span>
                )}
            </div>

            {/* Compare Button */}
            {cities.length >= 2 && (
                <button className="compare-btn" onClick={compareWeather} disabled={loading || isComparing}>
                    {loading || isComparing ? '⏳ Comparing...' : '📊 Compare Weather'}
                </button>
            )}

            {/* Error Message */}
            {error && (
                <div className="compare-error">
                    <AlertTriangle size={16} color="#ff6b6b" />
                    <span>{error}</span>
                    <button onClick={() => setError(null)}>×</button>
                </div>
            )}

            {/* ===== COMPARISON RESULTS ===== */}
            {comparisonData && comparisonData.results && comparisonData.results.length > 0 && (
                <div className="compare-results">
                    <h4>📈 Comparison Results</h4>
                    
                    {/* Weather Cards for each city */}
                    <div className="compare-city-cards">
                        {comparisonData.results.map((city, i) => {
                            const color = colors[i % colors.length];
                            const metrics = city.metrics || {};
                            const weather = city.weather || {};
                            
                            return (
                                <div key={i} className="city-card" style={{ borderColor: color }}>
                                    <div className="city-card-header" style={{ background: color + '20' }}>
                                        <span>{city.name}</span>
                                        <span className="city-score">{metrics.weather_score || 0}%</span>
                                    </div>
                                    <div className="city-card-body">
                                        <div className="city-param">
                                            <Thermometer size={14} color={color} />
                                            <span>{weather.temperature || 'N/A'}°C</span>
                                        </div>
                                        <div className="city-param">
                                            <Droplets size={14} color={color} />
                                            <span>{weather.humidity || 'N/A'}%</span>
                                        </div>
                                        <div className="city-param">
                                            <Wind size={14} color={color} />
                                            <span>{weather.wind || 'N/A'} km/h</span>
                                        </div>
                                        <div className="city-param">
                                            <CloudRain size={14} color={color} />
                                            <span>{weather.rainfall || 'N/A'} mm</span>
                                        </div>
                                        <div className="city-param">
                                            <div className="comfort-bar" style={{ width: `${metrics.comfort_index || 0}%`, background: color }} />
                                            <span>Comfort: {metrics.comfort_index || 0}%</span>
                                        </div>
                                    </div>
                                </div>
                            );
                        })}
                    </div>

                    {/* Statistics */}
                    {comparisonData.comparison && (
                        <div className="compare-stats">
                            <div className="stat-row">
                                <span>🏆 Best Weather</span>
                                <strong>{comparisonData.comparison.ranking?.best_weather || '-'}</strong>
                            </div>
                            <div className="stat-row">
                                <span>🌡️ Temperature Range</span>
                                <strong>{comparisonData.comparison.statistics?.temperature?.lowest}°C - {comparisonData.comparison.statistics?.temperature?.highest}°C</strong>
                            </div>
                            <div className="stat-row">
                                <span>💧 Humidity Range</span>
                                <strong>{comparisonData.comparison.statistics?.humidity?.lowest}% - {comparisonData.comparison.statistics?.humidity?.highest}%</strong>
                            </div>
                            <div className="stat-row">
                                <span>💨 Wind Range</span>
                                <strong>{comparisonData.comparison.statistics?.wind?.lowest} - {comparisonData.comparison.statistics?.wind?.highest} km/h</strong>
                            </div>
                        </div>
                    )}

                    {/* Insights */}
                    {comparisonData.insights && comparisonData.insights.length > 0 && (
                        <div className="compare-insights">
                            <strong>💡 Insights</strong>
                            {comparisonData.insights.map((insight, i) => (
                                <div key={i} className="insight-item">{insight}</div>
                            ))}
                        </div>
                    )}

                    <button className="clear-btn" onClick={clearAll}>Clear All</button>
                </div>
            )}
            
            {/* No Results State */}
            {cities.length >= 2 && !comparisonData && !loading && !error && !isComparing && (
                <div className="compare-no-results">
                    <span>Click "Compare Weather" to see results</span>
                </div>
            )}
        </div>
    );
}