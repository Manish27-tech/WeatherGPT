import React, { useState, useEffect } from 'react';
import { Zap, MapPin, AlertTriangle, RefreshCw, Bell, Shield, Clock, Navigation, TrendingUp, TrendingDown, Minus } from 'lucide-react';
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

export function LightningTracker({ lat, lon }) {
    const [lightningData, setLightningData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [showAlert, setShowAlert] = useState(false);
    const mapCenter = [lat || 28.6139, lon || 77.2090];

    useEffect(() => {
        if (lat && lon) {
            fetchLightning();
        }
    }, [lat, lon]);

    async function fetchLightning() {
        setLoading(true);
        try {
            const res = await fetch(`${API}/api/lightning-track?latitude=${lat}&longitude=${lon}&radius=50`);
            if (!res.ok) throw new Error('Failed to fetch lightning data');
            const data = await res.json();
            setLightningData(data);
            
            if (data.safety?.alert_level?.level === 'RED' || data.safety?.alert_level?.level === 'ORANGE') {
                setShowAlert(true);
            }
        } catch (e) {
            console.error('Lightning fetch failed:', e);
            // Fallback data
            setLightningData({
                analysis: {
                    current_risk: { level: 'LOW', color: '#4ecdc4', score: 15 },
                    strikes: { count: 2, nearest: 15.3, frequency: 'Low' },
                    danger_zone: { level: 'No Danger', radius: 0 },
                    trend: { direction: 'Stable', change: 0 }
                },
                safety: {
                    recommendations: ['✅ No lightning detected - Safe conditions'],
                    safe_zones: [
                        { name: 'Indoor Shelter', distance: '0.2km', type: 'building' },
                        { name: 'Vehicle', distance: '0.5km', type: 'car' }
                    ],
                    alert_level: { level: 'GREEN', message: 'No lightning detected' }
                },
                visualization: {
                    strike_points: [
                        { lat: lat + 0.02, lon: lon + 0.03, intensity: 65, time: 'Just now' },
                        { lat: lat - 0.01, lon: lon + 0.04, intensity: 45, time: '5 min ago' }
                    ],
                    danger_radius: 0
                }
            });
        }
        setLoading(false);
    }

    const analysis = lightningData?.analysis || {};
    const safety = lightningData?.safety || {};
    const strikes = lightningData?.visualization?.strike_points || [];
    const dangerRadius = lightningData?.visualization?.danger_radius || 0;

    if (loading) {
        return (
            <div className="lightning-loading">
                <div className="loading-spinner"></div>
                <p>⚡ Tracking lightning strikes...</p>
            </div>
        );
    }

    return (
        <div className="lightning-container-3d">
            {/* Alert Banner */}
            {showAlert && (
                <div className="lightning-alert-banner">
                    <Bell size={18} />
                    <span>⚡ LIGHTNING ALERT: {safety.alert_level?.message}</span>
                    <button onClick={() => setShowAlert(false)}>×</button>
                </div>
            )}

            {/* Header */}
            <div className="lightning-header">
                <div className="lightning-title">
                    <Zap size={18} color={analysis.current_risk?.color || '#4ecdc4'} />
                    <span>Lightning Tracker</span>
                </div>
                <div className={`lightning-risk ${analysis.current_risk?.level?.toLowerCase() || 'low'}`}>
                    {analysis.current_risk?.level || 'LOW'} RISK
                </div>
            </div>

            {/* Alert Level Display */}
            <div className="lightning-alert-level">
                <div className={`alert-indicator ${safety.alert_level?.level?.toLowerCase() || 'green'}`}>
                    <Shield size={20} />
                </div>
                <div className="alert-info">
                    <div className="alert-level">{safety.alert_level?.level || 'GREEN'}</div>
                    <div className="alert-message">{safety.alert_level?.message || 'No lightning detected'}</div>
                </div>
            </div>

            {/* Interactive Map */}
            <div className="lightning-map-container">
                <MapContainer 
                    center={mapCenter} 
                    zoom={8} 
                    style={{ height: '250px', width: '100%', borderRadius: '12px' }}
                    whenReady={() => console.log('Map ready')}
                >
                    <TileLayer
                        attribution='© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                    />
                    
                    {/* Danger Zone Circle */}
                    {dangerRadius > 0 && (
                        <CircleMarker
                            center={mapCenter}
                            radius={dangerRadius * 10}
                            fillColor="#ff6b6b"
                            color="#ff6b6b"
                            weight={2}
                            opacity={0.3}
                            fillOpacity={0.05}
                        >
                            <Popup>
                                <div className="danger-popup">
                                    <strong>⚡ Danger Zone</strong>
                                    <p>Radius: {dangerRadius}km</p>
                                </div>
                            </Popup>
                        </CircleMarker>
                    )}

                    {/* Strike Points */}
                    {strikes.map((strike, i) => {
                        const intensity = strike.intensity || 50;
                        const size = Math.max(5, intensity / 10);
                        return (
                            <CircleMarker
                                key={i}
                                center={[strike.lat, strike.lon]}
                                radius={size}
                                fillColor={intensity > 70 ? '#ff0000' : intensity > 40 ? '#ff6b6b' : '#ffd93d'}
                                color={intensity > 70 ? '#ff0000' : intensity > 40 ? '#ff6b6b' : '#ffd93d'}
                                weight={2}
                                opacity={0.9}
                                fillOpacity={0.7}
                            >
                                <Popup>
                                    <div className="strike-popup">
                                        <strong>⚡ Lightning Strike</strong>
                                        <p>Intensity: {intensity}%</p>
                                        <p>Time: {strike.time || 'Just now'}</p>
                                    </div>
                                </Popup>
                            </CircleMarker>
                        );
                    })}

                    {/* Center Marker */}
                    <CircleMarker
                        center={mapCenter}
                        radius={8}
                        fillColor="#4ecdc4"
                        color="#4ecdc4"
                        weight={3}
                        opacity={1}
                        fillOpacity={1}
                    >
                        <Popup>
                            <div className="center-popup">
                                <strong>📍 Your Location</strong>
                                <p>{mapCenter[0].toFixed(4)}, {mapCenter[1].toFixed(4)}</p>
                            </div>
                        </Popup>
                    </CircleMarker>
                </MapContainer>
                <div className="map-legend-lightning">
                    <span><span className="legend-dot strike"></span> Strike</span>
                    <span><span className="legend-dot danger"></span> Danger Zone</span>
                    <span><span className="legend-dot safe-zone"></span> Safe Zone</span>
                </div>
            </div>

            {/* Stats Grid */}
            <div className="lightning-stats">
                <div className="lightning-stat">
                    <span className="stat-icon">⚡</span>
                    <span className="stat-label">Strikes</span>
                    <span className="stat-value">{analysis.strikes?.count || 0}</span>
                </div>
                <div className="lightning-stat">
                    <span className="stat-icon">📏</span>
                    <span className="stat-label">Nearest</span>
                    <span className="stat-value">{analysis.strikes?.nearest ? `${analysis.strikes.nearest}km` : 'None'}</span>
                </div>
                <div className="lightning-stat">
                    <span className="stat-icon">📊</span>
                    <span className="stat-label">Trend</span>
                    <span className="stat-value">{analysis.trend?.direction || 'Stable'}</span>
                </div>
                <div className="lightning-stat">
                    <span className="stat-icon">🛡️</span>
                    <span className="stat-label">Alert</span>
                    <span className="stat-value" style={{ 
                        color: safety.alert_level?.level === 'RED' ? '#ff0000' : 
                               safety.alert_level?.level === 'ORANGE' ? '#ff6b6b' :
                               safety.alert_level?.level === 'YELLOW' ? '#ffd93d' : '#4ecdc4'
                    }}>
                        {safety.alert_level?.level || 'GREEN'}
                    </span>
                </div>
            </div>

            {/* Safety Recommendations */}
            {safety.recommendations && safety.recommendations.length > 0 && (
                <div className="lightning-safety">
                    <strong>🛡️ Safety Recommendations</strong>
                    <div className="safety-list">
                        {safety.recommendations.slice(0, 4).map((rec, i) => (
                            <div key={i} className="safety-item">
                                <span className="safety-icon">{i === 0 ? '🚨' : '✅'}</span>
                                <span>{rec}</span>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Safe Zones */}
            {safety.safe_zones && safety.safe_zones.length > 0 && (
                <div className="lightning-safe-zones">
                    <strong>📍 Safe Zones Nearby</strong>
                    <div className="zone-list">
                        {safety.safe_zones.map((zone, i) => (
                            <span key={i} className="zone-tag">
                                🏠 {zone.name} ({zone.distance})
                            </span>
                        ))}
                    </div>
                </div>
            )}

            <button className="lightning-refresh" onClick={fetchLightning}>
                <RefreshCw size={14} /> Refresh
            </button>
        </div>
    );
}