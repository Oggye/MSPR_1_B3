# =========================================================
# ETL/audit/quick_audit.py
# Audit rapide - Aperçu des 10 premières lignes
# =========================================================

import pandas as pd
from pathlib import Path

def quick_audit():
    """Affiche les 10 premières lignes de chaque fichier du pipeline."""
    
    # Liste de tous les fichiers à auditer
    files_to_check = [
        # RAW
        ("RAW - back_on_track", Path("data/raw/back_on_track/view_ontd_list.csv")),
        ("RAW - back_on_track", Path("data/raw/back_on_track/view_ontd_cities.csv")),
        ("RAW - eurostat", Path("data/raw/eurostat/rail_pas.csv")),
        ("RAW - gtfs_fr", Path("data/raw/gtfs_fr/stops.csv")),
        ("RAW - gtfs_fr", Path("data/raw/gtfs_fr/routes.csv")),
        ("RAW - gtfs_fr", Path("data/raw/gtfs_fr/agency.csv")),
        
        # PROCESSED
        ("PROCESSED - back_on_track", Path("data/processed/back_on_track/view_ontd_list.csv")),
        ("PROCESSED - back_on_track", Path("data/processed/back_on_track/view_ontd_cities.csv")),
        ("PROCESSED - eurostat", Path("data/processed/eurostat/rail_pas_clean.csv")),
        ("PROCESSED - gtfs_fr", Path("data/processed/gtfs_fr/stops_clean.csv")),
        ("PROCESSED - gtfs_fr", Path("data/processed/gtfs_fr/routes_clean.csv")),
        ("PROCESSED - gtfs_fr", Path("data/processed/gtfs_fr/agency_clean.csv")),
        
        # WAREHOUSE
        ("WAREHOUSE", Path("data/warehouse/routes.csv")),
        ("WAREHOUSE", Path("data/warehouse/cities.csv")),
        ("WAREHOUSE", Path("data/warehouse/countries.csv")),
        ("WAREHOUSE", Path("data/warehouse/operators.csv")),
        ("WAREHOUSE", Path("data/warehouse/route_countries.csv")),
    ]
    
    print("🔍 AUDIT RAPIDE - 10 PREMIÈRES LIGNES")
    print("=" * 80)
    
    for category, file_path in files_to_check:
        print(f"\n{'='*40}")
        print(f"📁 {category}")
        print(f"📄 {file_path.name}")
        print(f"{'='*40}")
        
        if not file_path.exists():
            print("❌ FICHIER INTROUVABLE")
            continue
        
        try:
            df = pd.read_csv(file_path)
            print(f"📊 Dimensions: {df.shape[0]} lignes × {df.shape[1]} colonnes")
            print(f"📋 Colonnes: {list(df.columns)}")
            
            print("\n📝 CONTENU (10 premières lignes):")
            print("-" * 40)
            
            # Configurer pandas pour un affichage large
            pd.set_option('display.max_columns', None)
            pd.set_option('display.width', None)
            pd.set_option('display.max_colwidth', 30)
            
            if len(df) > 0:
                print(df.head(10).to_string())
            else:
                print("⚠️ FICHIER VIDE")
                
        except Exception as e:
            print(f"❌ ERREUR DE LECTURE: {str(e)}")
        
        print("-" * 40)
    
    print("\n" + "=" * 80)
    print("✅ AUDIT RAPIDE TERMINÉ")

if __name__ == "__main__":
    quick_audit()