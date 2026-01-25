#==============================================================================
# Fichier: etl/transform/enrichment.py
#==============================================================================

"""
Enrichissement des données et préparation pour le data warehouse
"""
import pandas as pd
import numpy as np
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def enrich_and_prepare_for_warehouse(processed_dir: str, warehouse_dir: str) -> dict:
    """
    Enrichit les données transformées et les prépare pour le data warehouse
    """
    logger.info("🔗 Enrichissement et préparation pour le data warehouse...")
    
    # 1. Charger les données transformées
    # Back on Track - trains de nuit
    night_trains_path = Path(processed_dir) / "back_on_track" / "night_trains_processed.csv"
    night_trains = pd.read_csv(night_trains_path) if night_trains_path.exists() else pd.DataFrame()
    
    # Eurostat - passagers
    passengers_path = Path(processed_dir) / "eurostat" / "passengers_processed.csv"
    passengers = pd.read_csv(passengers_path) if passengers_path.exists() else pd.DataFrame()
    
    # Eurostat - trafic
    traffic_path = Path(processed_dir) / "eurostat" / "traffic_processed.csv"
    traffic = pd.read_csv(traffic_path) if traffic_path.exists() else pd.DataFrame()
    
    # Émissions
    emissions_path = Path(processed_dir) / "emissions" / "co2_emissions_processed.csv"
    emissions = pd.read_csv(emissions_path) if emissions_path.exists() else pd.DataFrame()
    
    # GTFS France
    gtfs_fr_path = Path(processed_dir) / "gtfs" / "fr" / "routes_processed.csv"
    gtfs_fr = pd.read_csv(gtfs_fr_path) if gtfs_fr_path.exists() else pd.DataFrame()
    
    # GTFS Suisse
    gtfs_ch_path = Path(processed_dir) / "gtfs" / "ch" / "routes_processed.csv"
    gtfs_ch = pd.read_csv(gtfs_ch_path) if gtfs_ch_path.exists() else pd.DataFrame()
    
    # GTFS Allemagne
    gtfs_de_path = Path(processed_dir) / "gtfs" / "de" / "routes_processed.csv"
    gtfs_de = pd.read_csv(gtfs_de_path) if gtfs_de_path.exists() else pd.DataFrame()
    
    # 2. Créer les DIMENSIONS (doit être fait avant les faits)
    
    # DIMENSION PAYS - Table maître des pays
    all_countries = pd.DataFrame()
    
    # Collecter tous les pays uniques de toutes les sources
    country_sources = []
    
    if not passengers.empty and 'geo' in passengers.columns:
        country_sources.append(passengers[['geo', 'country_name']].drop_duplicates())
    
    if not emissions.empty and 'country_code' in emissions.columns:
        country_sources.append(emissions[['country_code', 'country_name']].drop_duplicates())
    
    if not night_trains.empty and 'country_code' in night_trains.columns:
        # Ajouter les noms de pays pour Back on Track
        country_mapping = {
            'FR': 'France', 'DE': 'Germany', 'CH': 'Switzerland',
            'IT': 'Italy', 'ES': 'Spain', 'GB': 'United Kingdom',
            'BE': 'Belgium', 'NL': 'Netherlands', 'AT': 'Austria',
            'HU': 'Hungary', 'CZ': 'Czech Republic', 'PL': 'Poland',
            'DK': 'Denmark', 'SE': 'Sweden', 'NO': 'Norway'
        }
        night_trains['country_name'] = night_trains['country_code'].map(country_mapping)
        night_trains['country_name'] = night_trains['country_name'].fillna('Unknown')
        country_sources.append(night_trains[['country_code', 'country_name']].drop_duplicates())
    
    # Combiner toutes les sources
    if country_sources:
        all_countries = pd.concat(country_sources, ignore_index=True).drop_duplicates()
        all_countries = all_countries.rename(columns={'geo': 'country_code'})
        # S'assurer que nous avons une colonne country_code
        if 'country_code' not in all_countries.columns and 'geo' in all_countries.columns:
            all_countries['country_code'] = all_countries['geo']
        # Supprimer les doublons
        all_countries = all_countries.drop_duplicates(subset=['country_code'])
    
    # Créer l'ID pays
    all_countries['country_id'] = range(1, len(all_countries) + 1)
    dim_countries = all_countries[['country_id', 'country_code', 'country_name']]
    
    # DIMENSION ANNÉES
    all_years = set()
    
    if not passengers.empty and 'year' in passengers.columns:
        all_years.update(passengers['year'].dropna().astype(int).tolist())
    
    if not traffic.empty and 'year' in traffic.columns:
        all_years.update(traffic['year'].dropna().astype(int).tolist())
    
    if not emissions.empty and 'year' in emissions.columns:
        all_years.update(emissions['year'].dropna().astype(int).tolist())
    
    if not night_trains.empty and 'year' in night_trains.columns:
        all_years.update(night_trains['year'].dropna().astype(int).tolist())
    
    dim_years = pd.DataFrame({'year': sorted(all_years)})
    dim_years['year_id'] = range(1, len(dim_years) + 1)
    dim_years['is_after_2010'] = dim_years['year'] >= 2010
    
    # DIMENSION OPÉRATEURS
    all_operators = pd.DataFrame()
    
    if not night_trains.empty and 'operators' in night_trains.columns:
        operators_from_trains = night_trains[['operators']].drop_duplicates()
        operators_from_trains = operators_from_trains.rename(columns={'operators': 'operator_name'})
        all_operators = pd.concat([all_operators, operators_from_trains], ignore_index=True)
    
    # Ajouter les opérateurs GTFS
    gtfs_sources = []
    if not gtfs_fr.empty and 'agency_name' in gtfs_fr.columns:
        gtfs_sources.append(gtfs_fr[['agency_name']].drop_duplicates())
    if not gtfs_ch.empty and 'agency_name' in gtfs_ch.columns:
        gtfs_sources.append(gtfs_ch[['agency_name']].drop_duplicates())
    if not gtfs_de.empty and 'agency_name' in gtfs_de.columns:
        gtfs_sources.append(gtfs_de[['agency_name']].drop_duplicates())
    
    if gtfs_sources:
        gtfs_operators = pd.concat(gtfs_sources, ignore_index=True).drop_duplicates()
        gtfs_operators = gtfs_operators.rename(columns={'agency_name': 'operator_name'})
        all_operators = pd.concat([all_operators, gtfs_operators], ignore_index=True)
    
    # Nettoyer les noms d'opérateurs
    all_operators = all_operators.drop_duplicates()
    all_operators['operator_id'] = range(1, len(all_operators) + 1)
    dim_operators = all_operators[['operator_id', 'operator_name']]
    
    # 3. Créer les FAITS avec les clés étrangères
    
    # FAITS : Trains de nuit
    facts_night_trains = pd.DataFrame()
    if not night_trains.empty:
        facts_night_trains = night_trains.copy()
        
        # Ajouter les clés étrangères
        # Lier avec pays
        if not dim_countries.empty and 'country_code' in facts_night_trains.columns:
            country_mapping = dict(zip(dim_countries['country_code'], dim_countries['country_id']))
            facts_night_trains['country_id'] = facts_night_trains['country_code'].map(country_mapping)
        
        # Lier avec années
        if not dim_years.empty and 'year' in facts_night_trains.columns:
            year_mapping = dict(zip(dim_years['year'], dim_years['year_id']))
            facts_night_trains['year_id'] = facts_night_trains['year'].map(year_mapping)
        
        # Lier avec opérateurs
        if not dim_operators.empty and 'operators' in facts_night_trains.columns:
            operator_mapping = dict(zip(dim_operators['operator_name'], dim_operators['operator_id']))
            facts_night_trains['operator_id'] = facts_night_trains['operators'].map(operator_mapping)
        
        # Sélectionner les colonnes pour les faits
        fact_cols = ['fact_id', 'route_id', 'night_train', 'country_id', 'year_id', 'operator_id']
        available_cols = [col for col in fact_cols if col in facts_night_trains.columns]
        facts_night_trains = facts_night_trains[available_cols]
    
    # FAITS : Statistiques pays (métriques agrégées)
    facts_country_stats = pd.DataFrame()
    if not passengers.empty and not emissions.empty:
        # Préparer les données passagers
        passengers_agg = passengers.groupby(['geo', 'year'])['passengers'].mean().reset_index()
        passengers_agg = passengers_agg.rename(columns={'geo': 'country_code'})
        
        # Préparer les données émissions
        emissions_agg = emissions.groupby(['country_code', 'year'])['co2_emissions'].mean().reset_index()
        
        # Fusionner
        metrics = pd.merge(
            passengers_agg,
            emissions_agg,
            on=['country_code', 'year'],
            how='left'
        )
        
        # Calculer les métriques
        metrics['co2_per_passenger'] = metrics['co2_emissions'] / metrics['passengers']
        metrics['co2_per_passenger'] = metrics['co2_per_passenger'].replace([np.inf, -np.inf], np.nan)
        
        # Ajouter les clés étrangères
        # Lier avec pays
        if not dim_countries.empty:
            country_mapping = dict(zip(dim_countries['country_code'], dim_countries['country_id']))
            metrics['country_id'] = metrics['country_code'].map(country_mapping)
        
        # Lier avec années
        if not dim_years.empty:
            year_mapping = dict(zip(dim_years['year'], dim_years['year_id']))
            metrics['year_id'] = metrics['year'].map(year_mapping)
        
        # Créer un ID unique pour chaque enregistrement
        metrics['stat_id'] = range(1, len(metrics) + 1)
        
        # Sélectionner les colonnes pour les faits
        fact_cols = ['stat_id', 'country_id', 'year_id', 'passengers', 'co2_emissions', 'co2_per_passenger']
        available_cols = [col for col in fact_cols if col in metrics.columns]
        facts_country_stats = metrics[available_cols]
    
    # 4. Table DASHBOARD_METRICS (agrégé par pays)
    dashboard_metrics = pd.DataFrame()
    if not facts_country_stats.empty:
        # Agrégation par pays
        dashboard_metrics = facts_country_stats.groupby('country_id').agg({
            'passengers': 'mean',
            'co2_emissions': 'mean',
            'co2_per_passenger': 'mean'
        }).reset_index()
        
        # Ajouter le nom du pays
        country_info = dict(zip(dim_countries['country_id'], dim_countries['country_name']))
        dashboard_metrics['country_name'] = dashboard_metrics['country_id'].map(country_info)
        
        # Réorganiser les colonnes
        dashboard_metrics = dashboard_metrics[['country_id', 'country_name', 'passengers', 'co2_emissions', 'co2_per_passenger']]
    
    # 5. Sauvegarder dans le data warehouse
    warehouse_path = Path(warehouse_dir)
    warehouse_path.mkdir(parents=True, exist_ok=True)
    
    # Dimensions d'abord
    if not dim_countries.empty:
        dim_countries.to_csv(warehouse_path / "dim_countries.csv", index=False)
        logger.info(f"✅ dim_countries: {len(dim_countries)} pays")
    
    if not dim_years.empty:
        dim_years.to_csv(warehouse_path / "dim_years.csv", index=False)
        logger.info(f"✅ dim_years: {len(dim_years)} années")
    
    if not dim_operators.empty:
        dim_operators.to_csv(warehouse_path / "dim_operators.csv", index=False)
        logger.info(f"✅ dim_operators: {len(dim_operators)} opérateurs")
    
    # Faits ensuite
    if not facts_night_trains.empty:
        facts_night_trains.to_csv(warehouse_path / "facts_night_trains.csv", index=False)
        logger.info(f"✅ facts_night_trains: {len(facts_night_trains)} trajets")
    
    if not facts_country_stats.empty:
        facts_country_stats.to_csv(warehouse_path / "facts_country_stats.csv", index=False)
        logger.info(f"✅ facts_country_stats: {len(facts_country_stats)} statistiques")
    
    # Table dashboard
    if not dashboard_metrics.empty:
        dashboard_metrics.to_csv(warehouse_path / "dashboard_metrics.csv", index=False)
        logger.info(f"✅ dashboard_metrics: {len(dashboard_metrics)} pays")
    
    logger.info(f"✅ Data warehouse préparé dans {warehouse_path}")
    
    # 6. Créer un script SQL de création des tables
    create_sql = """
-- Script de création des tables du data warehouse ObRail
-- Ordre de chargement: 1. Dimensions, 2. Faits

-- DIMENSIONS
CREATE TABLE IF NOT EXISTS dim_countries (
    country_id INTEGER PRIMARY KEY,
    country_code VARCHAR(10) NOT NULL,
    country_name VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_years (
    year_id INTEGER PRIMARY KEY,
    year INTEGER NOT NULL,
    is_after_2010 BOOLEAN NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_operators (
    operator_id INTEGER PRIMARY KEY,
    operator_name VARCHAR(200) NOT NULL
);

-- FAITS
CREATE TABLE IF NOT EXISTS facts_night_trains (
    fact_id INTEGER PRIMARY KEY,
    route_id VARCHAR(50),
    night_train VARCHAR(200),
    country_id INTEGER,
    year_id INTEGER,
    operator_id INTEGER,
    FOREIGN KEY (country_id) REFERENCES dim_countries(country_id),
    FOREIGN KEY (year_id) REFERENCES dim_years(year_id),
    FOREIGN KEY (operator_id) REFERENCES dim_operators(operator_id)
);

CREATE TABLE IF NOT EXISTS facts_country_stats (
    stat_id INTEGER PRIMARY KEY,
    country_id INTEGER,
    year_id INTEGER,
    passengers NUMERIC,
    co2_emissions NUMERIC,
    co2_per_passenger NUMERIC,
    FOREIGN KEY (country_id) REFERENCES dim_countries(country_id),
    FOREIGN KEY (year_id) REFERENCES dim_years(year_id)
);

-- VUE POUR DASHBOARD
CREATE VIEW IF NOT EXISTS dashboard_view AS
SELECT 
    c.country_name,
    c.country_code,
    AVG(s.passengers) as avg_passengers,
    AVG(s.co2_emissions) as avg_co2_emissions,
    AVG(s.co2_per_passenger) as avg_co2_per_passenger
FROM facts_country_stats s
JOIN dim_countries c ON s.country_id = c.country_id
GROUP BY c.country_id, c.country_name, c.country_code;
"""
    
    with open(warehouse_path / "create_tables.sql", 'w', encoding='utf-8') as f:
        f.write(create_sql)
    
    # 7. Créer un rapport de traçabilité (SANS CARACTÈRES SPÉCIAUX)
    traceability_report = {
        'transformations_applied': [
            'Nettoyage des valeurs manquantes',
            'Standardisation des formats de pays',
            'Filtrage des donnees avant 2010',
            'Creation des cles etrangeres',
            'Calcul des metriques agregees'
        ],
        'data_sources': ['back_on_track', 'eurostat', 'emissions', 'gtfs_fr', 'gtfs_ch', 'gtfs_de'],
        'tables_created': {
            'dimensions': [
                'dim_countries.csv',
                'dim_years.csv', 
                'dim_operators.csv'
            ],
            'facts': [
                'facts_night_trains.csv',
                'facts_country_stats.csv'
            ],
            'dashboard': 'dashboard_metrics.csv'
        },
        'foreign_keys_established': [
            'facts_night_trains.country_id -> dim_countries.country_id',
            'facts_night_trains.year_id -> dim_years.year_id',
            'facts_night_trains.operator_id -> dim_operators.operator_id',
            'facts_country_stats.country_id -> dim_countries.country_id',
            'facts_country_stats.year_id -> dim_years.year_id'
        ],
        'data_quality': {
            'total_countries': len(dim_countries) if not dim_countries.empty else 0,
            'total_years': len(dim_years) if not dim_years.empty else 0,
            'total_operators': len(dim_operators) if not dim_operators.empty else 0,
            'night_train_records': len(facts_night_trains) if not facts_night_trains.empty else 0,
            'country_stats_records': len(facts_country_stats) if not facts_country_stats.empty else 0
        }
    }
    
    # Sauvegarder le rapport avec encodage UTF-8
    import json
    with open(warehouse_path / "warehouse_schema_report.json", 'w', encoding='utf-8') as f:
        json.dump(traceability_report, f, indent=2, ensure_ascii=False)
    
    return traceability_report