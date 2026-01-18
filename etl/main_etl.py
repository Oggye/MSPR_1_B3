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
# (à compléter plus tard)

# --- CHARGEMENT ---
# (à compléter plus tard)

def run_etl():
    print("🚀 Lancement du pipeline ETL...")
    print(f"Date et heure : {datetime.now()}")
    print("=" * 50)
    
    # EXTRACTION
    print("📥 PHASE 1 : EXTRACTION")
    print("-" * 30)
    
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
    
    print("✅ Extraction terminée")
    print("=" * 50)
    
    # TRANSFORMATION (à venir)
    print("🔄 PHASE 2 : TRANSFORMATION")
    print("-" * 30)
    print("⏳ Phase transformation à implémenter...")
    time.sleep(1)
    print("✅ Transformation terminée (simulée)")
    print("=" * 50)
    
    # CHARGEMENT (à venir)
    print("💾 PHASE 3 : CHARGEMENT")
    print("-" * 30)
    print("⏳ Phase chargement à implémenter...")
    time.sleep(1)
    print("✅ Chargement terminé (simulé)")
    print("=" * 50)
    
    print("🎉 Pipeline ETL terminé avec succès !")

if __name__ == "__main__":
    run_etl()