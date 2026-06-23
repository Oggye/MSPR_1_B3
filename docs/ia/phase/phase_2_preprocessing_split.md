# Phase 2 — Préparation des Données : Preprocessing et Split

---

## 1. Contexte

### Objectif de l'étape

Mettre en place le **pipeline de prétraitement** des features et la **stratégie de séparation** train/test, afin de préparer les données à l'entraînement des modèles candidats.

### Position dans le projet

Cette étape intervient entre la construction des datasets (Phase 1) et l'entraînement des modèles (Phase 4). Elle est implémentée dans le module `train_utils.py`, partagé par tous les scripts d'entraînement.

### Lien avec le cahier des charges

Le cahier des charges impose de :
- **construire les ensembles train / validation / test** ;
- réaliser l'**encodage, normalisation/standardisation** des variables ;
- respecter les **bonnes pratiques de séparation et d'évaluation des données**.

---

## 2. Travaux réalisés

### Module principal

**`ia/src/ml/models/train_utils.py`** — utilitaires partagés pour les deux axes ML.

Ce module expose :
- `load_regression_data()` / `load_classification_data()` : chargement et validation des features
- `prepare_regression_data()` / `prepare_classification_data()` : preprocessing + split
- `build_preprocessor()` : construction du pipeline `ColumnTransformer`

---

## 3. Fonctionnement

### 3.1 Définition des features

**Features numériques (identiques pour les deux axes)**

```python
NUMERIC_FEATURES = [
    "year",
    "co2_emissions",
    "co2_per_passenger",
    "co2_lag1",
    "passengers_lag1",
    "passengers_lag2",
]
```

**Feature catégorielle**

```python
CATEGORICAL_FEATURES = ["country_name"]
```

**Cibles**
- Régression : `passengers`
- Classification : `en_declin`

### 3.2 Pipeline de prétraitement

```python
ColumnTransformer(
    transformers=[
        ("num", StandardScaler(), numeric_features),
        ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), categorical_features),
    ],
    remainder="drop"
)
```

| Transformation | Appliquée à | Justification |
|---------------|-------------|---------------|
| `StandardScaler` | Features numériques | Centre et réduit les variables (moyenne=0, écart-type=1). Indispensable pour les modèles sensibles à l'échelle (Ridge, Logistic, MLP). |
| `OneHotEncoder` | `country_name` | Transforme les 41 pays en variables binaires. `handle_unknown="ignore"` protège l'inférence contre des pays inconnus. |

Après transformation, chaque observation possède **47 features** : 6 numériques standardisées + 41 colonnes OHE (une par pays).

### 3.3 Stratégie de split

**Régression**
```python
train_test_split(X, y, test_size=0.20, random_state=42)
```

**Classification**
```python
train_test_split(X, y, test_size=0.20, stratify=y, random_state=42)
```

| Paramètre | Valeur | Justification |
|-----------|--------|---------------|
| `test_size` | 0.20 | 80 % train / 20 % test — standard pour un dataset de 546 lignes |
| `random_state` | 42 | Reproductibilité garantie |
| `stratify=y` | Classification uniquement | Préserve la proportion 61,9/38,1 % dans le train et le test |

### 3.4 Résultat du split

Confirmé par les logs d'exécution :

```
X_train: (436, 47) | X_test: (110, 47)
```

| Ensemble | Lignes | Features |
|----------|--------|----------|
| Train | 436 | 47 |
| Test | 110 | 47 |

### 3.5 Application du prétraitement

Le prétraitement est **ajusté sur le train uniquement** (`fit_transform`), puis **appliqué au test** (`transform`) :

```python
X_train_p = preprocessor.fit_transform(X_train)
X_test_p  = preprocessor.transform(X_test)
```

Cette pratique évite toute **fuite d'information** du test vers le train (data leakage de preprocessing).

---

## 4. Résultats obtenus

| Indicateur | Valeur |
|-----------|--------|
| Observations totales | 546 |
| Features après OHE | 47 (6 numériques + 41 OHE pays) |
| Lignes entraînement | 436 (79,9 %) |
| Lignes test | 110 (20,1 %) |
| Preprocesseur régression sauvegardé | `data/ml/preprocessor_regression.joblib` |
| Preprocesseur classification sauvegardé | `data/ml/preprocessor_classification.joblib` |

---

## 5. Difficultés rencontrées

### Limite identifiée : stratégie de split temporel

Le split aléatoire (`train_test_split`) ne respecte pas la structure temporelle des données. Un même pays peut apparaître à la fois dans le train (années 2015–2022) et dans le test (années 2012–2014), ce qui introduit une **légère fuite temporelle** : le modèle peut apprendre des patterns d'un pays qui seront utilisés pour prédire ses propres années passées.

La stratégie idéale serait un **`GroupShuffleSplit(groups=country_id)`**, qui garantit que chaque pays n'apparaît que dans un seul ensemble. Toutefois, avec 41 pays et 546 lignes (environ 13 observations par pays), ce split réduirait drastiquement la taille des données d'entraînement et complexifierait l'équilibre des classes.

> **Choix retenu** : `train_test_split` aléatoire stratifié, justifié par la simplicité et la taille du dataset. Ce choix est documenté et mentionné comme limite dans le rapport final.

---

## 6. Correctifs appliqués

- Usage de `stratify=y` en classification pour compenser le déséquilibre de classes
- `fit` du preprocesseur uniquement sur le train, `transform` sur le test (protection anti-leakage)
- `handle_unknown="ignore"` sur le OHE pour la robustesse en production

---

## 7. Impact sur la suite du projet

- Le pipeline de preprocessing est **réutilisé à l'identique** par tous les scripts d'entraînement (logistique, Random Forest, XGBoost, MLP, Ridge)
- Les preprocesseurs `.joblib` sauvegardés sont indispensables pour le script `predict.py` et l'API FastAPI (Phase 10–11)
- Le split 80/20 avec `random_state=42` garantit la **reproductibilité** de tous les résultats

---

## 8. Livrables produits

| Livrable | Chemin | Description |
|----------|--------|-------------|
| Module utilitaires | `ia/src/ml/models/train_utils.py` | Preprocessing, split, évaluation |
| Preprocesseur régression | `data/ml/preprocessor_regression.joblib` | Pipeline StandardScaler + OHE |
| Preprocesseur classification | `data/ml/preprocessor_classification.joblib` | Pipeline StandardScaler + OHE |
