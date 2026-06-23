# Rapport d'Évaluation et Sélection du Modèle Final

---

## 1. Contexte

### Objectif

Ce rapport présente l'évaluation comparative de tous les modèles entraînés, justifie le choix des métriques retenues, et documente la sélection des modèles finaux pour les deux axes ML du projet ObRail.

### Lien avec le cahier des charges

> *"Évaluer chaque modèle avec les métriques pertinentes selon le type de tâche. Sélectionner le modèle final. Documenter les performances et limites."*

---

## 2. Configuration expérimentale

| Paramètre | Valeur |
|-----------|--------|
| Dataset total | 546 observations |
| Ensemble train | 436 observations (79,9 %) |
| Ensemble test | 110 observations (20,1 %) |
| Random state | 42 (tous les modèles) |
| Stratification | Oui (classification uniquement) |
| Features après preprocessing | 47 (6 numériques + 41 OHE pays) |

---

## 3. Axe 1 — Classification : Détection des pays en déclin

### 3.1 Choix et justification des métriques

**Métrique principale : F1-Score**

Le F1-Score est retenu comme critère de sélection principal pour les raisons suivantes :
- Le dataset présente un **déséquilibre modéré** (61,9 % classe 0 / 38,1 % classe 1)
- Un classifieur naïf prédisant toujours "En croissance" atteindrait une accuracy de 61,9 % sans valeur prédictive
- Le F1 pénalise équitablement les **faux positifs** (pays sains classés en déclin, risque de décision incorrecte) et les **faux négatifs** (pays en déclin non détectés, risque de non-intervention)

**Métrique complémentaire : ROC-AUC**

Le ROC-AUC mesure la capacité discriminante globale du classifieur indépendamment du seuil de décision. Il est particulièrement utile pour comparer des modèles sur des datasets déséquilibrés.

### 3.2 Résultats complets

*Source : `ia/reports/comparison_classification.csv` — résultats d'exécution réels*

| Modèle | Accuracy | Precision | Recall | **F1** ⭐ | ROC-AUC |
|--------|:--------:|:---------:|:------:|:--------:|:-------:|
| Logistic Regression | 0.6455 | 0.5385 | 0.5000 | 0.5185 | 0.6929 |
| Random Forest | 0.6909 | 0.6250 | 0.4762 | 0.5405 | **0.8146** |
| **XGBoost** | **0.7091** | **0.6250** | **0.5952** | **0.6098** | 0.7959 |
| MLP | 0.5636 | 0.1250 | 0.0238 | 0.0400 | 0.3414 |

### 3.3 Analyse par modèle

**Logistic Regression**
Modèle de référence linéaire. Performance honorable (F1 = 0.5185) indiquant qu'une partie du signal est linéairement séparable. Recall de 50 % signifie qu'un pays en déclin sur deux est correctement détecté. Interprétable via les coefficients.

**Random Forest**
Meilleur ROC-AUC (0.8146) — excellente capacité discriminante globale. Le recall plus faible (0.4762) explique un F1 légèrement inférieur à XGBoost : Random Forest est plus conservateur dans ses prédictions positives (privilégie la précision sur le recall).

**XGBoost** ✅ *Modèle sélectionné*
Meilleur F1 (0.6098) et meilleure accuracy (0.7091). Recall de 0.5952 : détecte 59,5 % des pays réellement en déclin, avec une précision de 62,5 %. C'est le meilleur compromis sur le critère principal.

**MLP (Réseau de neurones)**
Échec de convergence sur ce dataset. F1 = 0.04, recall = 0.024 indiquent que le modèle prédit quasi-systématiquement la classe 0 (En croissance). Ce comportement est typique des réseaux de neurones sous-dimensionnés sur des datasets tabulaires de petite taille (< 500 observations). Le MLP est éliminé.

### 3.4 Modèle sélectionné — Classification

**→ XGBoost Classifier** (`ia/models/xgboost_clf.joblib`)

| Critère | Valeur |
|---------|--------|
| F1-Score | **0.6098** |
| Accuracy | 0.7091 |
| Precision | 0.6250 |
| Recall | 0.5952 |
| ROC-AUC | 0.7959 |

---

## 4. Axe 2 — Régression : Prévision de la fréquentation

### 4.1 Choix et justification des métriques

**Métrique principale : R² (coefficient de détermination)**

Le R² mesure la proportion de la variance de `passengers` expliquée par le modèle. Il est retenu car :
- Il est **indépendant de l'échelle** de `passengers` (qui varie de 0 à 1 080 000), ce qui permet une comparaison directe entre modèles
- Il fourni une interprétation intuitive : R² = 0.996 signifie que le modèle explique 99,6 % de la variance observée

**Métrique complémentaire : MAE**

Le MAE (Mean Absolute Error) est interprétable directement en unité métier (milliers de passagers) et constitue un indicateur opérationnel utile pour les décideurs d'ObRail.

**Pourquoi pas le RMSE seul ?**

Le RMSE est sensible aux valeurs extrêmes (grands pays). Utilisé seul, il pénalise disproportionnellement les modèles qui font de grosses erreurs sur l'Allemagne ou la France, sans refléter leur performance générale. Il est présenté en complément du R² et du MAE.

### 4.2 Résultats complets

*Source : `ia/reports/comparison_regression.csv` — résultats d'exécution réels*

| Modèle | MAE | RMSE | **R²** ⭐ |
|--------|:---:|:----:|:--------:|
| **Ridge** | **4 338.8** | **9 074.0** | **0.9962** |
| Random Forest | 4 965.7 | 26 039.2 | 0.9684 |
| XGBoost | 5 215.1 | 29 427.6 | 0.9596 |

### 4.3 Analyse par modèle

**Ridge** ✅ *Modèle sélectionné*
Résultats remarquables : meilleur R² (0.9962), meilleur MAE (4 338.8), meilleur RMSE (9 074.0). Ce résultat s'explique par la **forte autocorrélation temporelle** des séries de fréquentation : la relation entre `passengers_lag1`, `passengers_lag2` et `passengers` est quasi-linéaire pour la majorité des pays. Ridge capture parfaitement cette linéarité.

**Random Forest**
R² de 0.9684 — très bonne performance, mais RMSE nettement plus élevé (26 039) révélant des erreurs importantes sur les grands pays. Les méthodes par arbres peinent à extrapoler au-delà des valeurs vues en entraînement.

**XGBoost**
R² de 0.9596, RMSE le plus élevé (29 427). Le gradient boosting ne surpasse pas Ridge sur ce dataset où la relation est principalement linéaire.

### 4.4 Point d'attention — R² élevé

Le R² de 0.9962 de Ridge est élevé. Ce résultat est **attendu et légitime** dans le contexte d'une série temporelle avec variables lag : `passengers_lag1` (fréquentation de l'année précédente) est le prédicteur le plus fort de `passengers` de l'année N. Cela ne constitue pas un leakage car :
- `passengers_lag1` est la fréquentation de l'année **N-1**, pas de l'année N
- La valeur cible (`passengers` de l'année N) n'est jamais utilisée comme feature

Ce point mérite d'être expliqué explicitement lors de la soutenance.

### 4.5 Modèle sélectionné — Régression

**→ Ridge Regression** (`ia/models/ridge_reg.joblib`)

| Critère | Valeur |
|---------|--------|
| R² | **0.9962** |
| MAE | 4 338.8 |
| RMSE | 9 074.0 |

---

## 5. Synthèse de sélection

| Axe | Modèle final | Critère principal | Valeur | Statut |
|-----|-------------|------------------|--------|--------|
| Classification | XGBoost | F1-Score | 0.6098 | ✅ Sélectionné |
| Régression | Ridge | R² | 0.9962 | ✅ Sélectionné |

---

## 6. Limites identifiées

### Classification
- F1 de 0.6098 signifie que 39 % des pays en déclin ne sont pas détectés (recall = 0.595) et que 37,5 % des pays classés en déclin le sont à tort (precision = 0.625). Des marges d'amélioration existent via l'optimisation des hyperparamètres (Phase 6).
- Le dataset de 546 lignes est de taille modeste. Un dataset plus grand (données mensuelles ou trimestrielles) améliorerait les performances.

### Régression
- Ridge suppose une relation **linéaire** entre les features et la cible. Si des effets non-linéaires existent (ex : effet COVID en 2020), Ridge les approxime mais ne les capture pas parfaitement.
- Le RMSE de 9 074 représente une erreur absolue importante sur les petits pays (médiane 14 178) — à interpréter avec précaution.

---

## 7. Prochaine étape

Les deux modèles sélectionnés (XGBoost clf, Ridge reg) seront soumis à une **optimisation des hyperparamètres** (Phase 6 — `optimize_xgboost.py`) pour tenter d'améliorer le F1 de classification. Ridge étant déjà optimal sur ses paramètres limités (alpha), l'optimisation portera principalement sur XGBoost.

---

## 8. Livrables produits

| Livrable | Chemin | Statut |
|----------|--------|--------|
| Rapport évaluation | `docs/rapport_evaluation.md` (ce document) | ✅ |
| Rapport CSV classification | `ia/reports/comparison_classification.csv` | ✅ |
| Rapport CSV régression | `ia/reports/comparison_regression.csv` | ✅ |
| Modèle clf sélectionné | `ia/models/xgboost_clf.joblib` | ✅ |
| Modèle reg sélectionné | `ia/models/ridge_reg.joblib` | ✅ |
| Visualisations (matrices, ROC, scatter) | `docs/fig_*.png` | ❌ À produire |
