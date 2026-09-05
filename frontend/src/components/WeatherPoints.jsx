import React, { useState, useEffect } from 'react';
import { Trophy, Star, Zap, Award, Sparkles, Medal } from 'lucide-react';

export function WeatherPoints({ weather, onQuestionAsk }) {
    const [points, setPoints] = useState(() => {
        const saved = localStorage.getItem('weatherPoints');
        return saved ? parseInt(saved) : 0;
    });
    const [level, setLevel] = useState(() => {
        const saved = localStorage.getItem('weatherLevel');
        return saved ? parseInt(saved) : 1;
    });
    const [achievements, setAchievements] = useState(() => {
        const saved = localStorage.getItem('weatherAchievements');
        return saved ? JSON.parse(saved) : [];
    });
    const [showAchievement, setShowAchievement] = useState(null);
    
    useEffect(() => {
        localStorage.setItem('weatherPoints', points);
        localStorage.setItem('weatherLevel', level);
        localStorage.setItem('weatherAchievements', JSON.stringify(achievements));
    }, [points, level, achievements]);
    
    // Check for achievements
    useEffect(() => {
        const newAchievements = [];
        
        if (points >= 50 && !achievements.includes('first_50')) {
            newAchievements.push({ id: 'first_50', name: 'Weather Explorer', icon: '🌤️', desc: 'Earned 50 XP' });
        }
        if (points >= 100 && !achievements.includes('first_100')) {
            newAchievements.push({ id: 'first_100', name: 'Weather Master', icon: '🌈', desc: 'Earned 100 XP' });
        }
        if (points >= 250 && !achievements.includes('first_250')) {
            newAchievements.push({ id: 'first_250', name: 'Weather Guru', icon: '🏆', desc: 'Earned 250 XP' });
        }
        if (level >= 5 && !achievements.includes('level_5')) {
            newAchievements.push({ id: 'level_5', name: 'Level 5 Achieved!', icon: '⭐', desc: 'Reached Level 5' });
        }
        if (level >= 10 && !achievements.includes('level_10')) {
            newAchievements.push({ id: 'level_10', name: 'Weather Legend', icon: '👑', desc: 'Reached Level 10' });
        }
        
        if (newAchievements.length > 0) {
            setAchievements(prev => [...prev, ...newAchievements.map(a => a.id)]);
            // Show the newest achievement
            setShowAchievement(newAchievements[newAchievements.length - 1]);
            setTimeout(() => setShowAchievement(null), 5000);
        }
    }, [points, level]);
    
    // Award points when user asks a question
    useEffect(() => {
        if (onQuestionAsk) {
            const handleQuestion = () => {
                const earned = Math.floor(Math.random() * 5) + 2;
                setPoints(prev => prev + earned);
                if (points + earned > level * 100) {
                    setLevel(prev => prev + 1);
                }
            };
            // This would be triggered by the ask function
            window.awardWeatherPoints = handleQuestion;
        }
    }, [onQuestionAsk, points]);
    
    const nextLevelPoints = level * 100;
    const progress = Math.min(100, (points / nextLevelPoints) * 100);
    
    return (
        <div className="points-container-3d">
            <div className="points-display">
                <div className="points-header">
                    <Trophy size={18} color="#ffd93d" />
                    <span>Weather Explorer</span>
                    <span className="points-badge">🎯 {points} XP</span>
                </div>
                
                <div className="points-level-bar">
                    <div className="level-info">
                        <span>Level {level}</span>
                        <span>{points} / {nextLevelPoints} XP</span>
                    </div>
                    <div className="progress-bar">
                        <div className="progress-fill" style={{ width: `${progress}%` }} />
                    </div>
                </div>
                
                <div className="points-achievements">
                    {achievements.length > 0 && (
                        <div className="achievement-count">
                            <Award size={14} color="#ffd93d" />
                            <span>{achievements.length} Achievements</span>
                        </div>
                    )}
                    {achievements.slice(-2).map((ach, i) => (
                        <span key={i} className="achievement-badge">🏅 {ach}</span>
                    ))}
                </div>
            </div>
            
            {/* Achievement Popup */}
            {showAchievement && (
                <div className="achievement-popup">
                    <div className="achievement-content">
                        <span className="achievement-icon">{showAchievement.icon}</span>
                        <div>
                            <strong>{showAchievement.name}</strong>
                            <span>{showAchievement.desc}</span>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}