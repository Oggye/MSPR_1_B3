## **API ENDPOINTS OBLIGATOIRES**

### **1. ENDPOINTS DE CONSULTATION DES DONNÉES**

#### **A. Données statistiques par pays**
- **GET** `/api/countries/stats`
  - Retourne toutes les statistiques par pays (passagers, émissions CO2)
  - Doit permettre le filtrage par année, pays, seuil d'émissions
  - **Tables utilisées**: `facts_country_stats`, `dim_countries`, `dim_years`
  - **Données**: passengers, co2_emissions, co2_per_passenger, country_name, year

#### **B. Trains de nuit**
- **GET** `/api/night-trains`
  - Liste tous les trains de nuit avec leurs caractéristiques
  - Filtres par pays, opérateur, année
  - **Tables utilisées**: `facts_night_trains`, `dim_countries`, `dim_operators`, `dim_years`
  - **Données**: night_train, country_name, operator_name, year

#### **C. Métriques dashboard**
- **GET** `/api/dashboard/metrics`
  - Données agrégées pour le tableau de bord
  - **Table utilisée**: `dashboard_metrics` (vue SQL)
  - **Données**: country_name, avg_passengers, avg_co2_emissions, avg_co2_per_passenger

### **2. ENDPOINTS D'ANALYSE COMPARATIVE**

#### **D. Comparaison trains jour/nuit**
- **GET** `/api/comparison/train-types`
  - Compare les indicateurs par type de train (à créer via jointures)
  - Doit montrer l'impact environnemental comparé
  - **Tables**: `facts_night_trains` + données statistiques extrapolées

#### **E. Impact CO2 par pays**
- **GET** `/api/analysis/co2-impact`
  - Analyse l'impact CO2 par passager par pays
  - Classement des pays les plus/peu performants
  - **Tables**: `facts_country_stats`, `dim_countries`

### **3. ENDPOINTS DE RECHERCHE ET FILTRAGE**

#### **F. Recherche par opérateur**
- **GET** `/api/operators/{operator_id}/stats`
  - Statistiques détaillées par opérateur ferroviaire
  - **Tables**: `facts_night_trains`, `dim_operators`, jointure avec statistiques

#### **G. Filtrage temporel**
- **GET** `/api/statistics/timeline`
  - Évolution des indicateurs dans le temps (2010-2024)
  - Permet de voir les tendances
  - **Tables**: `facts_country_stats`, `dim_years`

### **4. ENDPOINTS DE MÉTADONNÉES**

#### **H. Métadonnées et qualité**
- **GET** `/api/metadata/quality`
  - Retourne le rapport de qualité des données
  - **Source**: fichier `quality_reports.json` ou table dédiée
  - Montre la traçabilité ETL

#### **I. Sources de données**
- **GET** `/api/metadata/sources`
  - Liste et description des sources de données utilisées
  - Justification des choix (conforme au cahier des charges)

### **5. ENDPOINTS POUR TABLEAU DE BORD**

#### **J. Indicateurs clés (KPIs)**
- **GET** `/api/kpis/summary`
  - Retourne les KPI principaux pour le dashboard
  - Ex: nombre total de trains, pays couverts, réduction CO2 estimée

#### **K. Visualisation géographique**
- **GET** `/api/geographic/coverage`
  - Données pour carte interactive (pays couverts, densité ferroviaire)
  - **Tables**: `dim_countries` + statistiques agrégées

## **ENDPOINTS AVANCÉS (Points bonus)**

### **6. ANALYSE PRÉDICTIVE**

#### **L. Projections tendances**
- **GET** `/api/predictions/trends`
  - Projections simples basées sur données historiques
  - Montre la capacité à préparer les données pour l'IA

#### **M. Recommandations politiques**
- **GET** `/api/recommendations/policy`
  - Suggestions basées sur les données (pays à améliorer, bonnes pratiques)

### **7. EXPORT DE DONNÉES**

#### **N. Export formats multiples**
- **GET** `/api/export/{format}`
  - Export en CSV, JSON, Excel
  - Conforme aux besoins des institutions européennes

### **8. DOCUMENTATION AUTOMATIQUE**

#### **O. Documentation interactive**
- **GET** `/api/docs`
  - Documentation Swagger/OpenAPI automatique
  - Exemples de requêtes

## **TABLES ET DONNÉES PAR ENDPOINT**

### **Table `dim_countries`** (48 pays)
- Utilisée par: Tous les endpoints avec filtrage géographique
- Champs: country_id, country_code, country_name

### **Table `dim_years`** (15 années: 2010-2024)
- Utilisée par: Analyse temporelle, filtres chronologiques
- Champs: year_id, year, is_after_2010

### **Table `dim_operators`** (37 opérateurs)
- Utilisée par: Analyse par opérateur, trains de nuit
- Champs: operator_id, operator_name

### **Table `facts_country_stats`** (611 enregistrements)
- Utilisée par: Analyse CO2, statistiques, dashboard
- Champs: stat_id, country_id, year_id, passengers, co2_emissions, co2_per_passenger

### **Table `facts_night_trains`** (196 enregistrements)
- Utilisée par: Trains de nuit, comparaison modale
- Champs: fact_id, route_id, night_train, country_id, year_id, operator_id

### **Vue `dashboard_metrics`** (41 enregistrements)
- Utilisée par: Dashboard, indicateurs synthétiques
- Champs: country_name, country_code, avg_passengers, avg_co2_emissions, avg_co2_per_passenger
