# ia/src/ml/models/train_logistic.py
# Axe Classification — Régression Logistique

from sklearn.linear_model import LogisticRegression
from .train_utils import (
    load_classification_data, prepare_classification_data,
    evaluate_classification, save_model_and_metrics
)


def train_logistic():
    print("\n--- Classification : Logistic Regression ---")

    X, y = load_classification_data()
    X_train, X_test, y_train, y_test, preprocessor = prepare_classification_data(X, y)

    model = LogisticRegression(
        max_iter=1000,
        random_state=42,
        class_weight="balanced"
    )
    model.fit(X_train, y_train)

    metrics = evaluate_classification(model, X_test, y_test)
    print("Métriques :")
    for k, v in metrics.items():
        print(f"  {k}: {v:.4f}" if v is not None else f"  {k}: N/A")

    save_model_and_metrics(model, metrics, "logistic", axis="clf")


if __name__ == "__main__":
    train_logistic()