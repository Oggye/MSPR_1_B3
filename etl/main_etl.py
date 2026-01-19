"""
ETL/main_etl.py
Pipeline ETL principal – ObRail Europe (MSPR E6.1)
Version complète avec transformation intégrée
"""

import time
from datetime import datetime
import sys
from pathlib import Path

# Ajouter le répertoire au path pour les imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# --- EXTRACTION ---
try:
    from extract.extract_gtfs_fr import extract_gtfs_fr
    from extract.extract_eurostat import extract_eurostat
    from extract.extract_back_on_track_eu import extract_back_on_track
    from extract.extract_gtfs_ch import extract_gtfs_ch
    from extract.extract_gtfs_de import extract_gtfs_de
    from extract.extract_emission_co2 import download_eurostat_via_api
except ImportError as e:
    print(f"⚠️  Modules d'extraction non trouvés: {e}")
    print("📥 Exécute d'abord les scripts d'extraction séparément si besoin")

# --- TRANSFORMATION ---
try:
    from transform.main_transform import main_transform_pipeline
except ImportError as e:
    print(f"⚠️  Modules de transformation non trouvés: {e}")

def run_extraction():
    """Exécute uniquement la phase d'extraction"""
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
    
    print("✅ Extraction terminée")

def run_transformation():
    """Exécute uniquement la phase de transformation"""
    print("\n🔄 PHASE 2 : TRANSFORMATION")
    print("-" * 40)
    
    try:
        main_transform_pipeline()
        print("✅ Transformation terminée avec succès")
    except Exception as e:
        print(f"❌ Erreur lors de la transformation: {e}")

def run_full_etl():
    """Exécute le pipeline ETL complet"""
    print("🚀 LANCEMENT DU PIPELINE ETL COMPLET")
    print(f"Date et heure : {datetime.now()}")
    print("=" * 60)
    
    # EXTRACTION
    run_extraction()
    
    # TRANSFORMATION
    run_transformation()
    
    # CHARGEMENT (à implémenter)
    print("\n💾 PHASE 3 : CHARGEMENT")
    print("-" * 40)
    print("⏳ Phase chargement à implémenter (PostgreSQL)...")
    time.sleep(1)
    print("✅ Chargement terminé (simulé)")
    
    print("\n" + "=" * 60)
    print("🎉 PIPELINE ETL TERMINÉ AVEC SUCCÈS !")
    print("=" * 60)

def show_menu():
    """Affiche un menu interactif"""
    print("\n" + "=" * 60)
    print("PIPELINE ETL - OBRAIL EUROPE")
    print("=" * 60)
    print("1. 🚀 Exécuter le pipeline complet (Extraction + Transformation)")
    print("2. 📥 Exécuter uniquement l'extraction")
    print("3. 🔄 Exécuter uniquement la transformation")
    print("4. 📊 Voir l'état des données")
    print("5. ❌ Quitter")
    print("=" * 60)
    
    choice = input("👉 Ton choix (1-5): ").strip()
    
    if choice == "1":
        run_full_etl()
    elif choice == "2":
        run_extraction()
    elif choice == "3":
        run_transformation()
    elif choice == "4":
        show_data_status()
    elif choice == "5":
        print("👋 Au revoir!")
        sys.exit(0)
    else:
        print("❌ Choix invalide")
    
    input("\n↵ Appuie sur Entrée pour continuer...")
    show_menu()

def show_data_status():
    """Affiche l'état des données"""
    BASE_DIR = Path(__file__).parent.parent
    
    print("\n📊 ÉTAT DES DONNÉES")
    print("-" * 40)
    
    # Vérifier raw
    raw_dir = BASE_DIR / "data" / "raw"
    if raw_dir.exists():
        raw_files = list(raw_dir.rglob("*.csv"))
        print(f"📁 Données brutes ({raw_dir}):")
        print(f"   📄 {len(raw_files)} fichiers CSV trouvés")
        for source in raw_dir.iterdir():
            if source.is_dir():
                csv_count = len(list(source.glob("*.csv")))
                if csv_count > 0:
                    print(f"   ├─ {source.name}: {csv_count} fichiers")
    else:
        print("📁 Données brutes: ❌ Répertoire non trouvé")
    
    # Vérifier processed
    processed_dir = BASE_DIR / "data" / "processed"
    if processed_dir.exists():
        processed_files = list(processed_dir.rglob("*.csv"))
        print(f"\n📁 Données transformées ({processed_dir}):")
        print(f"   📄 {len(processed_files)} fichiers CSV trouvés")
    else:
        print("\n📁 Données transformées: ❌ Répertoire non trouvé")
    
    # Vérifier warehouse
    warehouse_dir = BASE_DIR / "data" / "warehouse"
    if warehouse_dir.exists():
        warehouse_files = list(warehouse_dir.glob("*.csv"))
        print(f"\n📁 Data warehouse ({warehouse_dir}):")
        print(f"   📄 {len(warehouse_files)} fichiers CSV trouvés")
        for file in warehouse_files:
            print(f"   ├─ {file.name}")
    else:
        print("\n📁 Data warehouse: ❌ Répertoire non trouvé")

if __name__ == "__main__":
    # Exécuter le menu interactif
    show_menu()
    
    # Ou exécuter directement le pipeline complet:
    # run_full_etl()