"""
Script principal qui orchestre toutes les transformations.
"""
import sys
from pathlib import Path

# Ajout du chemin du projet
sys.path.append(str(Path(__file__).parent.parent.parent))

from etl.transform.gtfs_transformer import GTFSTransformer
from etl.transform.eurostat_transformer import EurostatTransformer
from etl.transform.night_train_transformer import NightTrainTransformer
from etl.transform.data_enricher import DataEnricher

import logging
from datetime import datetime

def setup_global_logging():
    """Configure le logging global."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(f'logs/transformation_{datetime.now().strftime("%Y%m%d")}.log'),
            logging.StreamHandler()
        ]
    )

def main():
    """Fonction principale de transformation."""
    setup_global_logging()
    logger = logging.getLogger('main_transformer')
    
    logger.info("=== DÉBUT DU PIPELINE DE TRANSFORMATION ===")
    
    # Chemins
    base_path = Path('data')
    raw_path = base_path / 'raw'
    processed_path = base_path / 'processed'
    warehouse_path = base_path / 'warehouse'
    
    # Création des répertoires
    processed_path.mkdir(parents=True, exist_ok=True)
    warehouse_path.mkdir(parents=True, exist_ok=True)
    (processed_path / 'metrics').mkdir(parents=True, exist_ok=True)
    
    try:
        # 1. Transformation GTFS
        logger.info("Transformation GTFS...")
        for country in ['fr', 'ch', 'de']:
            logger.info(f"  - Traitement GTFS {country.upper()}")
            transformer = GTFSTransformer(country)
            raw_country_path = raw_path / f'gtfs_{country}'
            
            if raw_country_path.exists():
                transformer.transform_all(raw_country_path, processed_path)
            else:
                logger.warning(f"Répertoire GTFS {country} non trouvé: {raw_country_path}")
        
        # 2. Transformation Eurostat
        logger.info("Transformation Eurostat...")
        eurostat_transformer = EurostatTransformer()
        
        # Passagers
        eurostat_raw = raw_path / 'eurostat'
        if eurostat_raw.exists():
            eurostat_transformer.transform_passengers(eurostat_raw, processed_path)
            eurostat_transformer.transform_emissions(eurostat_raw, processed_path)
        else:
            logger.warning("Répertoire Eurostat non trouvé")
        
        # 3. Transformation trains de nuit
        logger.info("Transformation trains de nuit...")
        night_transformer = NightTrainTransformer()
        
        night_raw = raw_path / 'back_on_track'
        if night_raw.exists():
            night_transformer.transform_cities(night_raw, processed_path)
            night_transformer.transform_routes(night_raw, processed_path)
        else:
            logger.warning("Répertoire Back on Track non trouvé")
        
        # 4. Enrichissement et création du schéma en étoile
        logger.info("Enrichissement des données...")
        enricher = DataEnricher()
        enricher.create_star_schema(processed_path, warehouse_path)
        
        # 5. Rapport final
        logger.info("Génération du rapport de qualité...")
        generate_quality_report(processed_path, warehouse_path)
        
        logger.info("=== TRANSFORMATION TERMINÉE AVEC SUCCÈS ===")
        
    except Exception as e:
        logger.error(f"ERREUR CRITIQUE DANS LE PIPELINE: {e}")
        raise

def generate_quality_report(processed_path, warehouse_path):
    """Génère un rapport de qualité des données transformées."""
    import json
    from pathlib import Path
    
    report = {
        'timestamp': datetime.now().isoformat(),
        'datasets': {},
        'quality_metrics': {}
    }
    
    # Analyse des fichiers transformés
    processed_files = list(processed_path.rglob('*.parquet'))
    
    for file_path in processed_files:
        try:
            df = pd.read_parquet(file_path)
            relative_path = file_path.relative_to(processed_path)
            
            report['datasets'][str(relative_path)] = {
                'rows': len(df),
                'columns': len(df.columns),
                'null_percentage': (df.isnull().sum().sum() / (len(df) * len(df.columns)) * 100),
                'duplicates': len(df) - len(df.drop_duplicates()),
                'memory_mb': df.memory_usage(deep=True).sum() / 1024**2
            }
        except Exception as e:
            print(f"Erreur analyse {file_path}: {e}")
    
    # Sauvegarde du rapport
    report_path = warehouse_path / 'quality_report.json'
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"Rapport de qualité généré: {report_path}")

if __name__ == '__main__':
    import pandas as pd
    main()