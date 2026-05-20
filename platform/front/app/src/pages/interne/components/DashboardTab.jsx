import React from "react";
import StatusCard from "./StatusCard";

const formatNumber = (value, decimals = 2) => {
  if (value === null || value === undefined || Number.isNaN(value)) return "N/A";
  return Number(value).toFixed(decimals);
};

export default function DashboardTab({ data, lastUpdated }) {
  const metrics = data?.metrics || {};
  const totals = data?.db_totals || {};
  const dockerServices = data?.docker?.services || [];
  const runningServices = dockerServices.filter((service) =>
    String(service.State || service.Status || "").toLowerCase().includes("running")
  );

  return (
    <div className="tab-content">
      <section className="status-grid">
        <StatusCard
          label="API FastAPI"
          value={metrics.api_up === 1 ? "UP" : "DOWN"}
          detail="Valeur Prometheus up{job=fastapi}"
          status={metrics.api_up === 1 ? "ok" : "danger"}
        />
        <StatusCard
          label="Prometheus"
          value={data?.prometheus?.available ? "Connecte" : "Indisponible"}
          detail={data?.prometheus?.target?.scrapeUrl || "Target API non detectee"}
          status={data?.prometheus?.available ? "ok" : "warning"}
        />
        <StatusCard
          label="Grafana"
          value={data?.grafana?.available ? "Connecte" : "Indisponible"}
          detail={`${data?.grafana?.dashboards?.length || 0} dashboard(s)`}
          status={data?.grafana?.available ? "ok" : "warning"}
        />
        <StatusCard
          label="Docker"
          value={data?.docker?.available ? `${runningServices.length}/${dockerServices.length}` : "N/A"}
          detail={data?.docker?.available ? "services actifs" : "Docker non accessible depuis l'API"}
          status={data?.docker?.available ? "ok" : "warning"}
        />
      </section>

      <section className="metric-grid">
        <article className="metric-card">
          <span>Requetes API</span>
          <strong>{formatNumber(metrics.requests_per_minute)} / min</strong>
          <p>Depuis Prometheus : sum(rate(http_requests_total[1m])) * 60</p>
        </article>
        <article className="metric-card">
          <span>Erreurs serveur</span>
          <strong>{formatNumber(metrics.errors_5xx_per_second, 4)} / s</strong>
          <p>Statuts 5xx detectes par prometheus-fastapi-instrumentator.</p>
        </article>
        <article className="metric-card">
          <span>Latence P95</span>
          <strong>{formatNumber((metrics.latency_p95_seconds || 0) * 1000, 1)} ms</strong>
          <p>95% des requetes sont plus rapides que cette valeur.</p>
        </article>
        <article className="metric-card">
          <span>Total trains (DB)</span>
          <strong>{totals.total_trains ?? "N/A"}</strong>
          <p>Nuit: {totals.total_night_trains ?? "N/A"} | Jour: {totals.total_day_trains ?? "N/A"}</p>
        </article>
      </section>

      <section className="panel">
        <div className="panel-heading">
          <div>
            <h2>Endpoints les plus utilises</h2>
            <p>Valeurs reelles Prometheus, en requetes par minute.</p>
          </div>
          <span className="muted">MAJ : {lastUpdated || "N/A"}</span>
        </div>
        <div className="endpoint-list">
          {(metrics.endpoints || []).map((item) => (
            <div key={item.metric?.handler || "unknown"} className="endpoint-row">
              <span>{item.metric?.handler || "unknown"}</span>
              <meter min="0" max={Math.max(1, metrics.endpoints?.[0]?.value || 1)} value={item.value} />
              <strong>{formatNumber(item.value)}</strong>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
