import React from "react";

export default function PipelinesTab({ data }) {
  const dockerServices = data?.docker?.services || [];
  const ci = data?.ci_cd || {};
  const ciRuns = ci.runs || [];
  const apiService = dockerServices.find((service) => service.Service === "api");
  const frontService = dockerServices.find((service) => service.Service === "front");

  return (
    <div className="tab-content">
      <section className="panel">
        <div className="panel-heading">
          <div>
            <h2>Pipeline local</h2>
            <p>Vue simple basee sur les services construits et l'etat Docker Compose.</p>
          </div>
          <span className={ci.available ? "pill ok" : "pill warning"}>
            {ci.available ? "GitHub Actions connecte" : "GitHub Actions indisponible"}
          </span>
        </div>

        <div className="pipeline-steps">
          <article>
            <span>1</span>
            <h3>Build API</h3>
            <p>{apiService ? apiService.State || apiService.Status : "Service API non detecte"}</p>
          </article>
          <article>
            <span>2</span>
            <h3>Build Front</h3>
            <p>{frontService ? frontService.State || frontService.Status : "Service front non detecte"}</p>
          </article>
          <article>
            <span>3</span>
            <h3>Tests</h3>
            <p>Executables depuis l'onglet Tests & Qualite.</p>
          </article>
          <article>
            <span>4</span>
            <h3>Monitoring</h3>
            <p>Prometheus et Grafana verifient l'API en continu.</p>
          </article>
        </div>
      </section>

      <section className="panel">
        <h2>GitHub Actions</h2>
        {ciRuns.length > 0 ? (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Workflow</th>
                  <th>Branche</th>
                  <th>Status</th>
                  <th>Conclusion</th>
                  <th>Maj</th>
                </tr>
              </thead>
              <tbody>
                {ciRuns.map((run) => (
                  <tr key={`${run.name}-${run.updated_at}`}>
                    <td>{run.url ? <a href={run.url} target="_blank" rel="noreferrer">{run.name}</a> : run.name}</td>
                    <td>{run.branch || "N/A"}</td>
                    <td>{run.status || "N/A"}</td>
                    <td>{run.conclusion || "N/A"}</td>
                    <td>{run.updated_at || "N/A"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="text-block">
            {ci.message || "Connexion GitHub Actions non disponible."}
            {ci.error ? ` Detail: ${ci.error}` : ""}
          </p>
        )}
      </section>
    </div>
  );
}
