import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';

export function MLPrediction({ lat, lon }) {
    const [predictions, setPredictions] = useState(null);
    const [loading, setLoading] = useState(false);
    
    useEffect(() => {
        fetchPredictions();
    }, [lat, lon]);
    
    async function fetchPredictions() {
        setLoading(true);
        try {
            const res = await fetch(`/api/ml/predict?latitude=${lat}&longitude=${lon}&hours=12`);
            const data = await res.json();
            setPredictions(data);
        } catch (e) {
            console.error('Prediction failed:', e);
        }
        setLoading(false);
    }
    
    if (!predictions) return <div>Loading predictions...</div>;
    
    return (
        <div className="ml-prediction-panel">
            <h3>🤖 AI Weather Prediction</h3>
            <div className="accuracy-badge">
                Accuracy: {(predictions.accuracy_score * 100).toFixed(1)}%
            </div>
            <div className="chart-container">
                <LineChart width={600} height={300} data={predictions.predictions}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="hour" />
                    <YAxis />
                    <Tooltip />
                    <Line type="monotone" dataKey="temperature" stroke="#8884d8" />
                </LineChart>
            </div>
            <div className="prediction-grid">
                {predictions.predictions.slice(0, 6).map((p, i) => (
                    <div key={i} className="prediction-card">
                        <span>+{p.hour}h</span>
                        <strong>{p.temperature}°C</strong>
                        <small>Conf: {(p.confidence * 100).toFixed(0)}%</small>
                    </div>
                ))}
            </div>
        </div>
    );
}