import React, {useEffect, useState, useRef, Suspense} from "react";
import {createRoot} from "react-dom/client";
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Float, Sparkles, Stars } from '@react-three/drei';
import { motion, AnimatePresence } from 'framer-motion';
import {
  CloudSun, MapPin, Mic, Send, ShieldAlert, Sprout, Car, 
  Radio, Languages, RefreshCw, CheckCircle2, TrendingUp, 
  TrendingDown, Minus, AlertTriangle, Bell, Thermometer,
  Droplets, Wind, CloudRain, Map, Activity, Calendar,
  Eye, Gauge, Compass, Cloud, Sun, Moon, Search
} from "lucide-react";
import { RiskHeatmap } from './components/RiskHeatmap';
import { InteractiveMap } from './components/InteractiveMap';
import { WeatherCharts } from './components/WeatherCharts';
import "./styles.css";

const API = import.meta.env.VITE_API_URL || "http://localhost:8000";

const demoLocations = [
  {name:"Ludhiana", latitude:30.9010, longitude:75.8573},
  {name:"New Delhi", latitude:28.6139, longitude:77.2090},
  {name:"Mumbai", latitude:19.0760, longitude:72.8777},
  {name:"Kolkata", latitude:22.5726, longitude:88.3639},
];

// ==================== 3D WEATHER SCENE ====================
function WeatherScene({ weather, isNight }) {
  const [rainParticles, setRainParticles] = useState([]);
  const rain = weather?.current?.rain || 0;
  
  useEffect(() => {
    if (rain > 0.5) {
      const count = Math.min(Math.floor(rain * 50), 300);
      const positions = [];
      for (let i = 0; i < count; i++) {
        positions.push(
          (Math.random() - 0.5) * 20,
          Math.random() * 10,
          (Math.random() - 0.5) * 20
        );
      }
      setRainParticles(positions);
    } else {
      setRainParticles([]);
    }
  }, [rain]);

  return (
    <group>
      <ambientLight intensity={isNight ? 0.2 : 0.6} />
      <directionalLight position={[5, 10, 5]} intensity={isNight ? 0.3 : 1.2} />
      <pointLight position={[0, 5, 0]} intensity={0.5} color={isNight ? "#4488ff" : "#ffdd88"} />
      
      <Stars radius={30} depth={50} count={1500} factor={4} saturation={0} fade speed={0.3} />
      <Sparkles count={150} scale={20} size={0.3} speed={0.4} opacity={0.5} />
      
      {rainParticles.length > 0 && (
        <group>
          {rainParticles.slice(0, 200).map((pos, i) => (
            <mesh key={i} position={[pos[0], pos[1], pos[2]]}>
              <sphereGeometry args={[0.04, 4, 4]} />
              <meshStandardMaterial color="#4488ff" transparent opacity={0.6} />
            </mesh>
          ))}
        </group>
      )}
      
      <Float speed={0.3} rotationIntensity={0.1} floatIntensity={0.2}>
        <group position={[-3, 4, -3]}>
          <mesh><sphereGeometry args={[0.8, 16, 16]} /><meshStandardMaterial color={isNight ? "#334466" : "#ffffff"} opacity={0.6} transparent /></mesh>
          <mesh position={[0.7, 0.2, 0]}><sphereGeometry args={[0.6, 16, 16]} /><meshStandardMaterial color={isNight ? "#445577" : "#f0f0ff"} opacity={0.6} transparent /></mesh>
          <mesh position={[-0.7, 0.2, 0]}><sphereGeometry args={[0.6, 16, 16]} /><meshStandardMaterial color={isNight ? "#445577" : "#f0f0ff"} opacity={0.6} transparent /></mesh>
          <mesh position={[0, -0.3, 0.5]}><sphereGeometry args={[0.5, 16, 16]} /><meshStandardMaterial color={isNight ? "#445577" : "#f0f0ff"} opacity={0.5} transparent /></mesh>
        </group>
      </Float>
      
      <Float speed={0.4} rotationIntensity={0.15} floatIntensity={0.25}>
        <group position={[3, 3.5, -2]}>
          <mesh><sphereGeometry args={[0.6, 16, 16]} /><meshStandardMaterial color={isNight ? "#334466" : "#ffffff"} opacity={0.5} transparent /></mesh>
          <mesh position={[0.6, 0.1, 0]}><sphereGeometry args={[0.5, 16, 16]} /><meshStandardMaterial color={isNight ? "#445577" : "#f0f0ff"} opacity={0.5} transparent /></mesh>
          <mesh position={[-0.6, 0.1, 0]}><sphereGeometry args={[0.5, 16, 16]} /><meshStandardMaterial color={isNight ? "#445577" : "#f0f0ff"} opacity={0.5} transparent /></mesh>
        </group>
      </Float>
      
      <Float speed={0.8} rotationIntensity={0.3} floatIntensity={0.4}>
        <group position={[0, 0.5, 0]}>
          <mesh rotation={[Math.PI / 3, 0, 0]}>
            <ringGeometry args={[1.8, 2.0, 64]} />
            <meshStandardMaterial color={isNight ? "#4488ff" : "#4ecdc4"} transparent opacity={0.15} side={2} />
          </mesh>
          <mesh>
            <sphereGeometry args={[1.4, 64, 64]} />
            <meshStandardMaterial color={isNight ? "#1a2a4a" : "#4a8a8a"} metalness={0.3} roughness={0.4} emissive={isNight ? "#224488" : "#88ddbb"} emissiveIntensity={0.15} />
          </mesh>
          <mesh scale={1.05}>
            <sphereGeometry args={[1.4, 32, 32]} />
            <meshStandardMaterial color={isNight ? "#4488ff" : "#66ddbb"} transparent opacity={0.08} wireframe />
          </mesh>
          <mesh scale={1.01}>
            <sphereGeometry args={[1.4, 24, 24]} />
            <meshStandardMaterial color={isNight ? "#4488ff" : "#4ecdc4"} transparent opacity={0.06} wireframe />
          </mesh>
        </group>
      </Float>
      
      <group>
        {[...Array(40)].map((_, i) => {
          const angle = (i / 40) * Math.PI * 2;
          const radius = 2.8 + Math.sin(i * 0.7) * 0.4;
          const speed = 0.0003 + Math.sin(i * 0.3) * 0.0002;
          return (
            <mesh key={i} position={[Math.cos(angle + Date.now() * speed) * radius, 0.5 + Math.sin(angle * 2 + Date.now() * speed * 0.7) * 0.8, Math.sin(angle + Date.now() * speed) * radius]} scale={0.04}>
              <sphereGeometry args={[0.5, 6, 6]} />
              <meshStandardMaterial color={isNight ? "#88bbff" : "#ffdd88"} emissive={isNight ? "#4488ff" : "#ffaa44"} emissiveIntensity={0.3} />
            </mesh>
          );
        })}
      </group>
    </group>
  );
}

// ==================== 3D WEATHER CARD ====================
function WeatherCard3D({ weather, isNight }) {
  const temp = weather?.current?.temperature_2m || 0;
  const condition = weather?.current?.weather_code || 0;
  
  const getEmoji = () => {
    if (condition === 0) return isNight ? "🌙" : "☀️";
    if (condition <= 3) return isNight ? "🌤️" : "⛅";
    if (condition <= 20) return "☁️";
    if (condition >= 61) return "🌧️";
    if (condition >= 95) return "⛈️";
    return "🌤️";
  };
  
  return (
    <motion.div 
      className="weather-card-3d"
      initial={{ scale: 0.8, opacity: 0, rotateY: -20 }}
      animate={{ scale: 1, opacity: 1, rotateY: 0 }}
      transition={{ duration: 0.8, ease: "easeOut" }}
      style={{
        background: isNight 
          ? 'linear-gradient(135deg, rgba(15,25,45,0.85), rgba(25,45,80,0.75))'
          : 'linear-gradient(135deg, rgba(20,40,70,0.85), rgba(40,80,120,0.75))',
      }}
    >
      <div className="card-3d-content">
        <div className="card-3d-emoji">{getEmoji()}</div>
        <div className="card-3d-temp">{Math.round(temp)}°</div>
        <div className="card-3d-details">
          <span>💧 {Math.round(weather?.current?.relative_humidity_2m || 0)}%</span>
          <span>💨 {Math.round(weather?.current?.wind_speed_10m || 0)} km/h</span>
        </div>
        <div className="card-3d-glow" />
      </div>
    </motion.div>
  );
}

// ==================== MAIN APP ====================
function App(){
  const [location,setLocation]=useState(demoLocations[0]);
  const [weather,setWeather]=useState(null);
  const [question,setQuestion]=useState("Should I spray pesticides today?");
  const [role,setRole]=useState("farmer");
  const [answer,setAnswer]=useState(null);
  const [loading,setLoading]=useState(false);
  const [city,setCity]=useState("");
  const [searchResults,setSearchResults]=useState([]);
  const [language,setLanguage]=useState("en-IN");
  const [notice,setNotice]=useState("");
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [alertModal, setAlertModal] = useState(null);
  const [websocket, setWebsocket] = useState(null);
  const [connected, setConnected] = useState(false);
  const [showHeatmap, setShowHeatmap] = useState(false);
  const [showMap, setShowMap] = useState(true);
  const [diseaseRisk, setDiseaseRisk] = useState(null);
  const [isNight, setIsNight] = useState(false);
  const [activeTab, setActiveTab] = useState('chat');
  const [cropYield, setCropYield] = useState(null);
  const [selectedCrop, setSelectedCrop] = useState('wheat');
  
  const current = weather?.current || {};
  const derived = weather?.derived || {};
  
  useEffect(() => {
    const hour = new Date().getHours();
    setIsNight(hour < 6 || hour > 18);
  }, []);

  const metric = (key, unit="") => current[key] == null ? "—" : `${Math.round(current[key]*10)/10}${unit}`;

  // WebSocket connection
  useEffect(() => {
    const clientId = `client_${Date.now()}`;
    const ws = new WebSocket(`${API.replace('http', 'ws')}/ws/${clientId}`);
    
    ws.onopen = () => {
      setConnected(true);
      setNotice("🟢 Connected to real-time updates");
      ws.send(JSON.stringify({
        type: "subscribe_alerts",
        location: {latitude: location.latitude, longitude: location.longitude}
      }));
    };
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === "alert") {
        setAlertModal(data);
        setNotice(`⚠️ Alert: ${data.message}`);
      } else if (data.type === "weather_update") {
        setWeather(data.data);
      }
    };
    
    ws.onclose = () => setConnected(false);
    setWebsocket(ws);
    
    return () => ws.close();
  }, []);

  useEffect(() => {
    if (websocket && connected) {
      websocket.send(JSON.stringify({
        type: "subscribe_alerts",
        location: {latitude: location.latitude, longitude: location.longitude}
      }));
    }
  }, [location]);

  // Load weather
  async function loadWeather(loc=location){
    setLoading(true); 
    setNotice("");
    try{
      const r = await fetch(`${API}/api/weather?latitude=${loc.latitude}&longitude=${loc.longitude}`);
      if(!r.ok) throw new Error(await r.text());
      const data = await r.json();
      setWeather(data);
      setNotice(`✅ Weather updated: ${data.current.temperature_2m}°C`);
      
      // Auto-check disease and crop yield with GET requests (fixed!)
      await checkDiseaseRisk(loc.latitude, loc.longitude);
      await checkCropYield(loc.latitude, loc.longitude);
      
    } catch(e){
      console.error("Weather load error:", e);
      setNotice("❌ Backend connection failed.");
    } finally {
      setLoading(false);
    }
  }
  
  useEffect(() => {
    loadWeather(location);
  }, [location.latitude, location.longitude]);

  // Check disease risk - UPDATED to GET
  async function checkDiseaseRisk(lat, lon) {
    try {
      const r = await fetch(`${API}/api/crop/disease?latitude=${lat}&longitude=${lon}`);
      if (r.ok) {
        const data = await r.json();
        setDiseaseRisk(data);
        console.log("✅ Disease risk data:", data);
      } else {
        console.warn("Disease risk endpoint returned:", r.status);
      }
    } catch (e) {
      console.error('Disease check failed:', e);
    }
  }

  // Check crop yield - UPDATED to GET
  async function checkCropYield(lat, lon) {
    try {
      const r = await fetch(`${API}/api/crop/yield?crop=${selectedCrop}&latitude=${lat}&longitude=${lon}&soil_quality=medium`);
      if (r.ok) {
        const data = await r.json();
        setCropYield(data);
        console.log("✅ Crop yield data:", data);
      } else {
        console.warn("Crop yield endpoint returned:", r.status);
      }
    } catch (e) {
      console.error('Crop yield check failed:', e);
    }
  }

  // Search city
  async function searchCity(){
    if(city.trim().length < 2) return;
    try {
      const r = await fetch(`${API}/api/geocode?name=${encodeURIComponent(city)}`);
      const d = await r.json(); 
      setSearchResults(d.results || []);
    } catch (e) {
      console.error("Search failed:", e);
    }
  }

  // Ask question
  async function ask(){
    setLoading(true); 
    setAnswer(null);
    setNotice("");
    
    try{
      const r = await fetch(`${API}/api/chat`, {
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify({
          question,
          latitude: location.latitude,
          longitude: location.longitude,
          role
        })
      });
      
      if(!r.ok) {
        const errorText = await r.text();
        throw new Error(errorText || `HTTP ${r.status}`);
      }
      
      const data = await r.json();
      setAnswer(data);
      setNotice(`✅ Advisory generated - Risk: ${data.risk}`);
      
    } catch(e){
      console.error("Chat error:", e);
      setNotice(`❌ Could not generate advisory: ${e.message}`);
    } finally {
      setLoading(false);
    }
  }

  // Speak function
  function speak(){
    if(!answer || !("speechSynthesis" in window)) return;
    setIsSpeaking(true);
    const u = new SpeechSynthesisUtterance(answer.answer);
    u.lang = language;
    u.onend = () => setIsSpeaking(false);
    u.onerror = () => setIsSpeaking(false);
    window.speechSynthesis.cancel(); 
    window.speechSynthesis.speak(u);
  }

  // Voice input
  function voiceInput(){
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    if(!SR){
      setNotice("Browser speech recognition is unavailable.");
      return;
    }
    const rec = new SR(); 
    rec.lang = language; 
    rec.onresult = e => setQuestion(e.results[0][0].transcript); 
    rec.start();
  }

  const riskClass = answer?.risk?.toLowerCase() || "low";
  const trendIcon = derived?.trend === "rising" ? <TrendingUp size={14} className="trend-up"/> :
                    derived?.trend === "falling" ? <TrendingDown size={14} className="trend-down"/> :
                    <Minus size={14} className="trend-stable"/>;

  return (
    <div className="app-3d">
      {/* 3D Background */}
      <div className="canvas-container">
        <Canvas camera={{ position: [0, 2, 8], fov: 60 }}>
          <WeatherScene weather={weather} isNight={isNight} />
          <OrbitControls 
            enableZoom={false} 
            enablePan={false} 
            autoRotate 
            autoRotateSpeed={0.3}
            maxPolarAngle={Math.PI / 2.5}
            minPolarAngle={Math.PI / 3}
          />
        </Canvas>
      </div>

      <div className="glow-overlay" />

      {/* Header */}
      <motion.header 
        className="topbar-3d"
        initial={{ y: -100 }}
        animate={{ y: 0 }}
        transition={{ duration: 0.6, type: "spring" }}
      >
        <div className="brand-3d">
          <div className="logo-3d"><CloudSun size={24} color="#4ecdc4" /></div>
          <div>
            <b>WeatherGPT</b>
            <span>Advanced Meteorological Intelligence</span>
          </div>
        </div>
        <div className="top-actions-3d">
          <span className="live-3d">
            <span className="dot-pulse" /> {connected ? 'LIVE' : 'RECONNECTING'}
          </span>
          <button className="glass-btn" onClick={() => loadWeather()} title="Refresh Weather">
            <RefreshCw size={16} />
          </button>
          <button className={`glass-btn ${showMap ? 'active' : ''}`} onClick={() => setShowMap(!showMap)} title="Toggle Map">
            <Map size={16} />
          </button>
          <button className={`glass-btn ${showHeatmap ? 'active' : ''}`} onClick={() => setShowHeatmap(!showHeatmap)} title="Toggle Heatmap">
            <Activity size={16} />
          </button>
          {alertModal && (
            <button className="alert-btn-3d" onClick={() => setAlertModal(null)}>
              <Bell size={16} />
              <span className="alert-badge">!</span>
            </button>
          )}
        </div>
      </motion.header>

      {/* Main Content */}
      <div className="main-3d">
        {/* Left Panel */}
        <motion.aside 
          className="left-panel-3d"
          initial={{ x: -80, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.2 }}
        >
          <WeatherCard3D weather={weather} isNight={isNight} />
          
          {/* Location Search */}
          <div className="search-3d">
            <input 
              value={city} 
              onChange={e => setCity(e.target.value)} 
              onKeyDown={e => e.key === "Enter" && searchCity()} 
              placeholder="Search city..." 
            />
            <button onClick={searchCity}><Search size={16} /></button>
          </div>
          
          {searchResults.length > 0 && (
            <div className="search-results-3d">
              {searchResults.map(x => (
                <button key={`${x.latitude}${x.longitude}`} onClick={() => {
                  setLocation({name: x.name, latitude: x.latitude, longitude: x.longitude});
                  setSearchResults([]);
                  setCity(x.name);
                }}>
                  <MapPin size={12} /> {x.name}, {x.country}
                </button>
              ))}
            </div>
          )}

          <div className="location-info-3d">
            <MapPin size={14} color="#4ecdc4" />
            <span className="location-name-3d">{location.name}</span>
            <span className="location-coords-3d">{location.latitude.toFixed(2)}, {location.longitude.toFixed(2)}</span>
          </div>

          {/* Metrics Grid */}
          <div className="metrics-grid-3d">
            {[
              { icon: <Thermometer size={14} />, label: 'Temp', value: metric("temperature_2m","°C") },
              { icon: <Droplets size={14} />, label: 'Humidity', value: metric("relative_humidity_2m","%") },
              { icon: <CloudRain size={14} />, label: 'Rain', value: metric("rain"," mm") },
              { icon: <Wind size={14} />, label: 'Wind', value: metric("wind_speed_10m"," km/h") },
            ].map((m, i) => (
              <motion.div 
                key={i} 
                className="metric-3d"
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ delay: 0.3 + i * 0.1 }}
              >
                <span className="metric-icon-3d">{m.icon}</span>
                <span className="metric-label-3d">{m.label}</span>
                <span className="metric-value-3d">{m.value}</span>
              </motion.div>
            ))}
          </div>

          {derived && (
            <div className="analytics-3d">
              <div className="analytics-item-3d">
                <span>Comfort</span>
                <strong>{derived.comfort_index || 'moderate'}</strong>
              </div>
              <div className="analytics-item-3d">
                <span>Heat Index</span>
                <strong>{derived.heat_index ? `${derived.heat_index}°C` : '—'}</strong>
              </div>
              <div className="analytics-item-3d">
                <span>Trend</span>
                <strong>{trendIcon} {derived.trend || 'stable'}</strong>
              </div>
            </div>
          )}
        </motion.aside>

        {/* Right Panel */}
        <motion.section 
          className="right-panel-3d"
          initial={{ x: 80, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.4 }}
        >
          {/* Tab Navigation */}
          <div className="tab-nav-3d">
            <button className={`tab-btn-3d ${activeTab === 'chat' ? 'active' : ''}`} onClick={() => setActiveTab('chat')}>
              <Radio size={14} /> Chat
            </button>
            <button className={`tab-btn-3d ${activeTab === 'map' ? 'active' : ''}`} onClick={() => setActiveTab('map')}>
              <Map size={14} /> Map
            </button>
            <button className={`tab-btn-3d ${activeTab === 'charts' ? 'active' : ''}`} onClick={() => setActiveTab('charts')}>
              <Activity size={14} /> Charts
            </button>
            <button className={`tab-btn-3d ${activeTab === 'disease' ? 'active' : ''}`} onClick={() => setActiveTab('disease')}>
              <Sprout size={14} /> Disease
            </button>
          </div>

          {/* Chat Tab */}
          {activeTab === 'chat' && (
            <div className="tab-content-3d">
              <div className="chat-header-3d">
                <div className="chat-title-3d">
                  <Radio size={16} color="#4ecdc4" />
                  <span>Weather Assistant</span>
                </div>
                <div className="chat-badge-3d">AI-Powered</div>
              </div>

              <div className="roles-3d">
                {[
                  ["farmer","🌾 Farmer"],
                  ["disaster","🚨 Disaster"],
                  ["urban","🏙️ Urban"],
                  ["traveler","✈️ Travel"]
                ].map(([v,t]) => (
                  <motion.button
                    key={v}
                    className={`role-btn-3d ${role === v ? 'active' : ''}`}
                    onClick={() => setRole(v)}
                    whileHover={{ scale: 1.03 }}
                    whileTap={{ scale: 0.95 }}
                  >
                    {t}
                  </motion.button>
                ))}
              </div>

              <div className="chatbox-3d">
                <div className="chat-avatar-3d"><CloudSun size={20} color="#4ecdc4" /></div>
                <div>
                  <b>WeatherGPT</b>
                  <p>Ask me about weather, risk, farming, travel, events or emergency planning.</p>
                </div>
              </div>

              <AnimatePresence>
                {answer && (
                  <motion.div 
                    className={`answer-3d ${riskClass}`}
                    initial={{ scale: 0.95, opacity: 0, y: 20 }}
                    animate={{ scale: 1, opacity: 1, y: 0 }}
                    exit={{ scale: 0.95, opacity: 0 }}
                    transition={{ duration: 0.3 }}
                  >
                    <div className="answer-header-3d">
                      <span className={`risk-badge-3d ${riskClass}`}>⚠️ {answer.risk}</span>
                      <span className="confidence-3d">{answer.confidence}</span>
                    </div>
                    <div className="answer-text-3d"><p>{answer.answer}</p></div>
                    {answer.actions && answer.actions.length > 0 && (
                      <div className="actions-3d">
                        <strong>Recommended Actions</strong>
                        {answer.actions.map((a,i) => <div key={i} className="action-item-3d">✅ {a}</div>)}
                      </div>
                    )}
                    {answer.evidence && (
                      <div className="evidence-3d">
                        {answer.evidence.map((e,i) => <span key={i} className="evidence-tag-3d">{e}</span>)}
                      </div>
                    )}
                    <button className="speak-btn-3d" onClick={speak} disabled={isSpeaking}>
                      <Languages size={14} /> {isSpeaking ? 'Speaking...' : 'Speak Advisory'}
                    </button>
                  </motion.div>
                )}
              </AnimatePresence>

              <div className="composer-3d">
                <div className="composer-input-3d">
                  <textarea 
                    value={question} 
                    onChange={e => setQuestion(e.target.value)} 
                    onKeyDown={e => { if(e.key === "Enter" && !e.shiftKey) { e.preventDefault(); ask(); } }} 
                    placeholder="Ask a weather question..."
                    rows={2}
                  />
                </div>
                <div className="composer-actions-3d">
                  <select className="lang-select-3d" value={language} onChange={e => setLanguage(e.target.value)}>
                    <option value="en-IN">🇬🇧 English</option>
                    <option value="hi-IN">🇮🇳 हिन्दी</option>
                    <option value="pa-IN">🇮🇳 ਪੰਜਾਬੀ</option>
                    <option value="ta-IN">🇮🇳 தமிழ்</option>
                    <option value="te-IN">🇮🇳 తెలుగు</option>
                  </select>
                  <button className="mic-btn-3d" onClick={voiceInput}><Mic size={16} /></button>
                  <motion.button 
                    className="send-btn-3d" 
                    onClick={ask} 
                    disabled={loading}
                    whileHover={{ scale: 1.03 }}
                    whileTap={{ scale: 0.95 }}
                  >
                    {loading ? <RefreshCw className="spin" size={16} /> : <Send size={16} />}
                    <span>Ask</span>
                  </motion.button>
                </div>
              </div>
            </div>
          )}

          {/* Map Tab */}
          {activeTab === 'map' && (
            <div className="tab-content-3d map-tab">
              <InteractiveMap 
                onLocationSelect={async (lat, lon, name) => {
                  setLocation({name, latitude: lat, longitude: lon});
                  await loadWeather({latitude: lat, longitude: lon});
                }}
                currentLocation={location}
                weatherData={weather}
              />
            </div>
          )}

          {/* Charts Tab */}
          {activeTab === 'charts' && (
            <div className="tab-content-3d charts-tab">
              <WeatherCharts weatherData={weather} />
            </div>
          )}

          {/* Disease Tab */}
          {activeTab === 'disease' && (
            <div className="tab-content-3d disease-tab">
              <h4 style={{fontSize: '16px', color: '#ffffff', marginBottom: '12px'}}>
                <Sprout size={16} style={{marginRight: '8px'}} /> Crop Disease Risk
              </h4>
              {diseaseRisk && diseaseRisk.disease_risks ? (
                <div className="disease-container-3d">
                  {diseaseRisk.disease_risks.map((d, i) => (
                    <div key={i} className={`disease-card-3d ${d.level.toLowerCase()}`}>
                      <div className="disease-icon-3d">{d.icon}</div>
                      <div>
                        <h5>{d.name}</h5>
                        <span className={`risk-badge-small ${d.level.toLowerCase()}`}>{d.level}</span>
                        <p>{d.description}</p>
                        <small>💊 {d.treatment}</small>
                      </div>
                    </div>
                  ))}
                  {diseaseRisk.advisory && (
                    <div className="disease-advisory-3d">
                      <h5>{diseaseRisk.advisory.message}</h5>
                      <ul>
                        {diseaseRisk.advisory.actions.map((a, i) => <li key={i}>{a}</li>)}
                      </ul>
                    </div>
                  )}
                </div>
              ) : (
                <p style={{color: '#556688', fontSize: '13px'}}>Loading disease data...</p>
              )}
              
              {/* Crop Yield */}
              <h4 style={{fontSize: '16px', color: '#ffffff', marginTop: '18px', marginBottom: '10px'}}>
                <Calendar size={16} style={{marginRight: '8px'}} /> Crop Yield Prediction
              </h4>
              <div className="crop-yield-3d">
                <select 
                  value={selectedCrop} 
                  onChange={e => {
                    setSelectedCrop(e.target.value); 
                    checkCropYield(location.latitude, location.longitude);
                  }}
                >
                  <option value="wheat">🌾 Wheat</option>
                  <option value="rice">🍚 Rice</option>
                  <option value="maize">🌽 Maize</option>
                  <option value="cotton">🌿 Cotton</option>
                  <option value="potato">🥔 Potato</option>
                  <option value="tomato">🍅 Tomato</option>
                </select>
                {cropYield ? (
                  <div className="yield-result-3d">
                    <div className="yield-value">
                      {cropYield.predicted_yield} <span>tons/hectare</span>
                    </div>
                    <div className="yield-confidence">
                      Confidence: {(cropYield.confidence * 100).toFixed(0)}%
                    </div>
                    <div className="yield-recommendations">
                      {cropYield.recommendations && cropYield.recommendations.map((r, i) => (
                        <div key={i}>📋 {r}</div>
                      ))}
                    </div>
                  </div>
                ) : (
                  <p style={{color: '#556688', fontSize: '13px', marginTop: '8px'}}>
                    Select a crop to see yield prediction
                  </p>
                )}
              </div>
            </div>
          )}
        </motion.section>
      </div>

      {/* Heatmap Overlay */}
      {showHeatmap && (
        <motion.div 
          className="heatmap-overlay-3d"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: 20 }}
        >
          <div className="heatmap-header-3d">
            <h4><Activity size={16} /> Risk Heatmap</h4>
            <button className="close-heatmap" onClick={() => setShowHeatmap(false)}>✕</button>
          </div>
          <RiskHeatmap lat={location.latitude} lon={location.longitude} weather={weather} />
        </motion.div>
      )}

      {/* Toast */}
      <AnimatePresence>
        {notice && (
          <motion.div 
            className={`toast-3d ${notice.includes('⚠️') ? 'warning' : notice.includes('✅') ? 'success' : ''}`}
            initial={{ x: 100, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: 100, opacity: 0 }}
            transition={{ duration: 0.3 }}
          >
            {notice}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Alert Modal */}
      {alertModal && (
        <div className="alert-modal-3d">
          <div className="alert-content-3d">
            <h3><AlertTriangle size={24} color="#ffd93d" /> Weather Alert</h3>
            <p className="alert-risk-3d">Risk: {alertModal.risk}</p>
            <p>{alertModal.message}</p>
            <button onClick={() => setAlertModal(null)}>Dismiss</button>
          </div>
        </div>
      )}

      <footer className="footer-3d">
        WeatherGPT v3.0 • Tekathon 5.0 • PS 26068 • Not a replacement for official IMD warnings
      </footer>
    </div>
  );
}

createRoot(document.getElementById("root")).render(<App/>)