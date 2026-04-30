# etl/transform/dim_stops.py
import pandas as pd
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def build_dim_stops(processed_dir: str, warehouse_dir: str) -> pd.DataFrame:
    logger.info("🚏 Construction de la dimension des arrêts (dim_stops)...")
    stops_list = []
    countries = ['fr', 'ch', 'de']
    for country in countries:
        stops_path = Path(processed_dir) / "gtfs" / country / "stops_processed.csv"
        if stops_path.exists():
            df = pd.read_csv(stops_path)
            # On garde les colonnes indispensables
            cols = ['stop_name', 'stop_lat', 'stop_lon']
            if 'stop_id' in df.columns:
                cols.append('stop_id')
            df = df[cols].copy()
            df['source_country'] = country.upper()
            stops_list.append(df)
        else:
            logger.warning(f"⚠️ Fichier stops manquant pour {country} : {stops_path}")

    if not stops_list:
        logger.error("Aucun fichier stops trouvé.")
        return pd.DataFrame()

    all_stops = pd.concat(stops_list, ignore_index=True)
    all_stops['stop_name'] = all_stops['stop_name'].str.strip().str.lower()
    # Dédoublonnage par nom + pays
    all_stops = all_stops.drop_duplicates(subset=['stop_name', 'source_country'])
    # Supprimer les arrêts sans coordonnées
    all_stops = all_stops.dropna(subset=['stop_lat', 'stop_lon'])

    all_stops['stop_id_dim'] = range(1, len(all_stops) + 1)

    warehouse_path = Path(warehouse_dir)
    warehouse_path.mkdir(parents=True, exist_ok=True)
    all_stops.to_csv(warehouse_path / "dim_stops.csv", index=False)
    logger.info(f"✅ dim_stops créée : {len(all_stops)} arrêts uniques.")
    return all_stops