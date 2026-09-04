import React, { useState } from 'react';

export function CropDisease({ lat, lon }) {
    const [diseases, setDiseases] = useState(null);
    const [loading, setLoading] = useState(false);
    
    async function checkDiseases() {
        setLoading(true);
        try {
            const res = await fetch(`/api/crop/disease?latitude=${lat}&longitude=${lon}`);
            const data = await res.json();
            setDiseases(data);
        } catch (e) {
            console.error('Disease check failed:', e);
        }
        setLoading(false);
    }
    
    return (
        <div className="crop-disease-panel">
            <h3>🌾 Crop Disease Risk</h3>
            <button onClick={checkDiseases} disabled={loading}>
                {loading ? 'Analyzing...' : 'Check Crops'}
            </button>
            
            {diseases && (
                <div className="disease-results">
                    {diseases.disease_risks.map((d, i) => (
                        <div key={i} className={`disease-card ${d.level.toLowerCase()}`}>
                            <span className="disease-icon">{d.icon}</span>
                            <div>
                                <h4>{d.name}</h4>
                                <span className={`risk-badge ${d.level.toLowerCase()}`}>
                                    {d.level} RISK
                                </span>
                                <p>{d.description}</p>
                                <small>Treatment: {d.treatment}</small>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}