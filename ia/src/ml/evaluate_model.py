# ia/src/ml/evaluate_model.py

import pandas as pd
import json
from .config import MODELS_DIR, REPORTS_DIR
from .models.train_utils import load_model_and_metrics


def load_all_metrics(axis="clf"):
    if axis == "clf":
        model_names = ["logistic", "random_forest", "xgboost", "mlp"]
    else:
        model_names = ["ridge", "random_forest", "xgboost"]

    data = []
    for name in model_names:
        try:
            _, metrics = load_model_and_metrics(name, axis=axis)
            metrics["model"] = name
            data.append(metrics)
        except FileNotFoundError as e:
            print(f"⚠️  {e}")
    return pd.DataFrame(data)


def save_comparison(df, filename):
    if df is None or df.empty:
        print("Aucune métrique à comparer.")
        return
    output_path = REPORTS_DIR / filename
    df.to_csv(output_path, index=False)
    print(f"✅ Rapport sauvegardé : {output_path}")
    print(df.to_string(index=False))


def main():
    print("\n📊 Comparaison — Axe Classification (en_declin)")
    df_clf = load_all_metrics(axis="clf")
    if not df_clf.empty:
        cols = [c for c in ["model", "accuracy", "precision", "recall", "f1", "roc_auc"]
                if c in df_clf.columns]
        save_comparison(df_clf[cols], "comparison_classification.csv")

    print("\n📊 Comparaison — Axe Régression (passengers)")
    df_reg = load_all_metrics(axis="reg")
    if not df_reg.empty:
        cols = [c for c in ["model", "mae", "rmse", "r2"] if c in df_reg.columns]
        save_comparison(df_reg[cols], "comparison_regression.csv")


if __name__ == "__main__":
    main()