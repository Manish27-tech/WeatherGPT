import React, { useState, useEffect, useRef } from 'react';
import { AlertCircle, MapPin } from 'lucide-react';

const API = import.meta.env.VITE_API_URL || "http://localhost:8000";

export function RiskHeatmap({ lat, lon, weather, onClose }) {
    const [heatmapData, setHeatmapData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const canvasRef = useRef(null);

    useEffect(() => {
        if (lat && lon) {
            fetchHeatmap();
        }
    }, [lat, lon]);

    async function fetchHeatmap() {
        setLoading(true);
        setError(null);
        try {
            const url = `${API}/api/heatmap?latitude=${lat}&longitude=${lon}&radius=0.3`;
            console.log('Fetching heatmap from:', url);
            
            const res = await fetch(url);
            if (!res.ok) {
                throw new Error(`HTTP ${res.status}: ${await res.text()}`);
            }
            const data = await res.json();
            console.log('Heatmap data received:', data);
            setHeatmapData(data);
            
            // Draw after state update
            setTimeout(() => drawHeatmap(data), 100);
        } catch (e) {
            console.error('Heatmap fetch failed:', e);
            setError(e.message);
            // Generate fallback data
            const fallbackData = generateFallbackData(lat, lon);
            setHeatmapData(fallbackData);
            setTimeout(() => drawHeatmap(fallbackData), 100);
        }
        setLoading(false);
    }

    function generateFallbackData(lat, lon) {
        const grid = [];
        const size = 5;
        const step = 0.12;
        const startLat = lat - 0.24;
        const startLon = lon - 0.24;
        
        for (let i = 0; i < size; i++) {
            for (let j = 0; j < size; j++) {
                const gridLat = startLat + i * step;
                const gridLon = startLon + j * step;
                const distance = Math.sqrt(
                    (gridLat - lat)**2 + (gridLon - lon)**2
                );
                const risk = Math.max(0.1, Math.min(0.9, 
                    0.3 + 0.5 * Math.exp(-distance * 3) + 0.2 * Math.random()
                ));
                grid.push({
                    latitude: gridLat,
                    longitude: gridLon,
                    risk_score: risk,
                    risk_level: risk > 0.7 ? 'HIGH' : risk > 0.4 ? 'MODERATE' : 'LOW',
                    row: i,
                    col: j
                });
            }
        }
        return {
            grid: grid,
            center: { latitude: lat, longitude: lon },
            radius: 0.3,
            grid_size: 5,
            stats: {
                highest_risk: Math.max(...grid.map(g => g.risk_score)),
                lowest_risk: Math.min(...grid.map(g => g.risk_score)),
                average_risk: grid.reduce((s, g) => s + g.risk_score, 0) / grid.length,
                high_zones: grid.filter(g => g.risk_level === 'HIGH').length,
                moderate_zones: grid.filter(g => g.risk_level === 'MODERATE').length,
                low_zones: grid.filter(g => g.risk_level === 'LOW').length
            },
            timestamp: new Date().toISOString()
        };
    }

    function drawHeatmap(data) {
        const canvas = canvasRef.current;
        if (!canvas) {
            console.log('Canvas not ready');
            return;
        }
        
        const rect = canvas.parentElement.getBoundingClientRect();
        const size = Math.min(rect.width - 20, 500);
        canvas.width = size;
        canvas.height = size;
        
        const ctx = canvas.getContext('2d');
        const gridSize = data.grid_size || 5;
        const cellSize = size / gridSize;
        
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        // Draw background
        ctx.fillStyle = '#07110f';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        // Draw grid cells
        data.grid.forEach((cell) => {
            const row = cell.row || Math.floor(data.grid.indexOf(cell) / gridSize);
            const col = cell.col || data.grid.indexOf(cell) % gridSize;
            
            const x = col * cellSize;
            const y = row * cellSize;
            
            // Color based on risk
            let color;
            const risk = cell.risk_score;
            if (risk >= 0.7) {
                // Red gradient for high risk
                const intensity = (risk - 0.7) / 0.3;
                color = `rgba(255, ${Math.round(50 * (1 - intensity))}, ${Math.round(50 * (1 - intensity))}, ${0.7 + 0.3 * intensity})`;
            } else if (risk >= 0.4) {
                // Yellow/Orange for moderate risk
                const intensity = (risk - 0.4) / 0.3;
                color = `rgba(255, ${Math.round(200 + 55 * intensity)}, ${Math.round(50 * (1 - intensity))}, ${0.6 + 0.3 * intensity})`;
            } else {
                // Green for low risk
                const intensity = risk / 0.4;
                color = `rgba(${Math.round(50 + 205 * intensity)}, ${Math.round(200 + 55 * intensity)}, ${Math.round(200 + 55 * intensity)}, ${0.4 + 0.4 * intensity})`;
            }
            
            ctx.fillStyle = color;
            ctx.fillRect(x, y, cellSize, cellSize);
            
            // Border
            ctx.strokeStyle = 'rgba(255,255,255,0.08)';
            ctx.lineWidth = 1;
            ctx.strokeRect(x, y, cellSize, cellSize);
            
            // Risk percentage text
            if (cellSize > 40) {
                ctx.fillStyle = 'rgba(255,255,255,0.85)';
                ctx.font = `${Math.min(cellSize * 0.25, 14)}px Manrope, sans-serif`;
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                ctx.fillText(`${Math.round(risk * 100)}%`, x + cellSize/2, y + cellSize/2);
            }
        });
        
        // Draw center marker
        const centerX = Math.floor(gridSize / 2) * cellSize + cellSize/2;
        const centerY = Math.floor(gridSize / 2) * cellSize + cellSize/2;
        
        // Outer glow
        const gradient = ctx.createRadialGradient(centerX, centerY, 2, centerX, centerY, 20);
        gradient.addColorStop(0, 'rgba(255,255,255,0.9)');
        gradient.addColorStop(0.5, 'rgba(255,255,255,0.3)');
        gradient.addColorStop(1, 'rgba(255,255,255,0)');
        ctx.fillStyle = gradient;
        ctx.beginPath();
        ctx.arc(centerX, centerY, 20, 0, 2 * Math.PI);
        ctx.fill();
        
        // Center point
        ctx.fillStyle = '#ffffff';
        ctx.beginPath();
        ctx.arc(centerX, centerY, 6, 0, 2 * Math.PI);
        ctx.fill();
        
        ctx.fillStyle = '#000000';
        ctx.font = `${Math.min(cellSize * 0.2, 12)}px sans-serif`;
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText('📍', centerX, centerY + 1);
    }

    if (loading) {
        return (
            <div className="heatmap-loading">
                <div className="spinner"></div>
                <p>Generating risk heatmap...</p>
            </div>
        );
    }

    if (error) {
        return (
            <div className="heatmap-error">
                <AlertCircle size={24} color="#ff6b6b" />
                <p>Error loading heatmap: {error}</p>
                <button onClick={fetchHeatmap}>Retry</button>
            </div>
        );
    }

    const stats = heatmapData?.stats || {};

    return (
        <div className="heatmap-container">
            <div className="heatmap-canvas-wrapper">
                <canvas 
                    ref={canvasRef} 
                    className="heatmap-canvas"
                />
                <div className="heatmap-overlay-info">
                    <div className="heatmap-stats">
                        <div className="stat-item">
                            <span className="stat-label">Highest Risk</span>
                            <span className="stat-value" style={{color: stats.highest_risk >= 0.7 ? '#ff6b6b' : '#ffd93d'}}>
                                {stats.highest_risk ? Math.round(stats.highest_risk * 100) : 0}%
                            </span>
                        </div>
                        <div className="stat-item">
                            <span className="stat-label">Risk Zones</span>
                            <span className="stat-value">
                                {stats.high_zones || 0}
                            </span>
                        </div>
                        <div className="stat-item">
                            <span className="stat-label">Avg Risk</span>
                            <span className="stat-value">
                                {stats.average_risk ? Math.round(stats.average_risk * 100) : 0}%
                            </span>
                        </div>
                    </div>
                </div>
            </div>
            
            <div className="heatmap-legend">
                <div className="legend-item">
                    <span className="legend-color low"></span>
                    <span>Low Risk (0-40%)</span>
                </div>
                <div className="legend-item">
                    <span className="legend-color moderate"></span>
                    <span>Moderate Risk (40-70%)</span>
                </div>
                <div className="legend-item">
                    <span className="legend-color high"></span>
                    <span>High Risk (70-100%)</span>
                </div>
            </div>
            
            <div className="heatmap-info">
                <p>
                    <MapPin size={14} style={{display: 'inline', marginRight: '6px'}}/>
                    {lat.toFixed(4)}, {lon.toFixed(4)}
                </p>
                <p>
                    <AlertCircle size={14} style={{display: 'inline', marginRight: '6px'}}/>
                    {new Date(heatmapData?.timestamp || Date.now()).toLocaleTimeString()}
                </p>
            </div>
        </div>
    );
}