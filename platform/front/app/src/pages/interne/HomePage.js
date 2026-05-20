import React, { useMemo, useState } from "react";
import AlertBanner from "./components/AlertBanner";
import DashboardTab from "./components/DashboardTab";
import LogsTab from "./components/LogsTab";
import MonitoringTab from "./components/MonitoringTab";
import PipelinesTab from "./components/PipelinesTab";
import TestsTab from "./components/TestsTab";
import { useMonitoring } from "./hooks/useMonitoring";
import "./HomePage.css";

const tabs = [
  { id: "dashboard", label: "Dashboard" },
  { id: "monitoring", label: "Monitoring" },
  { id: "logs", label: "Docker & API" },
  { id: "tests", label: "Tests & Qualite" },
  { id: "pipelines", label: "CI/CD" },
];

export default function HomePage() {
  const [activeTab, setActiveTab] = useState("dashboard");
  const [refreshMs, setRefreshMs] = useState(30000);
  const {
    data,
    loading,
    error,
    lastUpdated,
    refresh,
    runDiagnostic,
    runTestsByCategory,
    actionState,
    testCategories,
  } = useMonitoring(refreshMs);

  const alerts = useMemo(() => {
    const next = [];
    if (error) {
      next.push({ level: "danger", message: error });
    }
    if (data && data.metrics?.api_up !== 1) {
      next.push({ level: "danger", message: "L'API FastAPI n'est pas vue comme disponible par Prometheus." });
    }
    if (data && !data.prometheus?.available) {
      next.push({ level: "warning", message: "Prometheus est indisponible depuis l'API interne." });
    }
    if (data && !data.grafana?.available) {
      next.push({ level: "warning", message: "Grafana est indisponible depuis l'API interne." });
    }
    if (data?.metrics?.errors_5xx_per_second > 0) {
      next.push({ level: "warning", message: "Des erreurs serveur 5xx sont detectees sur l'API." });
    }
    return next;
  }, [data, error]);

  return (
    <main className="internal-page">
      <header className="internal-header">
        <div>
          <p className="eyebrow">Supervision interne</p>
          <h1>ObRail Operations</h1>
          <p className="header-subtitle">
            API, monitoring, qualite des donnees, tests et infrastructure.
          </p>
        </div>

        <div className="header-actions">
          <label>
            Rafraichissement
            <select value={refreshMs} onChange={(event) => setRefreshMs(Number(event.target.value))}>
              <option value={10000}>10 s</option>
              <option value={30000}>30 s</option>
              <option value={60000}>1 min</option>
              <option value={300000}>5 mins</option>
              <option value={600000}>10 mins</option>
            </select>
          </label>
          <button type="button" className="primary-button" onClick={refresh}>
            Actualiser
          </button>
        </div>
      </header>

      <nav className="tab-bar" aria-label="Navigation interne">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            type="button"
            className={activeTab === tab.id ? "tab-button active" : "tab-button"}
            onClick={() => setActiveTab(tab.id)}
          >
            {tab.label}
          </button>
        ))}
      </nav>

      {alerts.map((alert, index) => (
        <AlertBanner key={`${alert.level}-${index}`} level={alert.level}>
          {alert.message}
        </AlertBanner>
      ))}

      {loading && !data ? (
        <section className="panel loading-panel">
          <div className="loader" />
          <p>Chargement des valeurs reelles...</p>
        </section>
      ) : (
        <>
          {activeTab === "dashboard" && <DashboardTab data={data} lastUpdated={lastUpdated} />}
          {activeTab === "monitoring" && <MonitoringTab data={data} />}
          {activeTab === "logs" && <LogsTab data={data} />}
          {activeTab === "tests" && (
            <TestsTab
              data={data}
              actionState={actionState}
              testCategories={testCategories}
              onRunDiagnostic={runDiagnostic}
              onRunTestsByCategory={runTestsByCategory}
            />
          )}
          {activeTab === "pipelines" && <PipelinesTab data={data} />}
        </>
      )}
    </main>
  );
}
