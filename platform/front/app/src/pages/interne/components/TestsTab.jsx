import React from "react";

const renderReportValue = (value) => {
  if (Array.isArray(value)) return value.join(", ");
  if (value && typeof value === "object") return JSON.stringify(value);
  return String(value ?? "N/A");
};

export default function TestsTab({ data, actionState, onRunDiagnostic, onRunTests }) {
  const quality = data?.reports?.quality || {};
  const diagnostic = actionState?.diagnostic?.report || data?.reports?.diagnostic;
  const qualitySummary = quality.summary || {};
  const dataQuality = quality.traceability?.data_quality || {};

  return (
    <div className="tab-content">
      <section className="metric-grid">
        <article className="metric-card">
          <span>Sources traitees</span>
          <strong>{qualitySummary.total_sources_processed || 0}</strong>
          <p>Rapport qualite : quality_reports.json</p>
        </article>
        <article className="metric-card">
          <span>Lignes estimees</span>
          <strong>{qualitySummary.total_records_estimated || 0}</strong>
          <p>Total estime dans le rapport qualite.</p>
        </article>
        <article className="metric-card">
          <span>Pays</span>
          <strong>{dataQuality.total_countries || 0}</strong>
          <p>{dataQuality.unknown_countries || 0} pays inconnus.</p>
        </article>
        <article className="metric-card">
          <span>Trains de nuit</span>
          <strong>{dataQuality.night_train_records || 0}</strong>
          <p>Enregistrements warehouse.</p>
        </article>
      </section>

      <section className="panel">
        <div className="panel-heading">
          <div>
            <h2>Rapport de qualite</h2>
            <p>Valeurs lues depuis le fichier expose par l'API.</p>
          </div>
          <span className={qualitySummary.success ? "pill ok" : "pill warning"}>
            {qualitySummary.success ? "OK" : "A verifier"}
          </span>
        </div>
        <div className="report-grid">
          {(quality.reports || []).map((report) => (
            <article className="report-item" key={report.source}>
              <h3>{report.source}</h3>
              {Object.entries(report)
                .filter(([key]) => key !== "source")
                .slice(0, 6)
                .map(([key, value]) => (
                  <p key={key}>
                    <span>{key}</span>
                    <strong>{renderReportValue(value)}</strong>
                  </p>
                ))}
            </article>
          ))}
        </div>
      </section>

      <section className="panel">
        <div className="panel-heading">
          <div>
            <h2>Diagnostic ETL</h2>
            <p>Lance etl/audit/diagnostic.py depuis l'API si le script est accessible.</p>
          </div>
          <button type="button" className="primary-button" onClick={onRunDiagnostic} disabled={actionState?.runningDiagnostic}>
            {actionState?.runningDiagnostic ? "Diagnostic en cours" : "Lancer le diagnostic"}
          </button>
        </div>
        {actionState?.diagnostic?.stderr && <pre className="console-output danger">{actionState.diagnostic.stderr}</pre>}
        {actionState?.diagnostic?.stdout && <pre className="console-output">{actionState.diagnostic.stdout}</pre>}
        {diagnostic ? (
          <pre className="console-output">{JSON.stringify(diagnostic, null, 2)}</pre>
        ) : (
          <p className="muted">Aucun rapport diagnostic disponible pour le moment.</p>
        )}
      </section>

      <section className="panel">
        <div className="panel-heading">
          <div>
            <h2>Tests backend</h2>
            <p>Execution pytest via l'API interne si le dossier de tests est monte.</p>
          </div>
          <button type="button" className="secondary-button" onClick={onRunTests} disabled={actionState?.runningTests}>
            {actionState?.runningTests ? "Tests en cours" : "Lancer les tests"}
          </button>
        </div>
        {actionState?.tests ? (
          <pre className={actionState.tests.success ? "console-output" : "console-output danger"}>
            {actionState.tests.stdout || actionState.tests.stderr || actionState.tests.error}
          </pre>
        ) : (
          <p className="muted">Aucun lancement de tests depuis cette page.</p>
        )}
      </section>
    </div>
  );
}
