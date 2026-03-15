## **API ENDPOINTS OBLIGATOIRES**

### **1. ENDPOINTS DE CONSULTATION DES DONNÉES**

#### **A. Données statistiques par pays**
- **GET** `/api/countries/stats`
  - Retourne toutes les statistiques par pays (passagers, émissions CO2)
  - Doit permettre le filtrage par année, pays, seuil d'émissions
  - **Tables utilisées**: `facts_country_stats`, `dim_countries`, `dim_years`
  - **Données**: passengers, co2_per_passenger, country_code, year

#### **B. Trains de nuit**
- **GET** `/api/night-trains`
  - Liste tous les trains de nuit avec leurs caractéristiques
  - Filtres par pays, opérateur, année
  - **Tables utilisées**: `facts_night_trains`, `dim_countries`, `dim_operators`, `dim_years`
  - **Données**: night_train, country_name, operator_name, year

#### **C. Métriques dashboard**
- **GET** `/api/dashboard/metrics`
  - Données agrégées pour le tableau de bord
  - **Vue utilisée**: `dashboard_metrics`

### **2. ENDPOINTS D'ANALYSE COMPARATIVE**

#### **D. Comparaison trains jour/nuit**
- **GET** `/api/analysis/train-types-comparison`
  - Compare les indicateurs par type de train (à créer via jointures)
  - Doit montrer l'impact environnemental comparé
  - **Tables**: `facts_night_trains` + données statistiques extrapolées

#### **E. Impact CO2 par pays**
- **GET** `/api/statistics/co2-ranking`
  - Analyse l'impact CO2 par passager par pays
  - Classement des pays les plus/peu performants
  - **Vue utilisée**: `dashboard_metrics`

### **3. ENDPOINTS DE RECHERCHE ET FILTRAGE**

#### **F. Recherche par opérateur**
- **GET** `/api/operators/{operator_id}/stats`
  - Statistiques détaillées par opérateur ferroviaire
  - **Tables**: `facts_night_trains`, `dim_operators`, `dim_countries`

#### **G. Filtrage temporel**
- **GET** `/api/statistics/timeline`
  - Évolution des indicateurs dans le temps (2010-2024)
  - Permet de voir les tendances
  - **Tables**: `facts_country_stats`, `facts_night_trains`, `dim_years`

### **4. ENDPOINTS DE MÉTADONNÉES**

#### **H. Métadonnées et qualité**
- **GET** `/api/metadata/quality`
  - Retourne le rapport de qualité des données
  - **Source**: fichier `quality_reports.json`
  - Montre la traçabilité ETL

#### **I. Sources de données**
- **GET** `/api/metadata/sources`
  - Liste et description des sources de données utilisées
  - Justification des choix (conforme au cahier des charges)

### **5. ENDPOINTS POUR TABLEAU DE BORD**

#### **J. Indicateurs clés (KPIs)**
- **GET** `/api/dashboard/kpis`
  - Retourne les KPI principaux pour le dashboard
  - **Tables**: `facts_night_trains`, `facts_country_stats`, `dim_countries`,`dim_operators`, `dim_years`

#### **K. Visualisation géographique**
- **GET** `/api/geographic/coverage`
  - Données pour carte interactive (pays couverts, densité ferroviaire)
  - **Tables**: `facts_night_trains`, `dim_countries`

## **ENDPOINTS AVANCÉS**

#### **L. Recommandations politiques**
- **GET** `/api/analysis/policy-recommendations`
  - Suggestions basées sur les données (pays à améliorer, bonnes pratiques)
  - **Tables**: `facts_country_stats`,`facts_night_trains`, `dim_countries`

### **8. DOCUMENTATION AUTOMATIQUE**

#### **M. Documentation interactive**
- **GET** `/api/docs`
  - Documentation Swagger/OpenAPI automatique
  - Exemples de requêtes

## **TABLES ET DONNÉES PAR ENDPOINT**

### **Table `dim_countries`** (48 pays dont 1 UNKNOWN)
- Utilisée par: Tous les endpoints avec filtrage géographique
- Champs: country_id, country_code, country_name

### **Table `dim_years`** (15 années: 2010-2024)
- Utilisée par: Analyse temporelle, filtres chronologiques
- Champs: year_id, year, is_after_2010

### **Table `dim_operators`** (65 opérateurs)
- Utilisée par: Analyse par opérateur, trains de nuit
- Champs: operator_id, operator_name

### **Table `facts_country_stats`** (701 enregistrements)
- Utilisée par: Analyse CO2, statistiques, dashboard
- Champs: stat_id, country_id, year_id, passengers, co2_emissions, co2_per_passenger

### **Table `facts_night_trains`** (2057 enregistrements)
- Utilisée par: Trains de nuit, comparaison modale
- Champs: fact_id, route_id, night_train, country_id, year_id, operator_id

### **Vue `dashboard_metrics`** (47 enregistrements)
- Utilisée par: Dashboard, indicateurs synthétiques
- Champs: country_name, country_code, avg_passengers, avg_co2_emissions, avg_co2_per_passenger

## Structure du backend API ObRail
```
└── server/
    ├── DocAPI.md
    ├── Dockerfile
    ├── requirements.txt
    └── app/
        ├── __init__.py
        ├── main.py              # Point d'entrée principal
        ├── models.py            # Modèles SQLAlchemy
        ├── database.py          # Configuration DB
        ├── dependencies.py      # Dépendances (sessions DB, etc.)
        ├── routers/             # Dossier des routeurs API
        │   ├── __init__.py
        │   ├── countries.py     # Endpoints pays
        │   ├── night_trains.py  # Endpoints trains de nuit
        │   ├── statistics.py    # Endpoints statistiques
        │   ├── dashboard.py     # Endpoints dashboard
        │   ├── analysis.py      # Endpoints analyse avancée
        │   ├── operators.py     # Endpoints opérateurs
        │   └── metadata.py      # Endpoints métadonnées
        ├── schemas/             # Schémas Pydantic
        │   ├── __init__.py
        │   ├── base.py
        │   ├── countries.py
        │   ├── operators.py
        │   ├── trains.py
        │   └── statistics.py
        └── reports/             # Dossier des rapports de qualité ETL
            └── quality_reports.json    # Rapport généré par le pipeline ETL
```