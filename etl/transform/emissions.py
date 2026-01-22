#==============================================================================
# Fichier: etl/transform/emissions.py
#==============================================================================



"""
Transformation des données d'émissions CO2
"""
import pandas as pd
import numpy as np
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def transform_emissions(raw_dir: str, processed_dir: str) -> None:
    """
    Transforme les données d'émissions CO2
    """
    logger.info("🌍 Transformation des données d'émissions...")
    
    emissions_path = Path(raw_dir) / "emission_co2" / "eurostat_env_air_gge_sdmx.csv"
    
    # Charger uniquement les colonnes nécessaires (pour économiser de la mémoire)
    cols = ['airpol', 'geo', 'TIME_PERIOD', 'OBS_VALUE']
    emissions_df = pd.read_csv(emissions_path, usecols=cols)
    
    # Filtrer uniquement le CO2 (pas CH4, N2O, etc.)
    emissions_df = emissions_df[emissions_df['airpol'] == 'CO2']
    
    # Renommer les colonnes
    emissions_df = emissions_df.rename(columns={
        'TIME_PERIOD': 'year',
        'OBS_VALUE': 'co2_emissions',
        'geo': 'country_code'
    })
    
    # Conversion des types
    emissions_df['year'] = pd.to_numeric(emissions_df['year'], errors='coerce')
    emissions_df['co2_emissions'] = pd.to_numeric(emissions_df['co2_emissions'], errors='coerce')
    
    # Garder uniquement après 2010
    emissions_df = emissions_df[emissions_df['year'] >= 2010]
    
    # Remplacer les valeurs manquantes par la moyenne par pays
    for country in emissions_df['country_code'].unique():
        mask = emissions_df['country_code'] == country
        avg = emissions_df.loc[mask, 'co2_emissions'].mean()
        emissions_df.loc[mask, 'co2_emissions'] = emissions_df.loc[mask, 'co2_emissions'].fillna(avg)
    
    # Si moyenne est NaN (pas de données), utiliser moyenne globale
    global_avg = emissions_df['co2_emissions'].mean()
    emissions_df['co2_emissions'] = emissions_df['co2_emissions'].fillna(global_avg)
    
    # Ajouter des métriques d'émissions par passager (à enrichir plus tard)
    # Pour l'instant, on garde les données brutes
    
    # Sauvegarder
    save_dir = Path(processed_dir) / "emissions"
    save_dir.mkdir(parents=True, exist_ok=True)
    
    emissions_df.to_csv(save_dir / "co2_emissions_processed.csv", index=False)
    
    logger.info(f"✅ Émissions sauvegardées: {save_dir}")
    
    # Rapport qualité
    quality_report = {
        'source': 'emissions',
        'total_records': len(emissions_df),
        'countries': emissions_df['country_code'].nunique(),
        'years_range': (emissions_df['year'].min(), emissions_df['year'].max()),
        'avg_co2': emissions_df['co2_emissions'].mean(),
        'missing_values_before': emissions_df['co2_emissions'].isna().sum(),
        'missing_values_after': 0  # Tous remplis
    }
    
    return quality_report