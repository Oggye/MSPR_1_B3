# Rapport d'Évaluation et Sélection du Modèle Final
**Projet ObRail Europe — MSPR RNCP36581**

---

## 1. Configuration expérimentale

| Paramètre | Valeur |
|---|---|
| Dataset total | 546 observations |
| Train / Test | 436 / 110 (80/20) |
| Random state | 42 (tous les modèles) |
| Stratification | Oui (classification uniquement) |
| Features après encodage | 47 (6 numériques + 41 pays OneHotEncoder) |
| Optimisation | RandomizedSearchCV, 30 itérations, 5 folds |

---

## 2. Classification — Détection des pays en déclin

### Pourquoi le F1-Score comme métrique principale ?

Le dataset est légèrement déséquilibré (62 % / 38 %). Un modèle qui prédirait toujours
"En croissance" obtiendrait 62 % d'accuracy sans aucune valeur. Le F1 pénalise
équitablement les deux types d'erreurs — déclin non détecté et fausse alarme.

### Résultats

| Modèle | Accuracy | Precision | Recall | **F1** ⭐ | ROC-AUC |
|---|:---:|:---:|:---:|:---:|:---:|
| Logistic Regression | 0.645 | 0.538 | 0.500 | 0.519 | 0.693 |
| Random Forest | 0.691 | 0.625 | 0.476 | 0.541 | 0.815 |
| XGBoost (base) | 0.709 | 0.625 | 0.595 | 0.610 | 0.796 |
| MLP | 0.564 | 0.125 | 0.024 | 0.040 | 0.341 |
| **XGBoost (optimisé)** ✅ | **0.764** | **0.722** | **0.619** | **0.667** | **0.826** |

### Analyse

- **Logistic Regression** : performance correcte pour un modèle linéaire. Confirme qu'une partie du signal est capturale sans complexité.
- **Random Forest** : meilleur ROC-AUC de base (0.815), mais recall faible — il manque trop de pays en déclin.
- **MLP** : échec complet (F1 = 0.04). Trop peu de données pour qu'un réseau de neurones converge sur 436 lignes. Ce résultat illustre pourquoi les réseaux de neurones ne sont pas adaptés aux petits datasets tabulaires.
- **XGBoost optimisé** : meilleur sur tous les critères après optimisation des hyperparamètres.

### Gain apporté par l'optimisation de XGBoost

| Métrique | Avant | Après | Gain |
|---|:---:|:---:|:---:|
| F1-Score | 0.610 | **0.667** | +9.3 % |
| Accuracy | 0.709 | **0.764** | +7.8 % |
| Precision | 0.625 | **0.722** | +15.5 % |
| ROC-AUC | 0.796 | **0.826** | +3.8 % |

Paramètres retenus : `n_estimators=300, max_depth=4, learning_rate=0.05, subsample=0.8, scale_pos_weight=1.5`

### ✅ Modèle retenu — Classification : XGBoost optimisé

`ia/models/xgboost_optimized_clf.joblib` — F1 = **0.667**, ROC-AUC = **0.826**

---

## 3. Régression — Prévision de la fréquentation

### Pourquoi le R² comme métrique principale ?

La variable `passengers` varie de 0 à 1 080 000 selon les pays. Le R² est indépendant
de cette échelle et s'interprète directement : R² = 0.99 signifie que le modèle explique
99 % de la variation observée entre les pays et les années.
Le MAE complète l'analyse en donnant une erreur concrète en milliers de passagers.

### Résultats

| Modèle | MAE | RMSE | **R²** ⭐ |
|---|:---:|:---:|:---:|
| **Ridge (base)** ✅ | **4 339** | **9 074** | **0.9962** |
| Ridge (optimisé) | 4 674 | 11 370 | 0.9940 |
| Random Forest | 4 966 | 26 039 | 0.9684 |
| XGBoost (optimisé) | 5 576 | 28 508 | 0.9621 |
| XGBoost (base) | 5 215 | 29 428 | 0.9596 |

### Analyse

- **Ridge baseline** est le meilleur modèle sur les trois métriques sans exception.
- **Ridge optimisé** : la recherche d'hyperparamètres a trouvé un alpha = 0.1, qui s'avère moins bon que l'alpha par défaut (1.0). L'optimisation a donc **dégradé** les performances — Ridge baseline reste la référence.
- **Random Forest et XGBoost** : bons R² (> 0.96) mais RMSE trois fois plus élevé que Ridge, révélant des erreurs importantes sur les grands pays (France, Allemagne). Les méthodes ensemblistes peinent à interpoler des séries temporelles très stables.
- **Pourquoi Ridge domine ?** La fréquentation ferroviaire d'une année à l'autre est quasi-linéaire : un pays avec 100 000 passagers en N-1 en aura probablement un nombre proche en N. Ridge capture exactement cette inertie.

> **⚠️ Point jury — R² élevé :** Un R² de 0.9962 est légitime ici. `passengers_lag1` (année N-1) est naturellement très corrélé à `passengers` (année N). Il ne s'agit pas d'un leakage car la valeur cible de l'année N n'est **jamais utilisée** comme feature.

### ✅ Modèle retenu — Régression : Ridge baseline

`ia/models/ridge_reg.joblib` — R² = **0.9962**, MAE = **4 339**

---

## 4. Synthèse

| Axe | Modèle final | Critère | Score |
|---|---|---|---|
| Classification (en_declin) | XGBoost optimisé | F1-Score | **0.667** |
| Régression (passengers) | Ridge baseline | R² | **0.9962** |

---

## 5. Limites

**Classification**
Le recall de 0.619 signifie que 38 % des pays réellement en déclin ne sont pas détectés.
Avec seulement 546 lignes, les marges d'amélioration sont limitées sans nouvelles données.

**Régression**
Le RMSE de 9 074 représente une erreur significative pour les petits pays
(médiane = 14 178 passagers). L'impact du COVID-19 en 2020 est un outlier
qui peut pénaliser les prédictions autour de cette période.

**Générales**
42 pays × 15 ans reste un dataset modeste. Des données trimestrielles
ou mensuelles permettraient d'améliorer la généralisation des deux modèles.

---

## 6. Livrables

| Livrable | Chemin | Statut |
|---|---|---|
| Rapport d'évaluation | `docs/rapport_evaluation.md` | ✅ |
| CSV classification | `ia/reports/comparison_classification.csv` | ✅ |
| CSV régression | `ia/reports/comparison_regression.csv` | ✅ |
| Modèle clf final | `ia/models/xgboost_optimized_clf.joblib` | ✅ |
| Modèle reg final | `ia/models/ridge_reg.joblib` | ✅ |
| Visualisations | `docs/fig_*.png` | ❌ Phase 5 |