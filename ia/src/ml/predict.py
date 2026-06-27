# ia/src/ml/predict.py
#
# Script de prédiction ObRail Europe — version améliorée
#
# Améliorations vs version initiale :
#   - Cache LRU des artefacts (modèle + preprocesseur) : évite le rechargement disque
#     à chaque appel depuis l'API (gain ~200-500ms/requête)
#   - Fallback modèle optimisé → modèle de base (comportement initial conservé)
#   - Logging structuré des prédictions pour traçabilité
#   - Validation renforcée des features avant transformation
#   - Messages d'erreur enrichis pour diagnostics

import argparse
import json
import logging
import sys
from functools import lru_cache
from pathlib import Path

import joblib
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
MODELS_DIR  = ROOT / "ia" / "models"
DATA_ML_DIR = ROOT / "data" / "ml"

logger = logging.getLogger("obrail.ml.predict")


# ---------------------------------------------------------------------------
# Résolution des chemins avec fallback
# ---------------------------------------------------------------------------

def _resolve_model_path(axis: str) -> tuple[Path, Path]:
    """
    Résout les chemins du modèle et du preprocesseur pour un axe donné.
    Priorité : modèle optimisé → modèle de base.
    Lève FileNotFoundError avec un message clair si aucun n'est trouvable.
    """
    if axis == "classification":
        candidates = [
            MODELS_DIR / "xgboost_optimized_clf.joblib",
            MODELS_DIR / "xgboost_clf.joblib",
        ]
        prep_path = DATA_ML_DIR / "preprocessor_classification.joblib"
    else:
        candidates = [
            MODELS_DIR / "ridge_optimized_reg.joblib",
            MODELS_DIR / "ridge_reg.joblib",
        ]
        prep_path = DATA_ML_DIR / "preprocessor_regression.joblib"

    model_path = next((p for p in candidates if p.exists()), None)

    if model_path is None:
        tried = ", ".join(str(p) for p in candidates)
        raise FileNotFoundError(
            f"Aucun modèle trouvé pour l'axe '{axis}'. "
            f"Fichiers cherchés : {tried}. "
            f"Lancez d'abord run_training.py (et optionnellement optimize_xgboost_ridge.py)."
        )

    if not prep_path.exists():
        raise FileNotFoundError(
            f"Preprocesseur introuvable : {prep_path}. "
            f"Lancez d'abord run_training.py."
        )

    return model_path, prep_path


# ---------------------------------------------------------------------------
# Cache des artefacts — chargement unique en mémoire
# ---------------------------------------------------------------------------

@lru_cache(maxsize=4)
def _load_artifacts_cached(model_path_str: str, prep_path_str: str):
    """
    Charge et met en cache le modèle et le preprocesseur.
    Le cache est indexé par les chemins de fichiers (strings, hashable).
    Utiliser des strings plutôt que des Path objects (non-hashable par lru_cache).
    """
    model_path = Path(model_path_str)
    prep_path  = Path(prep_path_str)

    logger.info(f"Chargement du modèle depuis : {model_path.name}")
    model = joblib.load(model_path)
    preprocessor = joblib.load(prep_path)
    logger.info(f"Modèle chargé et mis en cache : {model_path.name}")

    return model, preprocessor


def load_artifacts(axis: str):
    """
    Retourne (model, preprocessor) depuis le cache ou depuis le disque.
    Premier appel : charge depuis le disque (~300ms).
    Appels suivants : retourne depuis le cache mémoire (~0ms).
    """
    model_path, prep_path = _resolve_model_path(axis)
    return _load_artifacts_cached(str(model_path), str(prep_path))


# ---------------------------------------------------------------------------
# Features attendues par axe (doit correspondre à train_utils.py)
# ---------------------------------------------------------------------------

EXPECTED_FEATURES = [
    "year",
    "co2_emissions",
    "co2_per_passenger",
    "co2_lag1",
    "passengers_lag1",
    "passengers_lag2",
    "country_name",
]


def _build_input_df(
    country: str,
    year: int,
    co2_emissions: float,
    co2_per_passenger: float,
    co2_lag1: float,
    passengers_lag1: float,
    passengers_lag2: float,
) -> pd.DataFrame:
    """Construit et valide le DataFrame d'entrée."""
    row = {
        "year": year,
        "co2_emissions": co2_emissions,
        "co2_per_passenger": co2_per_passenger,
        "co2_lag1": co2_lag1,
        "passengers_lag1": passengers_lag1,
        "passengers_lag2": passengers_lag2,
        "country_name": country,
    }
    df = pd.DataFrame([row])
    # Vérification de cohérence
    missing = [f for f in EXPECTED_FEATURES if f not in df.columns]
    if missing:
        raise ValueError(f"Features manquantes dans le DataFrame d'entrée : {missing}")
    return df


# ---------------------------------------------------------------------------
# Fonction de prédiction principale
# ---------------------------------------------------------------------------

def predict(
    axis: str,
    country: str,
    year: int,
    co2_emissions: float,
    co2_per_passenger: float,
    co2_lag1: float,
    passengers_lag1: float,
    passengers_lag2: float,
) -> dict:
    """
    Point d'entrée unique pour toutes les prédictions ObRail.

    Parameters
    ----------
    axis : "classification" | "regression"
    country : nom du pays (doit correspondre au référentiel d'entraînement)
    year : année de prédiction (>= 2013)
    co2_emissions : émissions CO₂ totales (kt)
    co2_per_passenger : émissions CO₂ / passager (kg)
    co2_lag1 : co2_per_passenger année N-1
    passengers_lag1 : passagers année N-1 (k)
    passengers_lag2 : passagers année N-2 (k)

    Returns
    -------
    dict avec les clés : axis, country, year, prediction, label, [probability]
    """
    if axis not in ("classification", "regression"):
        raise ValueError(f"Axe invalide : '{axis}'. Valeurs acceptées : classification, regression.")

    model, preprocessor = load_artifacts(axis)
    input_df = _build_input_df(
        country, year, co2_emissions, co2_per_passenger,
        co2_lag1, passengers_lag1, passengers_lag2,
    )

    X = preprocessor.transform(input_df)
    result = {"axis": axis, "country": country, "year": year}

    if axis == "classification":
        pred = int(model.predict(X)[0])
        result["prediction"] = pred
        result["label"] = "En déclin" if pred == 1 else "En croissance"
        if hasattr(model, "predict_proba"):
            proba = model.predict_proba(X)[0]
            result["probability"] = round(float(proba[1]), 4)
        else:
            result["probability"] = None
    else:
        pred = float(model.predict(X)[0])
        result["prediction"] = round(pred, 2)
        result["label"] = f"{max(0, round(pred)):,} milliers de passagers prévus"

    logger.debug(
        f"[{axis.upper()}] {country} {year} → {result['prediction']} "
        f"({result.get('label', '')})"
    )
    return result


# ---------------------------------------------------------------------------
# Interface CLI (usage standalone ou tests)
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="ObRail Europe — Script de prédiction ML",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples :
  python -m ia.src.ml.predict --axis classification --country France --year 2024 \\
    --co2_emissions 24800 --co2_per_passenger 1.75 --co2_lag1 25100 \\
    --passengers_lag1 88000 --passengers_lag2 86500

  python -m ia.src.ml.predict --axis regression --country Germany --year 2025 \\
    --co2_emissions 32000 --co2_per_passenger 1.60 --co2_lag1 31500 \\
    --passengers_lag1 120000 --passengers_lag2 118000 --json
        """,
    )
    parser.add_argument("--axis", choices=["classification", "regression"], required=True)
    parser.add_argument("--country", required=True)
    parser.add_argument("--year", type=int, required=True)
    parser.add_argument("--co2_emissions", type=float, required=True)
    parser.add_argument("--co2_per_passenger", type=float, required=True)
    parser.add_argument("--co2_lag1", type=float, required=True)
    parser.add_argument("--passengers_lag1", type=float, required=True)
    parser.add_argument("--passengers_lag2", type=float, required=True)
    parser.add_argument("--json", action="store_true", help="Sortie en format JSON brut")
    args = parser.parse_args()

    logging.basicConfig(level=logging.WARNING)  # Silencieux en CLI sauf erreurs

    try:
        result = predict(
            args.axis, args.country, args.year,
            args.co2_emissions, args.co2_per_passenger,
            args.co2_lag1, args.passengers_lag1, args.passengers_lag2,
        )
    except FileNotFoundError as e:
        print(f"\n❌ Modèle introuvable : {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erreur : {e}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"\n[{result['axis'].upper()}] {result['country']} — {result['year']}")
        print(f"  Prédiction    : {result['prediction']}")
        print(f"  Interprétation: {result['label']}")
        if result.get("probability") is not None:
            print(f"  Probabilité   : {result['probability']:.1%}")


if __name__ == "__main__":
    main()