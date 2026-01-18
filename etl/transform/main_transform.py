"""
Script principal de transformation orchestrant tous les processus
"""
import logging
from pathlib import Path
import json
from datetime import datetime

from .back_on_track import transform_back_on_track
from .eurostat import transform_eurostat
from .emissions import transform_emissions
from .gtfs import transform_all_gtfs
from .enrichment import enrich_and_prepare_for_warehouse

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main_transform_pipeline():
    """
    Pipeline principal de transformation
    """
    logger.info("🚀 Démarrage du pipeline de transformation ETL")
    
    # Configuration des chemins
    BASE_DIR = Path(__file__).parent.parent.parent
    RAW_DIR = BASE_DIR / "data" / "raw"
    PROCESSED_DIR = BASE_DIR / "data" / "processed"
    WAREHOUSE_DIR = BASE_DIR / "data" / "warehouse"
    
    # S'assurer que les répertoires existent
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    WAREHOUSE_DIR.mkdir(parents=True, exist_ok=True)
    
    quality_reports = []
    
    try:
        # 1. Transformation Back on Track
        logger.info("=== Transformation Back on Track ===")
        report1 = transform_back_on_track(str(RAW_DIR), str(PROCESSED_DIR))
        quality_reports.append(report1)
        
        # 2. Transformation Eurostat
        logger.info("=== Transformation Eurostat ===")
        report2 = transform_eurostat(str(RAW_DIR), str(PROCESSED_DIR))
        quality_reports.append(report2)
        
        # 3. Transformation Émissions
        logger.info("=== Transformation Émissions CO2 ===")
        report3 = transform_emissions(str(RAW_DIR), str(PROCESSED_DIR))
        quality_reports.append(report3)
        
        # 4. Transformation GTFS
        logger.info("=== Transformation GTFS ===")
        reports_gtfs = transform_all_gtfs(str(RAW_DIR), str(PROCESSED_DIR))
        quality_reports.extend(reports_gtfs)
        
        # 5. Enrichissement et préparation pour le data warehouse
        logger.info("=== Enrichissement et préparation Data Warehouse ===")
        traceability_report = enrich_and_prepare_for_warehouse(
            str(PROCESSED_DIR), 
            str(WAREHOUSE_DIR)
        )
        
        # 6. Sauvegarder les rapports de qualité
        quality_report_path = WAREHOUSE_DIR / "quality_reports.json"
        with open(quality_report_path, 'w') as f:
            json.dump({
                'execution_date': datetime.now().isoformat(),
                'reports': quality_reports,
                'summary': {
                    'total_sources_processed': len(quality_reports),
                    'total_records_estimated': sum(r.get('total_records', 0) for r in quality_reports if r),
                    'success': True
                }
            }, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Pipeline de transformation terminé avec succès!")
        logger.info(f"📊 Rapports sauvegardés dans: {quality_report_path}")
        logger.info(f"📁 Data warehouse prêt dans: {WAREHOUSE_DIR}")
        
        # Afficher un résumé
        print("\n" + "="*50)
        print("RÉSUMÉ DE LA TRANSFORMATION")
        print("="*50)
        for report in quality_reports:
            if report:
                source = report.get('source', 'Inconnu')
                records = report.get('total_records', report.get('passengers_records', 0))
                print(f"• {source.upper():<20} : {records:,} enregistrements traités")
        
        print(f"• {'TOTAL':<20} : {sum(r.get('total_records', 0) for r in quality_reports if r):,} enregistrements")
        print("="*50)
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de la transformation: {e}")
        raise

if __name__ == "__main__":
    main_transform_pipeline()