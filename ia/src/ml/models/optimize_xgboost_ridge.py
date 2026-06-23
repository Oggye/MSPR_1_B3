# Importer les bibliothèques
import pandas as pd
import json
from sklearn.model_selection import RandomizedSearchCV, GridSearchCV
from sklearn.linear_model import Ridge
import xgboost as xgb
from .train_utils import (
    load_classification_data, prepare_classification_data,
    load_regression_data, prepare_regression_data,
    save_model_and_metrics, evaluate_classification, evaluate_regression 
)

# Optimisation de la Classification (F1)
def optimize_xgboost_clf():
    print("\n--- Optimisation Classification : XGBoost ---")

    X, y = load_classification_data()
    X_train, X_test, y_train, y_test, preprocessor = prepare_classification_data(X, y)

    # Définir la grille de paramètres (comme dans le guide)
    param_dist = {
        'n_estimators': [50, 100, 200, 300],
        'max_depth': [2, 3, 4, 5],
        'learning_rate': [0.01, 0.05, 0.1, 0.2],
        'subsample': [0.7, 0.8, 1.0],
        'scale_pos_weight': [1, 1.5, 2]  # Important pour le déséquilibre
    }

    # Initialiser le modèle de base
    xgb_model = xgb.XGBClassifier(random_state=42, eval_metric='logloss')

    # Lancer la RandomizedSearchCV
    random_search = RandomizedSearchCV(
        estimator=xgb_model,
        param_distributions=param_dist,
        n_iter=30, # on teste 30 combinaisons aléatoires
        scoring='f1', # on optimise le F1
        cv=5,  # validation croisée à 5 folds
        verbose=1,
        random_state=42,
        n_jobs=-1
    )
    random_search.fit(X_train, y_train)

    # Récupérer le meilleur modèle et ses paramètres
    best_model = random_search.best_estimator_
    print("Meilleurs paramètres trouvés :", random_search.best_params_)
    print(f"Meilleur F1 (CV) : {random_search.best_score_:.4f}")

    # Évaluer sur le jeu de test
    metrics = evaluate_classification(best_model, X_test, y_test)
    print("Métriques sur le jeu de test :")
    for k, v in metrics.items():
        print(f"  {k}: {v:.4f}" if v is not None else f"  {k}: N/A")

    # Sauvegarder le modèle optimisé
    save_model_and_metrics(best_model, metrics, "xgboost_optimized", preprocessor=preprocessor, axis="clf")

# Optimisation de la Régression (R²) - XGBoost   
def optimize_xgboost_reg():
    print("\n--- Optimisation Régression : XGBoost ---")

    X, y = load_regression_data()
    X_train, X_test, y_train, y_test, preprocessor = prepare_regression_data(X, y)

    # Grille de paramètres pour la régression
    param_dist = {
        'n_estimators': [50, 100, 200, 300],
        'max_depth': [2, 3, 4, 5],
        'learning_rate': [0.01, 0.05, 0.1, 0.2],
        'subsample': [0.7, 0.8, 1.0],
    }

    xgb_model = xgb.XGBRegressor(random_state=42, eval_metric='rmse')

    # Ici, on optimise le R²
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
    print("Meilleurs paramètres trouvés :", random_search.best_params_)
    print(f"Meilleur R² (CV) : {random_search.best_score_:.4f}")

    metrics = evaluate_regression(best_model, X_test, y_test)
    print("Métriques sur le jeu de test :")
    for k, v in metrics.items():
        print(f"  {k}: {v:.4f}")

    save_model_and_metrics(best_model, metrics, "xgboost_optimized", preprocessor=preprocessor, axis="reg")

# Optimisation de la Régression (R²) - Ridge 
def optimize_ridge_reg():
    print("\n--- Optimisation Régression : Ridge ---")

    X, y = load_regression_data()
    X_train, X_test, y_train, y_test, preprocessor = prepare_regression_data(X, y)
    
    # Définir la grille de paramètres
    param_grid = {
        'alpha': [0.01, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 50.0, 100.0]
    }

    # GridSearchCV (cross-validation)
    ridge = Ridge(random_state=42)
    grid_search = GridSearchCV(
        ridge,
        param_grid,
        scoring='r2',  # On optimise sur le R²
        cv=5,
        n_jobs=-1
    )
    grid_search.fit(X_train, y_train)

    # Récupérer le meilleur modèle
    best_model = grid_search.best_estimator_
 
    print("Meilleur alpha :", grid_search.best_params_['alpha'])
    print(f"Meilleur R² (CV) : {grid_search.best_score_:.4f}")

    # Évaluation sur le jeu de test
    metrics = evaluate_regression(best_model, X_test, y_test)
    print("Métriques sur le jeu de test :")
    for k, v in metrics.items():
        print(f"  {k}: {v:.4f}")

    save_model_and_metrics(best_model, metrics, "ridge_optimized", preprocessor=preprocessor, axis="reg")

# Comparaison Avant/Après
def compare_results():
    print("\n--- Comparaison Avant/Après ---")
    
    def get_metric(model_name, metric):
        try:
            with open(f"ia/models/{model_name}_metrics.json", 'r') as f:
                data = json.load(f)
                value = data.get(metric, 'N/A')
                if isinstance(value, (int, float)):
                    return f"{value:.4f}"
                return str(value)
        except:
            return 'N/A'
    
    # Récupération des métriques
    f1_before = get_metric("xgboost_clf", "f1")
    f1_after = get_metric("xgboost_optimized_clf", "f1")
    r2_xgb_before = get_metric("xgboost_reg", "r2")
    r2_xgb_after = get_metric("xgboost_optimized_reg", "r2")
    r2_ridge_before = get_metric("ridge_reg", "r2")
    r2_ridge_after = get_metric("ridge_optimized_reg", "r2")
    
    # Affichage
    print(f"\nClassification XGBoost — Avant : F1 = {f1_before}  |  Après : F1 = {f1_after}")
    print(f"Régression XGBoost     — Avant : R² = {r2_xgb_before}  |  Après : R² = {r2_xgb_after}")
    print(f"Régression Ridge       — Avant : R² = {r2_ridge_before}  |  Après : R² = {r2_ridge_after}")
    
    # Améliorations
    print("\nAméliorations :")
    
    if f1_before != 'N/A' and f1_after != 'N/A':
        diff = float(f1_after) - float(f1_before)
        print(f"  XGBoost Clf F1 : {diff:+.4f}")
    else:
        print(f"  XGBoost Clf F1 : Données manquantes")

    if r2_xgb_before != 'N/A' and r2_xgb_after != 'N/A':
        diff = float(r2_xgb_after) - float(r2_xgb_before)
        print(f"  XGBoost Reg R² : {diff:+.4f}")
    else:
        print(f"  XGBoost Reg R² : Données manquantes")

    if r2_ridge_before != 'N/A' and r2_ridge_after != 'N/A':
        diff = float(r2_ridge_after) - float(r2_ridge_before)
        print(f"  Ridge Reg R²   : {diff:+.4f}")
    else:
        print(f"  Ridge Reg R²   : Données manquantes")


if __name__ == "__main__":
    optimize_xgboost_clf()
    optimize_xgboost_reg()
    optimize_ridge_reg()
    compare_results()