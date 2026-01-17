"""
Transformation des données Back on Track (trains de nuit)
"""
import pandas as pd
import numpy as np
import logging
import re
from pathlib import Path
from .config import DATA_RAW, DATA_PROCESSED, COUNTRY_CODES

logger = logging.getLogger(__name__)

class BackOnTrackTransformer:
    """Transforme les données des trains de nuit"""
    
    def __init__(self):
        self.raw_path = DATA_RAW / "back_on_track"
        self.processed_path = DATA_PROCESSED / "back_on_track"
        self.processed_path.mkdir(exist_ok=True)
    
    def clean_cities(self):
        """Nettoie les données des villes"""
        logger.info("Nettoyage des données villes Back on Track")
        
        file_path = self.raw_path / "view_ontd_cities.csv"
        if not file_path.exists():
            logger.error("Fichier view_ontd_cities.csv introuvable")
            return None
        
        try:
            df = pd.read_csv(file_path)
            
            # Nettoyage des noms de colonnes
            df.columns = df.columns.str.lower().str.replace(' ', '_')
            
            # Gestion des valeurs manquantes
            df['stop_cityname_romanized'] = df['stop_cityname_romanized'].fillna('Unknown')
            
            # Extraction des pays depuis stop_id si manquant
            if 'stop_country' not in df.columns or df['stop_country'].isnull().all():
                # Pattern pour code pays à la fin du stop_id
                def extract_country(stop_id):
                    if isinstance(stop_id, str):
                        # Cherche un code pays de 2 lettres à la fin
                        match = re.search(r'([A-Z]{2})$', stop_id)
                        if match:
                            return match.group(1)
                    return 'Unknown'
                
                df['stop_country'] = df['stop_id'].apply(extract_country)
            
            # Standardisation des codes pays
            df['country_code'] = df['stop_country'].str.upper()
            df['country_name'] = df['country_code'].map(COUNTRY_CODES).fillna('Unknown')
            
            # Nettoyage des route_ids (séparés par des virgules)
            if 'stop_route_ids' in df.columns:
                # Compter le nombre de routes
                df['num_routes'] = df['stop_route_ids'].apply(
                    lambda x: len(str(x).split(',')) if pd.notna(x) else 0
                )
            
            # Sauvegarde
            output_path = self.processed_path / "cities_clean.csv"
            df.to_csv(output_path, index=False)
            logger.info(f"Villes nettoyées : {len(df)} lignes")
            
            return df
            
        except Exception as e:
            logger.error(f"Erreur lors du nettoyage des villes: {e}")
            return None
    
    def clean_routes(self):
        """Nettoie les données des routes"""
        logger.info("Nettoyage des données routes Back on Track")
        
        file_path = self.raw_path / "view_ontd_list.csv"
        if not file_path.exists():
            logger.error("Fichier view_ontd_list.csv introuvable")
            return None
        
        try:
            df = pd.read_csv(file_path)
            
            # Nettoyage des colonnes
            df.columns = df.columns.str.lower().str.replace(' ', '_')
            
            # Extraction des pays
            if 'countries' in df.columns:
                # Les pays sont séparés par des virgules
                df['countries_list'] = df['countries'].str.split(',')
                df['num_countries'] = df['countries_list'].apply(lambda x: len(x) if isinstance(x, list) else 0)
                
                # Premier pays comme pays principal
                df['main_country'] = df['countries_list'].apply(
                    lambda x: x[0].strip() if isinstance(x, list) and len(x) > 0 else 'Unknown'
                )
            
            # Nettoyage des opérateurs
            if 'operators' in df.columns:
                df['operators'] = df['operators'].fillna('Unknown')
            
            # Indicateur de train de nuit
            df['is_night_train'] = df['night_train'].notna()
            
            # Extraction de l'itinéraire principal (premier arrêt -> dernier arrêt)
            def extract_main_itinerary(itinerary):
                if pd.isna(itinerary):
                    return None
                # Format commun: "Ville1 – Ville2"
                parts = str(itinerary).split('–')
                if len(parts) >= 2:
                    return parts[0].strip(), parts[-1].strip()
                return None, None
            
            df[['origin_city', 'destination_city']] = df['itinerary'].apply(
                lambda x: pd.Series(extract_main_itinerary(x))
            )
            
            # Sauvegarde
            output_path = self.processed_path / "routes_clean.csv"
            df.to_csv(output_path, index=False)
            logger.info(f"Routes nettoyées : {len(df)} lignes")
            
            return df
            
        except Exception as e:
            logger.error(f"Erreur lors du nettoyage des routes: {e}")
            return None