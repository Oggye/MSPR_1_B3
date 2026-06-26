# Phase 11 — API FastAPI

---

## 1. Contexte

### Objectif de l'étape

Exposer les deux modèles de prédiction via une API REST construite avec FastAPI, afin de permettre une intégration applicative des prédictions ObRail Europe.

### Position dans le projet

Cette phase succède directement au script de prédiction (Phase 10). Elle constitue la couche d'exposition des modèles ML, consommable par n'importe quel client HTTP (front-end, partenaires, outils de monitoring).

### Lien avec le cahier des charges

Le cahier des charges ObRail impose de :
- **Fournir un prototype d'API REST** (FastAPI / Flask) exposant une route `/predict` ;
- **Intégrer l'API dans l'application** ou à défaut documenter cette intégration ;
- **Identifier les métriques pertinentes** pour le monitoring du modèle en production.

---

## 2. Travaux réalisés

### Script principal

**`ia/src/ml/api.py`** — API FastAPI exposant les routes de prédiction.

### Dépendances

```
fastapi
uvicorn
scikit-learn>=1.3.0
xgboost>=2.0.0
joblib>=1.2.0
pandas>=1.5.0
numpy>=1.24.0
```

---

## 3. Fonctionnement

### 3.1 Structure de l'API

L'API est construite avec FastAPI et expose quatre routes :

| Route | Méthode | Description |
|-------|---------|-------------|
| `/` | GET | Route racine — vérification que l'API est active |
| `/health` | GET | Health check — statut de l'API |
| `/predict/classification` | POST | Prédiction de déclin ferroviaire |
| `/predict/regression` | POST | Prévision du volume de passagers |

### 3.2 Schéma d'entrée

Les deux routes `/predict` acceptent le même schéma JSON défini via Pydantic :

```python
class PredictionInput(BaseModel):
    country: str
    year: int
    co2_emissions: float
    co2_per_passenger: float
    co2_lag1: float
    passengers_lag1: float
    passengers_lag2: float
```

La validation des types est automatique grâce à Pydantic — une requête mal formée retourne une erreur 422 avec un message explicite.

### 3.3 Réutilisation de predict.py

L'API réutilise directement la fonction `predict()` du script Phase 10 :

```python
from ia.src.ml.predict import predict

@app.post("/predict/classification")
def predict_classification(data: PredictionInput):
    result = predict(axis="classification", **data.model_dump())
    return result
```

Cette architecture évite toute duplication de code et garantit que la logique de prédiction est identique en CLI et en API.

### 3.4 Documentation automatique

FastAPI génère automatiquement une documentation interactive Swagger UI accessible à :

```
http://127.0.0.1:8000/docs
```

Cette interface permet de tester les routes directement depuis le navigateur sans outil externe.

---

## 4. Résultats obtenus

### Test route `/predict/classification`

**Requête :**
```json
{
  "country": "France",
  "year": 2024,
  "co2_emissions": 24800,
  "co2_per_passenger": 1.75,
  "co2_lag1": 25100,
  "passengers_lag1": 88000,
  "passengers_lag2": 86500
}
```

**Réponse (HTTP 200) :**
```json
{
  "axis": "classification",
  "country": "France",
  "year": 2024,
  "prediction": 0,
  "label": "En croissance",
  "probability": 0.0287
}
```

### Test route `/predict/regression`

**Réponse (HTTP 200) :**
```json
{
  "axis": "regression",
  "country": "France",
  "year": 2024,
  "prediction": 114583.42,
  "label": "114,583 milliers de passagers prévus"
}
```

---

## 5. Métriques de monitoring identifiées

Dans le cadre d'une mise en production, les métriques suivantes seraient pertinentes pour le monitoring du modèle :

| Métrique | Description |
|----------|-------------|
| **Latence des requêtes** | Temps de réponse moyen de l'API (ms) |
| **Taux d'erreur** | Proportion de requêtes en erreur (4xx, 5xx) |
| **Distribution des prédictions** | Proportion de prédictions "En déclin" vs "En croissance" dans le temps |
| **Data drift** | Évolution de la distribution des features en entrée par rapport aux données d'entraînement |
| **Model drift** | Dégradation des métriques du modèle sur de nouvelles données réelles |
| **Nombre de requêtes** | Volume de requêtes par route et par période |

---

## 6. Difficultés rencontrées

- **Conflit de versions Python** : `uvicorn` installé globalement utilisait un Python différent de celui où `xgboost` était installé, provoquant des erreurs `No module named 'xgboost'` à l'exécution de l'API. Résolution : utilisation systématique de `python -m uvicorn` pour garantir le bon environnement Python.
- **Déploiement cloud** : le déploiement sur Railway a échoué en raison de dépendances lourdes (`geopandas`, `psycopg2`) présentes dans le `requirements.txt` principal. L'API fonctionne correctement en local.

---

## 7. Correctifs appliqués

- Remplacement de `uvicorn ia.src.ml.api:app` par `python -m uvicorn ia.src.ml.api:app` pour résoudre le conflit de versions.
- Gestion des exceptions avec `HTTPException(status_code=500)` pour retourner des messages d'erreur lisibles côté client.

---

## 8. Impact sur la suite du projet

- L'API constitue la couche d'intégration principale entre les modèles ML et les utilisateurs finaux (équipe data ObRail, partenaires).
- La documentation Swagger générée automatiquement permet une prise en main immédiate par des équipes non-techniques.
- Les métriques de monitoring identifiées constituent la base d'un système de supervision MLOps à mettre en place en phase de production.

---

## 9. Livrables produits

| Livrable | Chemin | Statut |
|----------|--------|--------|
| API FastAPI | `ia/src/ml/api.py` | ✅ Produit |
| Documentation Swagger | `http://127.0.0.1:8000/docs` | ✅ Accessible en local |
| Route classification | `/predict/classification` | ✅ Fonctionnelle |
| Route régression | `/predict/regression` | ✅ Fonctionnelle |
| Route health check | `/health` | ✅ Fonctionnelle |

### Commande de lancement

```bash
python -m uvicorn ia.src.ml.api:app --reload
```

L'API est alors accessible sur `http://127.0.0.1:8000`.