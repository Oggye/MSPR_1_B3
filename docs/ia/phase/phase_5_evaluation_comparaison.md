# Phase 5 — Évaluation et Comparaison des Modèles

---

## 1. Contexte

### Objectif de l'étape

Analyser et comparer les performances de tous les modèles entraînés, sélectionner les métriques pertinentes selon chaque axe, et produire les tableaux comparatifs servant de base à la sélection du modèle final.

### Position dans le projet

Cette phase succède directement à l'entraînement (Phase 4). Elle produit les rapports comparatifs et prépare la décision de sélection (Phase 7).

### Lien avec le cahier des charges

Le cahier des charges impose de :
- **évaluer chaque modèle avec les métriques pertinentes** selon le type de tâche ;
- **justifier le choix des métriques** ;
- produire un **rapport d'évaluation et des visualisations** ;
- **sélectionner le modèle final** avec justification.

---

## 2. Travaux réalisés

### Script d'évaluation

**`ia/src/ml/evaluate_model.py`** — charge les métriques sauvegardées de chaque modèle et produit les tableaux comparatifs.

Les rapports sont exportés vers :
- `ia/reports/comparison_classification.csv`
- `ia/reports/comparison_regression.csv`

---

## 3. Fonctionnement

### 3.1 Métriques de classification

| Métrique | Description | Pertinence pour ce projet |
|----------|-------------|--------------------------|
| **Accuracy** | Taux de prédictions correctes | Indicateur global, limité en cas de déséquilibre |
| **Precision** | Parmi les pays classés "en déclin", combien le sont vraiment | Limite les fausses alarmes (pays sains classés à tort) |
| **Recall** | Parmi les pays réellement en déclin, combien sont détectés | Limite les déclin non détectés |
| **F1-Score** ⭐ | Moyenne harmonique precision/recall | **Critère principal** — équilibre les deux types d'erreurs sur un dataset déséquilibré |
| **ROC-AUC** | Capacité discriminante globale du classifieur | Mesure la qualité du scoring indépendamment du seuil |

> Le F1-Score est retenu comme **critère de sélection principal** car il pénalise équitablement les faux positifs et les faux négatifs. Sur un dataset avec 38,1 % de cas positifs, l'accuracy seule n'est pas représentative (un classifieur naïf prédisant toujours "0" atteindrait 61,9 %).

### 3.2 Métriques de régression

| Métrique | Description | Pertinence pour ce projet |
|----------|-------------|--------------------------|
| **MAE** | Erreur absolue moyenne (en milliers de passagers) | Interprétable directement en unité métier |
| **RMSE** | Racine de l'erreur quadratique moyenne | Pénalise fortement les grandes erreurs (sensible aux outliers) |
| **R²** ⭐ | Part de variance expliquée par le modèle | **Critère principal** — indépendant de l'échelle des données |

> Le R² est retenu comme **critère de sélection principal** car il permet de comparer les modèles indépendamment de l'unité et de l'échelle de `passengers` (qui varie de 0 à 1 080 000). Le MAE est utilisé en complément pour l'interprétation métier.

---

## 4. Résultats obtenus

### 4.1 Tableau comparatif — Classification (`en_declin`)

Source : `ia/reports/comparison_classification.csv` (résultats d'exécution réels)

| Modèle | Accuracy | Precision | Recall | F1 ⭐ | ROC-AUC |
|--------|----------|-----------|--------|--------|---------|
| Logistic Regression | 0.6455 | 0.5385 | 0.5000 | 0.5185 | 0.6929 |
| Random Forest | 0.6909 | 0.6250 | 0.4762 | 0.5405 | **0.8146** |
| **XGBoost** | **0.7091** | **0.6250** | **0.5952** | **0.6098** | 0.7959 |
| MLP | 0.5636 | 0.1250 | 0.0238 | 0.0400 | 0.3414 |

**Analyse :**

- **XGBoost** est le meilleur modèle sur le critère principal F1 (0.6098) et sur l'accuracy (0.7091). Il détecte 59,5 % des pays en déclin avec une précision de 62,5 %.
- **Random Forest** présente le meilleur ROC-AUC (0.8146), indiquant une excellente capacité discriminante globale. Son recall plus faible (0.4762) explique un F1 légèrement inférieur.
- **Logistic Regression** offre une performance honorable (F1 = 0.5185) pour un modèle linéaire, confirmant qu'une partie du signal est linéairement séparable.
- **MLP** échoue sur ce dataset : F1 = 0.04, recall = 0.024. Le réseau prédit quasi-systématiquement la classe majoritaire (0). Ce comportement est typique de réseaux de neurones sous-dimensionnés entraînés sur de petits datasets.

### 4.2 Tableau comparatif — Régression (`passengers`)

Source : `ia/reports/comparison_regression.csv` (résultats d'exécution réels)

| Modèle | MAE | RMSE | R² ⭐ |
|--------|-----|------|-------|
| **Ridge** | **4 338.8** | **9 074.0** | **0.9962** |
| Random Forest | 4 965.7 | 26 039.2 | 0.9684 |
| XGBoost | 5 215.1 | 29 427.6 | 0.9596 |

**Analyse :**

- **Ridge** domine sur tous les critères : meilleur MAE, meilleur RMSE, meilleur R². Ce résultat s'explique par la **forte autocorrélation temporelle** des séries de fréquentation : la relation entre `passengers_lag1`, `passengers_lag2` et `passengers` est quasi-linéaire pour la plupart des pays.
- **Random Forest et XGBoost** présentent un RMSE beaucoup plus élevé. Cela reflète leurs difficultés sur les **grands pays** (Allemagne, France, Italie) où la distribution de `passengers` est très asymétrique et les erreurs absolues importantes.
- Le R² de 0.9962 du Ridge sur un dataset de série temporelle avec lags est élevé mais **attendu et légitime** : les lags capturent 99 % de la variance temporelle de la fréquentation.

### 4.3 Synthèse de sélection

| Axe | Modèle sélectionné | Critère | Valeur |
|-----|--------------------|---------|--------|
| Classification | XGBoost | F1-Score | 0.6098 |
| Régression | Ridge | R² | 0.9962 |

---

## 5. Difficultés rencontrées

- **MLP défaillant** : la convergence du réseau est insuffisante sur 436 observations. Les valeurs de precision (0.125) et recall (0.024) indiquent que le modèle prédit massivement la classe 0. Ce comportement suggère que le MLP n'a pas convergé vers un minimum utile, probablement en raison d'un manque de données et d'une sensibilité élevée à l'initialisation.
- **RMSE élevé des méthodes ensemblistes** en régression : Random Forest et XGBoost peinent sur les observations extrêmes (grands pays), car ces méthodes moyennent des prédictions d'arbres qui ne peuvent pas extrapoler au-delà des valeurs vues en entraînement.
- **Visualisations non disponibles** : les matrices de confusion, courbes ROC et graphiques actual vs predicted sont identifiés comme livrables de la Phase 5 mais n'ont pas encore été produits (notebook `02_evaluation.ipynb` à réaliser).

---

## 6. Correctifs appliqués

- Utilisation du **F1-Score** plutôt que l'accuracy comme critère principal en classification, pour tenir compte du déséquilibre des classes
- Utilisation du **R²** plutôt du RMSE seul en régression, pour comparer les modèles indépendamment de l'échelle

---

## 7. Impact sur la suite du projet

- XGBoost classification et Ridge régression sont les **candidats prioritaires pour l'optimisation** (Phase 6)
- Les métriques documentées servent de **baseline** pour mesurer l'amélioration après optimisation
- L'échec du MLP constitue un **résultat scientifique valide** : il démontre que les données tabulaires de petite taille sont mieux servies par le boosting

---

## 8. Livrables produits

| Livrable | Chemin | Statut |
|----------|--------|--------|
| Script d'évaluation | `ia/src/ml/evaluate_model.py` | ✅ Produit |
| Rapport classification | `ia/reports/comparison_classification.csv` | ✅ Produit |
| Rapport régression | `ia/reports/comparison_regression.csv` | ✅ Produit |
| Notebook évaluation | `notebooks/02_evaluation.ipynb` | ❌ À produire |
| Matrices de confusion | `docs/fig_confusion_matrices.png` | ❌ À produire |
| Courbes ROC | `docs/fig_roc_curves.png` | ❌ À produire |
| Actual vs Predicted | `docs/fig_actual_vs_predicted.png` | ❌ À produire |
