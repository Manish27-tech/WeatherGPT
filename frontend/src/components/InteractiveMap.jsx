import React, { useEffect, useRef, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMapEvents, CircleMarker } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { Thermometer, Droplets, Wind, CloudRain, Eye, Gauge } from 'lucide-react';

// Fix for default markers in Leaflet
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
    iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
    iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

function LocationMarker({ onLocationSelect, currentLocation }) {
    const [position, setPosition] = useState(null);
    
    useMapEvents({
        click(e) {
            const { lat, lng } = e.latlng;
            setPosition(e.latlng);
            // Reverse geocode or use coordinates as name
            const name = `${lat.toFixed(2)}, ${lng.toFixed(2)}`;
            onLocationSelect(lat, lng, name);
        },
    });

    if (!position) return null;

    return (
        <CircleMarker 
            center={position} 
            radius={8}
            fillColor="#ff6b6b"
            color="#fff"
            weight={2}
            opacity={1}
            fillOpacity={0.8}
        >
            <Popup>
                <div className="map-popup">
                    <strong>📍 Selected Location</strong>
                    <p>{position.lat.toFixed(4)}, {position.lng.toFixed(4)}</p>
                    <small>Click to load weather data</small>
                </div>
            </Popup>
        </CircleMarker>
    );
}

function WeatherMarker({ lat, lon, weather }) {
    if (!weather || !weather.current) return null;
    
    const current = weather.current;
    const temp = current.temperature_2m;
    const humidity = current.relative_humidity_2m;
    const wind = current.wind_speed_10m;
    const rain = current.rain || 0;
    
    // Determine marker color based on temperature
    let color = '#4ecdc4'; // cool
    if (temp > 35) color = '#ff6b6b'; // hot
    else if (temp > 28) color = '#ffd93d'; // warm
    else if (temp < 10) color = '#74b9ff'; // cold
    
    return (
        <Marker position={[lat, lon]}>
            <Popup className="weather-popup">
                <div className="weather-popup-content">
                    <h4>🌤️ Current Weather</h4>
                    <div className="popup-grid">
                        <div className="popup-item">
                            <Thermometer size={16} />
                            <span>{temp}°C</span>
                        </div>
                        <div className="popup-item">
                            <Droplets size={16} />
                            <span>{humidity}%</span>
                        </div>
                        <div className="popup-item">
                            <Wind size={16} />
                            <span>{wind} km/h</span>
                        </div>
                        <div className="popup-item">
                            <CloudRain size={16} />
                            <span>{rain} mm</span>
                        </div>
                    </div>
                </div>
            </Popup>
        </Marker>
    );
}

function MapClickHandler({ onLocationSelect }) {
    useMapEvents({
        click(e) {
            const { lat, lng } = e.latlng;
            const name = `${lat.toFixed(2)}, ${lng.toFixed(2)}`;
            onLocationSelect(lat, lng, name);
        },
    });
    return null;
}

export function InteractiveMap({ onLocationSelect, currentLocation, weatherData }) {
    const mapRef = useRef(null);
    const [mapLoaded, setMapLoaded] = useState(false);
    
    // Default center (India)
    const center = currentLocation ? 
        [currentLocation.latitude, currentLocation.longitude] : 
        [20.5937, 78.9629];

    useEffect(() => {
        // Center map on current location
        if (mapRef.current && currentLocation) {
            const map = mapRef.current;
            map.setView([currentLocation.latitude, currentLocation.longitude], 6);
        }
    }, [currentLocation]);

    return (
        <div className="map-wrapper">
            <MapContainer 
                center={center} 
                zoom={5} 
                style={{ height: '500px', width: '100%', borderRadius: '12px' }}
                ref={mapRef}
                whenReady={() => setMapLoaded(true)}
            >
                <TileLayer
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                />
                <TileLayer
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                />
                
                {/* Click handler */}
                <MapClickHandler onLocationSelect={onLocationSelect} />
                
                {/* Current location marker */}
                {currentLocation && (
                    <Marker position={[currentLocation.latitude, currentLocation.longitude]}>
                        <Popup>
                            <div className="weather-popup">
                                <h4>📍 {currentLocation.name}</h4>
                                {weatherData && weatherData.current && (
                                    <div className="popup-weather">
                                        <p>🌡️ {weatherData.current.temperature_2m}°C</p>
                                        <p>💧 {weatherData.current.relative_humidity_2m}%</p>
                                        <p>💨 {weatherData.current.wind_speed_10m} km/h</p>
                                    </div>
                                )}
                            </div>
                        </Popup>
                    </Marker>
                )}
            </MapContainer>
            
            <div className="map-legend">
                <div className="map-legend-item">
                    <span className="legend-dot" style={{background: '#ff6b6b'}}></span>
                    <span>Hot (&gt;35°C)</span>
                </div>
                <div className="map-legend-item">
                    <span className="legend-dot" style={{background: '#ffd93d'}}></span>
                    <span>Warm (28-35°C)</span>
                </div>
                <div className="map-legend-item">
                    <span className="legend-dot" style={{background: '#4ecdc4'}}></span>
                    <span>Moderate (10-28°C)</span>
                </div>
                <div className="map-legend-item">
                    <span className="legend-dot" style={{background: '#74b9ff'}}></span>
                    <span>Cold (&lt;10°C)</span>
                </div>
            </div>
            
            <div className="map-instructions">
                <p>💡 Click anywhere on the map to get weather data for that location</p>
            </div>
        </div>
    );
}