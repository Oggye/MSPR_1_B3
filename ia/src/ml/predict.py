# Fichier: ia/src/ml/predict.py

import argparse
import json
import sys
from pathlib import Path
import joblib
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
MODELS_DIR  = ROOT / "ia" / "models"
DATA_ML_DIR = ROOT / "data" / "ml"

CLF_MODEL_PATH = MODELS_DIR / "xgboost_optimized_clf.joblib"
REG_MODEL_PATH = MODELS_DIR / "ridge_optimized_reg.joblib"
CLF_PREP_PATH  = DATA_ML_DIR / "preprocessor_classification.joblib"
REG_PREP_PATH  = DATA_ML_DIR / "preprocessor_regression.joblib"

def load_artifacts(axis):
    if axis == "classification":
        model_path, prep_path = CLF_MODEL_PATH, CLF_PREP_PATH
    else:
        model_path, prep_path = REG_MODEL_PATH, REG_PREP_PATH
    for p in (model_path, prep_path):
        if not p.exists():
            raise FileNotFoundError(f"Fichier introuvable : {p}")
    return joblib.load(model_path), joblib.load(prep_path)

def predict(axis, country, year, co2_emissions, co2_per_passenger,
            co2_lag1, passengers_lag1, passengers_lag2):
    model, preprocessor = load_artifacts(axis)
    input_df = pd.DataFrame([{
        "year": year, "co2_emissions": co2_emissions,
        "co2_per_passenger": co2_per_passenger, "co2_lag1": co2_lag1,
        "passengers_lag1": passengers_lag1, "passengers_lag2": passengers_lag2,
        "country_name": country,
    }])
    X = preprocessor.transform(input_df)
    result = {"axis": axis, "country": country, "year": year}
    if axis == "classification":
        pred = int(model.predict(X)[0])
        result["prediction"] = pred
        result["label"] = "En déclin" if pred == 1 else "En croissance"
        if hasattr(model, "predict_proba"):
            result["probability"] = round(float(model.predict_proba(X)[0][1]), 4)
    else:
        pred = float(model.predict(X)[0])
        result["prediction"] = round(pred, 2)
        result["label"] = f"{round(pred):,} milliers de passagers prévus"
    return result

def main():
    parser = argparse.ArgumentParser(description="ObRail Europe — Script de prédiction")
    parser.add_argument("--axis", choices=["classification", "regression"], required=True)
    parser.add_argument("--country", required=True)
    parser.add_argument("--year", type=int, required=True)
    parser.add_argument("--co2_emissions", type=float, required=True)
    parser.add_argument("--co2_per_passenger", type=float, required=True)
    parser.add_argument("--co2_lag1", type=float, required=True)
    parser.add_argument("--passengers_lag1", type=float, required=True)
    parser.add_argument("--passengers_lag2", type=float, required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result = predict(
        args.axis, args.country, args.year,
        args.co2_emissions, args.co2_per_passenger,
        args.co2_lag1, args.passengers_lag1, args.passengers_lag2
    )
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