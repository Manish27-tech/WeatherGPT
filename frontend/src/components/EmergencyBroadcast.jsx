import React, { useState, useEffect } from 'react';
import { Bell, AlertTriangle, CheckCircle, RefreshCw, Send, Clock, Users, Radio, Shield, Zap, CloudRain, Wind, Sun } from 'lucide-react';

const API = import.meta.env.VITE_API_URL || "http://localhost:8000";

export function EmergencyBroadcast({ lat, lon }) {
    const [alertType, setAlertType] = useState('flood');
    const [intensity, setIntensity] = useState(50);
    const [message, setMessage] = useState('');
    const [activeAlerts, setActiveAlerts] = useState([]);
    const [alertHistory, setAlertHistory] = useState([]);
    const [loading, setLoading] = useState(false);
    const [broadcasting, setBroadcasting] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchAlerts();
    }, []);

    async function fetchAlerts() {
        setLoading(true);
        try {
            const res = await fetch(`${API}/api/emergency/alerts`);
            if (res.ok) {
                const data = await res.json();
                setActiveAlerts(data.alerts || []);
            }
            
            const historyRes = await fetch(`${API}/api/emergency/history?limit=5`);
            if (historyRes.ok) {
                const historyData = await historyRes.json();
                setAlertHistory(historyData.alerts || []);
            }
        } catch (e) {
            console.error('Failed to fetch alerts:', e);
            // Fallback data
            setActiveAlerts([
                { id: 1, severity: { level: 'HIGH', color: '#ff6b6b' }, message: 'Heavy rainfall warning for North India', timestamp: new Date().toISOString() }
            ]);
            setAlertHistory([
                { id: 1, severity: { level: 'MODERATE', color: '#ffd93d' }, message: 'Thunderstorm alert issued', timestamp: new Date(Date.now() - 3600000).toISOString() }
            ]);
        }
        setLoading(false);
    }

    async function broadcastAlert() {
        if (!message && !alertType) {
            alert('Please fill in alert details');
            return;
        }

        setBroadcasting(true);
        setError(null);

        const alertData = {
            type: alertType,
            intensity: intensity,
            message: message || `Emergency alert: ${alertType} warning issued`,
            latitude: lat,
            longitude: lon,
            location: 'Your location'
        };

        try {
            const res = await fetch(`${API}/api/emergency/broadcast`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(alertData)
            });

            if (!res.ok) throw new Error('Broadcast failed');

            const data = await res.json();
            setAlertHistory([data, ...alertHistory]);
            setMessage('');
            fetchAlerts();
        } catch (e) {
            console.error('Broadcast failed:', e);
            setError('Failed to broadcast alert');
        }
        setBroadcasting(false);
    }

    const alertTypes = [
        { value: 'flood', label: '🌊 Flood', icon: <CloudRain size={16} /> },
        { value: 'cyclone', label: '🌀 Cyclone', icon: <Wind size={16} /> },
        { value: 'heatwave', label: '🌡️ Heatwave', icon: <Sun size={16} /> },
        { value: 'storm', label: '⛈️ Storm', icon: <Zap size={16} /> },
        { value: 'lightning', label: '⚡ Lightning', icon: <Zap size={16} /> },
        { value: 'heavy_rain', label: '🌧️ Heavy Rain', icon: <CloudRain size={16} /> },
    ];

    return (
        <div className="emergency-container-3d">
            {/* Active Alerts */}
            <div className="emergency-active">
                <div className="emergency-header">
                    <Bell size={18} color="#ff6b6b" />
                    <span>Active Alerts</span>
                    <span className="alert-count">{activeAlerts.length}</span>
                </div>
                {activeAlerts.length > 0 ? (
                    activeAlerts.map((alert, i) => (
                        <div key={i} className="active-alert" style={{ borderColor: alert.severity?.color || '#ffd93d' }}>
                            <span className="alert-dot" style={{ background: alert.severity?.color || '#ffd93d' }}></span>
                            <span className="alert-message">{alert.message}</span>
                            <span className="alert-time">{new Date(alert.timestamp).toLocaleTimeString()}</span>
                        </div>
                    ))
                ) : (
                    <div className="no-alerts">✅ No active alerts</div>
                )}
            </div>

            {/* Broadcast Form */}
            <div className="emergency-broadcast">
                <div className="broadcast-header">
                    <Radio size={16} color="#4ecdc4" />
                    <span>Broadcast Alert</span>
                </div>

                <div className="broadcast-form">
                    <div className="form-group">
                        <label>Alert Type</label>
                        <select value={alertType} onChange={(e) => setAlertType(e.target.value)}>
                            {alertTypes.map(type => (
                                <option key={type.value} value={type.value}>{type.label}</option>
                            ))}
                        </select>
                    </div>

                    <div className="form-group">
                        <label>Intensity: {intensity}%</label>
                        <input 
                            type="range" 
                            min="10" 
                            max="100" 
                            value={intensity} 
                            onChange={(e) => setIntensity(parseInt(e.target.value))}
                            className="intensity-slider"
                            style={{ 
                                background: `linear-gradient(to right, #4ecdc4 ${intensity}%, #1a2a3a ${intensity}%)`
                            }}
                        />
                        <div className="intensity-labels">
                            <span>Low</span>
                            <span>High</span>
                        </div>
                    </div>

                    <div className="form-group">
                        <label>Message</label>
                        <textarea 
                            value={message} 
                            onChange={(e) => setMessage(e.target.value)}
                            placeholder="Enter emergency message..."
                            rows={2}
                        />
                    </div>

                    <button 
                        className="broadcast-btn" 
                        onClick={broadcastAlert} 
                        disabled={broadcasting}
                    >
                        {broadcasting ? '⏳ Broadcasting...' : '📢 Broadcast Alert'}
                    </button>

                    {error && (
                        <div className="broadcast-error">
                            <AlertTriangle size={14} color="#ff6b6b" />
                            <span>{error}</span>
                        </div>
                    )}
                </div>
            </div>

            {/* Alert History */}
            <div className="emergency-history">
                <div className="history-header">
                    <Clock size={14} color="#7fa79b" />
                    <span>Recent Alerts</span>
                </div>
                {alertHistory.length > 0 ? (
                    alertHistory.slice(0, 5).map((alert, i) => (
                        <div key={i} className="history-item">
                            <span className={`history-severity ${alert.severity?.level?.toLowerCase() || 'moderate'}`}>
                                {alert.severity?.level || 'MODERATE'}
                            </span>
                            <span className="history-message">{alert.message}</span>
                            <span className="history-time">{new Date(alert.timestamp).toLocaleTimeString()}</span>
                        </div>
                    ))
                ) : (
                    <div className="no-history">No alert history</div>
                )}
            </div>

            <button className="emergency-refresh" onClick={fetchAlerts}>
                <RefreshCw size={14} /> Refresh
            </button>
        </div>
    );
}