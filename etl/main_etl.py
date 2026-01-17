# =========================================================
# ETL/main_etl.py
# Pipeline ETL principal – ObRail Europe (MSPR E6.1)
# =========================================================

import time
from datetime import datetime

# --- EXTRACTION ---
from extract.extract_gtfs_fr import extract_gtfs_fr
from extract.extract_eurostat import extract_eurostat
from extract.extract_back_on_track_eu import extract_back_on_track
from extract.extract_gtfs_ch import extract_gtfs_ch
from extract.extract_gtfs_de import extract_gtfs_de
from extract.extract_emission_co2 import download_eurostat_via_api

# --- TRANSFORMATION ---
from transform.main_transform import main as run_transform_pipeline


def run_etl():
    print("🚀 Lancement du pipeline ETL ObRail Europe")
    print(f"Date et heure : {datetime.now()}")
    print("=" * 60)
    
    # =====================================================
    # PHASE 1 : EXTRACTION
    # =====================================================
    print("📥 PHASE 1 : EXTRACTION")
    print("-" * 40)
    
    extractors = [
        ("GTFS France", extract_gtfs_fr),
        ("Eurostat (trafic ferroviaire)", extract_eurostat),
        ("Back on Track EU", extract_back_on_track),
        ("GTFS Suisse", extract_gtfs_ch),
        ("GTFS Allemagne", extract_gtfs_de),
        ("Émissions CO2", download_eurostat_via_api),
    ]
    
    for name, func in extractors:
        print(f"📄 Extraction de {name}...")
        try:
            func()
            print(f"✅ {name} extrait avec succès")
        except Exception as e:
            print(f"❌ Erreur lors de l'extraction de {name}: {e}")
        print()
    
    print("✅ PHASE EXTRACTION TERMINÉE")
    print("=" * 60)
    
    # =====================================================
    # PHASE 2 : TRANSFORMATION
    # =====================================================
    print("🔄 PHASE 2 : TRANSFORMATION")
    print("-" * 40)
    
    try:
        run_transform_pipeline()
        print("✅ Transformation terminée avec succès")
    except Exception as e:
        print(f"❌ Erreur critique pendant la transformation : {e}")
        raise
    
    print("=" * 60)
    
    # =====================================================
    # PHASE 3 : CHARGEMENT (À VENIR)
    # =====================================================
    print("💾 PHASE 3 : CHARGEMENT")
    print("-" * 40)
    print("⏳ Phase chargement à implémenter (Data Warehouse / DB / BI)")
    time.sleep(1)
    print("✅ Chargement terminé (placeholder)")
    print("=" * 60)
    
    print("🎉 PIPELINE ETL TERMINÉ AVEC SUCCÈS")


if __name__ == "__main__":
    run_etl()
