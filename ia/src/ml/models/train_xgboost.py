# ia/src/ml/models/train_xgboost.py
# Axe Classification — XGBoost Classifier
# Axe Régression    — XGBoost Regressor

import xgboost as xgb
from .train_utils import (
    load_classification_data, prepare_classification_data, evaluate_classification,
    load_regression_data, prepare_regression_data, evaluate_regression,
    save_model_and_metrics
)


def train_xgboost():
    print("\n--- Classification : XGBoost ---")

    X, y = load_classification_data()
    X_train, X_test, y_train, y_test, preprocessor = prepare_classification_data(X, y)

    n_neg = (y == 0).sum()
    n_pos = (y == 1).sum()
    scale = float(n_neg / n_pos) if n_pos > 0 else 1.0

    model = xgb.XGBClassifier(
        n_estimators=100,
        learning_rate=0.1,
        max_depth=4,
        random_state=42,
        eval_metric="logloss",
        scale_pos_weight=scale
    )
    model.fit(X_train, y_train)

    metrics = evaluate_classification(model, X_test, y_test)
    print("Métriques classification :")
    for k, v in metrics.items():
        print(f"  {k}: {v:.4f}" if v is not None else f"  {k}: N/A")

    save_model_and_metrics(model, metrics, "xgboost", preprocessor=preprocessor, axis="clf")


def train_xgboost_regressor():
    print("\n--- Régression : XGBoost Regressor ---")

    X, y = load_regression_data()
    X_train, X_test, y_train, y_test, preprocessor = prepare_regression_data(X, y)

    model = xgb.XGBRegressor(
        n_estimators=100,
        learning_rate=0.1,
        max_depth=4,
        random_state=42,
        eval_metric="rmse"
    )
    model.fit(X_train, y_train)

    metrics = evaluate_regression(model, X_test, y_test)
    print("Métriques régression :")
    for k, v in metrics.items():
        print(f"  {k}: {v:.4f}")

    save_model_and_metrics(model, metrics, "xgboost", preprocessor=preprocessor, axis="reg")


if __name__ == "__main__":
    train_xgboost()
    train_xgboost_regressor()