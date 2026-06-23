# ia/src/ml/models/train_ridge.py
# Axe Régression — Ridge (modèle linéaire de référence)

from sklearn.linear_model import Ridge
from .train_utils import (
    load_regression_data, prepare_regression_data,
    evaluate_regression, save_model_and_metrics
)


def train_ridge():
    print("\n--- Régression : Ridge ---")

    X, y = load_regression_data()
    X_train, X_test, y_train, y_test, preprocessor = prepare_regression_data(X, y)

    model = Ridge(alpha=1.0)
    model.fit(X_train, y_train)

    metrics = evaluate_regression(model, X_test, y_test)
    print("Métriques :")
    for k, v in metrics.items():
        print(f"  {k}: {v:.4f}")

    save_model_and_metrics(model, metrics, "ridge", preprocessor=preprocessor, axis="reg")


if __name__ == "__main__":
    train_ridge()