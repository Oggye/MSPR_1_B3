# Phase 10 — Sauvegarde & Script Predict

---

## 1. Contexte

### Objectif de l'étape

Produire un script de prédiction autonome et reproductible (`predict.py`) permettant d'utiliser les modèles finaux sélectionnés sans passer par l'API, directement en ligne de commande.

### Position dans le projet

Cette phase intervient après la sélection et l'optimisation des modèles finaux (Phases 6 et 7). Elle constitue le pont entre les modèles entraînés et leur exposition via l'API (Phase 11).

### Lien avec le cahier des charges

Le cahier des charges ObRail impose de :
- **Sauvegarder le modèle final** (pickle/joblib) ;
- **Créer un script `predict.py`** simulant la future intégration API ;
- **Documenter la procédure** de prédiction et de ré-entraînement.

---

## 2. Travaux réalisés

### Script principal

**`ia/src/ml/predict.py`** — script de prédiction minimal reproductible.

### Artefacts utilisés

| Fichier | Rôle |
|---------|------|
| `ia/models/xgboost_optimized_clf.joblib` | Modèle de classification optimisé |
| `ia/models/ridge_optimized_reg.joblib` | Modèle de régression optimisé |
| `data/ml/preprocessor_classification.joblib` | Preprocesseur classification (StandardScaler + OHE) |
| `data/ml/preprocessor_regression.joblib` | Preprocesseur régression (StandardScaler + OHE) |

---

## 3. Fonctionnement

### 3.1 Chargement des artefacts

```python
def load_artifacts(axis: str):
    if axis == "classification":
        model_path, prep_path = CLF_MODEL_PATH, CLF_PREP_PATH
    else:
        model_path, prep_path = REG_MODEL_PATH, REG_PREP_PATH
    return joblib.load(model_path), joblib.load(prep_path)
```

La fonction vérifie l'existence des fichiers avant de les charger et lève une `FileNotFoundError` explicite si un fichier est manquant.

### 3.2 Construction du DataFrame d'entrée

```python
input_df = pd.DataFrame([{
    "year": year,
    "co2_emissions": co2_emissions,
    "co2_per_passenger": co2_per_passenger,
    "co2_lag1": co2_lag1,
    "passengers_lag1": passengers_lag1,
    "passengers_lag2": passengers_lag2,
    "country_name": country,
}])
```

Le DataFrame est construit à partir des paramètres fournis en ligne de commande, dans le même format que les données d'entraînement.

### 3.3 Prédiction

Le preprocesseur est appliqué en mode `transform` uniquement (pas de `fit`), puis le modèle produit une prédiction.

**Axe classification :**
- Prédiction : `0` (En croissance) ou `1` (En déclin)
- Probabilité de déclin via `predict_proba`

**Axe régression :**
- Prédiction : volume de passagers estimé (en milliers)

### 3.4 Interface CLI

Le script expose une interface en ligne de commande via `argparse` :

```bash
python -m ia.src.ml.predict \
  --axis classification \
  --country France \
  --year 2024 \
  --co2_emissions 24800 \
  --co2_per_passenger 1.75 \
  --co2_lag1 25100 \
  --passengers_lag1 88000 \
  --passengers_lag2 86500
```

L'option `--json` permet d'obtenir la sortie au format JSON brut, facilitant l'intégration future.

---

## 4. Résultats obtenus

### Axe classification — France 2024

```
[CLASSIFICATION] France — 2024
  Prédiction    : 0
  Interprétation: En croissance
  Probabilité   : 2.9%
```

### Axe régression — France 2024

```
[REGRESSION] France — 2024
  Prédiction    : 114583.42
  Interprétation: 114,583 milliers de passagers prévus
```

Les deux axes produisent des résultats cohérents avec les données historiques de la France, l'un des pays ferroviaires les plus actifs d'Europe.

---

## 5. Difficultés rencontrées

- **Conflits d'imports** : les scripts du projet utilisaient des imports relatifs (`from config import`) incompatibles avec le lancement en module (`python -m`). Correction appliquée : passage à `from .config import`.
- **Conflit de versions Python** : `uvicorn` installé globalement utilisait un Python différent de celui du projet. Résolution : utilisation systématique de `python -m uvicorn` pour garantir le bon environnement.

---

## 6. Correctifs appliqués

- Correction des imports relatifs dans `build_dataset.py` et `run_pipeline.py`.
- Ajout de vérifications d'existence des fichiers `.joblib` avant chargement.
- Gestion explicite des erreurs avec messages lisibles.

---

## 7. Impact sur la suite du projet

- Le script `predict.py` est directement réutilisé par l'API FastAPI (Phase 11) via `from ia.src.ml.predict import predict`.
- La fonction `predict()` est conçue comme une fonction pure, sans dépendances externes, facilement testable et intégrable.
- Les modèles `.joblib` sauvegardés sont les artefacts de production utilisés en Phase 11 et pour le cloud.

---

## 8. Livrables produits

| Livrable | Chemin | Statut |
|----------|--------|--------|
| Script de prédiction | `ia/src/ml/predict.py` | ✅ Produit |
| Modèle classification | `ia/models/xgboost_optimized_clf.joblib` | ✅ Sauvegardé |
| Modèle régression | `ia/models/ridge_optimized_reg.joblib` | ✅ Sauvegardé |
| Preprocesseur classification | `data/ml/preprocessor_classification.joblib` | ✅ Sauvegardé |
| Preprocesseur régression | `data/ml/preprocessor_regression.joblib` | ✅ Sauvegardé |

### Commandes de lancement

```bash
# Classification
python -m ia.src.ml.predict --axis classification --country France --year 2024 \
  --co2_emissions 24800 --co2_per_passenger 1.75 --co2_lag1 25100 \
  --passengers_lag1 88000 --passengers_lag2 86500

# Régression
python -m ia.src.ml.predict --axis regression --country France --year 2024 \
  --co2_emissions 24800 --co2_per_passenger 1.75 --co2_lag1 25100 \
  --passengers_lag1 88000 --passengers_lag2 86500
```