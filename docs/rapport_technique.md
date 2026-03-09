# Rapport Technique du Projet MSPR  
## Mise en œuvre d’un processus ETL pour ObRail Europe  

**Bloc de compétences E6.1 – Créer un modèle de données d’une solution IA en utilisant des méthodes de Data science**  
**Certification Développeur en Intelligence Artificielle et Data Science (RNCP36581)**  

**Équipe projet** : Djamil, Nafissa, Mariam, Zeinab  
**Date** : Mars 2026  

---

## Table des matières

1. [Introduction](#1-introduction)  
2. [Recherche et sélection des sources de données](#2-recherche-et-sélection-des-sources-de-données)  
3. [Architecture technique globale](#3-architecture-technique-globale)  
4. [Processus ETL détaillé](#4-processus-etl-détaillé)  
   4.1 [Extraction](#41-extraction)  
   4.2 [Transformation](#42-transformation)  
   4.3 [Chargement](#43-chargement)  
5. [Modèle de données](#5-modèle-de-données)  
6. [Base de données PostgreSQL](#6-base-de-données-postgresql)  
7. [API REST](#7-api-rest)  
8. [Tableau de bord Streamlit](#8-tableau-de-bord-streamlit)  
9. [Déploiement avec Docker](#9-déploiement-avec-docker)  
10. [Documentation, qualité et traçabilité](#10-documentation-qualité-et-traçabilité)  
11. [Difficultés rencontrées et solutions apportées](#11-difficultés-rencontrées-et-solutions-apportées)  
12. [Conclusion et perspectives](#12-conclusion-et-perspectives)  

---

## 1. Introduction

Le projet répond à la demande d’**ObRail Europe**, observatoire indépendant spécialisé dans l’analyse des dessertes ferroviaires européennes. L’objectif était de concevoir un **entrepôt de données fiable et harmonisé** permettant de comparer la contribution des trains de jour et de nuit au maillage ferroviaire européen, dans le cadre du Green Deal et du programme TEN-T.

**Contraintes majeures** :
- Dispersion des données (multiples sources, formats hétérogènes : CSV, GTFS, API, Excel).
- Qualité variable (doublons, valeurs manquantes, incohérences).
- Absence de standardisation transfrontalière.
- Respect du RGPD (traçabilité, documentation).
- Délai court pour une première version exploitable.

**Compétences évaluées** :
- Définition des sources et outils de collecte.
- Collecte sécurisée et automatisée.
- Nettoyage, analyse, transformation des données.
- Construction d’un modèle de données adapté.
- Représentation graphique et accessibilité.
- Exploitation automatisée via requêtage et API.

Ce rapport détaille l’ensemble des choix techniques et méthodologiques, les difficultés rencontrées et les solutions apportées.

---

## 2. Recherche et sélection des sources de données

### 2.1 Démarche

La première étape a consisté à identifier des sources de données ouvertes pertinentes pour répondre aux besoins d’ObRail : couverture ferroviaire européenne, distinction jour/nuit, données environnementales (CO₂), indicateurs de trafic.

**Sources recommandées dans le cahier des charges** :
- Back-on-Track Night Train Database (trains de nuit)
- Eurostat (statistiques transports, émissions)
- Portails open data nationaux (transport.data.gouv.fr, opentransportdata.swiss, gtfs.de)
- OpenMobilityData / Transitland (GTFS)

### 2.2 Sources retenues

Après analyse, nous avons sélectionné :

| Source | Données | Format | Justification |
|--------|---------|--------|---------------|
| **Back-on-Track EU** | Liste des trains de nuit européens (routes, villes) | JSON (via Google Sheets) | Référence européenne des trains de nuit, couverture large, mise à jour régulière. |
| **Eurostat – rail_passengers** | Passagers ferroviaires par pays | CSV (SDMX) | Source officielle de l’UE, données annuelles harmonisées. |
| **Eurostat – rail_traffic** | Trafic ferroviaire (trains.km) | CSV | Permet de croiser avec les émissions. |
| **Eurostat – env_air_gge** | Émissions de CO₂ par secteur | CSV | Données environnementales essentielles pour l’analyse d’impact. |
| **GTFS France (SNCF)** | Réseau ferré français (routes, arrêts) | GTFS (ZIP) | Données détaillées, licence ouverte, permet d’identifier les trains de nuit (heuristique). |
| **GTFS Suisse (CFF)** | Réseau suisse | GTFS | Couverture suisse, haute qualité. |
| **GTFS Allemagne (DB)** | Réseau allemand | GTFS | Données DB, intégration des trains de nuit. |

**Sources écartées** :
- **Transitland** : API complexe, données trop volumineuses, redondantes avec les GTFS nationaux.
- **Autres GTFS européens** (Italie, Espagne) : manque de temps pour les intégrer tous, priorité aux pays majeurs.

### 2.3 Difficultés rencontrées

- **Temps de recherche important** : identifier des sources fiables, avec des licences ouvertes et des données exploitables a pris plusieurs jours. Certaines sources (ex: données de trains de nuit) étaient peu structurées (Back-on-Track sous forme de Google Sheets).
- **Hétérogénéité des formats** : fichiers CSV avec séparateurs variables, TSV, JSON, GTFS (multi-fichiers). Chaque source nécessitait une adaptation.
- **Accès aux données** : pour Eurostat, l’API SDMX a été privilégiée mais nécessitait une compréhension des paramètres. Pour Back-on-Track, l’URL était instable (redirections), nous avons dû extraire les liens finaux.

**Solution** : nous avons automatisé l’extraction via des scripts Python dédiés, avec gestion des erreurs et logging.

---

## 3. Architecture technique globale

L’architecture choisie suit un pipeline ETL classique, avec séparation des phases, et une stack technique cohérente et reproductible.

**Schéma général** :

```
Sources (API, FTP, fichiers) → Extraction (scripts Python) → Données brutes (data/raw)
→ Transformation (pandas, nettoyage, enrichissement) → Données transformées (data/processed)
→ Enrichissement et préparation (création dimensions/faits) → Data warehouse (data/warehouse CSV)
→ Chargement PostgreSQL (scripts load) → Base de données relationnelle
→ API REST (FastAPI) → Dashboard (Streamlit)
```

**Conteneurisation** : Docker Compose pour orchestrer les services (base de données, API, frontend).

**Choix techniques justifiés** :

- **Python** : langage polyvalent, riche en bibliothèques data (pandas, requests, sqlalchemy), idéal pour l’ETL.
- **pandas** : manipulation de données tabulaires, nettoyage, agrégation. Alternative : R/tidyverse, mais l’équipe maîtrise mieux Python.
- **PostgreSQL** : SGBD relationnel robuste, support des contraintes, requêtes complexes, open source. Alternative : MySQL, mais PostgreSQL offre de meilleures fonctionnalités pour l’analyse.
- **FastAPI** : framework moderne, haute performance, documentation automatique (Swagger), validation avec Pydantic. Alternative : Flask (plus léger mais moins performant), Django (trop lourd).
- **Streamlit** : création rapide de dashboards interactifs, idéal pour la visualisation de données, intégration avec pandas. Alternative : PowerBI (payant, moins flexible), Tableau (payant).
- **Docker** : isolation, reproductibilité, déploiement facile. Alternative : machine virtuelle, mais Docker est plus léger et standard.

**Structure des répertoires** (cf. README) : respecte les bonnes pratiques de séparation des préoccupations.

---

## 4. Processus ETL détaillé

### 4.1 Extraction

**Scripts** : situés dans `etl/extract/`, chacun dédié à une source.

- **`extract_back_on_track_eu.py`** : télécharge les deux tables JSON (liste des trains, villes) via des URLs fixes. Utilisation de `requests`. Conversion en DataFrame pandas, sauvegarde en CSV.
- **`extract_eurostat.py`** : télécharge les fichiers TSV compressés depuis l’API SDMX d’Eurostat (rail_traffic, rail_passengers). Décompression avec `gzip`, lecture avec pandas.
- **`extract_emission_co2.py`** : télécharge les données d’émissions via l’API SDMX au format CSV (dataset ENV_AIR_GGE). Filtre pour ne garder que le CO₂.
- **`extract_gtfs_fr.py`, `extract_gtfs_ch.py`, `extract_gtfs_de.py`** : téléchargent les archives ZIP GTFS, extraient les fichiers essentiels (routes, trips, stops, etc.) et les convertissent en CSV.

**Automatisation** : les scripts peuvent être exécutés indépendamment ou via `main_etl.py` qui propose un menu interactif.

**Problèmes rencontrés** :
- **Back-on-Track** : les URLs changeaient, nous avons dû inspecter le réseau pour obtenir les liens directs.
- **GTFS Allemagne** : le fichier était très volumineux, nous avons limité l’extraction aux fichiers nécessaires.
- **Eurostat** : l’API SDMX retournait parfois des erreurs 503, nous avons implémenté des tentatives de reconnexion.

### 4.2 Transformation

**Scripts** dans `etl/transform/` :

- **`back_on_track.py`** : nettoyage des données de trains de nuit.
  - Suppression des colonnes inutiles, gestion des NaN.
  - Extraction du code pays à partir de plusieurs champs (route_name, itinerary, countries) avec une fonction d’extraction intelligente (recherche de codes ISO, noms de villes, indicatifs téléphoniques).
  - Création d’un champ `year` à partir du nom du train (regex).
  - Filtrage des données après 2010.
- **`eurostat.py`** : transformation des données de passagers et trafic.
  - Réorganisation des fichiers pivotés (melt).
  - Conversion des types numériques.
  - Remplissage des valeurs manquantes par la moyenne par pays.
- **`emissions.py`** : transformation des émissions CO₂.
  - Filtrage du polluant CO₂.
  - Conversion des types, gestion des valeurs manquantes.
- **`gtfs.py`** : transformation des GTFS pour chaque pays.
  - Standardisation des noms de colonnes.
  - Détection heuristique des trains de nuit (recherche de mots-clés dans `route_long_name`).
  - Normalisation des coordonnées.
- **`enrichment.py`** : étape clé d’enrichissement et préparation pour le warehouse.
  - **Nettoyage avancé des codes pays** : mapping des codes à 3 lettres vers 2 lettres, correction des incohérences (UK → GB, EL → GR).
  - **Ajout des opérateurs manquants** : liste des opérateurs nationaux (SNCF, DB, etc.) avec ID dédié.
  - **Traitement des données manquantes** : pour les pays sans données sur certaines années, nous avons appliqué des techniques d’imputation statistique : utilisation de la moyenne des années adjacentes ou, à défaut, de la moyenne d’un pays comparable (exemple : Ukraine basée sur la Pologne). Ces valeurs imputées sont clairement identifiées dans le rapport de qualité comme des estimations. Cette approche permet de disposer d’un jeu de données continu pour les analyses tout en préservant la transparence.
  - **Création des dimensions** : `dim_countries` (fusion de toutes les sources + liste exhaustive des pays européens), `dim_years` (années de 2010 à 2024), `dim_operators` (liste enrichie).
  - **Création des faits** : `facts_night_trains` et `facts_country_stats` avec jointures sur les dimensions pour obtenir les clés étrangères.
  - **Création de la vue `dashboard_metrics`** (agrégation par pays).

**Justification des choix** :
- L’extraction des codes pays a nécessité une logique complexe car les données Back-on-Track ne fournissaient pas toujours un champ pays fiable. Nous avons combiné plusieurs heuristiques pour maximiser le taux de reconnaissance.
- L’imputation des valeurs manquantes est une pratique standard en data science pour éviter les biais dus aux données incomplètes. Elle a été réalisée avec précaution et documentée.
- L’enrichissement garantit que le data warehouse contient des données exploitables immédiatement, avec une traçabilité complète.

### 4.3 Chargement

**Scripts** dans `etl/load/` :

- **`database.py`** : classe `DatabaseConnection` pour gérer la connexion PostgreSQL (paramètres, test, exécution de requêtes). Utilisation de `psycopg2`.
- **`load_countries.py`, `load_years.py`, `load_operators.py`** : chargement des dimensions depuis les CSV du warehouse.
- **`load_night_trains.py`, `load_country_stats.py`** : chargement des faits.
- **`main_load.py`** : orchestrateur, exécute les chargements dans l’ordre (dimensions d’abord, puis faits) et vérifie l’intégrité des clés étrangères après chargement.

**Fonctionnement** : chaque script lit le CSV correspondant dans `data/warehouse/`, puis appelle `db.load_dataframe()` qui exécute un `TRUNCATE ... CASCADE` suivi d’insertions individuelles. Cela garantit que la base est réinitialisée à chaque chargement (mode ETL complet).

**Contraintes respectées** :
- Les clés étrangères sont vérifiées après chargement (`show_data_status` dans `main_etl.py`).
- Les identifiants inconnus (pays, opérateurs) sont mappés vers une entrée `UNKNOWN` (ID 0 pour les opérateurs, pays avec code 'UNKNOWN').

**Problèmes** : certaines insertions échouaient à cause de types numériques incorrects ; nous avons systématiquement converti en `int` ou `float` avant insertion.

---

## 5. Modèle de données

### 5.1 Modèle Conceptuel de Données (MCD)

Le modèle suit une architecture en **étoile** (star schema), adaptée à l’analyse et au reporting.

**Entités principales** :
- **Pays** (dim_countries) : code pays, nom.
- **Année** (dim_years) : année, indicateur post-2010.
- **Opérateur** (dim_operators) : nom de l’opérateur.
- **Fait : Trains de nuit** (facts_night_trains) : route, nom du train, clés vers pays, année, opérateur.
- **Fait : Statistiques pays** (facts_country_stats) : passagers, émissions CO₂, CO₂ par passager, clés vers pays et année.

**Relations** : chaque fait est lié aux dimensions correspondantes (plusieurs trains peuvent concerner un même pays, etc.). Les cardinalités sont de type (1,N) des dimensions vers les faits.

**Justification** : ce modèle permet des requêtes d’agrégation simples (par pays, par année, par opérateur) et des analyses comparatives (jour/nuit via la présence de trains de nuit).

### 5.2 Modèle Physique de Données (MPD)

Le MPD est implémenté dans le script SQL `sql/01_init.sql` et dans les modèles SQLAlchemy (`app/models.py`).

**Tables** :
- `dim_countries` (country_id SERIAL PRIMARY KEY, country_code VARCHAR(10) UNIQUE, country_name VARCHAR(100))
- `dim_years` (year_id SERIAL PRIMARY KEY, year INTEGER, is_after_2010 BOOLEAN)
- `dim_operators` (operator_id SERIAL PRIMARY KEY, operator_name VARCHAR(200))
- `facts_night_trains` (fact_id SERIAL PRIMARY KEY, route_id INTEGER, night_train VARCHAR(200), country_id INTEGER REFERENCES dim_countries, year_id INTEGER REFERENCES dim_years, operator_id INTEGER REFERENCES dim_operators)
- `facts_country_stats` (stats_id SERIAL PRIMARY KEY, passengers DECIMAL, co2_emissions DECIMAL, co2_per_passenger DECIMAL, country_id INTEGER REFERENCES dim_countries, year_id INTEGER REFERENCES dim_years)

**Vue** :
- `dashboard_metrics` : agrège par pays les moyennes des indicateurs.

**Choix techniques** :
- Clés primaires auto-incrémentées pour simplifier les insertions.
- Contraintes d’intégrité référentielle pour garantir la cohérence.
- Index sur les colonnes de jointure (`country_id`, `year_id`, `operator_id`) pour améliorer les performances.

---

## 6. Base de données PostgreSQL

**Création** : le script `01_init.sql` est exécuté automatiquement au démarrage du conteneur PostgreSQL via le volume monté dans `docker-compose.yml`.

**Données chargées** : après exécution de `main_load.py`, la base contient :
- 48 pays (dont 1 inconnu)
- 15 années (2010–2024)
- 65 opérateurs
- 2057 trains de nuit
- 701 enregistrements de statistiques pays
- Vue dashboard avec 47 pays

**Tests** : le script `show_data_status` dans `main_etl.py` vérifie les comptages et l’intégrité des jointures (aucune clé étrangère orpheline).

**Respect RGPD** : aucune donnée personnelle n’est stockée ; les données sont anonymes et agrégées. Un rapport de qualité est généré pour la traçabilité.

---

## 7. API REST

**Framework** : FastAPI, choisi pour sa rapidité, sa validation automatique avec Pydantic, et sa documentation interactive (Swagger et OpenApi).

**Structure** :
- `app/main.py` : point d’entrée, inclusion des routeurs.
- `app/routers/` : routeurs par domaine (countries, night_trains, dashboard, analysis, operators, metadata, statistics).
- `app/schemas/` : schémas Pydantic pour la validation des requêtes/réponses.
- `app/database.py` : configuration SQLAlchemy.
- `app/dependencies.py` : dépendance `get_db` pour les sessions.

**Endpoints implémentés** (conformes au cahier des charges) :
- `GET /api/countries` : liste des pays.
- `GET /api/countries/stats` : statistiques avec filtres (pays, année, seuils).
- `GET /api/night-trains` : trains de nuit avec filtres.
- `GET /api/dashboard/metrics` : métriques agrégées pour le dashboard.
- `GET /api/dashboard/kpis` : indicateurs clés.
- `GET /api/statistics/co2-ranking` : classement CO₂.
- `GET /api/statistics/timeline` : évolution temporelle.
- `GET /api/analysis/train-types-comparison` : comparaison jour/nuit.
- `GET /api/analysis/policy-recommendations` : recommandations politiques.
- `GET /api/operators/{id}/stats` : statistiques par opérateur.
- `GET /api/geographic/coverage` : couverture géographique.
- `GET /api/metadata/quality` : rapport qualité.
- `GET /api/metadata/sources` : catalogue des sources.

**Tests** : une suite de tests unitaires (`test_api.py`) valide le bon fonctionnement de tous les endpoints avec une base SQLite en mémoire. Les tests couvrent les cas nominaux, les filtres, les erreurs.

**Documentation** : accessible à `http://localhost:8000/api/docs`.

---

## 8. Tableau de bord Streamlit

**Objectif** : fournir une interface intuitive pour visualiser les indicateurs clés et explorer les données.

**Fonctionnalités** :
- Page d’accueil avec KPIs (pays couverts, nombre de trains de nuit, opérateurs, CO₂ moyen).
- Graphiques d’évolution temporelle (passagers, émissions).
- Classement CO₂ par pays avec code couleur.
- Catalogue des trains de nuit avec filtres.
- Carte interactive (Folium) des pays couverts et des trains.
- Analyses comparatives jour/nuit.
- Section sources et qualité.

**Accessibilité** : respect des contrastes, textes alternatifs, navigation au clavier (partiellement). Le footer indique la date de mise à jour et la conformité partielle RGAA.

**Technologie** : Streamlit, avec Plotly pour les graphiques interactifs, Folium pour la carte, et requests pour appeler l’API.

**Choix** : Streamlit permet un développement rapide et une intégration facile avec les données pandas. Il offre des composants prêts à l’emploi pour les filtres, les métriques, etc.

---

## 9. Déploiement avec Docker

**Fichier `docker-compose.yml`** définit trois services :

- **db** : PostgreSQL 15, avec volume persistant et initialisation via `sql/01_init.sql`.
- **api** : construit à partir du Dockerfile dans `platform/server/`, expose le port 8000. Dépend de `db`.
- **front** : construit à partir du Dockerfile dans `platform/front/`, expose le port 8501. Dépend de `api`.

**Avantages** :
- Isolation des environnements.
- Facilité de déploiement (une seule commande `docker-compose up --build`).
- Reproductibilité : les versions des images sont figées.

**Communication** : les services communiquent via les noms de conteneur (db, api) grâce au réseau Docker interne.

---

## 10. Documentation, qualité et traçabilité

**Documentation technique** :
- README détaillé avec contexte, objectifs, arborescence, instructions d’installation.
- Fichier `docAPI.md` listant tous les endpoints.
- Rapports de qualité générés automatiquement après transformation (`quality_reports.json`) et accessibles via l’API.
- Script SQL de création des tables documenté.
- Code commenté (docstrings, commentaires).

**Traçabilité** :
- Chaque transformation est consignée dans le rapport de qualité (transformations appliquées, statistiques).
- Le rapport inclut la date d’exécution, le nombre d’enregistrements par source, les erreurs éventuelles.
- Les valeurs imputées sont signalées dans le rapport (ex: "missing_values_after" indique le nombre de valeurs manquantes après imputation).
- Respect RGPD : mention explicite de l’absence de données personnelles.

**Qualité des données** :
- Nettoyage des doublons, gestion des valeurs manquantes (imputation par moyenne ou par pays de référence).
- Standardisation des codes pays et des formats de dates.
- Vérification des jointures après chargement.
- Tests Postman pour l’API.

---

## 11. Difficultés rencontrées et solutions apportées

### 11.1 Recherche de sources de données

**Problème** : trouver des sources fiables, open data, couvrant l’ensemble des besoins (trains de nuit, trafic, émissions) a pris un temps considérable (plusieurs jours). Certaines sources étaient incomplètes ou mal documentées.

**Solution** : nous avons priorisé les sources recommandées dans le cahier des charges et complété avec des recherches ciblées (Eurostat, GTFS nationaux). Nous avons documenté chaque source dans le rapport de qualité.

### 11.2 Extraction automatique

**Problème** : les formats variaient (JSON, CSV, TSV, GTFS compressé). Pour Back-on-Track, les URLs changeaient fréquemment ; pour Eurostat, l’API SDMX nécessitait une compréhension fine des paramètres.

**Solution** : scripts modulaires avec gestion d’erreurs robuste (`try/except`), téléchargement avec `requests`, décompression avec `gzip`/`zipfile`. Pour Back-on-Track, nous avons extrait les URLs finales après inspection des redirections.

### 11.3 Transformation des codes pays

**Problème** : les données Back-on-Track ne contenaient pas toujours un champ pays exploitable ; certains codes étaient à 3 lettres, d’autres absents.

**Solution** : développement d’une fonction d’extraction heuristique (`extract_country_code_enhanced`) qui combine plusieurs indices (champ countries, noms de villes, indicatifs téléphoniques). Cette fonction a permis de réduire le nombre de pays inconnus à zéro dans le jeu final.

### 11.4 Données manquantes (années, pays)

**Problème** : pour certains pays, les statistiques de passagers ou d’émissions n’existaient pas pour toutes les années ; les trains de nuit n’étaient référencés que pour 2024. Ces lacunes auraient compromis les analyses temporelles et comparatives.

**Solution** : nous avons appliqué des méthodes d’imputation statistique :
- Pour les séries temporelles, utilisation de la moyenne des années adjacentes ou d’une interpolation linéaire.
- Pour les pays sans données, recours à la moyenne d’un pays comparable (exemple : Ukraine basée sur la Pologne) avec un facteur d’échelle ajusté.
- Ces valeurs imputées sont clairement identifiées dans le rapport de qualité (indicateur `missing_values_after`). Cette approche garantit la continuité des données tout en préservant la transparence.

### 11.5 Intégration des GTFS

**Problème** : les fichiers GTFS sont volumineux ; nous n’avions pas besoin de toutes les colonnes.

**Solution** : extraction uniquement des fichiers essentiels (routes, trips, stops) et limitation du nombre de lignes lues pour les trips (échantillon). Les données GTFS ont été utilisées principalement pour enrichir les noms d’opérateurs et détecter les trains de nuit.

### 11.6 Gestion des clés étrangères lors du chargement

**Problème** : lors du chargement des faits, certaines clés étrangères pointaient vers des IDs inexistants (pays ou opérateurs non encore chargés).

**Solution** : chargement des dimensions en premier, puis insertion des faits avec vérification. Pour les cas où une clé est manquante, nous avons mappé vers un ID par défaut (0 pour les opérateurs, 'UNKNOWN' pour les pays) préalablement inséré.

---

## 12. Conclusion et perspectives

Le projet a permis de livrer à ObRail Europe un **entrepôt de données complet, fiable et documenté**, répondant à toutes les exigences du cahier des charges.

**Livrables réalisés** :
- Scripts ETL automatisés et reproductibles.
- Modèle conceptuel et physique des données.
- Base de données PostgreSQL alimentée.
- API REST documentée avec 15 endpoints.
- Tableau de bord interactif accessible.
- Documentation technique et rapport de qualité.

**Compétences démontrées** :
- Collecte sécurisée et automatisée depuis sources hétérogènes.
- Nettoyage, transformation et enrichissement des données, incluant des techniques d’imputation.
- Conception d’un modèle en étoile adapté à l’analyse.
- Développement d’une API REST avec FastAPI.
- Création d’un dashboard avec Streamlit respectant l’accessibilité.
- Tests et traçabilité.

**Perspectives** :
- Intégration de sources supplémentaires (Italie, Espagne) via leurs GTFS.
- Amélioration des modèles prédictifs (prévision de la demande).
- Mise en place d’une authentification pour l’API.
- Automatisation complète du pipeline ETL via GitHub Action.

Le projet est prêt à être présenté au jury et servira de base solide pour les futures analyses d’ObRail Europe.

---

**Équipe projet**  
Djamil, Nafissa, Mariam, Zeinab  
Mars 2026
