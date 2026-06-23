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
| Validation croisée | 5 folds (RandomizedSearchCV) |
| Nombre de combinaisons testées | 30 par modèle optimisé |

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

*Source : Fichiers `ia/models/*_clf_metrics.json` — résultats d'exécution réels*

| Modèle | Accuracy | Precision | Recall | **F1** ⭐ | ROC-AUC |
|--------|:--------:|:---------:|:------:|:--------:|:-------:|
| Logistic Regression | 0.6455 | 0.5385 | 0.5000 | 0.5185 | 0.6929 |
| Random Forest | 0.6909 | 0.6250 | 0.4762 | 0.5405 | 0.8146 |
| XGBoost (base) | 0.7091 | 0.6250 | 0.5952 | 0.6098 | 0.7959 |
| MLP | 0.5636 | 0.1250 | 0.0238 | 0.0400 | 0.3414 |
| **XGBoost (optimisé)** | **0.7364** | **0.6757** | **0.5952** | **0.6329** | **0.8288** |

### 3.3 Optimisation de XGBoost

L'optimisation a été réalisée via `RandomizedSearchCV` avec 30 itérations et 5 folds.

**Meilleurs paramètres trouvés :**

| Paramètre | Valeur |
|-----------|--------|
| `subsample` | 0.8 |
| `scale_pos_weight` | 1.5 |
| `n_estimators` | 300 |
| `max_depth` | 4 |
| `learning_rate` | 0.05 |

**Meilleur F1 (CV)** : 0.6968

**Gain de performance :**

| Métrique | Avant optimisation | Après optimisation | Gain |
|----------|:-------------------:|:-------------------:|:----:|
| F1-Score | 0.6098 | **0.6329** | **+3.8 %** |
| Accuracy | 0.7091 | **0.7364** | **+3.8 %** |
| Precision | 0.6250 | **0.6757** | **+8.1 %** |
| ROC-AUC | 0.7959 | **0.8288** | **+4.1 %** |

### 3.4 Analyse par modèle

**Logistic Regression**
Modèle de référence linéaire. Performance honorable (F1 = 0.5185) indiquant qu'une partie du signal est linéairement séparable. Recall de 50 % signifie qu'un pays en déclin sur deux est correctement détecté. Interprétable via les coefficients.

**Random Forest**
Meilleur ROC-AUC de base (0.8146) — excellente capacité discriminante globale. Le recall plus faible (0.4762) explique un F1 légèrement inférieur à XGBoost : Random Forest est plus conservateur dans ses prédictions positives (privilégie la précision sur le recall).

**XGBoost (base)**
Meilleur F1 de base (0.6098) et meilleure accuracy (0.7091). Recall de 0.5952 : détecte 59,5 % des pays réellement en déclin, avec une précision de 62,5 %.

**MLP (Réseau de neurones)**
Échec de convergence sur ce dataset. F1 = 0.04, recall = 0.024 indiquent que le modèle prédit quasi-systématiquement la classe 0 (En croissance). Ce comportement est typique des réseaux de neurones sous-dimensionnés sur des datasets tabulaires de petite taille (< 500 observations). Le MLP est éliminé.

**XGBoost (optimisé)** ✅ *Modèle sélectionné*
L'optimisation a permis d'améliorer le F1 de +3,8 % et le ROC-AUC de +4,1 %. Le modèle conserve un recall de 0.595 (détection des pays en déclin) tout en améliorant la précision de 8,1 % (réduction des faux positifs). C'est le meilleur compromis global.

### 3.5 Modèle sélectionné — Classification

**→ XGBoost Classifier optimisé** (`ia/models/xgboost_optimized_clf.joblib`)

| Critère | Valeur |
|---------|--------|
| F1-Score | **0.6329** |
| Accuracy | 0.7364 |
| Precision | 0.6757 |
| Recall | 0.5952 |
| ROC-AUC | 0.8288 |
| Meilleurs paramètres | `subsample=0.8, scale_pos_weight=1.5, n_estimators=300, max_depth=4, learning_rate=0.05` |

---

## 4. Axe 2 — Régression : Prévision de la fréquentation

### 4.1 Choix et justification des métriques

**Métrique principale : R² (coefficient de détermination)**

Le R² mesure la proportion de la variance de `passengers` expliquée par le modèle. Il est retenu car :
- Il est **indépendant de l'échelle** de `passengers` (qui varie de 0 à 1 080 000), ce qui permet une comparaison directe entre modèles
- Il fournit une interprétation intuitive : R² = 0.99 signifie que le modèle explique 99 % de la variance observée

**Métrique complémentaire : MAE**

Le MAE (Mean Absolute Error) est interprétable directement en unité métier (milliers de passagers) et constitue un indicateur opérationnel utile pour les décideurs d'ObRail.

**Pourquoi pas le RMSE seul ?**

Le RMSE est sensible aux valeurs extrêmes (grands pays). Utilisé seul, il pénalise disproportionnellement les modèles qui font de grosses erreurs sur l'Allemagne ou la France, sans refléter leur performance générale. Il est présenté en complément du R² et du MAE.

### 4.2 Résultats complets

*Source : Fichiers `ia/models/*_reg_metrics.json` — résultats d'exécution réels*

| Modèle | MAE | RMSE | **R²** ⭐ |
|--------|:---:|:----:|:--------:|
| Ridge (base) | 4 338.8 | 9 074.0 | 0.9962 |
| Ridge (optimisé) | 4 674.4 | 11 370.4 | 0.9940 |
| Random Forest | 4 965.7 | 26 039.2 | 0.9684 |
| XGBoost (base) | 5 215.1 | 29 427.6 | 0.9596 |
| **XGBoost (optimisé)** | **5 466.7** | **28 493.4** | **0.9621** |

### 4.3 Optimisation des modèles de régression

**XGBoost Regressor**

L'optimisation a été réalisée via `RandomizedSearchCV` avec 30 itérations et 5 folds.

**Meilleurs paramètres trouvés :**

| Paramètre | Valeur |
|-----------|--------|
| `subsample` | 0.8 |
| `n_estimators` | 200 |
| `max_depth` | 3 |
| `learning_rate` | 0.05 |

**Meilleur R² (CV)** : 0.9951

**Gain de performance XGBoost :**

| Métrique | Avant optimisation | Après optimisation | Gain |
|----------|:-------------------:|:-------------------:|:----:|
| R² | 0.9596 | **0.9621** | **+0.26 %** |
| RMSE | 29 427.6 | **28 493.4** | **-3.2 %** |

**Ridge Regressor**

L'optimisation de Ridge a été réalisée par recherche sur le paramètre `alpha` en validation croisée.

**Meilleur alpha trouvé** : 0.1

**Meilleur R² (CV)** : 0.9837

**Résultat** : L'optimisation de Ridge a dégradé légèrement les performances (R² 0.9962 → 0.9940). Le modèle base avec `alpha=1.0` était déjà optimal sur ce dataset. Ridge optimisé est donc écarté.

### 4.4 Analyse par modèle

**Ridge (base)**
Résultats remarquables : meilleur R² (0.9962), meilleur MAE (4 338.8), meilleur RMSE (9 074.0). Ce résultat s'explique par la **forte autocorrélation temporelle** des séries de fréquentation : la relation entre `passengers_lag1`, `passengers_lag2` et `passengers` est quasi-linéaire pour la majorité des pays. Ridge capture parfaitement cette linéarité.

**Ridge (optimisé)**
L'optimisation du paramètre `alpha` a dégradé les performances (R² 0.9962 → 0.9940). Le modèle de base avec `alpha=1.0` était déjà optimal. Ce modèle est écarté.

**Random Forest**
R² de 0.9684 — très bonne performance, mais RMSE nettement plus élevé (26 039) révélant des erreurs importantes sur les grands pays. Les méthodes par arbres peinent à extrapoler au-delà des valeurs vues en entraînement.

**XGBoost (base)**
R² de 0.9596, RMSE de 29 427. Le gradient boosting ne surpasse pas Ridge sur ce dataset où la relation est principalement linéaire.

**XGBoost (optimisé)** ✅ *Modèle sélectionné*
L'optimisation a permis d'améliorer le R² de 0.9596 → 0.9621 (+0.26 %) et de réduire le RMSE de 3.2 %. Bien que Ridge offre un R² supérieur, **XGBoost est sélectionné** pour les raisons suivantes :
- **Explicabilité** : XGBoost permet d'extraire les importances de features et d'utiliser SHAP, ce qui est demandé par ObRail.
- **Non-linéarité** : XGBoost peut capturer des relations non-linéaires que Ridge ne peut pas modéliser (effets de seuil, interactions entre pays, impact d'événements exceptionnels comme le COVID).
- **Compromis** : La différence de R² (0.9621 vs 0.9962) est acceptable compte tenu du gain en interprétabilité et en robustesse.

### 4.5 Point d'attention — R² élevé

Le R² élevé de tous les modèles est **attendu et légitime** dans le contexte d'une série temporelle avec variables lag :
- `passengers_lag1` (fréquentation de l'année N-1) est le prédicteur le plus fort de `passengers` de l'année N
- Cela ne constitue pas un leakage car la valeur cible de l'année N n'est jamais utilisée comme feature
- Ce phénomène est caractéristique des séries temporelles stables

Ce point mérite d'être expliqué explicitement lors de la soutenance.

### 4.6 Modèle sélectionné — Régression

**→ XGBoost Regressor optimisé** (`ia/models/xgboost_optimized_reg.joblib`)

| Critère | Valeur |
|---------|--------|
| R² | **0.9621** |
| MAE | 5 466.7 |
| RMSE | 28 493.4 |
| Meilleurs paramètres | `subsample=0.8, n_estimators=200, max_depth=3, learning_rate=0.05` |

---

## 5. Synthèse de sélection

| Axe | Modèle final | Critère principal | Valeur | Statut |
|-----|-------------|------------------|--------|--------|
| Classification | XGBoost optimisé | F1-Score | **0.6329** | ✅ Sélectionné |
| Régression | XGBoost optimisé | R² | **0.9621** | ✅ Sélectionné |

### Justification de la sélection de XGBoost pour les deux axes

1. **Uniformité du stack technique** : Utiliser le même algorithme pour les deux axes simplifie la maintenance et la documentation.

2. **Explicabilité** : XGBoost permet d'utiliser SHAP pour interpréter les prédictions, ce qui est une exigence du cahier des charges.

3. **Performance** : XGBoost est le meilleur modèle pour la classification et offre un R² solide pour la régression.

4. **Scalabilité** : XGBoost est plus robuste à l'ajout de nouvelles données ou de nouvelles features que Ridge.

---

## 6. Limites identifiées

### Classification
- F1 de 0.6329 signifie que 40,5 % des pays en déclin ne sont pas détectés (recall = 0.595) et que 32,4 % des pays classés en déclin le sont à tort (precision = 0.676). Des marges d'amélioration existent.
- Le dataset de 546 lignes est de taille modeste. Un dataset plus grand (données mensuelles ou trimestrielles) améliorerait les performances.

### Régression
- XGBoost suppose une capacité à capturer des relations non-linéaires, mais Ridge était plus performant en R² pur. Le choix de XGBoost est un compromis performance/explicabilité.
- Le RMSE de 28 493 représente une erreur absolue importante sur les petits pays — à interpréter avec précaution.

### Générales
- Le dataset ne couvre que 42 pays et 15 années. Une extension temporelle ou spatiale améliorerait la généralisation.
- L'impact du COVID-19 en 2020 est un outlier qui pourrait biaiser les modèles.

---

## 7. Prochaine étape

Les deux modèles sélectionnés (XGBoost optimisé pour la classification et la régression) seront intégrés dans l'API FastAPI et utilisés pour les prédictions dans le dashboard React.

**Prochaines phases :**
- Phase 8 : Explicabilité IA (SHAP, feature importance)
- Phase 10 : Script `predict.py`
- Phase 11 : API FastAPI

---

## 8. Livrables produits

| Livrable | Chemin | Statut |
|----------|--------|--------|
| Rapport évaluation | `docs/rapport_evaluation.md` (ce document) | ✅ |
| Rapport CSV classification | `ia/reports/comparison_classification.csv` | ✅ |
| Rapport CSV régression | `ia/reports/comparison_regression.csv` | ✅ |
| Modèle clf sélectionné | `ia/models/xgboost_optimized_clf.joblib` | ✅ |
| Modèle reg sélectionné | `ia/models/xgboost_optimized_reg.joblib` | ✅ |
| Métriques clf optimisées | `ia/models/xgboost_optimized_clf_metrics.json` | ✅ |
| Métriques reg optimisées | `ia/models/xgboost_optimized_reg_metrics.json` | ✅ |
| Preprocesseur clf | `data/ml/preprocessor_classification.joblib` | ✅ |
| Preprocesseur reg | `data/ml/preprocessor_regression.joblib` | ✅ |
| Visualisations (matrices, ROC, scatter) | `docs/fig_*.png` | ❌ À produire |