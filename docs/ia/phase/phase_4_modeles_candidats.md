# Phase 4 — Modèles Candidats et Entraînement

---

## 1. Contexte

### Objectif de l'étape

Entraîner plusieurs modèles candidats sur les deux axes ML et comparer leurs performances, afin de sélectionner le modèle final le plus adapté à chaque tâche.

### Position dans le projet

Cette phase succède au preprocessing (Phase 2) et précède l'évaluation approfondie et l'optimisation (Phases 5–6). Elle constitue le cœur de la chaîne ML.

### Lien avec le cahier des charges

Le cahier des charges impose de :
- tester **plusieurs modèles algorithmiques** (régression, Random Forest, boosting, MLP) ;
- **justifier les choix retenus** ;
- produire un **tableau comparatif des modèles** ;
- évaluer chaque modèle avec les **métriques pertinentes** selon le type de tâche.

---

## 2. Travaux réalisés

### Script d'orchestration

**`ia/src/ml/run_training.py`** — lance l'entraînement complet des deux axes.

```bash
python -m ia.src.ml.run_training
```

### Scripts d'entraînement par modèle

| Script | Modèles entraînés |
|--------|------------------|
| `models/train_logistic.py` | Logistic Regression (clf) |
| `models/train_random_forest.py` | Random Forest (clf + reg) |
| `models/train_xgboost.py` | XGBoost (clf + reg) |
| `models/train_mlp.py` | MLP Classifier (clf) |
| `models/train_ridge.py` | Ridge Regression (reg) |

---

## 3. Fonctionnement

### 3.1 Architecture commune à tous les scripts

Chaque script suit le même pipeline :

```
1. load_*_data()          → chargement du dataset
2. prepare_*_data()       → preprocessing + split (train_utils)
3. model.fit(X_train, y_train)
4. evaluate_*(model, X_test, y_test)
5. save_model_and_metrics(model, metrics, nom, axis)
```

### 3.2 Modèles de classification (Axe 1)

**Logistic Regression** — baseline linéaire interprétable

```python
LogisticRegression(max_iter=1000, random_state=42, class_weight="balanced")
```
Justification : modèle de référence simple. `class_weight="balanced"` compense le déséquilibre 61,9/38,1 %. Interprétable via les coefficients.

---

**Random Forest Classifier** — méthode ensembliste robuste

```python
RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1, class_weight="balanced")
```
Justification : robuste aux outliers, gère bien l'hétérogénéité entre pays, peu sensible aux hyperparamètres. Fournit une importance des features native.

---

**XGBoost Classifier** — gradient boosting

```python
xgb.XGBClassifier(
    n_estimators=100, learning_rate=0.1, max_depth=4,
    random_state=42, eval_metric="logloss",
    scale_pos_weight=n_neg/n_pos   # ≈ 1.625
)
```
Justification : meilleure performance attendue sur données tabulaires. `scale_pos_weight` compense le déséquilibre des classes de façon équivalente à `class_weight`.

---

**MLP Classifier** — réseau de neurones

```python
MLPClassifier(
    hidden_layer_sizes=(64, 32), activation="relu", solver="adam",
    max_iter=500, random_state=42,
    early_stopping=True, validation_fraction=0.15
)
```
Justification : permet la comparaison deep learning vs boosting. `early_stopping` prévient le surapprentissage. Architecture à deux couches cachées (64, 32 neurones).

### 3.3 Modèles de régression (Axe 2)

**Ridge** — régression linéaire régularisée (baseline)

```python
Ridge(alpha=1.0)
```
Justification : modèle de référence linéaire. La régularisation L2 (alpha=1.0) prévient le surapprentissage sans trop contraindre les coefficients.

---

**Random Forest Regressor**

```python
RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
```
Justification : non-linéaire, robuste aux outliers de la distribution de `passengers`.

---

**XGBoost Regressor**

```python
xgb.XGBRegressor(
    n_estimators=100, learning_rate=0.1, max_depth=4,
    random_state=42, eval_metric="rmse"
)
```
Justification : gradient boosting adapté à la régression, attendu meilleur R² sur données tabulaires.

---

## 4. Résultats obtenus

### 4.1 Axe 1 — Classification (`en_declin`)

Résultats issus de l'exécution réelle de `run_training.py` :

| Modèle | Accuracy | Precision | Recall | F1 | ROC-AUC |
|--------|----------|-----------|--------|----|---------|
| Logistic Regression | 0.6455 | 0.5385 | 0.5000 | 0.5185 | 0.6929 |
| Random Forest | 0.6909 | 0.6250 | 0.4762 | 0.5405 | **0.8146** |
| **XGBoost** | **0.7091** | **0.6250** | **0.5952** | **0.6098** | 0.7959 |
| MLP | 0.5636 | 0.1250 | 0.0238 | 0.0400 | 0.3414 |

**Observations :**
- XGBoost obtient le meilleur F1 (0.6098) et la meilleure accuracy (0.7091)
- Random Forest présente le meilleur ROC-AUC (0.8146), indiquant une bonne capacité discriminante globale
- Le MLP sous-performe significativement : accuracy proche du hasard et F1 quasi nul, suggérant une convergence défaillante sur ce dataset de petite taille

### 4.2 Axe 2 — Régression (`passengers`)

| Modèle | MAE | RMSE | R² |
|--------|-----|------|-----|
| **Ridge** | **4 338.8** | **9 074.0** | **0.9962** |
| Random Forest | 4 965.7 | 26 039.2 | 0.9684 |
| XGBoost | 5 215.1 | 29 427.6 | 0.9596 |

**Observations :**
- Ridge obtient le meilleur R² (0.9962) et le meilleur MAE, ce qui est remarquable pour un modèle linéaire
- Le RMSE très élevé de Random Forest et XGBoost suggère des erreurs importantes sur les grands pays (forte variance de `passengers`)
- Le R² de 0.9962 du Ridge reflète la forte autocorrélation temporelle capturée par les variables lag

> **Attention — Point d'analyse** : un R² proche de 1.0 sur un dataset aussi structuré (series temporelles avec lags) est attendu mais mérite d'être discuté en soutenance. Il ne signifie pas nécessairement un leakage : les lags sont construits à partir de données historiques réelles distinctes de la cible de l'année N.

---

## 5. Difficultés rencontrées

- **MLP en échec** : le réseau de neurones ne converge pas correctement sur 436 observations. Les réseaux de neurones nécessitent généralement davantage de données pour rivaliser avec le boosting sur des datasets tabulaires de cette taille.
- **Hétérogénéité des pays** : la très forte disparité entre pays (de quelques dizaines à 1 080 000 milliers de passagers) rend la régression plus difficile pour les méthodes non-linéaires (RMSE élevé de RF et XGBoost).
- **R² très élevé en régression** : bien que légitime (lags + forte autocorrélation), ce résultat devra être contextualisé lors de la soutenance pour éviter toute suspicion de leakage.

---

## 6. Correctifs appliqués

- Utilisation de `class_weight="balanced"` et `scale_pos_weight` pour tous les modèles de classification, afin de compenser le déséquilibre 61,9/38,1 %
- `early_stopping=True` sur le MLP pour limiter le surapprentissage
- `random_state=42` sur tous les modèles pour la reproductibilité

---

## 7. Impact sur la suite du projet

- XGBoost est le **candidat principal en classification** pour l'optimisation (Phase 6)
- Ridge est le **candidat surprenant en régression** — à analyser plus finement en Phase 5
- Les métriques obtenues alimentent directement les tableaux de sélection du modèle final (Phase 7)
- Tous les modèles sont sauvegardés en `.joblib` pour intégration dans l'API (Phase 11)

---

## 8. Livrables produits

| Livrable | Chemin |
|----------|--------|
| Orchestrateur | `ia/src/ml/run_training.py` |
| Script Logistic | `ia/src/ml/models/train_logistic.py` |
| Script Random Forest | `ia/src/ml/models/train_random_forest.py` |
| Script XGBoost | `ia/src/ml/models/train_xgboost.py` |
| Script MLP | `ia/src/ml/models/train_mlp.py` |
| Script Ridge | `ia/src/ml/models/train_ridge.py` |
| Modèles sauvegardés | `ia/models/*.joblib` (7 fichiers) |
| Métriques JSON | `ia/models/*_metrics.json` (7 fichiers) |
| Rapport comparatif classification | `ia/reports/comparison_classification.csv` |
| Rapport comparatif régression | `ia/reports/comparison_regression.csv` |
