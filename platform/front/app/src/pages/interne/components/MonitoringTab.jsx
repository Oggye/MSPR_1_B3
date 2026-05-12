import React from "react";
import GrafanaPanel from "./GrafanaPanel";

const formatMs = (seconds) => {
  if (seconds === null || seconds === undefined || Number.isNaN(seconds)) return "N/A";
  return `${(Number(seconds) * 1000).toFixed(1)} ms`;
};

export default function MonitoringTab({ data }) {
  const metrics = data?.metrics || {};
  const targets = data?.prometheus?.targets || [];

  return (
    <div className="tab-content">
      <GrafanaPanel data={data} />

      <section className="panel">
        <div className="panel-heading">
          <div>
            <h2>Prometheus</h2>
            <p>Etat des targets scrapees par Prometheus.</p>
          </div>
          <span className={data?.prometheus?.available ? "pill ok" : "pill warning"}>
            {data?.prometheus?.available ? "Disponible" : "Indisponible"}
          </span>
        </div>

        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Job</th>
                <th>Instance</th>
                <th>Etat</th>
                <th>Dernier scrape</th>
                <th>Duree</th>
              </tr>
            </thead>
            <tbody>
              {targets.map((target) => (
                <tr key={target.scrapeUrl}>
                  <td>{target.labels?.job}</td>
                  <td>{target.labels?.instance}</td>
                  <td>
                    <span className={target.health === "up" ? "pill ok" : "pill danger"}>
                      {target.health}
                    </span>
                  </td>
                  <td>{target.lastScrape || "N/A"}</td>
                  <td>{target.lastScrapeDuration ? `${target.lastScrapeDuration.toFixed(4)} s` : "N/A"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className="panel two-columns">
        <div>
          <h2>Requetes suivies</h2>
          <dl className="definition-list">
            <dt>Trafic API</dt>
            <dd>sum(rate(http_requests_total[1m])) * 60 = {(metrics.requests_per_minute || 0).toFixed(2)} / min</dd>
            <dt>Erreurs API</dt>
            <dd>status=~"5..|5xx" = {(metrics.errors_5xx_per_second || 0).toFixed(4)} / s</dd>
            <dt>Latence moyenne</dt>
            <dd>{formatMs(metrics.latency_avg_seconds)}</dd>
            <dt>Latence P95</dt>
            <dd>{formatMs(metrics.latency_p95_seconds)}</dd>
          </dl>
        </div>
        <div>
          <h2>Lecture rapide</h2>
          <p className="text-block">
            Le trafic, les erreurs et les latences viennent directement de Prometheus.
            Grafana affiche le detail visuel avec les memes metriques, ce qui evite les valeurs statiques dans le front.
          </p>
        </div>
      </section>
    </div>
  );
}
