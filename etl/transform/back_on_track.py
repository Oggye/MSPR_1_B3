#==============================================================================
# Fichier: etl/transform/back_on_track.py
#==============================================================================

"""
Transformation des données Back on Track (trains de nuit)
"""
import pandas as pd
import numpy as np
from pathlib import Path
import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def transform_back_on_track(raw_dir: str, processed_dir: str) -> None:
    """
    Transforme les données Back on Track
    """
    logger.info("🚂 Transformation des données Back on Track...")
    
    # 1. Fichier des villes
    cities_path = Path(raw_dir) / "back_on_track" / "view_ontd_cities.csv"
    cities_df = pd.read_csv(cities_path)
    
    # Nettoyage
    cities_df = cities_df.copy()
    cities_df.columns = [col.strip().lower() for col in cities_df.columns]
    
    # Gérer valeurs manquantes
    cities_df['stop_cityname_romanized'] = cities_df['stop_cityname_romanized'].fillna('Inconnu')
    cities_df['stop_country'] = cities_df['stop_country'].fillna('UNKNOWN')
    
    # Standardiser les IDs
    cities_df['stop_id'] = cities_df['stop_id'].astype(str).str.strip()
    
    # Mapper les codes pays vers noms complets
    country_mapping = {
        'FR': 'France', 'DE': 'Germany', 'CH': 'Switzerland',
        'IT': 'Italy', 'ES': 'Spain', 'GB': 'United Kingdom',
        'BE': 'Belgium', 'NL': 'Netherlands', 'AT': 'Austria',
        'HU': 'Hungary', 'CZ': 'Czech Republic', 'PL': 'Poland',
        'DK': 'Denmark', 'SE': 'Sweden', 'NO': 'Norway'
    }
    
    # Convertir les codes pays (ex: FR, DE) en noms complets
    cities_df['country_name'] = cities_df['stop_country'].map(country_mapping)
    cities_df['country_name'] = cities_df['country_name'].fillna(cities_df['stop_country'])
    
    # Créer un code pays standardisé
    cities_df['country_code'] = cities_df['stop_country'].str[:2].str.upper()
    
    # Sauvegarder
    save_path = Path(processed_dir) / "back_on_track" / "cities_processed.csv"
    save_path.parent.mkdir(parents=True, exist_ok=True)
    cities_df.to_csv(save_path, index=False)
    logger.info(f"✅ Villes sauvegardées: {save_path}")
    
    # 2. Fichier des trains de nuit
    trains_path = Path(raw_dir) / "back_on_track" / "view_ontd_list.csv"
    trains_df = pd.read_csv(trains_path)
    
    # Nettoyage
    trains_df = trains_df.copy()
    trains_df.columns = [col.strip().lower() for col in trains_df.columns]
    
    # Extraire l'année du nom du train ou de l'ID
    def extract_year(text):
        if pd.isna(text):
            return 2024
        text = str(text)
        # Chercher un motif d'année
        match = re.search(r'20[0-2][0-9]', text)
        if match:
            return int(match.group())
        return 2024  # Année par défaut
    
    trains_df['year'] = trains_df['night_train'].apply(extract_year)
    
    # Standardiser les noms
    trains_df['night_train'] = trains_df['night_train'].fillna('Train de nuit')
    trains_df['operators'] = trains_df['operators'].fillna('Opérateur inconnu')
    
    # Créer un identifiant unique pour chaque route
    trains_df['route_id'] = trains_df['route_id'].astype(str).str.strip()
    
    # Extraire le pays de départ du nom du train
    def extract_country_code(route_name):
        if pd.isna(route_name):
            return 'UNKNOWN'
        route_name = str(route_name).upper()
        # Chercher des codes pays dans le nom
        for code in country_mapping.keys():
            if f' {code} ' in f' {route_name} ' or route_name.endswith(f' {code}'):
                return code
        return 'UNKNOWN'
    
    trains_df['country_code'] = trains_df['night_train'].apply(extract_country_code)
    
    # Sélectionner uniquement les données après 2010
    trains_df = trains_df[trains_df['year'] >= 2010]
    
    # Ajouter un identifiant unique pour les faits
    trains_df['fact_id'] = range(1, len(trains_df) + 1)
    
    # Sauvegarder
    save_path = Path(processed_dir) / "back_on_track" / "night_trains_processed.csv"
    trains_df.to_csv(save_path, index=False)
    logger.info(f"✅ Trains de nuit sauvegardés: {save_path}")
    
    # 3. Créer un rapport de qualité
    quality_report = {
        'source': 'back_on_track',
        'cities_total': len(cities_df),
        'cities_with_names': cities_df['stop_cityname_romanized'].notna().sum(),
        'trains_total': len(trains_df),
        'trains_after_2010': len(trains_df[trains_df['year'] >= 2010]),
        'countries_covered': trains_df['country_code'].nunique(),
        'years_range': (trains_df['year'].min(), trains_df['year'].max())
    }
    
    return quality_report