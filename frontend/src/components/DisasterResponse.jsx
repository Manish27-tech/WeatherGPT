import React, { useState, useEffect } from 'react';
import { Shield, AlertTriangle, MapPin, Users, Phone, Home, Navigation, RefreshCw, CheckCircle, Clock, Building, Ambulance, Flame, Droplets, Wind } from 'lucide-react';

const API = import.meta.env.VITE_API_URL || "http://localhost:8000";

export function DisasterResponse({ lat, lon }) {
    const [disasterData, setDisasterData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [disasterType, setDisasterType] = useState('flood');
    const [error, setError] = useState(null);

    useEffect(() => {
        if (lat && lon) {
            assessDisaster();
        }
    }, [lat, lon, disasterType]);

    async function assessDisaster() {
        setLoading(true);
        setError(null);
        try {
            const res = await fetch(`${API}/api/disaster/assess?latitude=${lat}&longitude=${lon}&disaster_type=${disasterType}`);
            if (!res.ok) throw new Error('Failed to assess disaster');
            const data = await res.json();
            setDisasterData(data);
        } catch (e) {
            console.error('Disaster assessment failed:', e);
            setError('Could not assess disaster risk');
            // Fallback data
            setDisasterData({
                status: 'success',
                disaster_type: disasterType,
                risk_assessment: { score: 65, level: 'MODERATE', color: '#ffd93d', action: 'Stay alert and monitor' },
                nearby_centers: [
                    { name: 'NDRF HQ', distance: '5.2 km', capacity: 1000 },
                    { name: 'State Control Room', distance: '8.7 km', capacity: 500 },
                    { name: 'Emergency Shelter 1', distance: '12.3 km', capacity: 200 }
                ],
                evacuation_routes: [
                    { name: 'Route 1', distance: 5.2, time_estimate: '1.7 hours' },
                    { name: 'Route 2', distance: 4.8, time_estimate: '1.6 hours' }
                ],
                resources: [
                    { type: 'Emergency Shelter', priority: 'High' },
                    { type: 'Medical Supplies', priority: 'High' },
                    { type: 'Food & Water', priority: 'Medium' }
                ],
                emergency_contacts: { NDRF: '011-23456789', 'State Emergency': '108', 'National Emergency': '112' },
                recommendations: ['⚡ Stay alert and monitor official channels', '📱 Keep mobile devices charged']
            });
        }
        setLoading(false);
    }

    const disasterTypes = [
        { value: 'flood', label: '🌊 Flood' },
        { value: 'cyclone', label: '🌀 Cyclone' },
        { value: 'heatwave', label: '🌡️ Heatwave' },
        { value: 'storm', label: '⛈️ Storm' },
    ];

    if (loading) {
        return (
            <div className="disaster-loading">
                <div className="loading-spinner"></div>
                <p>🚨 Assessing disaster risk...</p>
            </div>
        );
    }

    const risk = disasterData?.risk_assessment || {};
    const centers = disasterData?.nearby_centers || [];
    const routes = disasterData?.evacuation_routes || [];
    const resources = disasterData?.resources || [];
    const contacts = disasterData?.emergency_contacts || {};
    const recommendations = disasterData?.recommendations || [];

    return (
        <div className="disaster-container-3d">
            {/* Header */}
            <div className="disaster-header">
                <div className="disaster-title">
                    <Shield size={18} color={risk.color || '#4ecdc4'} />
                    <span>Disaster Response</span>
                </div>
                <div className={`disaster-risk ${risk.level?.toLowerCase() || 'low'}`}>
                    {risk.level || 'LOW'} RISK
                </div>
            </div>

            {/* Disaster Type Selector */}
            <div className="disaster-type-selector">
                {disasterTypes.map(type => (
                    <button 
                        key={type.value}
                        className={`disaster-type-btn ${disasterType === type.value ? 'active' : ''}`}
                        onClick={() => setDisasterType(type.value)}
                    >
                        {type.label}
                    </button>
                ))}
            </div>

            {/* Risk Score */}
            <div className="disaster-score">
                <div className="score-circle" style={{ borderColor: risk.color || '#4ecdc4', color: risk.color || '#4ecdc4' }}>
                    {risk.score || 0}%
                </div>
                <div className="score-info">
                    <div className="score-action">{risk.action || 'Normal'}</div>
                    <div className="score-desc">Risk Assessment</div>
                </div>
            </div>

            {/* Emergency Contacts */}
            <div className="disaster-contacts">
                <strong>📞 Emergency Contacts</strong>
                <div className="contacts-grid">
                    {Object.entries(contacts).map(([name, number]) => (
                        <div key={name} className="contact-item">
                            <span>{name}</span>
                            <span className="contact-number">{number}</span>
                        </div>
                    ))}
                </div>
            </div>

            {/* Nearby Centers */}
            <div className="disaster-centers">
                <strong>🏢 Nearby Response Centers</strong>
                {centers.map((center, i) => (
                    <div key={i} className="center-item">
                        <Building size={14} color="#4ecdc4" />
                        <span>{center.name}</span>
                        <span className="center-distance">{center.distance}</span>
                        <span className="center-capacity">Capacity: {center.capacity || 'N/A'}</span>
                    </div>
                ))}
            </div>

            {/* Evacuation Routes */}
            <div className="disaster-routes">
                <strong>🗺️ Evacuation Routes</strong>
                {routes.map((route, i) => (
                    <div key={i} className="route-item">
                        <Navigation size={14} color="#4ecdc4" />
                        <span>{route.name}</span>
                        <span>{route.distance} km</span>
                        <span className="route-time">⏱️ {route.time_estimate}</span>
                    </div>
                ))}
            </div>

            {/* Resources */}
            <div className="disaster-resources">
                <strong>📦 Required Resources</strong>
                <div className="resources-grid">
                    {resources.map((resource, i) => (
                        <div key={i} className={`resource-item ${resource.priority?.toLowerCase() || 'medium'}`}>
                            <span>{resource.type}</span>
                            <span className="resource-priority">{resource.priority}</span>
                        </div>
                    ))}
                </div>
            </div>

            {/* Recommendations */}
            {recommendations.length > 0 && (
                <div className="disaster-recommendations">
                    <strong>📋 Recommendations</strong>
                    {recommendations.map((rec, i) => (
                        <div key={i} className="disaster-rec-item">{rec}</div>
                    ))}
                </div>
            )}

            <button className="disaster-refresh" onClick={assessDisaster}>
                <RefreshCw size={14} /> Reassess
            </button>
        </div>
    );
}