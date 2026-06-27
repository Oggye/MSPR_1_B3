# ia/src/ml/models/optimize_xgboost_ridge.py
#
# CORRECTIF #9 : chemins des métriques JSON recalculés depuis la racine du projet
# via MODELS_DIR (importé depuis config), au lieu de chemins relatifs au répertoire
# de travail courant ("ia/models/...") qui échouaient silencieusement hors racine.
#
# CORRECTIF #10 : suppression de random_state=42 sur Ridge.
# Ridge (sklearn.linear_model.Ridge) n'accepte pas ce paramètre — il lève un TypeError
# dans certaines versions de scikit-learn et est ignoré dans d'autres.
# Ridge est un solveur déterministe (pas d'aléatoire), random_state n'a pas de sens.

import json
from pathlib import Path
from sklearn.model_selection import RandomizedSearchCV, GridSearchCV
from sklearn.linear_model import Ridge
import xgboost as xgb

from .train_utils import (
    load_classification_data, prepare_classification_data,
    load_regression_data, prepare_regression_data,
    save_model_and_metrics, evaluate_classification, evaluate_regression,
)
from ..config import MODELS_DIR


# ==================================================================
# Optimisation Classification XGBoost (F1)
# ==================================================================

def optimize_xgboost_clf():
    print("\n--- Optimisation Classification : XGBoost ---")

    X, y = load_classification_data()
    X_train, X_test, y_train, y_test, preprocessor = prepare_classification_data(X, y)

    param_dist = {
        'n_estimators': [50, 100, 200, 300],
        'max_depth': [2, 3, 4, 5],
        'learning_rate': [0.01, 0.05, 0.1, 0.2],
        'subsample': [0.7, 0.8, 1.0],
        'scale_pos_weight': [1, 1.5, 2],
    }

    xgb_model = xgb.XGBClassifier(random_state=42, eval_metric='logloss')

    random_search = RandomizedSearchCV(
        estimator=xgb_model,
        param_distributions=param_dist,
        n_iter=30,
        scoring='f1',
        cv=5,
        verbose=1,
        random_state=42,
        n_jobs=-1
    )
    random_search.fit(X_train, y_train)

    best_model = random_search.best_estimator_
    print("Meilleurs paramètres :", random_search.best_params_)
    print(f"Meilleur F1 (CV) : {random_search.best_score_:.4f}")

    metrics = evaluate_classification(best_model, X_test, y_test)
    print("Métriques sur le jeu de test :")
    for k, v in metrics.items():
        print(f"  {k}: {v:.4f}" if v is not None else f"  {k}: N/A")

    save_model_and_metrics(best_model, metrics, "xgboost_optimized", preprocessor=preprocessor, axis="clf")


# ==================================================================
# Optimisation Régression XGBoost (R²)
# ==================================================================

def optimize_xgboost_reg():
    print("\n--- Optimisation Régression : XGBoost ---")

    X, y = load_regression_data()
    X_train, X_test, y_train, y_test, preprocessor = prepare_regression_data(X, y)

    param_dist = {
        'n_estimators': [50, 100, 200, 300],
        'max_depth': [2, 3, 4, 5],
        'learning_rate': [0.01, 0.05, 0.1, 0.2],
        'subsample': [0.7, 0.8, 1.0],
    }

    xgb_model = xgb.XGBRegressor(random_state=42, eval_metric='rmse')

    random_search = RandomizedSearchCV(
        estimator=xgb_model,
        param_distributions=param_dist,
        n_iter=30,
        scoring='r2',
        cv=5,
        verbose=1,
        random_state=42,
        n_jobs=-1
    )
    random_search.fit(X_train, y_train)

    best_model = random_search.best_estimator_
    print("Meilleurs paramètres :", random_search.best_params_)
    print(f"Meilleur R² (CV) : {random_search.best_score_:.4f}")

    metrics = evaluate_regression(best_model, X_test, y_test)
    print("Métriques sur le jeu de test :")
    for k, v in metrics.items():
        print(f"  {k}: {v:.4f}")

    save_model_and_metrics(best_model, metrics, "xgboost_optimized", preprocessor=preprocessor, axis="reg")


# ==================================================================
# Optimisation Régression Ridge (R²)
# ==================================================================

def optimize_ridge_reg():
    print("\n--- Optimisation Régression : Ridge ---")

    X, y = load_regression_data()
    X_train, X_test, y_train, y_test, preprocessor = prepare_regression_data(X, y)

    param_grid = {
        'alpha': [0.01, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 50.0, 100.0]
    }

    # CORRECTIF #10 : Ridge() sans random_state (paramètre inexistant sur Ridge)
    ridge = Ridge()
    grid_search = GridSearchCV(
        ridge,
        param_grid,
        scoring='r2',
        cv=5,
        n_jobs=-1
    )
    grid_search.fit(X_train, y_train)

    best_model = grid_search.best_estimator_
    print("Meilleur alpha :", grid_search.best_params_['alpha'])
    print(f"Meilleur R² (CV) : {grid_search.best_score_:.4f}")

    metrics = evaluate_regression(best_model, X_test, y_test)
    print("Métriques sur le jeu de test :")
    for k, v in metrics.items():
        print(f"  {k}: {v:.4f}")

    save_model_and_metrics(best_model, metrics, "ridge_optimized", preprocessor=preprocessor, axis="reg")


# ==================================================================
# Comparaison Avant / Après
# ==================================================================

def _read_metric(model_name: str, metric: str) -> str:
    """
    CORRECTIF #9 : lecture des métriques via MODELS_DIR (chemin absolu résolu
    depuis config.py), au lieu de chemins relatifs au répertoire courant.
    Le bare except a été remplacé par un except explicite pour ne pas masquer
    des erreurs inattendues.
    """
    metrics_path = MODELS_DIR / f"{model_name}_metrics.json"
    try:
        with open(metrics_path, "r") as f:
            data = json.load(f)
        value = data.get(metric, "N/A")
        return f"{value:.4f}" if isinstance(value, (int, float)) else str(value)
    except (FileNotFoundError, json.JSONDecodeError):
        return "N/A"


def compare_results():
    print("\n--- Comparaison Avant/Après ---")

    pairs = [
        ("Classification XGBoost", "xgboost_clf",           "xgboost_optimized_clf",  "f1"),
        ("Régression XGBoost",     "xgboost_reg",           "xgboost_optimized_reg",  "r2"),
        ("Régression Ridge",       "ridge_reg",             "ridge_optimized_reg",    "r2"),
    ]

    print()
    for label, before_name, after_name, metric in pairs:
        before = _read_metric(before_name, metric)
        after  = _read_metric(after_name,  metric)
        print(f"{label} — Avant : {metric.upper()} = {before}  |  Après : {metric.upper()} = {after}")
        if before != "N/A" and after != "N/A":
            diff = float(after) - float(before)
            print(f"  → Amélioration : {diff:+.4f}")
        else:
            print("  → Données manquantes (modèle non encore entraîné)")


if __name__ == "__main__":
    optimize_xgboost_clf()
    optimize_xgboost_reg()
    optimize_ridge_reg()
    compare_results()