// fichier : platform/front/app/src/pages/ia/IaPage.js
//
// Page de prédiction IA — ObRail Europe
// Interface permettant d'interroger les modèles XGBoost (classification)
// et Ridge (régression) via l'API /api/predict.
//
// Architecture :
//   - Tout appel API passe par src/services/api.js (predictClassification / predictRegression)
//   - Le streaming est simulé côté client (affichage progressif des champs de la réponse)
//     pour être prêt à basculer sur un vrai stream SSE/WebSocket si l'API l'expose un jour.
//   - Le composant est découpé en sous-composants internes pour rester lisible.

import { useState, useRef, useEffect, useCallback } from 'react';
import { predictClassification, predictRegression } from '../../services/api';
import './IaPage.css';

// ---------------------------------------------------------------------------
// Constantes
// ---------------------------------------------------------------------------

// Liste des pays supportés par le modèle (référentiel OHE côté API)
const KNOWN_COUNTRIES = [
  'Austria','Belgium','Bulgaria','Croatia','Cyprus','Czech Republic',
  'Denmark','Estonia','Finland','France','Germany','Greece','Hungary',
  'Ireland','Italy','Latvia','Lithuania','Luxembourg','Malta',
  'Netherlands','Poland','Portugal','Romania','Slovakia','Slovenia',
  'Spain','Sweden','Albania','Bosnia and Herzegovina','Iceland',
  'Liechtenstein','Montenegro','North Macedonia','Norway','Serbia',
  'Switzerland','Turkey','United Kingdom','Belarus','Moldova','Ukraine',
].sort();

const DEFAULT_FORM = {
  country: 'France',
  year: 2024,
  co2_emissions: 24800,
  co2_per_passenger: 1.75,
  co2_lag1: 25100,
  passengers_lag1: 88000,
  passengers_lag2: 86500,
};

// Délai entre l'affichage de chaque "bloc" de réponse lors du faux streaming
const STREAM_DELAY_MS = 120;

// ---------------------------------------------------------------------------
// Sous-composant : champ de formulaire
// ---------------------------------------------------------------------------

function FormField({ label, name, type = 'number', value, onChange, options, hint }) {
  return (
    <div className="ia-field">
      <label className="ia-field__label" htmlFor={name}>
        {label}
        {hint && <span className="ia-field__hint">{hint}</span>}
      </label>
      {type === 'select' ? (
        <select
          id={name}
          name={name}
          className="ia-field__input"
          value={value}
          onChange={onChange}
        >
          {options.map(opt => (
            <option key={opt} value={opt}>{opt}</option>
          ))}
        </select>
      ) : (
        <input
          id={name}
          name={name}
          type={type}
          className="ia-field__input"
          value={value}
          onChange={onChange}
          step="any"
        />
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Sous-composant : badge de niveau de risque / tendance
// ---------------------------------------------------------------------------

function Badge({ label, variant }) {
  return <span className={`ia-badge ia-badge--${variant}`}>{label}</span>;
}

function getRiskVariant(level) {
  const map = { Faible: 'success', Modéré: 'warning', Élevé: 'danger', Critique: 'critical' };
  return map[level] || 'neutral';
}

function getTrendVariant(label) {
  const map = { Croissance: 'success', Stable: 'neutral', Déclin: 'danger' };
  return map[label] || 'neutral';
}

// ---------------------------------------------------------------------------
// Sous-composant : bloc de réponse classification (affiché progressivement)
// ---------------------------------------------------------------------------

function ClassificationResult({ data, visibleFields }) {
  if (!data) return null;

  const fields = [
    // [clé interne, composant JSX]
    ['header', (
      <div key="header" className="ia-result__header ia-anim">
        <div className="ia-result__prediction">
          <span className="ia-result__label">{data.label}</span>
          <Badge label={data.risk_level} variant={getRiskVariant(data.risk_level)} />
        </div>
        <div className="ia-result__confidence">
          <span>Confiance</span>
          <div className="ia-progress">
            <div
              className="ia-progress__bar"
              style={{ width: `${data.confidence_score}%` }}
            />
          </div>
          <span className="ia-result__pct">{data.confidence_score.toFixed(1)}%</span>
        </div>
      </div>
    )],
    ['message', (
      <p key="message" className="ia-result__message ia-anim">{data.business_message}</p>
    )],
    ['risk', (
      <div key="risk" className="ia-result__section ia-anim">
        <h4>Analyse du risque</h4>
        <p>{data.risk_description}</p>
        <p className="ia-result__prob">
          Probabilité de déclin : <strong>{(data.probability_decline * 100).toFixed(1)}%</strong>
        </p>
      </div>
    )],
    ['drivers', (
      <div key="drivers" className="ia-result__section ia-anim">
        <h4>Variables déterminantes</h4>
        <div className="ia-drivers">
          {data.key_drivers.map(d => (
            <div key={d.variable} className="ia-driver">
              <div className="ia-driver__name">{d.variable}</div>
              <div className="ia-driver__value">{d.value}</div>
              <div className={`ia-driver__dir ia-driver__dir--${d.direction === 'Favorable' ? 'up' : d.direction === 'Défavorable' ? 'down' : 'neutral'}`}>
                {d.direction}
              </div>
              <div className="ia-driver__expl">{d.explanation}</div>
            </div>
          ))}
        </div>
      </div>
    )],
    ['recommendations', (
      <div key="recs" className="ia-result__section ia-anim">
        <h4>Recommandations stratégiques</h4>
        <ul className="ia-recs">
          {data.recommendations.map((r, i) => <li key={i}>{r}</li>)}
        </ul>
      </div>
    )],
    ['meta', (
      <div key="meta" className="ia-result__meta ia-anim">
        <span>{data.metadata.model_name}</span>
        <span>·</span>
        <span>Inférence : {data.inference_ms} ms</span>
        <span>·</span>
        <span>Modèle du {data.metadata.training_date}</span>
      </div>
    )],
  ];

  return (
    <div className="ia-result">
      {fields.slice(0, visibleFields).map(([, jsx]) => jsx)}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Sous-composant : bloc de réponse régression (affiché progressivement)
// ---------------------------------------------------------------------------

function RegressionResult({ data, visibleFields }) {
  if (!data) return null;

  const fields = [
    ['header', (
      <div key="header" className="ia-result__header ia-anim">
        <div className="ia-result__prediction">
          <span className="ia-result__label">{data.prediction_display}</span>
          <Badge label={data.trend_label} variant={getTrendVariant(data.trend_label)} />
        </div>
        {data.trend_vs_lag1 !== null && (
          <div className="ia-result__trend">
            <span className={`ia-trend ${data.trend_vs_lag1 >= 0 ? 'ia-trend--up' : 'ia-trend--down'}`}>
              {data.trend_vs_lag1 >= 0 ? '▲' : '▼'} {Math.abs(data.trend_vs_lag1).toFixed(2)}% vs N−1
            </span>
            {data.trend_vs_lag2 !== null && (
              <span className={`ia-trend ${data.trend_vs_lag2 >= 0 ? 'ia-trend--up' : 'ia-trend--down'}`}>
                {data.trend_vs_lag2 >= 0 ? '▲' : '▼'} {Math.abs(data.trend_vs_lag2).toFixed(2)}% vs N−2
              </span>
            )}
          </div>
        )}
      </div>
    )],
    ['message', (
      <p key="message" className="ia-result__message ia-anim">{data.business_message}</p>
    )],
    ['drivers', (
      <div key="drivers" className="ia-result__section ia-anim">
        <h4>Variables déterminantes</h4>
        <div className="ia-drivers">
          {data.key_drivers.map(d => (
            <div key={d.variable} className="ia-driver">
              <div className="ia-driver__name">{d.variable}</div>
              <div className="ia-driver__value">{d.value}</div>
              <div className="ia-driver__expl">{d.explanation}</div>
            </div>
          ))}
        </div>
      </div>
    )],
    ['reliability', (
      <div key="reliability" className="ia-result__section ia-anim">
        <h4>Fiabilité du modèle</h4>
        <p>{data.reliability_note}</p>
      </div>
    )],
    ['meta', (
      <div key="meta" className="ia-result__meta ia-anim">
        <span>{data.metadata.model_name}</span>
        <span>·</span>
        <span>Inférence : {data.inference_ms} ms</span>
        <span>·</span>
        <span>Modèle du {data.metadata.training_date}</span>
      </div>
    )],
  ];

  return (
    <div className="ia-result">
      {fields.slice(0, visibleFields).map(([, jsx]) => jsx)}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Sous-composant : zone de warnings
// ---------------------------------------------------------------------------

function Warnings({ warnings }) {
  if (!warnings?.length) return null;
  return (
    <div className="ia-warnings ia-anim">
      {warnings.map((w, i) => (
        <div key={i} className="ia-warning">
          <span className="ia-warning__icon">⚠</span>
          <span>{w}</span>
        </div>
      ))}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Composant principal
// ---------------------------------------------------------------------------

export default function IaPage() {
  // --- État du formulaire ---
  const [form, setForm] = useState(DEFAULT_FORM);
  const [axis, setAxis] = useState('classification'); // 'classification' | 'regression'

  // --- État de la réponse et du streaming ---
  const [result, setResult] = useState(null);       // objet complet retourné par l'API
  const [visibleFields, setVisibleFields] = useState(0); // nombre de "blocs" affichés
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  // Référence pour le scroll automatique
  const resultRef = useRef(null);
  // Référence pour le timer de streaming
  const streamTimerRef = useRef(null);

  // Nettoyer le timer si le composant est démonté
  useEffect(() => {
    return () => clearTimeout(streamTimerRef.current);
  }, []);

  // Scroll automatique quand un nouveau bloc apparaît
  useEffect(() => {
    if (visibleFields > 0 && resultRef.current) {
      resultRef.current.scrollIntoView({ behavior: 'smooth', block: 'end' });
    }
  }, [visibleFields]);

  // --- Gestion du formulaire ---
  const handleChange = useCallback((e) => {
    const { name, value } = e.target;
    setForm(prev => ({
      ...prev,
      [name]: name === 'country' ? value : Number(value),
    }));
  }, []);

  // --- Simulation du streaming : afficher les blocs un à un ---
  const startStreaming = useCallback((totalFields) => {
    let current = 0;
    const tick = () => {
      current += 1;
      setVisibleFields(current);
      if (current < totalFields) {
        streamTimerRef.current = setTimeout(tick, STREAM_DELAY_MS);
      }
    };
    streamTimerRef.current = setTimeout(tick, STREAM_DELAY_MS);
  }, []);

  // --- Envoi de la requête ---
  const handleSubmit = useCallback(async () => {
    // Réinitialiser l'état
    clearTimeout(streamTimerRef.current);
    setResult(null);
    setVisibleFields(0);
    setError(null);
    setIsLoading(true);

    try {
      const payload = { ...form };
      const fn = axis === 'classification' ? predictClassification : predictRegression;
      const response = await fn(payload);
      const data = response.data;

      setResult(data);
      setIsLoading(false);

      // Nombre de blocs selon l'axe
      const totalFields = axis === 'classification' ? 6 : 5;
      startStreaming(totalFields);

    } catch (err) {
      setIsLoading(false);

      // Gestion des erreurs structurées (FastAPI renvoie { detail: { error, message } })
      if (err.response) {
        const detail = err.response.data?.detail;
        if (typeof detail === 'object') {
          setError(`${detail.error} — ${detail.message}`);
        } else {
          setError(detail || `Erreur ${err.response.status}`);
        }
      } else if (err.request) {
        setError('Impossible de joindre l\'API. Vérifiez que le serveur est démarré sur le port 8000.');
      } else {
        setError(err.message || 'Une erreur inattendue s\'est produite.');
      }
    }
  }, [form, axis, startStreaming]);

  // Envoi avec la touche Entrée dans un input numérique
  const handleKeyDown = useCallback((e) => {
    if (e.key === 'Enter' && !e.shiftKey && !isLoading) {
      e.preventDefault();
      handleSubmit();
    }
  }, [handleSubmit, isLoading]);

  // ---------------------------------------------------------------------------
  // Rendu
  // ---------------------------------------------------------------------------

  const maxFields = axis === 'classification' ? 6 : 5;
  const isStreaming = result !== null && visibleFields < maxFields;

  return (
    <div className="ia-page">
      {/* En-tête */}
      <header className="ia-header">
        <div className="ia-header__eyebrow">Analyse prédictive</div>
        <h1 className="ia-header__title">Modèles IA ferroviaires</h1>
        <p className="ia-header__desc">
          Interrogez les modèles d'apprentissage automatique d'ObRail Europe pour anticiper
          la fréquentation ferroviaire ou détecter un risque de déclin sur un réseau national.
        </p>
      </header>

      <div className="ia-layout">
        {/* ---- Panneau gauche : formulaire ---- */}
        <aside className="ia-panel ia-panel--form">
          {/* Sélecteur d'axe */}
          <div className="ia-axis-switcher">
            <button
              type="button"
              className={`ia-axis-btn ${axis === 'classification' ? 'ia-axis-btn--active' : ''}`}
              onClick={() => { setAxis('classification'); setResult(null); setError(null); }}
            >
              Déclin ferroviaire
            </button>
            <button
              type="button"
              className={`ia-axis-btn ${axis === 'regression' ? 'ia-axis-btn--active' : ''}`}
              onClick={() => { setAxis('regression'); setResult(null); setError(null); }}
            >
              Volume passagers
            </button>
          </div>

          {/* Description de l'axe sélectionné */}
          <p className="ia-axis-desc">
            {axis === 'classification'
              ? 'XGBoost optimisé — F1=0.63, ROC-AUC=0.83 — Détecte si un réseau ferroviaire est en croissance ou en déclin.'
              : 'Ridge régularisé — R²=0.996, MAE=4 339 k passagers — Prédit le volume de voyageurs pour l\'année cible.'}
          </p>

          {/* Champs de saisie */}
          <div className="ia-form" onKeyDown={handleKeyDown}>
            <FormField
              label="Pays"
              name="country"
              type="select"
              value={form.country}
              onChange={handleChange}
              options={KNOWN_COUNTRIES}
            />
            <FormField
              label="Année cible"
              name="year"
              value={form.year}
              onChange={handleChange}
              hint="2013 – 2035"
            />
            <div className="ia-field-group">
              <FormField
                label="Émissions CO₂ totales"
                name="co2_emissions"
                value={form.co2_emissions}
                onChange={handleChange}
                hint="k tonnes"
              />
              <FormField
                label="CO₂ / passager (N)"
                name="co2_per_passenger"
                value={form.co2_per_passenger}
                onChange={handleChange}
                hint="kg/passager"
              />
            </div>
            <FormField
              label="CO₂ / passager (N−1)"
              name="co2_lag1"
              value={form.co2_lag1}
              onChange={handleChange}
              hint="kg/passager"
            />
            <div className="ia-field-group">
              <FormField
                label="Passagers (N−1)"
                name="passengers_lag1"
                value={form.passengers_lag1}
                onChange={handleChange}
                hint="milliers"
              />
              <FormField
                label="Passagers (N−2)"
                name="passengers_lag2"
                value={form.passengers_lag2}
                onChange={handleChange}
                hint="milliers"
              />
            </div>

            <button
              type="button"
              className={`ia-submit ${isLoading ? 'ia-submit--loading' : ''}`}
              onClick={handleSubmit}
              disabled={isLoading}
              aria-busy={isLoading}
            >
              {isLoading ? (
                <>
                  <span className="ia-spinner" aria-hidden="true" />
                  Analyse en cours…
                </>
              ) : (
                'Lancer la prédiction'
              )}
            </button>
          </div>
        </aside>

        {/* ---- Panneau droit : résultat ---- */}
        <section className="ia-panel ia-panel--result" ref={resultRef}>
          {/* État vide */}
          {!isLoading && !result && !error && (
            <div className="ia-empty">
              <div className="ia-empty__icon" aria-hidden="true">◎</div>
              <p className="ia-empty__title">Aucune prédiction encore lancée</p>
              <p className="ia-empty__sub">
                Renseignez les paramètres à gauche et cliquez sur&nbsp;
                <em>Lancer la prédiction</em>.
              </p>
            </div>
          )}

          {/* État de chargement */}
          {isLoading && (
            <div className="ia-loading-state">
              <div className="ia-pulse-ring" aria-hidden="true">
                <div /><div /><div />
              </div>
              <p>Le modèle analyse les données…</p>
            </div>
          )}

          {/* Erreur */}
          {error && (
            <div className="ia-error ia-anim" role="alert">
              <div className="ia-error__icon" aria-hidden="true">✕</div>
              <div>
                <strong>Prédiction impossible</strong>
                <p>{error}</p>
              </div>
            </div>
          )}

          {/* Résultat */}
          {result && !isLoading && (
            <>
              {/* Avertissements (affichés immédiatement, hors streaming) */}
              <Warnings warnings={result.warnings} />

              {/* Résultat progressif selon l'axe */}
              {axis === 'classification' ? (
                <ClassificationResult data={result} visibleFields={visibleFields} />
              ) : (
                <RegressionResult data={result} visibleFields={visibleFields} />
              )}

              {/* Indicateur "en cours d'affichage" */}
              {isStreaming && (
                <div className="ia-stream-cursor" aria-hidden="true">▌</div>
              )}
            </>
          )}
        </section>
      </div>
    </div>
  );
}