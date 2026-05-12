import React from "react";

export default function PipelinesTab({ data }) {
  const dockerServices = data?.docker?.services || [];
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
          <span className="pill neutral">GitHub Actions configure</span>
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
        <h2>Etat de reference</h2>
        <p className="text-block">
          Le front affiche ici ce qui peut etre mesure localement. Pour l'historique complet GitHub Actions,
          il faudrait connecter l'API GitHub ou exposer les resultats CI dans un artefact lisible par l'application.
        </p>
      </section>
    </div>
  );
}
