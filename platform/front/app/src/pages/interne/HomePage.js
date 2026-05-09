import React, { useEffect, useState } from "react";
import "./HomePage.css";

const API_BASE_URL = "http://api:8000/api";

export default function HomePage() {
  // États pour les différentes sections
  const [systemStatus, setSystemStatus] = useState({
    api: false,
    database: false,
    etl: false,
    availability: 0,
    responseTime: 0
  });
  
  const [metrics, setMetrics] = useState({
    latency: [],
    traffic: [],
    errors: []
  });
  
  const [logs, setLogs] = useState({
    backend: [],
    etl: [],
    docker: []
  });
  
  const [tests, setTests] = useState({
    results: [],
    coverage: 0,
    lastRun: null
  });
  
  const [pipelines, setPipelines] = useState({
    lastPipeline: null,
    buildStatus: null,
    deployStatus: null,
    history: []
  });
  
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("dashboard");
  const [refreshInterval, setRefreshInterval] = useState(30000); // 30 secondes

  // Chargement initial
  useEffect(() => {
    chargerToutesLesDonnees();
    
    // Rafraîchissement automatique
    const interval = setInterval(() => {
      chargerToutesLesDonnees();
    }, refreshInterval);
    
    return () => clearInterval(interval);
  }, [refreshInterval]);

  const chargerToutesLesDonnees = async () => {
    setLoading(true);
    
    try {
      // Appels parallèles vers l'API
      const [
        healthRes,
        metricsRes,
        logsRes,
        testsRes,
        pipelinesRes
      ] = await Promise.all([
        fetch(`${API_BASE_URL}/health`).catch(() => null),
        fetch(`${API_BASE_URL}/metrics`).catch(() => null),
        fetch(`${API_BASE_URL}/logs`).catch(() => null),
        fetch(`${API_BASE_URL}/tests`).catch(() => null),
        fetch(`${API_BASE_URL}/pipelines`).catch(() => null)
      ]);
      
      // Traitement des données santé
      if (healthRes && healthRes.ok) {
        const healthData = await healthRes.json();
        setSystemStatus({
          api: true,
          database: healthData.database === "connected",
          etl: healthData.etl || false,
          availability: healthData.availability || 99.9,
          responseTime: healthData.response_time || 120
        });
      }
      
      // Traitement des métriques
      if (metricsRes && metricsRes.ok) {
        const metricsData = await metricsRes.json();
        setMetrics({
          latency: metricsData.latency || generateMockLatency(),
          traffic: metricsData.traffic || generateMockTraffic(),
          errors: metricsData.errors || generateMockErrors()
        });
      } else {
        // Données mockées pour démonstration
        setMetrics({
          latency: generateMockLatency(),
          traffic: generateMockTraffic(),
          errors: generateMockErrors()
        });
      }
      
      // Traitement des logs
      if (logsRes && logsRes.ok) {
        const logsData = await logsRes.json();
        setLogs(logsData);
      } else {
        setLogs(generateMockLogs());
      }
      
      // Traitement des tests
      if (testsRes && testsRes.ok) {
        const testsData = await testsRes.json();
        setTests(testsData);
      } else {
        setTests(generateMockTests());
      }
      
      // Traitement des pipelines
      if (pipelinesRes && pipelinesRes.ok) {
        const pipelinesData = await pipelinesRes.json();
        setPipelines(pipelinesData);
      } else {
        setPipelines(generateMockPipelines());
      }
      
      // Génération d'alertes
      generateAlerts();
      
    } catch (err) {
      console.error("Erreur lors du chargement:", err);
      // Données mockées en cas d'erreur
      setMetrics({
        latency: generateMockLatency(),
        traffic: generateMockTraffic(),
        errors: generateMockErrors()
      });
      setLogs(generateMockLogs());
      setTests(generateMockTests());
      setPipelines(generateMockPipelines());
    } finally {
      setLoading(false);
    }
  };
  
  // Fonctions de génération de données mockées
  const generateMockLatency = () => {
    return Array.from({ length: 20 }, (_, i) => ({
      time: new Date(Date.now() - (19 - i) * 60000).toLocaleTimeString(),
      value: Math.floor(Math.random() * 100) + 50
    }));
  };
  
  const generateMockTraffic = () => {
    return Array.from({ length: 20 }, (_, i) => ({
      time: new Date(Date.now() - (19 - i) * 60000).toLocaleTimeString(),
      value: Math.floor(Math.random() * 1000) + 200
    }));
  };
  
  const generateMockErrors = () => {
    return Array.from({ length: 20 }, (_, i) => ({
      time: new Date(Date.now() - (19 - i) * 60000).toLocaleTimeString(),
      value: Math.floor(Math.random() * 20)
    }));
  };
  
  const generateMockLogs = () => {
    return {
      backend: [
        { timestamp: new Date().toLocaleString(), level: "INFO", message: "API démarrée sur le port 8000" },
        { timestamp: new Date().toLocaleString(), level: "INFO", message: "Connexion DB établie" },
        { timestamp: new Date().toLocaleString(), level: "WARNING", message: "Requête lente détectée (2300ms)" },
      ],
      etl: [
        { timestamp: new Date().toLocaleString(), level: "INFO", message: "ETL exécuté avec succès" },
        { timestamp: new Date().toLocaleString(), level: "INFO", message: "34 nouvelles entrées ajoutées" },
      ],
      docker: [
        { timestamp: new Date().toLocaleString(), level: "INFO", message: "Conteneur obrail_api démarré" },
        { timestamp: new Date().toLocaleString(), level: "INFO", message: "Conteneur obrail_db en cours d'exécution" },
      ]
    };
  };
  
  const generateMockTests = () => {
    return {
      results: [
        { name: "Tests unitaires backend", status: "passed", duration: 1.2 },
        { name: "Tests d'intégration API", status: "passed", duration: 2.5 },
        { name: "Tests E2E frontend", status: "failed", duration: 3.1 },
        { name: "Tests de charge", status: "passed", duration: 15.3 },
      ],
      coverage: 87.5,
      lastRun: new Date().toLocaleString()
    };
  };
  
  const generateMockPipelines = () => {
    return {
      lastPipeline: {
        id: "#42",
        status: "success",
        time: new Date().toLocaleString(),
        duration: "3m 42s"
      },
      buildStatus: "success",
      deployStatus: "success",
      history: [
        { id: "#42", status: "success", time: new Date().toLocaleString() },
        { id: "#41", status: "success", time: new Date(Date.now() - 3600000).toLocaleString() },
        { id: "#40", status: "failed", time: new Date(Date.now() - 7200000).toLocaleString() },
        { id: "#39", status: "success", time: new Date(Date.now() - 10800000).toLocaleString() },
      ]
    };
  };
  
  const generateAlerts = () => {
    const newAlerts = [];
    
    // Vérification des conditions d'alerte
    if (!systemStatus.database) {
      newAlerts.push({ level: "critical", message: "La base de données est inaccessible !" });
    }
    
    if (systemStatus.responseTime > 500) {
      newAlerts.push({ level: "warning", message: `Latence API élevée : ${systemStatus.responseTime}ms` });
    }
    
    if (tests.results.some(t => t.status === "failed")) {
      newAlerts.push({ level: "warning", message: "Certains tests ont échoué" });
    }
    
    if (pipelines.buildStatus === "failed") {
      newAlerts.push({ level: "critical", message: "Le pipeline CI/CD a échoué" });
    }
    
    setAlerts(newAlerts);
  };
  
  if (loading && !systemStatus.api) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Chargement du tableau de bord technique...</p>
      </div>
    );
  }

  return (
    <main className="engineering-dashboard">
      {/* En-tête */}
      <div className="dashboard-header">
        <div>
          <h1>🔧 ObRail Europe - Tableau de bord Ingénieur</h1>
          <p className="dashboard-subtitle">Supervision technique & monitoring infrastructure</p>
        </div>
        <div className="refresh-control">
          <label>Rafraîchissement :</label>
          <select value={refreshInterval} onChange={(e) => setRefreshInterval(Number(e.target.value))}>
            <option value={10000}>10 secondes</option>
            <option value={30000}>30 secondes</option>
            <option value={60000}>1 minute</option>
          </select>
        </div>
      </div>
      
      {/* Onglets */}
      <div className="tabs">
        <button className={activeTab === "dashboard" ? "tab-active" : "tab"} onClick={() => setActiveTab("dashboard")}>
          📊 Dashboard
        </button>
        <button className={activeTab === "monitoring" ? "tab-active" : "tab"} onClick={() => setActiveTab("monitoring")}>
          📈 Surveillance
        </button>
        <button className={activeTab === "logs" ? "tab-active" : "tab"} onClick={() => setActiveTab("logs")}>
          📝 Logs
        </button>
        <button className={activeTab === "tests" ? "tab-active" : "tab"} onClick={() => setActiveTab("tests")}>
          🧪 Tests
        </button>
        <button className={activeTab === "pipelines" ? "tab-active" : "tab"} onClick={() => setActiveTab("pipelines")}>
          🔄 CI/CD
        </button>
      </div>
      
      {/* ALERTES */}
      {alerts.length > 0 && (
        <div className="alerts-container">
          {alerts.map((alert, idx) => (
            <div key={idx} className={`alert alert-${alert.level}`}>
              <strong>{alert.level === "critical" ? "🚨" : "⚠️"}</strong> {alert.message}
            </div>
          ))}
        </div>
      )}
      
      {/* SECTION 1 : TABLEAU DE BORD PRINCIPAL */}
      {activeTab === "dashboard" && (
        <>
          {/* État des services */}
          <div className="section">
            <h2>🏥 État des services</h2>
            <div className="status-grid">
              <div className={`status-card ${systemStatus.api ? "status-ok" : "status-critical"}`}>
                <div className="status-icon">{systemStatus.api ? "✅" : "❌"}</div>
                <h3>API REST</h3>
                <p>{systemStatus.api ? "Opérationnelle" : "Hors service"}</p>
              </div>
              
              <div className={`status-card ${systemStatus.database ? "status-ok" : "status-critical"}`}>
                <div className="status-icon">{systemStatus.database ? "✅" : "❌"}</div>
                <h3>Base de données</h3>
                <p>{systemStatus.database ? "Connectée" : "Déconnectée"}</p>
              </div>
              
              <div className={`status-card ${systemStatus.etl ? "status-ok" : "status-warning"}`}>
                <div className="status-icon">{systemStatus.etl ? "✅" : "⏳"}</div>
                <h3>ETL</h3>
                <p>{systemStatus.etl ? "En ligne" : "En attente"}</p>
              </div>
              
              <div className="status-card">
                <div className="status-icon">📊</div>
                <h3>Disponibilité</h3>
                <p>{systemStatus.availability}%</p>
              </div>
              
              <div className="status-card">
                <div className="status-icon">⚡</div>
                <h3>Temps de réponse</h3>
                <p>{systemStatus.responseTime}ms</p>
              </div>
            </div>
          </div>
          
          {/* Métriques rapides */}
          <div className="section">
            <h2>📊 Métriques temps réel</h2>
            <div className="metrics-quick">
              <div className="metric-quick-card">
                <div className="metric-value">{metrics.latency[metrics.latency.length - 1]?.value || 0}ms</div>
                <div className="metric-label">Latence moyenne</div>
              </div>
              <div className="metric-quick-card">
                <div className="metric-value">{metrics.traffic[metrics.traffic.length - 1]?.value || 0}</div>
                <div className="metric-label">Requêtes/minute</div>
              </div>
              <div className="metric-quick-card">
                <div className="metric-value">{metrics.errors[metrics.errors.length - 1]?.value || 0}</div>
                <div className="metric-label">Erreurs/minute</div>
              </div>
              <div className="metric-quick-card">
                <div className="metric-value">{tests.coverage}%</div>
                <div className="metric-label">Couverture tests</div>
              </div>
            </div>
          </div>
        </>
      )}
      
      {/* SECTION 2 : SURVEILLANCE */}
      {activeTab === "monitoring" && (
        <div className="section">
          <h2>📈 Surveillance détaillée</h2>
          
          <div className="graph-container">
            <h3>Latence API (ms)</h3>
            <div className="graph">
              {metrics.latency.map((point, i) => (
                <div key={i} className="graph-bar" style={{ height: `${point.value / 5}px` }}>
                  <div className="graph-tooltip">{point.value}ms</div>
                </div>
              ))}
            </div>
            <div className="graph-labels">
              {metrics.latency.map((point, i) => (
                <span key={i}>{point.time}</span>
              ))}
            </div>
          </div>
          
          <div className="graph-container">
            <h3>Trafic API (requêtes/minute)</h3>
            <div className="graph">
              {metrics.traffic.map((point, i) => (
                <div key={i} className="graph-bar traffic" style={{ height: `${point.value / 20}px` }}>
                  <div className="graph-tooltip">{point.value}</div>
                </div>
              ))}
            </div>
            <div className="graph-labels">
              {metrics.traffic.map((point, i) => (
                <span key={i}>{point.time}</span>
              ))}
            </div>
          </div>
          
          <div className="graph-container">
            <h3>Taux d'erreur (erreurs/minute)</h3>
            <div className="graph">
              {metrics.errors.map((point, i) => (
                <div key={i} className="graph-bar error" style={{ height: `${point.value * 10}px` }}>
                  <div className="graph-tooltip">{point.value}</div>
                </div>
              ))}
            </div>
            <div className="graph-labels">
              {metrics.errors.map((point, i) => (
                <span key={i}>{point.time}</span>
              ))}
            </div>
          </div>
        </div>
      )}
      
      {/* SECTION 3 : LOGS */}
      {activeTab === "logs" && (
        <div className="section">
          <h2>📝 Logs système</h2>
          
          <div className="logs-section">
            <h3>Backend API</h3>
            <div className="log-container">
              {logs.backend.map((log, i) => (
                <div key={i} className={`log-entry log-${log.level.toLowerCase()}`}>
                  <span className="log-time">[{log.timestamp}]</span>
                  <span className="log-level">{log.level}</span>
                  <span className="log-message">{log.message}</span>
                </div>
              ))}
            </div>
          </div>
          
          <div className="logs-section">
            <h3>ETL Pipeline</h3>
            <div className="log-container">
              {logs.etl.map((log, i) => (
                <div key={i} className={`log-entry log-${log.level.toLowerCase()}`}>
                  <span className="log-time">[{log.timestamp}]</span>
                  <span className="log-level">{log.level}</span>
                  <span className="log-message">{log.message}</span>
                </div>
              ))}
            </div>
          </div>
          
          <div className="logs-section">
            <h3>Docker / Infrastructure</h3>
            <div className="log-container">
              {logs.docker.map((log, i) => (
                <div key={i} className={`log-entry log-${log.level.toLowerCase()}`}>
                  <span className="log-time">[{log.timestamp}]</span>
                  <span className="log-level">{log.level}</span>
                  <span className="log-message">{log.message}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
      
      {/* SECTION 4 : TESTS */}
      {activeTab === "tests" && (
        <div className="section">
          <h2>🧪 Qualité & Tests</h2>
          
          <div className="coverage-card">
            <div className="coverage-percentage">
              <div className="coverage-circle" style={{ strokeDashoffset: 283 - (283 * tests.coverage / 100) }}>
                <span>{tests.coverage}%</span>
              </div>
            </div>
            <div className="coverage-info">
              <h3>Couverture des tests</h3>
              <p>Dernière exécution : {tests.lastRun || "Non exécutée"}</p>
            </div>
          </div>
          
          <div className="tests-list">
            <h3>Résultats des tests</h3>
            {tests.results.map((test, i) => (
              <div key={i} className={`test-result test-${test.status}`}>
                <div className="test-status">
                  {test.status === "passed" ? "✅" : test.status === "failed" ? "❌" : "⏳"}
                </div>
                <div className="test-info">
                  <div className="test-name">{test.name}</div>
                  <div className="test-duration">Durée : {test.duration}s</div>
                </div>
              </div>
            ))}
          </div>
          
          <button className="btn-run-tests" onClick={chargerToutesLesDonnees}>
            🚀 Exécuter les tests maintenant
          </button>
        </div>
      )}
      
      {/* SECTION 5 : CI/CD PIPELINES */}
      {activeTab === "pipelines" && (
        <div className="section">
          <h2>🔄 Pipelines CI/CD</h2>
          
          <div className="pipeline-status">
            <div className={`pipeline-card ${pipelines.buildStatus}`}>
              <h3>Build</h3>
              <div className="status-badge">
                {pipelines.buildStatus === "success" ? "✅ Succès" : pipelines.buildStatus === "failed" ? "❌ Échec" : "⏳ En cours"}
              </div>
            </div>
            
            <div className={`pipeline-card ${pipelines.deployStatus}`}>
              <h3>Deploiement</h3>
              <div className="status-badge">
                {pipelines.deployStatus === "success" ? "✅ Succès" : pipelines.deployStatus === "failed" ? "❌ Échec" : "⏳ En cours"}
              </div>
            </div>
          </div>
          
          <div className="last-pipeline">
            <h3>Dernier pipeline exécuté</h3>
            {pipelines.lastPipeline && (
              <div className="pipeline-details">
                <p><strong>ID:</strong> {pipelines.lastPipeline.id}</p>
                <p><strong>Statut:</strong> {pipelines.lastPipeline.status === "success" ? "✅ Succès" : "❌ Échec"}</p>
                <p><strong>Heure:</strong> {pipelines.lastPipeline.time}</p>
                <p><strong>Durée:</strong> {pipelines.lastPipeline.duration}</p>
              </div>
            )}
          </div>
          
          <div className="pipeline-history">
            <h3>Historique des pipelines</h3>
            <div className="history-timeline">
              {pipelines.history.map((pipe, i) => (
                <div key={i} className={`history-item ${pipe.status}`}>
                  <span className="history-id">{pipe.id}</span>
                  <span className="history-status">{pipe.status === "success" ? "✅" : "❌"}</span>
                  <span className="history-time">{pipe.time}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
      
      {/* Footer avec actualisation */}
      <div className="dashboard-footer">
        <div className="footer-left">
          <span className="dot green"></span>
          Système en supervision active
        </div>
        <div className="footer-center">
          Dernière mise à jour : {new Date().toLocaleString()}
        </div>
        <div className="footer-right">
          <button onClick={chargerToutesLesDonnees} className="btn-refresh">
            🔄 Rafraîchir
          </button>
        </div>
      </div>
    </main>
  );
}