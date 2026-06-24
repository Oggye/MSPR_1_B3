# Phase 6 — Optimisation des Modèles

---

## 1. Contexte

### Objectif de l'étape

Optimiser les modèles retenus après la comparaison de la Phase 5 afin d'améliorer le F1-Score pour la classification `en_declin` et le R² pour la régression `passengers`.

### Position dans le projet

Cette phase succède à l'évaluation comparative et prépare la sélection finale des modèles en confrontant les performances avant et après recherche d'hyperparamètres.

### Lien avec le cahier des charges

Le cahier des charges impose de justifier le choix des modèles, d'utiliser des métriques adaptées et de documenter les gains obtenus par optimisation.

---

## 2. Travaux réalisés

Le script **`ia/src/ml/models/optimize_xgboost_ridge.py`** optimise trois modèles : **XGBoost classification**, **XGBoost régression** et **Ridge régression**. Il recharge les datasets via `load_classification_data()` et `load_regression_data()`, applique les mêmes preprocessings que l'entraînement initial, lance une recherche d'hyperparamètres, évalue le meilleur estimateur sur le jeu de test, puis sauvegarde les modèles et métriques avec `save_model_and_metrics()`.

---

## 3. Fonctionnement

| Modèle | Méthode | Métrique optimisée | Validation croisée | Hyperparamètres recherchés |
|--------|---------|--------------------|--------------------|-----------------------------|
| XGBoost classification | `RandomizedSearchCV` | `f1` | `cv=5` | `n_estimators=[50,100,200,300]`, `max_depth=[2,3,4,5]`, `learning_rate=[0.01,0.05,0.1,0.2]`, `subsample=[0.7,0.8,1.0]`, `scale_pos_weight=[1,1.5,2]` |
| XGBoost regression | `RandomizedSearchCV` | `r2` | `cv=5` | `n_estimators=[50,100,200,300]`, `max_depth=[2,3,4,5]`, `learning_rate=[0.01,0.05,0.1,0.2]`, `subsample=[0.7,0.8,1.0]` |
| Ridge regression | `GridSearchCV` | `r2` | `cv=5` | `alpha=[0.01,0.1,0.5,1.0,2.0,5.0,10.0,50.0,100.0]` |

Pour XGBoost, `n_iter=30`, `random_state=42` et `n_jobs=-1` sont utilisés. Le score moyen de validation croisée est affiché par le script, mais sa valeur sauvegardée est **non présent dans le script**.

---

## 4. Résultats obtenus

### 4.1 Hyperparamètres initiaux

| Modèle | Hyperparamètres initiaux |
|--------|---------------------------|
| XGBoost classification | `n_estimators=100`, `learning_rate=0.1`, `max_depth=4`, `eval_metric=logloss`, `scale_pos_weight=n_neg/n_pos`, `subsample` : non présent dans le script initial, `random_state=42` |
| XGBoost régression | `n_estimators=100`, `learning_rate=0.1`, `max_depth=4`, `eval_metric=rmse`, `subsample` : non présent dans le script initial, `random_state=42` |
| Ridge régression | `alpha=1.0` |

### 4.2 Hyperparamètres optimisés

| Modèle | Hyperparamètres optimisés |
|--------|----------------------------|
| XGBoost classification | `n_estimators=300`, `max_depth=4`, `learning_rate=0.05`, `subsample=0.8`, `scale_pos_weight=1.5` |
| XGBoost régression | `n_estimators=200`, `max_depth=3`, `learning_rate=0.05`, `subsample=0.8` |
| Ridge régression | `alpha=0.1` |

### 4.3 Comparaison avant/après

| Modèle | Métrique principale | Avant | Après | Écart |
|--------|---------------------|-------|-------|-------|
| XGBoost classification | F1 | 0.6098 | 0.6329 | +0.0232 |
| XGBoost régression | R² | 0.9596 | 0.9621 | +0.0025 |
| Ridge régression | R² | 0.9962 | 0.9940 | -0.0022 |

**Analyse :** l'optimisation améliore XGBoost classification, avec une hausse du F1 et du ROC-AUC (0.7959 vers 0.8288), ce qui confirme l'intérêt de rechercher `scale_pos_weight` sur une cible déséquilibrée. XGBoost régression progresse légèrement en R² et RMSE, mais son MAE augmente (5 215.1 vers 5 466.7), indiquant un gain global limité. Ridge perd légèrement en R² et se dégrade en MAE/RMSE après optimisation ; l'alpha initial `1.0` reste donc plus performant sur le test que l'alpha optimisé par validation croisée.

---

## 5. Difficultés rencontrées

- Les meilleurs scores de validation croisée ne sont pas sauvegardés dans les fichiers JSON : ils sont seulement affichés en console.
- Les résultats de `best_params_` ne sont pas exportés dans un fichier dédié ; ils doivent être relus depuis les modèles `.joblib` ou la sortie d'exécution.
- L'optimisation Ridge améliore le critère de validation croisée mais dégrade la performance observée sur le jeu de test.

---

## 6. Correctifs appliqués

- Utilisation de `RandomizedSearchCV` pour limiter le coût de recherche sur XGBoost à 30 combinaisons.
- Utilisation de `GridSearchCV` pour Ridge, car une seule dimension (`alpha`) est testée.
- Conservation des métriques de test via les fichiers JSON pour permettre la comparaison avant/après.

---

## 7. Impact sur la suite du projet

XGBoost classification optimisé devient le meilleur candidat pour l'axe classification. Pour la régression, Ridge reste le modèle prioritaire, mais la version initiale doit être comparée explicitement à la version optimisée avant sélection finale.

---

## 8. Livrables produits

| Livrable | Chemin | Statut |
|----------|--------|--------|
| Script d'optimisation | `ia/src/ml/models/optimize_xgboost_ridge.py` | Produit |
| Modèle XGBoost classification optimisé | `ia/models/xgboost_optimized_clf.joblib` | Produit |
| Métriques XGBoost classification optimisé | `ia/models/xgboost_optimized_clf_metrics.json` | Produit |
| Modèle XGBoost régression optimisé | `ia/models/xgboost_optimized_reg.joblib` | Produit |
| Métriques XGBoost régression optimisé | `ia/models/xgboost_optimized_reg_metrics.json` | Produit |
| Modèle Ridge régression optimisé | `ia/models/ridge_optimized_reg.joblib` | Produit |
| Métriques Ridge régression optimisé | `ia/models/ridge_optimized_reg_metrics.json` | Produit |
| Préprocesseur classification | `data/ml/preprocessor_classification.joblib` | Produit |
| Préprocesseur régression | `data/ml/preprocessor_regression.joblib` | Produit |

---

## 9. Lancement & Préparation de la Phase 7

### Exécution du script

Pour lancer l'optimisation des modèles, exécuter la commande suivante depuis la racine du projet :

```bash
python -m ia.src.ml.models.optimize_xgboost_ridge
```

Cette commande entraîne les versions optimisées des modèles XGBoost et Ridge, sauvegarde les modèles au format `.joblib` ainsi que leurs métriques au format `.json`.

### Préparation de la Phase 7

Une première version du rapport d'évaluation final a été rédigée dans le fichier :

`docs/ia/phase/re.md`

Ce document constitue une base de travail pour la Phase 7 et devra être relu, complété et validé avant la rédaction de la version définitive du rapport de sélection des modèles.
