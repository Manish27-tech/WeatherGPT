import React, { useEffect, useRef } from 'react';
import { LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer, BarChart, Bar, ComposedChart } from 'recharts';

export function WeatherCharts({ weatherData }) {
    // Prepare data for all charts
    const hourlyData = weatherData?.hourly || {};
    const times = hourlyData.time || [];
    const temps = hourlyData.temperature_2m || [];
    const humidity = hourlyData.relative_humidity_2m || [];
    const rainfall = hourlyData.precipitation || [];
    const windSpeed = hourlyData.wind_speed_10m || [];
    const rainProb = hourlyData.precipitation_probability || [];

    // Create chart data for 24 hours
    const chartData = times.slice(0, 24).map((time, i) => ({
        time: time ? new Date(time).getHours() + ':00' : i + ':00',
        hour: i,
        temperature: Math.round(temps[i] || 0),
        humidity: Math.round(humidity[i] || 0),
        rainfall: Math.round((rainfall[i] || 0) * 10) / 10,
        windSpeed: Math.round((windSpeed[i] || 0) * 10) / 10,
        rainProbability: Math.round(rainProb[i] || 0),
    }));

    // Get current weather metrics
    const current = weatherData?.current || {};
    const currentTemp = Math.round(current.temperature_2m || 0);
    const currentHumidity = Math.round(current.relative_humidity_2m || 0);
    const currentRain = Math.round((current.rain || 0) * 10) / 10;
    const currentWind = Math.round((current.wind_speed_10m || 0) * 10) / 10;

    if (!chartData || chartData.length === 0) {
        return (
            <div className="chart-empty-3d">
                <div className="chart-empty-icon">📊</div>
                <p>No chart data available</p>
                <span>Weather data will appear here once available</span>
            </div>
        );
    }

    // Calculate stats
    const maxTemp = Math.max(...chartData.map(d => d.temperature));
    const minTemp = Math.min(...chartData.map(d => d.temperature));
    const avgTemp = Math.round(chartData.reduce((a, b) => a + b.temperature, 0) / chartData.length);
    const maxHumidity = Math.max(...chartData.map(d => d.humidity));
    const minHumidity = Math.min(...chartData.map(d => d.humidity));
    const totalRain = chartData.reduce((a, b) => a + b.rainfall, 0);
    const maxWind = Math.max(...chartData.map(d => d.windSpeed));

    // Find peak rain time
    const peakRain = chartData.reduce((a, b) => a.rainfall > b.rainfall ? a : b, { rainfall: 0 });
    const rainHours = chartData.filter(d => d.rainfall > 0.5);

    return (
        <div className="charts-container-3d">
            {/* Current Weather Summary */}
            <div className="weather-summary-3d">
                <div className="summary-item">
                    <span className="summary-icon">🌡️</span>
                    <span className="summary-label">Temperature</span>
                    <span className="summary-value">{currentTemp}°C</span>
                </div>
                <div className="summary-item">
                    <span className="summary-icon">💧</span>
                    <span className="summary-label">Humidity</span>
                    <span className="summary-value">{currentHumidity}%</span>
                </div>
                <div className="summary-item">
                    <span className="summary-icon">🌧️</span>
                    <span className="summary-label">Rainfall</span>
                    <span className="summary-value">{currentRain}mm</span>
                </div>
                <div className="summary-item">
                    <span className="summary-icon">💨</span>
                    <span className="summary-label">Wind</span>
                    <span className="summary-value">{currentWind} km/h</span>
                </div>
            </div>

            {/* Chart 1: Temperature Trend */}
            <div className="chart-card-3d">
                <div className="chart-header-3d">
                    <div className="chart-title-3d">
                        <span className="chart-icon">🌡️</span>
                        <span>24-Hour Temperature Trend</span>
                    </div>
                    <div className="chart-stats-3d">
                        <span className="stat-high">High: {maxTemp}°C</span>
                        <span className="stat-low">Low: {minTemp}°C</span>
                        <span className="stat-avg">Avg: {avgTemp}°C</span>
                    </div>
                </div>
                <div className="chart-wrapper-3d">
                    <ResponsiveContainer width="100%" height={180}>
                        <LineChart data={chartData}>
                            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                            <XAxis 
                                dataKey="time" 
                                stroke="rgba(127,167,155,0.3)" 
                                fontSize={9} 
                                interval={3}
                                tick={{ fill: 'rgba(127,167,155,0.5)' }}
                            />
                            <YAxis 
                                stroke="rgba(127,167,155,0.3)" 
                                fontSize={9}
                                tick={{ fill: 'rgba(127,167,155,0.5)' }}
                                domain={['auto', 'auto']}
                            />
                            <Tooltip 
                                contentStyle={{ 
                                    background: 'rgba(15,25,45,0.95)', 
                                    border: '1px solid rgba(78,205,196,0.15)',
                                    borderRadius: '10px',
                                    color: '#eaf7f2',
                                    fontSize: '12px'
                                }}
                                labelStyle={{ color: '#4ecdc4' }}
                            />
                            <Line 
                                type="monotone" 
                                dataKey="temperature" 
                                stroke="#4ecdc4" 
                                strokeWidth={2.5}
                                dot={{ fill: '#4ecdc4', r: 3 }}
                                activeDot={{ r: 6, fill: '#4ecdc4' }}
                            />
                        </LineChart>
                    </ResponsiveContainer>
                </div>
            </div>

            {/* Chart 2: Humidity Trend */}
            <div className="chart-card-3d">
                <div className="chart-header-3d">
                    <div className="chart-title-3d">
                        <span className="chart-icon">💧</span>
                        <span>24-Hour Humidity Trend</span>
                    </div>
                    <div className="chart-stats-3d">
                        <span className="stat-high">High: {maxHumidity}%</span>
                        <span className="stat-low">Low: {minHumidity}%</span>
                        <span className="stat-avg">Avg: {Math.round(chartData.reduce((a,b) => a + b.humidity, 0) / chartData.length)}%</span>
                    </div>
                </div>
                <div className="chart-wrapper-3d">
                    <ResponsiveContainer width="100%" height={150}>
                        <LineChart data={chartData}>
                            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                            <XAxis 
                                dataKey="time" 
                                stroke="rgba(127,167,155,0.3)" 
                                fontSize={9} 
                                interval={3}
                                tick={{ fill: 'rgba(127,167,155,0.5)' }}
                            />
                            <YAxis 
                                stroke="rgba(127,167,155,0.3)" 
                                fontSize={9}
                                tick={{ fill: 'rgba(127,167,155,0.5)' }}
                                domain={[0, 100]}
                            />
                            <Tooltip 
                                contentStyle={{ 
                                    background: 'rgba(15,25,45,0.95)', 
                                    border: '1px solid rgba(78,205,196,0.15)',
                                    borderRadius: '10px',
                                    color: '#eaf7f2',
                                    fontSize: '12px'
                                }}
                                labelStyle={{ color: '#4ecdc4' }}
                            />
                            <Line 
                                type="monotone" 
                                dataKey="humidity" 
                                stroke="#ffd93d" 
                                strokeWidth={2.5}
                                dot={{ fill: '#ffd93d', r: 3 }}
                                activeDot={{ r: 6, fill: '#ffd93d' }}
                            />
                        </LineChart>
                    </ResponsiveContainer>
                </div>
            </div>

            {/* Chart 3: Rainfall & Probability (Combo Chart) */}
            <div className="chart-card-3d">
                <div className="chart-header-3d">
                    <div className="chart-title-3d">
                        <span className="chart-icon">🌧️</span>
                        <span>Rainfall & Probability</span>
                    </div>
                    <div className="chart-stats-3d">
                        <span className="stat-rain">Total: {totalRain.toFixed(1)}mm</span>
                        {peakRain.rainfall > 0 && (
                            <span className="stat-peak">Peak: {peakRain.rainfall}mm</span>
                        )}
                        <span className="stat-hours">{rainHours.length}h of rain</span>
                    </div>
                </div>
                <div className="chart-wrapper-3d">
                    <ResponsiveContainer width="100%" height={160}>
                        <ComposedChart data={chartData}>
                            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                            <XAxis 
                                dataKey="time" 
                                stroke="rgba(127,167,155,0.3)" 
                                fontSize={9} 
                                interval={3}
                                tick={{ fill: 'rgba(127,167,155,0.5)' }}
                            />
                            <YAxis 
                                stroke="rgba(127,167,155,0.3)" 
                                fontSize={9}
                                tick={{ fill: 'rgba(127,167,155,0.5)' }}
                                yAxisId="left"
                            />
                            <YAxis 
                                stroke="rgba(127,167,155,0.3)" 
                                fontSize={9}
                                tick={{ fill: 'rgba(127,167,155,0.5)' }}
                                yAxisId="right"
                                orientation="right"
                                domain={[0, 100]}
                            />
                            <Tooltip 
                                contentStyle={{ 
                                    background: 'rgba(15,25,45,0.95)', 
                                    border: '1px solid rgba(78,205,196,0.15)',
                                    borderRadius: '10px',
                                    color: '#eaf7f2',
                                    fontSize: '12px'
                                }}
                                labelStyle={{ color: '#4ecdc4' }}
                            />
                            <Bar 
                                dataKey="rainfall" 
                                fill="rgba(78,205,196,0.4)"
                                yAxisId="left"
                                radius={[4, 4, 0, 0]}
                            />
                            <Line 
                                type="monotone" 
                                dataKey="rainProbability" 
                                stroke="#ff6b6b" 
                                strokeWidth={2}
                                dot={{ fill: '#ff6b6b', r: 2 }}
                                yAxisId="right"
                            />
                        </ComposedChart>
                    </ResponsiveContainer>
                </div>
                <div className="chart-legend-3d">
                    <span><span className="legend-bar" style={{background: 'rgba(78,205,196,0.4)'}}></span> Rainfall (mm)</span>
                    <span><span className="legend-line" style={{background: '#ff6b6b'}}></span> Rain Probability (%)</span>
                </div>
            </div>

            {/* Chart 4: Wind Speed Trend */}
            <div className="chart-card-3d">
                <div className="chart-header-3d">
                    <div className="chart-title-3d">
                        <span className="chart-icon">💨</span>
                        <span>24-Hour Wind Speed</span>
                    </div>
                    <div className="chart-stats-3d">
                        <span className="stat-high">Max: {maxWind} km/h</span>
                        <span className="stat-avg">Avg: {Math.round(chartData.reduce((a,b) => a + b.windSpeed, 0) / chartData.length)} km/h</span>
                    </div>
                </div>
                <div className="chart-wrapper-3d">
                    <ResponsiveContainer width="100%" height={150}>
                        <LineChart data={chartData}>
                            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                            <XAxis 
                                dataKey="time" 
                                stroke="rgba(127,167,155,0.3)" 
                                fontSize={9} 
                                interval={3}
                                tick={{ fill: 'rgba(127,167,155,0.5)' }}
                            />
                            <YAxis 
                                stroke="rgba(127,167,155,0.3)" 
                                fontSize={9}
                                tick={{ fill: 'rgba(127,167,155,0.5)' }}
                                domain={[0, 'auto']}
                            />
                            <Tooltip 
                                contentStyle={{ 
                                    background: 'rgba(15,25,45,0.95)', 
                                    border: '1px solid rgba(78,205,196,0.15)',
                                    borderRadius: '10px',
                                    color: '#eaf7f2',
                                    fontSize: '12px'
                                }}
                                labelStyle={{ color: '#4ecdc4' }}
                            />
                            <Line 
                                type="monotone" 
                                dataKey="windSpeed" 
                                stroke="#74b9ff" 
                                strokeWidth={2.5}
                                dot={{ fill: '#74b9ff', r: 3 }}
                                activeDot={{ r: 6, fill: '#74b9ff' }}
                            />
                        </LineChart>
                    </ResponsiveContainer>
                </div>
            </div>

            {/* Weather Summary Cards */}
            <div className="weather-insights-3d">
                <div className="insight-card">
                    <div className="insight-icon">🌡️</div>
                    <div className="insight-content">
                        <span className="insight-label">Temperature Range</span>
                        <span className="insight-value">{minTemp}°C - {maxTemp}°C</span>
                    </div>
                </div>
                <div className="insight-card">
                    <div className="insight-icon">💧</div>
                    <div className="insight-content">
                        <span className="insight-label">Humidity Range</span>
                        <span className="insight-value">{minHumidity}% - {maxHumidity}%</span>
                    </div>
                </div>
                <div className="insight-card">
                    <div className="insight-icon">🌧️</div>
                    <div className="insight-content">
                        <span className="insight-label">Total Rainfall</span>
                        <span className="insight-value">{totalRain.toFixed(1)} mm</span>
                    </div>
                </div>
                <div className="insight-card">
                    <div className="insight-icon">💨</div>
                    <div className="insight-content">
                        <span className="insight-label">Max Wind</span>
                        <span className="insight-value">{maxWind} km/h</span>
                    </div>
                </div>
            </div>
        </div>
    );
}