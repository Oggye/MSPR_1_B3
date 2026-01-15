"""
Transformer spécifique pour les données GTFS.
"""
from .base_transformer import BaseTransformer
import pandas as pd
import numpy as np
from pathlib import Path

class GTFSTransformer(BaseTransformer):
    """Transforme les données GTFS."""
    
    def __init__(self, country):
        super().__init__(f'gtfs_{country}')
        self.country = country
        self.country_codes = {'fr': 'FR', 'ch': 'CH', 'de': 'DE'}
    
    def transform_all(self, raw_path, processed_path):
        """Transforme tous les fichiers GTFS d'un pays."""
        try:
            # 1. Agences
            agencies = self.transform_agencies(raw_path, processed_path)
            
            # 2. Stops
            stops = self.transform_stops(raw_path, processed_path)
            
            # 3. Routes
            routes = self.transform_routes(raw_path, processed_path)
            
            # 4. Trips
            trips = self.transform_trips(raw_path, processed_path)
            
            # 5. Stop Times
            stop_times = self.transform_stop_times(raw_path, processed_path, trips, stops)
            
            # 6. Calendar
            calendar = self.transform_calendar(raw_path, processed_path)
            
            # Enrichissement des données
            enriched_data = self.enrich_data(
                agencies, stops, routes, trips, stop_times, calendar
            )
            
            # Sauvegarde des métriques
            self.save_metrics()
            
            return enriched_data
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la transformation GTFS {self.country}: {e}")
            raise
    
    def transform_agencies(self, raw_path, processed_path):
        """Transforme le fichier agency.csv."""
        file_path = Path(raw_path) / 'agency.csv'
        df = pd.read_csv(file_path)
        
        df_before = df.copy()
        
        # Nettoyage de base
        df['agency_name'] = df['agency_name'].apply(self.clean_text)
        df['agency_url'] = df['agency_url'].str.strip()
        
        # Ajout du code pays
        df['country_code'] = self.country_codes.get(self.country, self.country.upper())
        
        # Génération d'un ID unique
        df['agency_uid'] = df.apply(
            lambda x: self.generate_id(x['agency_id'], x['country_code']), axis=1
        )
        
        # Sauvegarde
        output_path = Path(processed_path) / f'agencies_{self.country}.parquet'
        df.to_parquet(output_path, index=False)
        
        self.log_transform('agencies', df_before, df)
        return df
    
    def transform_stops(self, raw_path, processed_path):
        """Transforme le fichier stops.csv."""
        file_path = Path(raw_path) / 'stops.csv'
        df = pd.read_csv(file_path)
        
        df_before = df.copy()
        
        # Nettoyage
        df['stop_name'] = df['stop_name'].apply(self.clean_text)
        
        # Gestion des valeurs manquantes
        df['stop_lat'] = df['stop_lat'].fillna(0)
        df['stop_lon'] = df['stop_lon'].fillna(0)
        
        # Validation géographique
        df.loc[df['stop_lat'].abs() > 90, 'stop_lat'] = 0
        df.loc[df['stop_lon'].abs() > 180, 'stop_lon'] = 0
        
        # Ajout du code pays
        df['country_code'] = self.country_codes.get(self.country, self.country.upper())
        
        # Génération d'ID unique
        df['stop_uid'] = df.apply(
            lambda x: self.generate_id(x['stop_id'], x['country_code']), axis=1
        )
        
        # Classification des types de gares
        df['stop_type'] = self.classify_stop(df['stop_name'])
        
        # Sauvegarde
        output_path = Path(processed_path) / f'stops_{self.country}.parquet'
        df.to_parquet(output_path, index=False)
        
        self.log_transform('stops', df_before, df)
        return df
    
    def classify_stop(self, stop_names):
        """Classifie les gares par type."""
        classifications = []
        for name in stop_names:
            if pd.isna(name):
                classifications.append('unknown')
                continue
            
            name_lower = str(name).lower()
            if any(term in name_lower for term in ['hbf', 'central', 'centraal', 'gare', 'main station']):
                classifications.append('major')
            elif any(term in name_lower for term in ['bahnhof', 'station', 'halt', 'arrêt']):
                classifications.append('medium')
            else:
                classifications.append('minor')
        return classifications
    
    def transform_routes(self, raw_path, processed_path):
        """Transforme le fichier routes.csv."""
        file_path = Path(raw_path) / 'routes.csv'
        df = pd.read_csv(file_path)
        
        df_before = df.copy()
        
        # Nettoyage
        df['route_long_name'] = df['route_long_name'].apply(self.clean_text)
        df['route_short_name'] = df['route_short_name'].str.strip()
        
        # Standardisation des types de route
        df['route_type_label'] = df['route_type'].apply(self.map_route_type)
        
        # Ajout du code pays
        df['country_code'] = self.country_codes.get(self.country, self.country.upper())
        
        # Génération d'ID unique
        df['route_uid'] = df.apply(
            lambda x: self.generate_id(x['route_id'], x['country_code']), axis=1
        )
        
        # Sauvegarde
        output_path = Path(processed_path) / f'routes_{self.country}.parquet'
        df.to_parquet(output_path, index=False)
        
        self.log_transform('routes', df_before, df)
        return df
    
    def map_route_type(self, route_type):
        """Mappe les codes GTFS route_type vers des labels."""
        route_type_map = {
            0: 'Tram',
            1: 'Metro',
            2: 'Rail',
            3: 'Bus',
            4: 'Ferry',
            7: 'Funicular',
            # Ajouter d'autres codes selon la spécification GTFS
        }
        return route_type_map.get(route_type, 'Other')
    
    def transform_stop_times(self, raw_path, processed_path, trips_df, stops_df):
        """Transforme le fichier stop_times.csv (optimisé pour gros fichiers)."""
        file_path = Path(raw_path) / 'stop_times.csv'
        
        # Lecture par chunks pour les gros fichiers
        chunks = []
        chunk_size = 100000
        
        for i, chunk in enumerate(pd.read_csv(file_path, chunksize=chunk_size)):
            # Nettoyage du chunk
            chunk = self.clean_stop_times_chunk(chunk)
            
            # Ajout d'informations des trips et stops
            chunk = pd.merge(chunk, trips_df[['trip_id', 'route_uid', 'service_id']], 
                           on='trip_id', how='left')
            chunk = pd.merge(chunk, stops_df[['stop_id', 'stop_uid', 'stop_name']], 
                           on='stop_id', how='left')
            
            chunks.append(chunk)
            
            if i % 10 == 0:
                self.logger.info(f"Traitement stop_times chunk {i}: {len(chunk)} lignes")
        
        # Concaténation
        df = pd.concat(chunks, ignore_index=True)
        
        # Génération d'ID unique pour stop_time
        df['stop_time_uid'] = df.apply(
            lambda x: self.generate_id(x['trip_id'], x['stop_id'], x['stop_sequence']), axis=1
        )
        
        # Conversion des heures
        df['arrival_seconds'] = df['arrival_time'].apply(self.time_to_seconds)
        df['departure_seconds'] = df['departure_time'].apply(self.time_to_seconds)
        
        # Calcul du temps d'arrêt
        df['dwell_time_seconds'] = df['departure_seconds'] - df['arrival_seconds']
        
        # Sauvegarde
        output_path = Path(processed_path) / f'stop_times_{self.country}.parquet'
        df.to_parquet(output_path, index=False)
        
        self.log_transform('stop_times', pd.DataFrame(), df)
        return df
    
    def clean_stop_times_chunk(self, chunk):
        """Nettoie un chunk de stop_times."""
        # Gestion des heures invalides (ex: "24:00:00" -> "00:00:00")
        chunk['arrival_time'] = chunk['arrival_time'].apply(self.fix_time_format)
        chunk['departure_time'] = chunk['departure_time'].apply(self.fix_time_format)
        
        # Valeurs manquantes
        chunk['pickup_type'] = chunk['pickup_type'].fillna(0).astype(int)
        chunk['drop_off_type'] = chunk['drop_off_type'].fillna(0).astype(int)
        
        return chunk
    
    def time_to_seconds(self, time_str):
        """Convertit HH:MM:SS en secondes."""
        if pd.isna(time_str):
            return 0
        
        try:
            parts = str(time_str).split(':')
            if len(parts) == 3:
                return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
            elif len(parts) == 2:
                return int(parts[0]) * 3600 + int(parts[1]) * 60
            else:
                return 0
        except:
            return 0
    
    def fix_time_format(self, time_str):
        """Corrige les formats de temps GTFS (ex: 24:30:00 -> 00:30:00)."""
        if pd.isna(time_str):
            return '00:00:00'
        
        time_str = str(time_str)
        if time_str.startswith('24'):
            return '00' + time_str[2:]
        elif time_str.startswith('25'):
            return '01' + time_str[2:]
        elif time_str.startswith('26'):
            return '02' + time_str[2:]
        return time_str