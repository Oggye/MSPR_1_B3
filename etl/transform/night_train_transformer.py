"""
Transformer pour les données des trains de nuit (Back on Track).
"""
from .base_transformer import BaseTransformer
import pandas as pd
import numpy as np
from pathlib import Path
import re

class NightTrainTransformer(BaseTransformer):
    """Transforme les données des trains de nuit."""
    
    def __init__(self):
        super().__init__('night_trains')
    
    def transform_cities(self, raw_path, processed_path):
        """Transforme les données des villes."""
        file_path = Path(raw_path) / 'view_ontd_cities.csv'
        df = pd.read_csv(file_path)
        
        df_before = df.copy()
        
        # Nettoyage
        df['stop_cityname_romanized'] = df['stop_cityname_romanized'].apply(self.clean_text)
        df['stop_cityname_route_ids'] = df['stop_cityname_route_ids'].fillna('')
        
        # Standardisation des codes pays
        df['country_code'] = df['stop_country'].apply(self.standardize_country_code)
        
        # Extraction des IDs de route
        df['route_ids_list'] = df['stop_route_ids'].apply(self.extract_route_ids)
        df['route_count'] = df['route_ids_list'].apply(len)
        
        # Classification
        df['city_class'] = df['route_count'].apply(self.classify_city)
        
        # Génération d'ID unique
        df['city_uid'] = df.apply(
            lambda x: self.generate_id(x['stop_id'], x['country_code']), axis=1
        )
        
        # Sauvegarde
        output_path = Path(processed_path) / 'night_cities.parquet'
        df.to_parquet(output_path, index=False)
        
        self.log_transform('cities', df_before, df)
        return df
    
    def transform_routes(self, raw_path, processed_path):
        """Transforme les données des routes de nuit."""
        file_path = Path(raw_path) / 'view_ontd_list.csv'
        df = pd.read_csv(file_path)
        
        df_before = df.copy()
        
        # Nettoyage
        df['night_train'] = df['night_train'].apply(self.clean_text)
        df['route_long_name'] = df['route_long_name'].apply(self.clean_text)
        
        # Extraction des pays
        df['countries_list'] = df['countries'].str.split(',')
        df['country_count'] = df['countries_list'].apply(len)
        
        # Extraction des opérateurs
        df['operators_list'] = df['operators'].str.split(',')
        
        # Standardisation des noms
        operator_map = {
            'ÖBB': 'OBB',
            'SNCF': 'SNCF',
            'DB': 'DB',
            'SBB': 'SBB',
            # Ajouter d'autres
        }
        df['operators_standardized'] = df['operators_list'].apply(
            lambda x: [operator_map.get(op.strip(), op.strip()) for op in x] if isinstance(x, list) else []
        )
        
        # Extraction des gares de l'itinéraire
        df['itinerary_stations'] = df['itinerary'].apply(self.extract_stations)
        
        # Calcul de la longueur estimée
        df['station_count'] = df['itinerary_stations'].apply(len)
        
        # Classification
        df['route_type'] = df.apply(
            lambda x: 'international' if x['country_count'] > 1 else 'domestic', axis=1
        )
        
        # Génération d'ID unique
        df['night_route_uid'] = df.apply(
            lambda x: self.generate_id(x['route_id'], 'night'), axis=1
        )
        
        # Sauvegarde
        output_path = Path(processed_path) / 'night_routes.parquet'
        df.to_parquet(output_path, index=False)
        
        self.log_transform('routes', df_before, df)
        return df
    
    def extract_route_ids(self, route_ids_str):
        """Extrait les IDs de route d'une chaîne."""
        if pd.isna(route_ids_str):
            return []
        
        try:
            # Supprime les espaces et split
            ids = str(route_ids_str).replace(' ', '').split(',')
            # Filtre les IDs valides
            return [int(id_) for id_ in ids if id_.isdigit()]
        except:
            return []
    
    def extract_stations(self, itinerary_str):
        """Extrait les noms de gares d'un itinéraire."""
        if pd.isna(itinerary_str):
            return []
        
        # Pattern pour extraire les noms de gares (améliorable)
        # Format typique: "Gare1 - Gare2 - Gare3"
        stations = []
        text = str(itinerary_str)
        
        # Split sur différents séparateurs
        for sep in [' – ', ' - ', ' — ', ' –', ' -', ' to ', ' → ']:
            if sep in text:
                stations = [s.strip() for s in text.split(sep)]
                break
        
        if not stations:
            # Fallback: split sur n'importe quel caractère non-alphanumérique répété
            stations = re.split(r'[^\w\s]+', text)
            stations = [s.strip() for s in stations if s.strip()]
        
        return stations
    
    def classify_city(self, route_count):
        """Classifie les villes selon leur connectivité."""
        if route_count >= 10:
            return 'hub_major'
        elif route_count >= 5:
            return 'hub_medium'
        elif route_count >= 2:
            return 'connected'
        else:
            return 'terminal'