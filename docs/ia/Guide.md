# GUIDE ML — MSPR ObRail Europe
### Prévision fréquentation + Détection déclin ferroviaire

---

## PHASE 0 — INCIDENT DATA LEAKAGE ✅ À documenter

Compétence clé : **Résoudre les incidents techniques**

Créer `docs/incident_data_leakage.md` :

```
1. Symptôme  → accuracy = 1.0 sur tous les modèles
2. Cause     → cible construite depuis les features (distance_km, duration_min)
3. Tentatives → cible pays (42 règles mémorisées) → cible vitesse (leakage indirect)
4. Diagnostic → facts_night_trains : aucune variable indépendante disponible
5. Solution   → pivot vers facts_country_stats + variables lag temporelles
6. Validation → cible en_declin ne dépend d'aucune feature d'entraînement
```

> ⭐ Préparer 3 slides sur cet incident pour la soutenance — c'est votre argument différenciant.

Livrables
```
docs/incident_data_leakage.md
```

---

## PHASE 1 — CONSTRUCTION DU DATASET ✅ Fait

`build_dataset.py` déjà opérationnel.

Rappel de ce qui est produit :

Dataset régression (`regression_dataset.csv`)
```
546 lignes | cible : passengers
Features : year, co2_emissions, co2_per_passenger,
           co2_lag1, passengers_lag1, passengers_lag2, country_name
```

Dataset classification (`classification_dataset.csv`)
```
546 lignes | cible : en_declin (0/1) — 61.9% / 38.1%
Features : identiques, sans passengers
```

Lancement :
```
python run_pipeline.py
```

Livrables
```
data/ml/regression_dataset.csv
data/ml/classification_dataset.csv
```

---

## PHASE 2 — ANALYSE EXPLORATOIRE ✅ Fait

Peut être faite en parallèle avec la veille.

Créer `notebooks/01_eda.ipynb`

1. Charger les datasets
```python
df_reg = pd.read_csv(REGRESSION_DATASET_PATH)
df_clf = pd.read_csv(CLASSIF_DATASET_PATH)
```

2. Vérifier qualité
```
Valeurs manquantes    → df.isna().sum()
Doublons              → df.duplicated().sum()
Statistiques          → df.describe()
```

3. Visualisations obligatoires

```
Distribution passengers       → histogramme + version log1p (asymétrie forte)
Évolution temporelle top pays → courbes year vs passengers (top 8)
Déséquilibre cible clf        → barplot en_declin 0/1
Matrice de corrélation        → heatmap features numériques
```

4. Tableau des variables → `docs/variables.md`

```
variable           | type  | rôle
year               | int   | Feature temporelle
co2_emissions      | float | Indicateur environnemental
co2_per_passenger  | float | Efficacité carbone (année N)
co2_lag1           | float | Efficacité carbone (année N-1)
passengers_lag1    | float | Fréquentation N-1
passengers_lag2    | float | Fréquentation N-2
country_name       | str   | Contexte pays (OHE)
passengers         | float | 🎯 Cible régression
en_declin          | int   | 🎯 Cible classification
```

Livrables
```
notebooks/01_eda.ipynb
docs/variables.md
docs/fig_distribution_passengers.png
docs/fig_evolution_temporelle.png
docs/fig_correlation_matrix.png
```

---

## PHASE 3 — PRÉPARATION & SPLIT ✅ Fait

`train_utils.py` déjà opérationnel.

Rappel de l'architecture :

Preprocessing
```
StandardScaler()   → features numériques (year, co2, lag…)
OneHotEncoder()    → country_name
ColumnTransformer  → combine les deux
```

Split
```
Régression     → train_test_split 80/20, random_state=42
Classification → train_test_split 80/20, stratify=y (équilibre classes)
```

> ⚠️ À mentionner en soutenance : un `GroupShuffleSplit(groups=country_id)` serait
> idéal pour éviter qu'un même pays apparaisse en train ET en test.
> Justifier le choix retenu (simplicité, dataset de 546 lignes).

Livrables
```
ia/src/ml/models/train_utils.py   (déjà fait)
```

---

## PHASE 4 — MODÈLES CANDIDATS ✅ Fait

`run_training.py` déjà opérationnel.

Lancement :
```
python -m ia.src.ml.run_training
```

Modèles classification entraînés
```
Logistic Regression   → baseline linéaire, interprétable
Random Forest         → robuste, gère bien hétérogénéité des pays
XGBoost               → meilleure performance attendue sur tabulaire
MLP                   → réseau de neurones, comparaison deep vs boosting
```

Modèles régression entraînés
```
Ridge             → baseline linéaire régularisé
Random Forest     → non-linéaire, robuste aux outliers
XGBoost           → gradient boosting, attendu meilleur R²
```

Chaque entraînement produit :
```
models/{nom}_{axe}.joblib
models/{nom}_{axe}_metrics.json
```

Livrables
```
ia/models/*.joblib
ia/models/*_metrics.json
```

---

## PHASE 5 — ÉVALUATION & COMPARAISON ✅ Fait (à compléter)

`evaluate_model.py` génère les tableaux comparatifs.

Métriques classification
```
Accuracy   → taux global
Precision  → faux positifs (pays classés en déclin à tort)
Recall     → faux négatifs (pays en déclin non détectés)
F1-Score   → 🎯 critère principal (dataset légèrement déséquilibré)
ROC-AUC    → performance globale du classifieur
```

Métriques régression
```
MAE   → erreur absolue moyenne (en milliers de passagers)
RMSE  → sensible aux gros écarts
R²    → 🎯 critère principal (part de variance expliquée)
```

Visualisations à produire dans `notebooks/02_evaluation.ipynb`
```
Matrices de confusion     → 4 modèles côte à côte
Courbes ROC               → toutes sur le même graphe
Actual vs Predicted       → scatter plot pour les 3 modèles régression
```

Livrables
```
ia/reports/comparison_classification.csv
ia/reports/comparison_regression.csv
notebooks/02_evaluation.ipynb
docs/fig_confusion_matrices.png
docs/fig_roc_curves.png
docs/fig_actual_vs_predicted.png
```

---

## PHASE 6 — OPTIMISATION ✅ Fait

Peut être faite en parallèle.

Créer `ia/src/ml/models/optimize_xgboost.py`

Objectif : améliorer XGBoost (meilleur candidat) sur les deux axes.

Paramètres à explorer
```
n_estimators    : [50, 100, 200, 300]
max_depth       : [2, 3, 4, 5]
learning_rate   : [0.01, 0.05, 0.1, 0.2]
subsample       : [0.7, 0.8, 1.0]
scale_pos_weight: [1, 1.5, 2]     (classification uniquement)
```

Méthode
```python
RandomizedSearchCV(estimator, param_distributions, n_iter=30,
                   scoring="f1",   # ou "r2" pour régression
                   cv=5, random_state=42)
```

Comparer avant / après
```
Classification XGBoost — Avant : F1 = ?  |  Après : F1 = ?
Régression XGBoost     — Avant : R² = ?  |  Après : R² = ?
```

Livrables
```
ia/src/ml/models/optimize_xgboost.py
ia/models/xgboost_clf_optimized.joblib
ia/models/xgboost_reg_optimized.joblib
```

---

## PHASE 7 — SÉLECTION DU MODÈLE FINAL ✅ Fait

Produire les tableaux de sélection dans `docs/rapport_evaluation.md`.

Tableau classification
```
Modèle                | Accuracy | F1   | ROC-AUC
Logistic Regression   |          |      |
Random Forest         |          |      |
XGBoost               |          |      |
XGBoost (optimisé) ✅ |          |      |
MLP                   |          |      |
```

Tableau régression
```
Modèle                | MAE | RMSE | R²
Ridge                 |     |      |
Random Forest         |     |      |
XGBoost               |     |      |
XGBoost (optimisé) ✅ |     |      |
```

Justification à rédiger
```
Pourquoi F1 et non accuracy (classification)
Pourquoi R² et non RMSE seul (régression)
Compromis performance / explicabilité / temps d'exécution
```

Livrables
```
docs/rapport_evaluation.md
```

---

## PHASE 8 — EXPLICABILITÉ IA ✅ Fait

Créer `notebooks/03_explicabilite.ipynb`

Feature Importance
```python
model.feature_importances_   # XGBoost natif
→ barplot horizontal, tri par importance décroissante
```

SHAP
```python
shap.TreeExplainer(model)
shap.summary_plot(shap_values, X_test)   # vision globale
shap.force_plot(...)                      # explication individuelle
```

Variables attendues comme importantes
```
passengers_lag1    → dynamique récente
passengers_lag2    → tendance 2 ans
co2_per_passenger  → indicateur d'efficacité
year               → tendance temporelle globale
```

Livrables
```
notebooks/03_explicabilite.ipynb
docs/fig_feature_importance_clf.png
docs/fig_feature_importance_reg.png
docs/fig_shap_clf.png
docs/fig_shap_reg.png
```

---

## PHASE 9 — BENCHMARK CLOUD ✅ À Mettre à jour

Peut être réalisé par une autre personne.

Comparer 3 services
```
Azure Machine Learning
AWS SageMaker AutoPilot
Google Vertex AI AutoML
```

Critères du tableau
```
Critère              | Azure | AWS | Vertex | Scikit-learn (retenu)
Prix / heure         |       |     |        | 0€
Données minimales    |       |     |        | Aucun minimum
Notre dataset (546)  |       |     |        | ✅ Adapté
Explicabilité        |       |     |        | SHAP natif
RGPD / local         |       |     |        | ✅ 100% local
Reproductibilité     |       |     |        | ✅ seeds + pipelines
```

Justification à rédiger : pourquoi scikit-learn/XGBoost local est retenu
```
546 lignes → en dessous des seuils recommandés Azure et Vertex
Données sensibles → aucun envoi vers le cloud (RGPD)
Reproductibilité totale → seeds, pipelines, GroupShuffleSplit
```

Livrables
```
docs/benchmark_cloud.md
```

---

## PHASE 10 — SAUVEGARDE & SCRIPT PREDICT ✅ Fait

La sauvegarde est déjà faite via `save_model_and_metrics()`.

Créer `predict.py` à la racine :

Entrée
```json
{
  "year": 2025,
  "co2_emissions": 2500,
  "co2_per_passenger": 0.019,
  "co2_lag1": 0.020,
  "passengers_lag1": 118000,
  "passengers_lag2": 115000,
  "country_name": "France"
}
```

Sortie
```json
{
  "passengers_pred_k": 121450.5,
  "en_declin": 0,
  "en_declin_label": "En croissance",
  "en_declin_proba": 0.1823
}
```

Livrables
```
predict.py
ia/models/model_metadata.json   (date, features, split strategy)
```

---

## PHASE 11 — API FASTAPI ✅ Fait

Créer `api/main.py`

Routes
```
GET  /health    → statut de l'API
POST /predict   → prédiction depuis JSON
GET  /metrics   → KPIs monitoring
```

Swagger automatique → `http://localhost:8000/docs`

Lancement
```
uvicorn api.main:app --reload
```

Livrables
```
api/main.py
```

---

## PHASE 12 — MONITORING À faire

Ajouter dans `api/main.py`

KPIs métier
```
% pays en déclin détectés
% pays en croissance
Confiance moyenne (predict_proba)
```

KPIs techniques
```
Temps d'inférence moyen (ms)
Taux d'erreurs API
```

Logs
```python
logging.info(f"year={year} | pred={pred:.0f} | declin={declin} | time={ms:.1f}ms")
→ logs/predictions.log
```

Livrables
```
logs/predictions.log
GET /metrics endpoint
```

---

## PHASE 13 — TESTS À faire

Créer `tests/test_predict.py`

Tester
```
Type de sortie régression      → float positif
Sortie classification binaire  → 0 ou 1
Probabilité dans [0, 1]        → sum(proba) ≈ 1.0
Nombre de features             → exactement 7 (6 num + country_name)
```

Lancement
```
pytest tests/ -v
```

Livrables
```
tests/test_predict.py
```

---

## PHASE 14 — CI/CD À faire (parallèle)

Créer `.github/workflows/ci.yml`

Pipeline
```
push sur main / develop
  → pip install -r requirements.txt
  → pytest tests/ -v
  → flake8 src/ api/ predict.py
```

Livrables
```
.github/workflows/ci.yml
```

---

## PHASE 15 — DOC RÉENTRAÎNEMENT À faire

Créer `docs/retraining.md`

Étapes
```
1. Mettre à jour facts_country_stats (nouvelles données Eurostat)
2. Relancer build_dataset.py → nouveaux CSV ML
3. Relancer run_training.py  → nouveaux modèles
4. Valider pytest            → R² et F1 ne baissent pas
5. Remplacer les .joblib en production
6. Redémarrer l'API
```

Déclencheurs
```
Annuel → nouvelles données Eurostat (Q1)
Alerte → confiance moyenne < 60% sur /metrics
```

Livrables
```
docs/retraining.md
```

---

## PHASE 16 — VEILLE TECHNIQUE À faire (dès J1, continu)

Créer `docs/veille.md`

Axe algorithmes
```
XGBoost vs LightGBM sur petits datasets tabulaires
Darts / Nixtla → bibliothèques séries temporelles (pertinent pour nos lag)
SHAP → standard explicabilité IA
```

Axe réglementaire
```
RGPD        → données agrégées par pays, aucune donnée personnelle
AI Act 2024 → nos modèles = risque minimal → transparence + doc obligatoires
```

Axe sécurité
```
OWASP API  → validation des inputs (Pydantic ✅), pas d'exposition d'IDs
Model Poisoning → données Eurostat falsifiées → vérification plausibilité
```

Livrables
```
docs/veille.md
```

---

## PHASE 17 — RAPPORT & SOUTENANCE À faire

Structure rapport
```
1. Contexte ObRail — mission, partenaires, Green Deal
2. Architecture warehouse — ETL, schéma des tables
3. ⭐ Incident data leakage — diagnostic, tentatives, résolution
4. Sujet ML retenu — justification, lien cahier des charges
5. Préparation des données — features, split, preprocessing
6. Modèles candidats — description + justification de chaque algo
7. Benchmark cloud — tableau + justification choix local
8. Entraînement & optimisation — résultats avant/après
9. Sélection finale — tableaux, critères, justification
10. Explicabilité SHAP — interprétation pour ObRail
11. API & monitoring — routes, métriques, logs
12. Tests & CI/CD
13. Veille technique
14. Limites & perspectives
```

Livrables
```
docs/rapport_technique.pdf
support_soutenance.pptx
```

---

## RÉCAPITULATIF DES LIVRABLES

```
✅ Fait          → Phases 1, 3, 4
⚠️ À compléter  → Phases 5 (visualisations)
❌ À faire       → Phases 0, 2, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17
```

Structure projet finale
```
ia/
├── src/ml/
│   ├── build_dataset.py        ✅
│   ├── config.py               ✅
│   ├── run_pipeline.py         ✅
│   ├── run_training.py         ✅
│   ├── evaluate_model.py       ✅
│   └── models/
│       ├── train_utils.py      ✅
│       ├── train_logistic.py   ✅
│       ├── train_mlp.py        ✅
│       ├── train_random_forest.py ✅
│       ├── train_ridge.py      ✅
│       ├── train_xgboost.py    ✅
│       └── optimize_xgboost.py ✅
├── models/                     ✅ (produit au run)
└── reports/                    ✅ (produit au run)
data/ml/                        ✅
api/main.py                     ❌
predict.py                      ❌
tests/test_predict.py           ❌
notebooks/
├── 01_eda.ipynb                ✅
├── 02_evaluation.ipynb         ✅
└── 03_explicabilite.ipynb      ❌
docs/
├── incident_data_leakage.md    ✅ ⭐
├── variables.md                ✅
├── benchmark_cloud.md          ❌
├── rapport_evaluation.md       ✅
├── veille.md                   ❌
└── retraining.md               ❌
.github/workflows/ci.yml        ❌
requirements.txt                ✅
```
