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
    
    # Extraire l'année si possible (ex: du nom du train)
    trains_df['year'] = 2024  # Année par défaut (dernière année connue)
    
    # Standardiser les noms
    trains_df['night_train'] = trains_df['night_train'].fillna('Train de nuit')
    trains_df['operators'] = trains_df['operators'].fillna('Opérateur inconnu')
    
    # Créer un identifiant unique pour chaque route
    trains_df['route_id'] = trains_df['route_id'].astype(str)
    
    # Sélectionner uniquement les données après 2010
    trains_df = trains_df[trains_df['year'] >= 2010]
    
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
        'missing_values_cities': cities_df.isnull().sum().to_dict(),
        'missing_values_trains': trains_df.isnull().sum().to_dict()
    }
    
    return quality_report