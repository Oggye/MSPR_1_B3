"""
Transformer pour les données Eurostat.
"""
from .base_transformer import BaseTransformer
import pandas as pd
import numpy as np
from pathlib import Path

class EurostatTransformer(BaseTransformer):
    """Transforme les données Eurostat."""
    
    def __init__(self):
        super().__init__('eurostat')
    
    def transform_passengers(self, raw_path, processed_path):
        """Transforme les données de passagers ferroviaires."""
        file_path = Path(raw_path) / 'rail_passengers.csv'
        df = pd.read_csv(file_path)
        
        df_before = df.copy()
        
        # Séparation de la première colonne
        df[['freq', 'unit', 'vehicle', 'geo']] = df['freq,unit,vehicle,geo\\TIME_PERIOD'].str.split(',', expand=True)
        
        # Suppression de la colonne originale
        df = df.drop(columns=['freq,unit,vehicle,geo\\TIME_PERIOD'])
        
        # Transformation en format long (tidy)
        df_long = df.melt(
            id_vars=['freq', 'unit', 'vehicle', 'geo'],
            var_name='year',
            value_name='passenger_km'
        )
        
        # Nettoyage des colonnes
        df_long['year'] = df_long['year'].str.strip().astype(int)
        
        # Conversion des valeurs
        df_long['passenger_km'] = pd.to_numeric(
            df_long['passenger_km'].replace(':', np.nan), 
            errors='coerce'
        )
        
        # Conversion en millions (THS -> millions)
        df_long['passenger_km_millions'] = df_long['passenger_km'] / 1000
        
        # Standardisation des codes pays
        df_long['country_code'] = df_long['geo'].apply(self.standardize_country_code)
        
        # Filtrage des données invalides
        df_long = df_long.dropna(subset=['passenger_km'])
        
        # Génération d'ID unique
        df_long['eurostat_uid'] = df_long.apply(
            lambda x: self.generate_id(x['country_code'], x['year'], 'passengers'), axis=1
        )
        
        # Sauvegarde
        output_path = Path(processed_path) / 'eurostat_passengers.parquet'
        df_long.to_parquet(output_path, index=False)
        
        self.log_transform('passengers', df_before, df_long)
        return df_long
    
    def transform_emissions(self, raw_path, processed_path):
        """Transforme les données d'émissions CO2."""
        file_path = Path(raw_path) / 'eurostat_env_air_gge_sdmx.csv'
        
        # Lecture avec types spécifiés pour éviter les warnings
        df = pd.read_csv(file_path, dtype={'OBS_FLAG': str, 'CONF_STATUS': str})
        
        df_before = df.copy()
        
        # Filtrage pour le transport ferroviaire
        # Dans les données Eurostat, chercher les codes pertinents
        # Ajuster selon la structure réelle de vos données
        rail_keywords = ['rail', 'train', '1.A.3.c']
        
        # Ici, vous devrez adapter en fonction de la structure exacte
        # Exemple de filtrage basique :
        df_rail = df[
            (df['airpol'] == 'CO2') &  # CO2 uniquement
            (df['src_crf'].str.contains('1.A.3.c', na=False))  # Transport ferroviaire
        ].copy()
        
        if len(df_rail) == 0:
            # Alternative si structure différente
            df_rail = df[df['airpol'] == 'CO2'].copy()
        
        # Nettoyage
        df_rail['OBS_VALUE'] = pd.to_numeric(df_rail['OBS_VALUE'], errors='coerce')
        df_rail['TIME_PERIOD'] = pd.to_numeric(df_rail['TIME_PERIOD'], errors='coerce')
        
        # Standardisation
        df_rail['country_code'] = df_rail['geo'].apply(self.standardize_country_code)
        df_rail['emissions_kt'] = df_rail['OBS_VALUE']  # MIO_T = kt (kilo-tonnes)
        
        # Calcul par passager-km (sera enrichi plus tard)
        df_rail['emissions_per_passenger_km'] = np.nan  # À calculer lors de l'enrichissement
        
        # Génération d'ID unique
        df_rail['emissions_uid'] = df_rail.apply(
            lambda x: self.generate_id(x['country_code'], x['TIME_PERIOD'], 'emissions'), axis=1
        )
        
        # Sélection des colonnes pertinentes
        columns_to_keep = [
            'country_code', 'TIME_PERIOD', 'emissions_kt', 
            'emissions_per_passenger_km', 'emissions_uid'
        ]
        
        df_rail = df_rail[columns_to_keep].rename(columns={'TIME_PERIOD': 'year'})
        
        # Sauvegarde
        output_path = Path(processed_path) / 'eurostat_emissions.parquet'
        df_rail.to_parquet(output_path, index=False)
        
        self.log_transform('emissions', df_before, df_rail)
        return df_rail