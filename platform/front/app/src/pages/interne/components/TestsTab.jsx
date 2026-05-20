import React from "react";

const renderReportValue = (value) => {
  if (Array.isArray(value)) return value.join(", ");
  if (value && typeof value === "object") return JSON.stringify(value);
  return String(value ?? "N/A");
};

const getLineClass = (line = "") => {
  const upper = line.toUpperCase();
  if (upper.includes("FAILED")) return "log-line failed";
  if (upper.includes("PASSED")) return "log-line passed";
  if (upper.includes("WARNING")) return "log-line warning";
  if (upper.includes("ERROR")) return "log-line failed";
  return "log-line";
};

const getStatusClass = (status) => {
  if (status === "passed") return "pill ok";
  if (status === "failed") return "pill danger";
  if (status === "running") return "pill warning";
  return "pill neutral";
};

const getStatusLabel = (status) => {
  if (status === "passed") return "Termine (OK)";
  if (status === "failed") return "Termine (KO)";
  if (status === "running") return "En cours";
  return "Idle";
};

export default function TestsTab({ data, actionState, testCategories, onRunDiagnostic, onRunTestsByCategory }) {
  const quality = data?.reports?.quality || {};
  const diagnostic = actionState?.diagnostic?.report || data?.reports?.diagnostic;
  const qualitySummary = quality.summary || {};
  const dataQuality = quality.traceability?.data_quality || {};
  const totals = data?.db_totals || {};
  const tests = actionState?.tests || {};

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
          <span>Total trains</span>
          <strong>{totals.total_trains ?? 0}</strong>
          <p>Nuit: {totals.total_night_trains ?? 0} | Jour: {totals.total_day_trains ?? 0}</p>
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
            <p>Execution detaillee en temps reel, par categorie independante.</p>
          </div>
        </div>
        <div className="tab-content">
          {(testCategories || []).map((category) => {
            const state = tests[category.key] || {};
            return (
              <article className="panel" key={category.key}>
                <div className="panel-heading">
                  <div>
                    <h3>{category.label}</h3>
                    <p>{state.count || 0} ligne(s) de log</p>
                  </div>
                  <div className="header-actions">
                    <span className={getStatusClass(state.status)}>{getStatusLabel(state.status)}</span>
                    <button
                      type="button"
                      className="secondary-button"
                      onClick={() => onRunTestsByCategory(category.key)}
                      disabled={state.running}
                    >
                      {state.running ? "Execution..." : "Lancer"}
                    </button>
                  </div>
                </div>
                {state.error && <pre className="console-output danger">{state.error}</pre>}
                <div className="console-output">
                  {(state.lines || []).length === 0 ? (
                    <span className="muted">Aucun log pour cette categorie.</span>
                  ) : (
                    (state.lines || []).map((line, idx) => (
                      <div key={`${category.key}-${idx}`} className={getLineClass(line)}>{line}</div>
                    ))
                  )}
                </div>
              </article>
            );
          })}
        </div>
      </section>
    </div>
  );
}
