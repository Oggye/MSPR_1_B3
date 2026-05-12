import React from "react";

export default function LogsTab({ data }) {
  const services = data?.docker?.services || [];
  const docker = data?.docker || {};

  return (
    <div className="tab-content">
      <section className="panel">
        <div className="panel-heading">
          <div>
            <h2>Docker Compose</h2>
            <p>Etat lu depuis la commande docker compose ps quand elle est accessible par l'API.</p>
          </div>
          <span className={docker.available ? "pill ok" : "pill warning"}>
            {docker.available ? "Accessible" : "Non accessible"}
          </span>
        </div>

        {services.length > 0 ? (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Service</th>
                  <th>Nom</th>
                  <th>Etat</th>
                  <th>Image</th>
                  <th>Ports</th>
                </tr>
              </thead>
              <tbody>
                {services.map((service) => (
                  <tr key={service.Name || service.Service}>
                    <td>{service.Service}</td>
                    <td>{service.Name}</td>
                    <td>{service.State || service.Status}</td>
                    <td>{service.Image}</td>
                    <td>{service.Publishers ? JSON.stringify(service.Publishers) : service.Ports}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <pre className="console-output">{docker.error || docker.stderr || "Aucune information Docker disponible."}</pre>
        )}
      </section>

      <section className="panel">
        <div className="panel-heading">
          <div>
            <h2>API interne</h2>
            <p>Dernier chargement des donnees techniques.</p>
          </div>
          <span className="pill neutral">{data?.generated_at || "N/A"}</span>
        </div>
        <pre className="console-output">
          {JSON.stringify(
            {
              prometheus: data?.prometheus?.available,
              grafana: data?.grafana?.available,
              api_up: data?.metrics?.api_up,
              requests_per_minute: data?.metrics?.requests_per_minute,
            },
            null,
            2
          )}
        </pre>
      </section>
    </div>
  );
}
