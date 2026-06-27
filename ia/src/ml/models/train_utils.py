# ia/src/ml/models/train_utils.py
#
# Utilitaires partagés pour les deux axes ML :
#   - Régression  : prévision de passengers
#   - Classification : détection des pays en déclin

import pandas as pd
import numpy as np
import joblib
import json

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, roc_auc_score,
    mean_absolute_error, mean_squared_error, r2_score
)

# CORRECTIF #1 : import relatif au lieu de l'import absolu "from ia.src.ml.config"
# L'import absolu cassait le module quand PYTHONPATH n'incluait pas la racine du projet
# (cas systématique dans Docker sans configuration explicite).
from ..config import (
    REGRESSION_DATASET_PATH, CLASSIF_DATASET_PATH,
    PREPROCESSOR_REG_PATH, PREPROCESSOR_CLF_PATH,
    MODELS_DIR
)

# ------------------------------------------------------------------
# Features — Régression
# ------------------------------------------------------------------
REG_NUMERIC_FEATURES = [
    "year",
    "co2_emissions",
    "co2_per_passenger",
    "co2_lag1",
    "passengers_lag1",
    "passengers_lag2",
]
REG_CATEGORICAL_FEATURES = ["country_name"]
REG_TARGET = "passengers"

# ------------------------------------------------------------------
# Features — Classification
# ------------------------------------------------------------------
CLF_NUMERIC_FEATURES = [
    "year",
    "co2_emissions",
    "co2_per_passenger",
    "co2_lag1",
    "passengers_lag1",
    "passengers_lag2",
]
CLF_CATEGORICAL_FEATURES = ["country_name"]
CLF_TARGET = "en_declin"


def build_preprocessor(numeric_features, categorical_features):
    """Pipeline de prétraitement générique."""
    return ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), numeric_features),
            ("cat",
             OneHotEncoder(handle_unknown="ignore", sparse_output=False),
             categorical_features),
        ],
        remainder="drop"
    )


# ==================================================================
# RÉGRESSION
# ==================================================================

def load_regression_data():
    df = pd.read_csv(REGRESSION_DATASET_PATH)

    missing = [c for c in REG_NUMERIC_FEATURES + REG_CATEGORICAL_FEATURES if c not in df.columns]
    if missing:
        raise ValueError(f"Colonnes manquantes dans le dataset régression : {missing}")

    X = df[REG_NUMERIC_FEATURES + REG_CATEGORICAL_FEATURES].copy()
    y = df[REG_TARGET].copy()

    print(f"   [Régression] Dataset : {X.shape[0]} obs, {X.shape[1]} features")
    print(f"   Cible 'passengers' — min: {y.min():.0f} | max: {y.max():.0f} | médiane: {y.median():.0f}")
    return X, y


def prepare_regression_data(X, y, test_size=0.20, random_state=42):
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )
    preprocessor = build_preprocessor(REG_NUMERIC_FEATURES, REG_CATEGORICAL_FEATURES)
    X_train_p = preprocessor.fit_transform(X_train)
    X_test_p  = preprocessor.transform(X_test)
    print(f"   X_train: {X_train_p.shape} | X_test: {X_test_p.shape}")
    return X_train_p, X_test_p, y_train, y_test, preprocessor


def evaluate_regression(model, X_test, y_test):
    y_pred = model.predict(X_test)
    mae  = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2   = r2_score(y_test, y_pred)
    return {
        "mae":  float(mae),
        "rmse": float(rmse),
        "r2":   float(r2),
    }


# ==================================================================
# CLASSIFICATION
# ==================================================================

def load_classification_data():
    df = pd.read_csv(CLASSIF_DATASET_PATH)

    missing = [c for c in CLF_NUMERIC_FEATURES + CLF_CATEGORICAL_FEATURES if c not in df.columns]
    if missing:
        raise ValueError(f"Colonnes manquantes dans le dataset classification : {missing}")

    if CLF_TARGET not in df.columns:
        raise ValueError(f"Cible '{CLF_TARGET}' absente. Relancez build_dataset.py.")

    X = df[CLF_NUMERIC_FEATURES + CLF_CATEGORICAL_FEATURES].copy()
    y = df[CLF_TARGET].copy()

    print(f"   [Classification] Dataset : {X.shape[0]} obs, {X.shape[1]} features")
    print(f"   Cible 'en_declin' : {y.value_counts().to_dict()}")
    return X, y


def prepare_classification_data(X, y, test_size=0.20, random_state=42):
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=test_size,
        stratify=y,
        random_state=random_state
    )
    preprocessor = build_preprocessor(CLF_NUMERIC_FEATURES, CLF_CATEGORICAL_FEATURES)
    X_train_p = preprocessor.fit_transform(X_train)
    X_test_p  = preprocessor.transform(X_test)
    print(f"   X_train: {X_train_p.shape} | X_test: {X_test_p.shape}")
    return X_train_p, X_test_p, y_train, y_test, preprocessor


def evaluate_classification(model, X_test, y_test):
    y_pred = model.predict(X_test)
    metrics = {
        "accuracy":  float(accuracy_score(y_test, y_pred)),
        "precision": float(precision_score(y_test, y_pred, zero_division=0)),
        "recall":    float(recall_score(y_test, y_pred, zero_division=0)),
        "f1":        float(f1_score(y_test, y_pred, zero_division=0)),
    }
    if hasattr(model, "predict_proba"):
        y_proba = model.predict_proba(X_test)[:, 1]
        metrics["roc_auc"] = float(roc_auc_score(y_test, y_proba))
    else:
        metrics["roc_auc"] = None
    return metrics


# ==================================================================
# SAUVEGARDE / CHARGEMENT
# ==================================================================

def save_model_and_metrics(model, metrics, model_name, preprocessor=None, axis="clf"):
    model_path   = MODELS_DIR / f"{model_name}_{axis}.joblib"
    metrics_path = MODELS_DIR / f"{model_name}_{axis}_metrics.json"

    joblib.dump(model, model_path)
    print(f"✅ Modèle sauvegardé : {model_path}")

    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"✅ Métriques sauvegardées : {metrics_path}")

    # CORRECTIF #11 : on ne sauvegarde le preprocesseur que si explicitement fourni,
    # sans écraser le fichier partagé à chaque appel. Le preprocesseur est identique
    # pour tous les modèles d'un même axe donc un seul enregistrement suffit.
    # On écrit uniquement si le fichier n'existe pas encore, pour ne pas écraser
    # une version antérieure valide.
    if preprocessor is not None:
        prep_path = PREPROCESSOR_CLF_PATH if axis == "clf" else PREPROCESSOR_REG_PATH
        if not prep_path.exists():
            joblib.dump(preprocessor, prep_path)
            print(f"✅ Preprocesseur sauvegardé : {prep_path}")
        else:
            print(f"ℹ️  Preprocesseur déjà présent, non écrasé : {prep_path}")


def load_model_and_metrics(model_name, axis="clf"):
    model_path   = MODELS_DIR / f"{model_name}_{axis}.joblib"
    metrics_path = MODELS_DIR / f"{model_name}_{axis}_metrics.json"

    if not model_path.exists() or not metrics_path.exists():
        raise FileNotFoundError(f"Modèle/métriques introuvables : {model_name}_{axis}")

    model = joblib.load(model_path)
    with open(metrics_path, "r") as f:
        metrics = json.load(f)
    return model, metrics