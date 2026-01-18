"""
Transformation des données GTFS (France, Suisse, Allemagne)
"""
import pandas as pd
import numpy as np
from pathlib import Path
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def transform_gtfs_country(raw_dir: str, processed_dir: str, country: str) -> dict:
    """
    Transforme les données GTFS d'un pays spécifique
    """
    logger.info(f"🚉 Transformation GTFS pour {country}...")
    
    country_dir = Path(raw_dir) / f"gtfs_{country.lower()}"
    
    # Charger les fichiers essentiels
    try:
        # Agency
        agency_path = country_dir / "agency.csv"
        agency_df = pd.read_csv(agency_path)
        
        # Routes
        routes_path = country_dir / "routes.csv"
        routes_df = pd.read_csv(routes_path)
        
        # Stops
        stops_path = country_dir / "stops.csv"
        stops_df = pd.read_csv(stops_path)
        
        # Trips (échantillon pour éviter la mémoire)
        trips_path = country_dir / "trips.csv"
        trips_df = pd.read_csv(trips_path, nrows=10000)  # Échantillon pour transformation
        
    except FileNotFoundError as e:
        logger.error(f"Fichier manquant pour {country}: {e}")
        return None
    
    # Standardisation des colonnes
    agency_df.columns = [col.strip().lower() for col in agency_df.columns]
    routes_df.columns = [col.strip().lower() for col in routes_df.columns]
    stops_df.columns = [col.strip().lower() for col in stops_df.columns]
    trips_df.columns = [col.strip().lower() for col in trips_df.columns]
    
    # 1. Nettoyage Agency
    agency_df['agency_name'] = agency_df['agency_name'].fillna(f"Opérateur {country}")
    agency_df['agency_url'] = agency_df['agency_url'].fillna('')
    agency_df['country'] = country
    
    # 2. Nettoyage Routes
    routes_df['route_short_name'] = routes_df['route_short_name'].fillna('')
    routes_df['route_long_name'] = routes_df['route_long_name'].fillna('')
    
    # Identifier les trains de nuit (simple heuristique)
    routes_df['is_night_train'] = routes_df['route_long_name'].str.contains(
        'night|nacht|nocturne|nightjet', case=False, na=False
    )
    
    # 3. Nettoyage Stops
    stops_df['stop_name'] = stops_df['stop_name'].fillna('Gare inconnue')
    
    # Normaliser les coordonnées
    for col in ['stop_lat', 'stop_lon']:
        if col in stops_df.columns:
            stops_df[col] = pd.to_numeric(stops_df[col], errors='coerce')
            # Remplacer valeurs extrêmes par moyenne
            avg = stops_df[col].mean()
            stops_df[col] = stops_df[col].fillna(avg)
    
    # 4. Nettoyage Trips
    trips_df = trips_df.dropna(subset=['trip_id'])
    
    # Sauvegarder
    save_dir = Path(processed_dir) / "gtfs" / country.lower()
    save_dir.mkdir(parents=True, exist_ok=True)
    
    agency_df.to_csv(save_dir / "agency_processed.csv", index=False)
    routes_df.to_csv(save_dir / "routes_processed.csv", index=False)
    stops_df.to_csv(save_dir / "stops_processed.csv", index=False)
    trips_df.to_csv(save_dir / "trips_processed.csv", index=False)
    
    logger.info(f"✅ GTFS {country} sauvegardé dans {save_dir}")
    
    # Rapport qualité
    quality_report = {
        'source': f'gtfs_{country}',
        'agencies': len(agency_df),
        'routes': len(routes_df),
        'stops': len(stops_df),
        'trips_sample': len(trips_df),
        'night_trains': routes_df['is_night_train'].sum(),
        'missing_coords': stops_df[['stop_lat', 'stop_lon']].isna().sum().to_dict()
    }
    
    return quality_report

def transform_all_gtfs(raw_dir: str, processed_dir: str) -> list:
    """
    Transforme tous les jeux de données GTFS
    """
    countries = ['fr', 'ch', 'de']
    reports = []
    
    for country in countries:
        report = transform_gtfs_country(raw_dir, processed_dir, country)
        if report:
            reports.append(report)
    
    return reports