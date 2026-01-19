"""
Script principal de transformation orchestrant tous les processus
Version corrigée avec gestion des types NumPy pour JSON
"""
import sys
import os
import logging
from pathlib import Path
import json
from datetime import datetime
import numpy as np

# Ajouter le répertoire parent au PYTHONPATH pour les imports absolus
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent
sys.path.insert(0, str(project_root))

# Maintenant on peut importer les modules
try:
    from etl.transform.back_on_track import transform_back_on_track
    from etl.transform.eurostat import transform_eurostat
    from etl.transform.emissions import transform_emissions
    from etl.transform.gtfs import transform_all_gtfs
    from etl.transform.enrichment import enrich_and_prepare_for_warehouse
except ImportError as e:
    print(f"❌ Erreur d'import: {e}")
    print("Assure-toi que:")
    print("1. Tu as bien créé tous les fichiers dans etl/transform/")
    print("2. Tu as un fichier __init__.py dans etl/transform/")
    print("3. Tu exécutes depuis la racine du projet")
    sys.exit(1)

logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class NumpyEncoder(json.JSONEncoder):
    """Encodeur JSON personnalisé pour gérer les types NumPy"""
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.bool_):
            return bool(obj)
        return super().default(obj)

def convert_numpy_types(obj):
    """Convertit récursivement les types NumPy en types Python natifs"""
    if isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, np.bool_):
        return bool(obj)
    else:
        return obj

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
    
    print(f"📁 Base dir: {BASE_DIR}")
    print(f"📁 Raw dir: {RAW_DIR}")
    print(f"📁 Processed dir: {PROCESSED_DIR}")
    print(f"📁 Warehouse dir: {WAREHOUSE_DIR}")
    
    # Vérifier que le répertoire raw existe
    if not RAW_DIR.exists():
        logger.error(f"❌ Le répertoire raw n'existe pas: {RAW_DIR}")
        logger.info("📥 Exécute d'abord l'extraction avec: python etl/main_etl.py")
        return
    
    # S'assurer que les répertoires existent
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    WAREHOUSE_DIR.mkdir(parents=True, exist_ok=True)
    
    quality_reports = []
    
    try:
        # 1. Transformation Back on Track
        print("\n" + "="*60)
        print("TRANSFORMATION BACK ON TRACK")
        print("="*60)
        report1 = transform_back_on_track(str(RAW_DIR), str(PROCESSED_DIR))
        if report1:
            quality_reports.append(convert_numpy_types(report1))
        
        # 2. Transformation Eurostat
        print("\n" + "="*60)
        print("TRANSFORMATION EUROSTAT")
        print("="*60)
        report2 = transform_eurostat(str(RAW_DIR), str(PROCESSED_DIR))
        if report2:
            quality_reports.append(convert_numpy_types(report2))
        
        # 3. Transformation Émissions
        print("\n" + "="*60)
        print("TRANSFORMATION ÉMISSIONS CO2")
        print("="*60)
        report3 = transform_emissions(str(RAW_DIR), str(PROCESSED_DIR))
        if report3:
            quality_reports.append(convert_numpy_types(report3))
        
        # 4. Transformation GTFS
        print("\n" + "="*60)
        print("TRANSFORMATION GTFS (FR, CH, DE)")
        print("="*60)
        reports_gtfs = transform_all_gtfs(str(RAW_DIR), str(PROCESSED_DIR))
        if reports_gtfs:
            quality_reports.extend([convert_numpy_types(r) for r in reports_gtfs if r])
        
        # 5. Enrichissement et préparation pour le data warehouse
        print("\n" + "="*60)
        print("ENRICHISSEMENT ET PRÉPARATION DATA WAREHOUSE")
        print("="*60)
        traceability_report = enrich_and_prepare_for_warehouse(
            str(PROCESSED_DIR), 
            str(WAREHOUSE_DIR)
        )
        
        # Convertir le rapport de traçabilité
        traceability_report = convert_numpy_types(traceability_report) if traceability_report else {}
        
        # 6. Sauvegarder les rapports de qualité
        quality_report_path = WAREHOUSE_DIR / "quality_reports.json"
        
        # Préparer les données pour JSON
        report_data = {
            'execution_date': datetime.now().isoformat(),
            'project': 'ObRail Europe - MSPR E6.1',
            'reports': quality_reports,
            'traceability': traceability_report,
            'summary': {
                'total_sources_processed': len(quality_reports),
                'total_records_estimated': sum(
                    r.get('total_records', 
                          r.get('passengers_records', 
                                r.get('traffic_records',
                                      r.get('agencies', 0)))) 
                    for r in quality_reports if r
                ),
                'success': True
            }
        }
        
        # Convertir les valeurs NumPy en Python natif
        report_data = convert_numpy_types(report_data)
        
        with open(quality_report_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False, cls=NumpyEncoder)
        
        print("\n" + "="*60)
        print("✅ PIPELINE DE TRANSFORMATION TERMINÉ AVEC SUCCÈS!")
        print("="*60)
        print(f"📊 Rapports sauvegardés dans: {quality_report_path}")
        print(f"📁 Data warehouse prêt dans: {WAREHOUSE_DIR}")
        
        # Afficher un résumé
        print("\n" + "="*60)
        print("RÉSUMÉ DE LA TRANSFORMATION")
        print("="*60)
        
        total_records = 0
        for report in quality_reports:
            if report:
                source = report.get('source', 'Inconnu').upper()
                records = report.get('total_records', 
                                   report.get('passengers_records',
                                            report.get('traffic_records',
                                                     report.get('agencies', 0))))
                records = records if records else 0
                total_records += records
                status = "✅" if records else "⚠️"
                print(f"{status} {source:<25} : {records:,} enregistrements")
        
        print("-"*60)
        print(f"📈 {'TOTAL':<25} : {total_records:,} enregistrements")
        print("="*60)
        
        # Vérifier les fichiers générés
        print("\n📁 CONTENU DU DATA WAREHOUSE:")
        print("-"*40)
        
        csv_files = []
        json_files = []
        
        for file in WAREHOUSE_DIR.glob("*.csv"):
            csv_files.append(file)
            # Compter les lignes pour info
            try:
                import pandas as pd
                df = pd.read_csv(file)
                print(f"📄 {file.name:<40} ({len(df):,} lignes)")
            except:
                print(f"📄 {file.name}")
        
        for file in WAREHOUSE_DIR.glob("*.json"):
            json_files.append(file)
            print(f"📋 {file.name}")
        
        if not csv_files and not json_files:
            print("❌ Aucun fichier trouvé dans le data warehouse")
        
        # Afficher aussi le contenu de processed
        print("\n📁 CONTENU DU RÉPERTOIRE PROCESSED:")
        print("-"*40)
        for source_dir in PROCESSED_DIR.iterdir():
            if source_dir.is_dir():
                csv_count = len(list(source_dir.rglob("*.csv")))
                if csv_count > 0:
                    print(f"📂 {source_dir.name:<20} : {csv_count} fichier(s)")
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de la transformation: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    main_transform_pipeline()