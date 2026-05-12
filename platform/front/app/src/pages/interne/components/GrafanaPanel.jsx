import React from "react";

export default function GrafanaPanel({ data }) {
  const dashboardUrl =
    data?.grafana?.dashboard_url ||
    "http://localhost:3001/d/obrail-api-monitoring/obrail-api-monitoring";
  const embedUrl = `${dashboardUrl}?orgId=1&kiosk`;

  return (
    <section className="panel grafana-panel">
      <div className="panel-heading">
        <div>
          <h2>Grafana</h2>
          <p>Dashboard Prometheus provisionne automatiquement.</p>
        </div>
        <a href={dashboardUrl} target="_blank" rel="noreferrer" className="secondary-button">
          Ouvrir Grafana
        </a>
      </div>
      <iframe src={embedUrl} title="Dashboard Grafana ObRail" />
    </section>
  );
}
