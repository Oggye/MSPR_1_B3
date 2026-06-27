# Rapport — Phases 10 & 11 : Prédiction & API REST

---

## Phase 10 — Script de prédiction (`predict.py`)

### Objectif

Créer un script autonome permettant d'utiliser les modèles entraînés pour produire des prédictions, sans passer par l'API. Ce script sert aussi de base directement réutilisée par l'API (Phase 11).

### Ce qui a été fait

Deux modèles finaux ont été sauvegardés au format `.joblib` :

- **XGBoost optimisé** → classification (déclin / croissance)
- **Ridge optimisé** → régression (volume de passagers)

Le script `predict.py` charge ces modèles avec un système de **cache mémoire** (`lru_cache`) : le premier appel charge les fichiers depuis le disque, les suivants sont instantanés. Un mécanisme de **fallback** est prévu : si le modèle optimisé est absent, il tente de charger le modèle de base.

La fonction principale `predict()` prend en entrée 8 paramètres (pays, année, émissions CO₂, lags passagers…) et retourne un dictionnaire avec la prédiction et son interprétation.

Le script est aussi utilisable directement en ligne de commande :

```bash
python -m ia.src.ml.predict --axis classification --country France --year 2024 \
  --co2_emissions 24800 --co2_per_passenger 1.75 --co2_lag1 25100 \
  --passengers_lag1 88000 --passengers_lag2 86500
```

### Résultats obtenus — France 2024

| Axe | Prédiction | Interprétation |
|-----|------------|----------------|
| Classification | 0 | En croissance (probabilité déclin : 2,9 %) |
| Régression | 114 583 | 114 583 milliers de passagers prévus |

### Difficultés rencontrées

- Les imports relatifs dans certains scripts causaient des erreurs lors du lancement en module (`python -m`). Corrigé en passant à `from .config import`.
- Vérification d'existence des fichiers `.joblib` ajoutée pour produire des messages d'erreur lisibles.

---

## Phase 11 — API REST avec FastAPI

### Objectif

Exposer les deux modèles via une API REST consommable par n'importe quel client HTTP (front-end, partenaires, outils de monitoring).

### Ce qui a été fait

L'API est construite avec **FastAPI** et réutilise directement la fonction `predict()` de la Phase 10 — aucune duplication de code.

Elle expose quatre routes :

| Route | Méthode | Rôle |
|-------|---------|------|
| `/` | GET | Vérification que l'API est active |
| `/health` | GET | Health check |
| `/predict/classification` | POST | Prédiction de déclin ferroviaire |
| `/predict/regression` | POST | Prévision du volume de passagers |

Les deux routes `/predict` acceptent le même schéma JSON validé automatiquement par **Pydantic** (erreur 422 si les données sont mal formées).

La version améliorée du router (`predict.py`) enrichit les réponses avec :

- un **niveau de risque** (Faible / Modéré / Élevé / Critique)
- un **score de confiance** du modèle
- des **recommandations métier** adaptées au résultat
- les **variables les plus influentes** sur la prédiction
- des **avertissements** si le pays est inconnu du modèle ou si la prédiction est hors plage réaliste
- le **temps d'inférence** en millisecondes

Un **avertissement automatique** est émis si le pays soumis n'a pas été vu lors de l'entraînement (41 pays européens connus).

FastAPI génère automatiquement une **documentation Swagger** accessible sur `http://127.0.0.1:8000/docs`, permettant de tester les routes directement depuis le navigateur.

### Lancement

```bash
python -m uvicorn ia.src.ml.api:app --reload
```

### Métriques de monitoring identifiées

| Métrique | Description |
|----------|-------------|
| Latence | Temps de réponse moyen (ms) |
| Taux d'erreur | Proportion de requêtes 4xx / 5xx |
| Distribution des prédictions | Évolution du ratio déclin / croissance dans le temps |
| Data drift | Dérive des valeurs d'entrée vs données d'entraînement |
| Model drift | Dégradation des performances sur de nouvelles données réelles |

### Difficultés rencontrées

- **Conflit de versions Python** : `uvicorn` installé globalement utilisait un environnement différent de celui contenant `xgboost`. Résolu en utilisant systématiquement `python -m uvicorn`.
- **Déploiement cloud** : le déploiement sur Railway a échoué à cause de dépendances lourdes (`geopandas`, `psycopg2`) dans le `requirements.txt` principal. L'API fonctionne correctement en local.

---

## Livrables produits

| Livrable | Chemin | Statut |
|----------|--------|--------|
| Script de prédiction | `ia/src/ml/predict.py` | ✅ |
| Modèle classification | `ia/models/xgboost_optimized_clf.joblib` | ✅ |
| Modèle régression | `ia/models/ridge_optimized_reg.joblib` | ✅ |
| API FastAPI | `ia/src/ml/api.py` | ✅ |
| Router enrichi | `platform/server/app/routers/predict.py` | ✅ |
| Documentation Swagger | `http://127.0.0.1:8000/docs` | ✅ (en local) |