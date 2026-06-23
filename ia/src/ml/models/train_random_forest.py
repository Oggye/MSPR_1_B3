# ia/src/ml/models/train_random_forest.py
# Axe Classification — Random Forest
# Axe Régression    — Random Forest Regressor

from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from .train_utils import (
    load_classification_data, prepare_classification_data, evaluate_classification,
    load_regression_data, prepare_regression_data, evaluate_regression,
    save_model_and_metrics
)


def train_random_forest():
    print("\n--- Classification : Random Forest ---")

    X, y = load_classification_data()
    X_train, X_test, y_train, y_test, preprocessor = prepare_classification_data(X, y)

    model = RandomForestClassifier(
        n_estimators=100,
        random_state=42,
        n_jobs=-1,
        class_weight="balanced"
    )
    model.fit(X_train, y_train)

    metrics = evaluate_classification(model, X_test, y_test)
    print("Métriques classification :")
    for k, v in metrics.items():
        print(f"  {k}: {v:.4f}" if v is not None else f"  {k}: N/A")

    save_model_and_metrics(model, metrics, "random_forest", axis="clf")


def train_random_forest_regressor():
    print("\n--- Régression : Random Forest Regressor ---")

    X, y = load_regression_data()
    X_train, X_test, y_train, y_test, preprocessor = prepare_regression_data(X, y)

    model = RandomForestRegressor(
        n_estimators=100,
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train, y_train)

    metrics = evaluate_regression(model, X_test, y_test)
    print("Métriques régression :")
    for k, v in metrics.items():
        print(f"  {k}: {v:.4f}")

    save_model_and_metrics(model, metrics, "random_forest", preprocessor=preprocessor, axis="reg")


if __name__ == "__main__":
    train_random_forest()
    train_random_forest_regressor()