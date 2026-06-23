# ia/src/ml/models/train_mlp.py
# Axe Classification — MLP Classifier

from sklearn.neural_network import MLPClassifier
from .train_utils import (
    load_classification_data, prepare_classification_data,
    evaluate_classification, save_model_and_metrics
)


def train_mlp():
    print("\n--- Classification : MLP (Neural Network) ---")

    X, y = load_classification_data()
    X_train, X_test, y_train, y_test, preprocessor = prepare_classification_data(X, y)

    model = MLPClassifier(
        hidden_layer_sizes=(64, 32),
        activation="relu",
        solver="adam",
        max_iter=500,
        random_state=42,
        early_stopping=True,
        validation_fraction=0.15
    )
    model.fit(X_train, y_train)

    metrics = evaluate_classification(model, X_test, y_test)
    print("Métriques :")
    for k, v in metrics.items():
        print(f"  {k}: {v:.4f}" if v is not None else f"  {k}: N/A")

    save_model_and_metrics(model, metrics, "mlp", axis="clf")


if __name__ == "__main__":
    train_mlp()