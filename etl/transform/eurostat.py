#==============================================================================
# Fichier: etl/transform/eurostat.py
#==============================================================================

"""
Transformation des données Eurostat (passagers et trafic)
"""
import pandas as pd
import numpy as np
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def transform_eurostat(raw_dir: str, processed_dir: str) -> None:
    """
    Transforme les données Eurostat
    """
    logger.info("📊 Transformation des données Eurostat...")
    
    # 1. Passagers ferroviaires
    passengers_path = Path(raw_dir) / "eurostat" / "rail_passengers.csv"
    passengers_df = pd.read_csv(passengers_path)
    
    # Ce fichier a une structure pivotée - on le transpose
    if 'freq,unit,vehicle,geo\\TIME_PERIOD' in passengers_df.columns:
        passengers_df = pd.melt(
            passengers_df,
            id_vars=['freq,unit,vehicle,geo\\TIME_PERIOD'],
            var_name='year',
            value_name='passengers'
        )
        
        # Séparer la colonne composite
        passengers_df[['freq', 'unit', 'vehicle', 'geo']] = passengers_df['freq,unit,vehicle,geo\\TIME_PERIOD'].str.split(',', expand=True)
        passengers_df = passengers_df.drop(columns=['freq,unit,vehicle,geo\\TIME_PERIOD'])
    
    # Nettoyage
    passengers_df['year'] = pd.to_numeric(passengers_df['year'], errors='coerce')
    passengers_df['passengers'] = pd.to_numeric(passengers_df['passengers'], errors='coerce')
    
    # Garder uniquement après 2010
    passengers_df = passengers_df[passengers_df['year'] >= 2010]
    
    # Remplacer les valeurs manquantes par la moyenne par pays
    for country in passengers_df['geo'].unique():
        mask = passengers_df['geo'] == country
        avg = passengers_df.loc[mask, 'passengers'].mean()
        passengers_df.loc[mask, 'passengers'] = passengers_df.loc[mask, 'passengers'].fillna(avg)
    
    # Ajouter des noms de pays
    country_names = {
        'FR': 'France', 'DE': 'Germany', 'CH': 'Switzerland',
        'IT': 'Italy', 'ES': 'Spain', 'UK': 'United Kingdom',
        'BE': 'Belgium', 'NL': 'Netherlands', 'AT': 'Austria',
        'AL': 'Albania', 'BG': 'Bulgaria', 'CZ': 'Czech Republic',
        'DK': 'Denmark', 'EE': 'Estonia', 'FI': 'Finland',
        'EL': 'Greece', 'HR': 'Croatia', 'HU': 'Hungary',
        'IE': 'Ireland', 'IS': 'Iceland', 'LI': 'Liechtenstein',
        'LT': 'Lithuania', 'LU': 'Luxembourg', 'LV': 'Latvia',
        'ME': 'Montenegro', 'MK': 'North Macedonia', 'MT': 'Malta',
        'NO': 'Norway', 'PL': 'Poland', 'PT': 'Portugal',
        'RO': 'Romania', 'RS': 'Serbia', 'SE': 'Sweden',
        'SI': 'Slovenia', 'SK': 'Slovakia', 'TR': 'Turkey',
        'CY': 'Cyprus'
    }
    
    passengers_df['country_name'] = passengers_df['geo'].map(country_names)
    passengers_df['country_name'] = passengers_df['country_name'].fillna('Unknown')
    
    # 2. Trafic ferroviaire
    traffic_path = Path(raw_dir) / "eurostat" / "rail_traffic.csv"
    traffic_df = pd.read_csv(traffic_path)
    
    # Traiter de la même manière
    if 'freq,train,vehicle,mot_nrg,unit,geo\\TIME_PERIOD' in traffic_df.columns:
        traffic_df = pd.melt(
            traffic_df,
            id_vars=['freq,train,vehicle,mot_nrg,unit,geo\\TIME_PERIOD'],
            var_name='year',
            value_name='traffic'
        )
        
        # Séparer la colonne composite
        traffic_df[['freq', 'train', 'vehicle', 'mot_nrg', 'unit', 'geo']] = traffic_df['freq,train,vehicle,mot_nrg,unit,geo\\TIME_PERIOD'].str.split(',', expand=True)
        traffic_df = traffic_df.drop(columns=['freq,train,vehicle,mot_nrg,unit,geo\\TIME_PERIOD'])
    
    # Nettoyage
    traffic_df['year'] = pd.to_numeric(traffic_df['year'], errors='coerce')
    traffic_df['traffic'] = pd.to_numeric(traffic_df['traffic'], errors='coerce')
    
    # Garder uniquement après 2010
    traffic_df = traffic_df[traffic_df['year'] >= 2010]
    
    # Remplacer les valeurs manquantes par la moyenne
    for country in traffic_df['geo'].unique():
        mask = traffic_df['geo'] == country
        avg = traffic_df.loc[mask, 'traffic'].mean()
        traffic_df.loc[mask, 'traffic'] = traffic_df.loc[mask, 'traffic'].fillna(avg)
    
    # Ajouter des noms de pays
    traffic_df['country_name'] = traffic_df['geo'].map(country_names)
    traffic_df['country_name'] = traffic_df['country_name'].fillna('Unknown')
    
    # Sauvegarder
    save_dir = Path(processed_dir) / "eurostat"
    save_dir.mkdir(parents=True, exist_ok=True)
    
    passengers_df.to_csv(save_dir / "passengers_processed.csv", index=False)
    traffic_df.to_csv(save_dir / "traffic_processed.csv", index=False)
    
    logger.info(f"✅ Données Eurostat sauvegardées dans {save_dir}")
    
    # Rapport qualité
    quality_report = {
        'source': 'eurostat',
        'passengers_records': len(passengers_df),
        'traffic_records': len(traffic_df),
        'countries_passengers': passengers_df['geo'].nunique(),
        'countries_traffic': traffic_df['geo'].nunique(),
        'years_range_passengers': (int(passengers_df['year'].min()), int(passengers_df['year'].max())),
        'years_range_traffic': (int(traffic_df['year'].min()), int(traffic_df['year'].max()))
    }
    
    return quality_report