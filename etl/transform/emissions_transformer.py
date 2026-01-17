"""
Transformation des données d'émissions CO2
"""
import pandas as pd
import numpy as np
import logging
from pathlib import Path
from .config import DATA_RAW, DATA_PROCESSED, COUNTRY_CODES

logger = logging.getLogger(__name__)

class EmissionsTransformer:
    """Transforme les données d'émissions"""
    
    def __init__(self):
        self.raw_path = DATA_RAW / "emission_co2"
        self.processed_path = DATA_PROCESSED / "emissions"
        self.processed_path.mkdir(exist_ok=True)
    
    def clean_emissions(self):
        """Nettoie les données d'émissions"""
        logger.info("Nettoyage des données d'émissions")
        
        file_path = self.raw_path / "eurostat_env_air_gge_sdmx.csv"
        if not file_path.exists():
            logger.error("Fichier d'émissions introuvable")
            return None
        
        try:
            # Lecture avec spécification des types pour éviter le warning
            dtypes = {
                'DATAFLOW': 'str',
                'LAST UPDATE': 'str',
                'freq': 'str',
                'unit': 'str',
                'airpol': 'str',
                'src_crf': 'str',
                'geo': 'str',
                'TIME_PERIOD': 'int32',
                'OBS_VALUE': 'float64',
                'OBS_FLAG': 'str',
                'CONF_STATUS': 'str'
            }
            
            # Lecture par chunks pour les gros fichiers
            chunks = []
            for chunk in pd.read_csv(file_path, dtype=dtypes, chunksize=100000, low_memory=False):
                chunks.append(chunk)
            
            df = pd.concat(chunks, ignore_index=True)
            
            # Filtrage sur les émissions CO2 du transport ferroviaire
            # Selon la documentation Eurostat, cherchons les bonnes catégories
            df_co2 = df[
                (df['airpol'].str.contains('CO2', na=False)) &
                (df['src_crf'].str.contains('1.A.3.c', na=False))  # Transport ferroviaire
            ].copy()
            
            # Filtrage des pays pertinents
            df_co2 = df_co2[df_co2['geo'].isin(COUNTRY_CODES.keys())]
            
            # Ajout du nom du pays
            df_co2['country_name'] = df_co2['geo'].map(COUNTRY_CODES)
            
            # Renommage des colonnes
            df_co2 = df_co2.rename(columns={
                'TIME_PERIOD': 'year',
                'OBS_VALUE': 'co2_emissions_kt'
            })
            
            # Conversion en kilotonnes si nécessaire
            if 'unit' in df_co2.columns and df_co2['unit'].str.contains('MIO_T').any():
                # Déjà en millions de tonnes, conversion en kilotonnes
                df_co2['co2_emissions_kt'] = df_co2['co2_emissions_kt'] * 1000
            
            # Sélection des colonnes utiles
            cols_to_keep = ['country_name', 'geo', 'year', 'co2_emissions_kt']
            df_co2 = df_co2[[col for col in cols_to_keep if col in df_co2.columns]]
            
            # Agrégation par pays et année
            df_agg = df_co2.groupby(['country_name', 'geo', 'year'], as_index=False).agg({
                'co2_emissions_kt': 'sum'
            })
            
            # Filtrage des années récentes
            df_agg = df_agg[df_agg['year'] >= 2000]
            
            # Sauvegarde
            output_path = self.processed_path / "emissions_clean.csv"
            df_agg.to_csv(output_path, index=False)
            logger.info(f"Émissions nettoyées : {len(df_agg)} lignes")
            
            return df_agg
            
        except Exception as e:
            logger.error(f"Erreur lors du nettoyage des émissions: {e}")
            return None