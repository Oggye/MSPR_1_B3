# Documentation des Tests
 
## Vue d'ensemble
 
| Catégorie | Fichiers | Tests | Durée | Résultat |
|---|---|---|---|---|
| Tests Unitaires | 6 | 23 | — | ✅ 23/23 |
| Tests d'Intégration | 11 | 37 | 1.80s | ✅ 37/37 |
| **Total** | **17** | **60** | | **✅ 60/60** |
 
> Environnement : Python 3.12.1 · pytest 7.4.3 · Windows
 
---
 
## 1. Tests Unitaires
 
### Structure
 
```
test/
└── unit/
    ├── test_analysis_unit.py
    ├── test_dashboard_unit.py
    ├── test_internal_unit.py
    ├── test_metadata_unit.py
    ├── test_night_trains_unit.py
    └── test_statistics_unit.py
```
 
| Fichier | Tests | Fonctions couvertes |
|---|---|---|
| `test_analysis_unit.py` | 3 | `compare_train_types`, `get_policy_recommendations`, cas liste vide |
| `test_dashboard_unit.py` | 2 | Agrégation des KPIs, gestion base vide |
| `test_internal_unit.py` | 6 | `read_json`, `scan_csv_dir`, `run_command`, `first_ok` |
| `test_metadata_unit.py` | 4 | `quality_report` (fichier présent, manquant, erreur), catalogue sources |
| `test_night_trains_unit.py` | 5 | `to_response` (train de nuit, de jour, valeurs nulles), `apply_pagination` |
| `test_statistics_unit.py` | 3 | Timeline, ranking CO2, ranking CO2 vide |
 
 
### Objectif
 
Vérifier chaque fonction **de manière isolée**, sans dépendance à des services externes.
 
**Ce qui est exclu :**
- ❌ Base de données PostgreSQL réelle
- ❌ FastAPI `TestClient`
- ❌ Appels HTTP
**Outils utilisés :**
- `pytest` — framework de tests
- `unittest.mock.MagicMock` — simulation des dépendances
- `SimpleNamespace` — simulation d'objets DB
- Appels directs aux fonctions des routers
### Résultat
 
```
✅ 23/23 tests passent — 100% de succès
```
 
---
 
## 2. Tests d'Intégration (API + DB)
 
### Structure
 
```
test/
└── integration/
    └── api_db/
        ├── conftest.py
        ├── test_analysis.py
        ├── test_countries.py
        ├── test_dashboard.py
        ├── test_geographic.py
        ├── test_internal.py
        ├── test_main.py
        ├── test_metadata.py
        ├── test_night_trains.py
        ├── test_operators.py
        ├── test_statistics.py
        └── test_validation.py
```
 
| Fichier | Endpoints couverts | Tests |
|---|---|---|
| `conftest.py` | Configuration partagée (fixtures) | — |
| `test_analysis.py` | `/api/analysis/*` | 2 |
| `test_countries.py` | `/api/countries/*` | 5 |
| `test_dashboard.py` | `/api/dashboard/*` | 2 |
| `test_geographic.py` | `/api/geographic/*` | 1 |
| `test_internal.py` | Endpoints internes | 3 |
| `test_main.py` | Endpoints de base | 4 |
| `test_metadata.py` | `/api/metadata/*` | 2 |
| `test_night_trains.py` | `/api/night-trains/*` | 8 |
| `test_operators.py` | `/api/operators/*` | 3 |
| `test_statistics.py` | `/api/statistics/*` | 2 |
| `test_validation.py` | Validation des réponses | 5 |
 
### Configuration partagée (`conftest.py`)
 
| Élément | Valeur |
|---|---|
| Base de données | SQLite en mémoire (isolation totale) |
| Fixtures | `client`, `db_session`, `sample_data` |
| Modèles | Tous les modèles SQLAlchemy importés |
 
Chaque test s'exécute sur une base de données fraîche et indépendante.
 
### Résultat
 
```
✅ 37/37 tests passent — 100% de succès — 1.80s
```
 
- **Couverture** : tous les endpoints principaux testés
- **Isolation** : chaque test utilise sa propre base de données
- **Maintenabilité** : structure modulaire, facile à étendre
---
 
## 3. Méthodologie
 
```
1. Rédaction des tests basée sur la documentation API
        ↓
2. Exécution et identification des erreurs
        ↓
3. Analyse des vraies réponses API pour ajuster les assertions
        ↓
4. Ajustement des données de test pour couvrir tous les cas
        ↓
5. Vérification finale — exécution complète de la suite
```
 
---
 
## 4. Lancer les tests
 
### Prérequis
 
```bash
pip install pytest
```
 
### Exécution
 
Depuis le répertoire `platform/server` :
 
```bash
# Tous les tests
pytest -v
 
# Tests unitaires uniquement
pytest test/unit -v
 
# Tests d'intégration uniquement
pytest test/integration -v
```
