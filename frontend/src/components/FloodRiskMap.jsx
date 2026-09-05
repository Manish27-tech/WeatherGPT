import React, { useState, useEffect, useRef } from 'react';
import { AlertTriangle, MapPin, Droplets, Wind, Thermometer, RefreshCw, Bell, AlertCircle, Shield, Home, Navigation, Waves } from 'lucide-react';
import { MapContainer, TileLayer, CircleMarker, Popup, Polyline, useMap } from 'react-leaflet';
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

function FloodMapView({ center, zoom, riskData, waterBodies, evacuationZones }) {
    const map = useMap();
    
    useEffect(() => {
        if (center) {
            map.setView(center, zoom || 10);
        }
    }, [center, map]);

    return (
        <>
            {/* Risk Zones - Colored circles */}
            {riskData?.risk_grid?.map((point, i) => {
                const risk = point.risk || 30;
                const color = risk > 70 ? '#ff0000' : risk > 50 ? '#ff6b6b' : risk > 30 ? '#ffd93d' : '#4ecdc4';
                return (
                    <CircleMarker
                        key={i}
                        center={[point.lat, point.lon]}
                        radius={Math.max(5, risk / 10)}
                        fillColor={color}
                        color={color}
                        weight={1}
                        opacity={0.8}
                        fillOpacity={0.6}
                    >
                        <Popup>
                            <div className="flood-popup">
                                <strong>Risk: {risk}%</strong>
                                <p>Location: {point.lat.toFixed(4)}, {point.lon.toFixed(4)}</p>
                            </div>
                        </Popup>
                    </CircleMarker>
                );
            })}

            {/* Evacuation Zones */}
            {evacuationZones?.safe_zones?.map((zone, i) => (
                <CircleMarker
                    key={`evac-${i}`}
                    center={[
                        center[0] + (i * 0.02),
                        center[1] + (i * 0.015)
                    ]}
                    radius={15}
                    fillColor="#2ecc71"
                    color="#2ecc71"
                    weight={2}
                    opacity={0.8}
                    fillOpacity={0.3}
                >
                    <Popup>
                        <div className="evac-popup">
                            <strong>🛡️ {zone.name}</strong>
                            <p>Distance: {zone.distance}</p>
                            <p>Direction: {zone.direction}</p>
                        </div>
                    </Popup>
                </CircleMarker>
            ))}

            {/* Water Bodies */}
            {waterBodies?.name && waterBodies?.name !== "No major water body nearby" && (
                <CircleMarker
                    center={[
                        center[0] + 0.03,
                        center[1] + 0.02
                    ]}
                    radius={20}
                    fillColor="#3498db"
                    color="#3498db"
                    weight={2}
                    opacity={0.6}
                    fillOpacity={0.2}
                >
                    <Popup>
                        <div className="water-popup">
                            <strong>🌊 {waterBodies.name}</strong>
                            <p>Distance: {waterBodies.distance}km</p>
                            <p>Risk Level: {waterBodies.risk_level}</p>
                        </div>
                    </Popup>
                </CircleMarker>
            )}
        </>
    );
}

export function FloodRiskMap({ lat, lon, locationName }) {
    const [floodData, setFloodData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [showAlert, setShowAlert] = useState(false);
    const mapCenter = [lat || 28.6139, lon || 77.2090];

    useEffect(() => {
        if (lat && lon) {
            fetchFloodRisk();
        }
    }, [lat, lon]);

    async function fetchFloodRisk() {
        setLoading(true);
        setError(null);
        try {
            const res = await fetch(`${API}/api/flood-risk?latitude=${lat}&longitude=${lon}&name=${locationName || ''}`);
            if (!res.ok) throw new Error('Failed to fetch flood risk');
            const data = await res.json();
            setFloodData(data);
            
            // Show alert if high risk
            if (data.risk_assessment?.level === 'HIGH' || data.risk_assessment?.level === 'CRITICAL') {
                setShowAlert(true);
            }
        } catch (e) {
            console.error('Flood risk fetch failed:', e);
            setError('Could not fetch flood risk data');
            // Fallback data for demo
            setFloodData({
                analysis: {
                    elevation: { value: 15, level: 'Medium Risk' },
                    rainfall: { last_24h: 12.5, forecast_7d: 45.2, trend: 'Increasing' },
                    water_bodies: { name: 'Ganges River', distance: 15.2, risk_level: 'Medium' }
                },
                risk_assessment: {
                    overall_score: 45,
                    level: 'MODERATE',
                    color: '#ffd93d',
                    urgency: 'Monitor conditions closely'
                },
                recommendations: [
                    '⚡ Prepare for possible flooding',
                    '📦 Pack emergency supplies',
                    '🔒 Secure important documents',
                    '📱 Keep emergency contacts ready'
                ],
                evacuation_plan: {
                    required: false,
                    priority: 'LOW',
                    safe_zones: [
                        { name: 'Higher Ground', distance: '2.5km', direction: 'North-East' },
                        { name: 'Community Shelter', distance: '3.2km', direction: 'West' }
                    ]
                },
                visualization_data: {
                    risk_grid: [
                        { lat: lat + 0.01, lon: lon + 0.02, risk: 65 },
                        { lat: lat - 0.01, lon: lon + 0.01, risk: 45 },
                        { lat: lat + 0.02, lon: lon - 0.01, risk: 75 },
                        { lat: lat - 0.02, lon: lon - 0.02, risk: 35 },
                        { lat: lat + 0.015, lon: lon + 0.015, risk: 55 },
                        { lat: lat - 0.015, lon: lon - 0.015, risk: 40 },
                        { lat: lat + 0.025, lon: lon + 0.005, risk: 80 },
                        { lat: lat - 0.025, lon: lon + 0.025, risk: 30 },
                    ]
                }
            });
        }
        setLoading(false);
    }

    const risk = floodData?.risk_assessment || {};
    const analysis = floodData?.analysis || {};
    const recommendations = floodData?.recommendations || [];
    const evacuation = floodData?.evacuation_plan || {};
    const riskGrid = floodData?.visualization_data?.risk_grid || [];

    if (loading) {
        return (
            <div className="flood-loading">
                <div className="loading-spinner"></div>
                <p>🌊 Analyzing flood risk...</p>
            </div>
        );
    }

    if (error) {
        return (
            <div className="flood-error">
                <AlertTriangle size={24} color="#ff6b6b" />
                <span>{error}</span>
                <button onClick={fetchFloodRisk}>Retry</button>
            </div>
        );
    }

    return (
        <div className="flood-container-3d">
            {/* Alert Banner */}
            {showAlert && (
                <div className="flood-alert-banner">
                    <Bell size={18} />
                    <span>⚠️ FLOOD WARNING: {risk.level} risk detected in your area!</span>
                    <button onClick={() => setShowAlert(false)}>×</button>
                </div>
            )}

            {/* Header */}
            <div className="flood-header">
                <div className="flood-title">
                    <Waves size={18} color={risk.color || '#4ecdc4'} />
                    <span>Flood Risk Analysis</span>
                </div>
                <div className={`flood-risk-badge ${risk.level?.toLowerCase() || 'low'}`}>
                    {risk.level || 'LOW'} RISK
                </div>
            </div>

            {/* Risk Score Display */}
            <div className="flood-score-display">
                <div className="score-circle" style={{ borderColor: risk.color, color: risk.color }}>
                    {risk.overall_score || 0}%
                </div>
                <div className="score-info">
                    <div className="score-label">Flood Risk Score</div>
                    <div className="score-status">{risk.urgency || 'Normal'}</div>
                </div>
            </div>

            {/* Interactive Map */}
            <div className="flood-map-container">
                <MapContainer 
                    center={mapCenter} 
                    zoom={10} 
                    style={{ height: '280px', width: '100%', borderRadius: '12px' }}
                >
                    <TileLayer
                        attribution='© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                    />
                    <FloodMapView 
                        center={mapCenter}
                        zoom={10}
                        riskData={{ risk_grid: riskGrid }}
                        waterBodies={analysis.water_bodies}
                        evacuationZones={evacuation}
                    />
                </MapContainer>
                <div className="map-legend-flood">
                    <span><span className="legend-dot high"></span> High Risk</span>
                    <span><span className="legend-dot moderate"></span> Moderate Risk</span>
                    <span><span className="legend-dot low"></span> Low Risk</span>
                    <span><span className="legend-dot safe"></span> Safe Zone</span>
                </div>
            </div>

            {/* Metrics Grid */}
            <div className="flood-metrics">
                <div className="flood-metric">
                    <span className="metric-icon">📏</span>
                    <span className="metric-label">Elevation</span>
                    <span className="metric-value">{analysis.elevation?.value || 0}m</span>
                    <span className="metric-status">{analysis.elevation?.level || 'Unknown'}</span>
                </div>
                <div className="flood-metric">
                    <span className="metric-icon">🌧️</span>
                    <span className="metric-label">24h Rainfall</span>
                    <span className="metric-value">{analysis.rainfall?.last_24h || 0}mm</span>
                    <span className="metric-status">{analysis.rainfall?.trend || 'Stable'}</span>
                </div>
                <div className="flood-metric">
                    <span className="metric-icon">📅</span>
                    <span className="metric-label">7-Day Forecast</span>
                    <span className="metric-value">{analysis.rainfall?.forecast_7d || 0}mm</span>
                    <span className="metric-status">Expected</span>
                </div>
                <div className="flood-metric">
                    <span className="metric-icon">🌊</span>
                    <span className="metric-label">Water Body</span>
                    <span className="metric-value">{analysis.water_bodies?.name || 'None'}</span>
                    <span className="metric-status">{analysis.water_bodies?.risk_level || 'Safe'}</span>
                </div>
            </div>

            {/* Recommendations */}
            {recommendations.length > 0 && (
                <div className="flood-recommendations">
                    <strong>📋 Recommendations</strong>
                    <div className="rec-list">
                        {recommendations.slice(0, 4).map((rec, i) => (
                            <div key={i} className="flood-rec-item">
                                <span className="rec-icon">{i === 0 ? '🚨' : '✅'}</span>
                                <span>{rec}</span>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Evacuation Info */}
            {evacuation.required && (
                <div className="flood-evacuation">
                    <AlertTriangle size={18} color="#ff6b6b" />
                    <div>
                        <strong>⚠️ Evacuation Advisory</strong>
                        <p>Priority: {evacuation.priority}</p>
                        <div className="safe-zones">
                            {evacuation.safe_zones?.map((zone, i) => (
                                <span key={i} className="safe-zone-tag">
                                    🏠 {zone.name} ({zone.distance})
                                </span>
                            ))}
                        </div>
                    </div>
                </div>
            )}

            <button className="flood-refresh" onClick={fetchFloodRisk}>
                <RefreshCw size={14} /> Refresh Data
            </button>
        </div>
    );
}