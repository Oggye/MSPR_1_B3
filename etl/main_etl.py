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

# --- NETTOYAGE ---
from transform.clean_gtfs_fr import clean_agency, clean_routes, clean_stops
from transform.clean_eurostat import clean_eurostat
from transform.clean_back_on_track import clean_back_on_track

# --- HARMONISATION ---
from transform.harmonize_back_on_track import harmonize_back_on_track
from transform.harmonize_back_on_track_cities import harmonize_back_on_track_cities
from transform.harmonize_operators import harmonize_operators
from transform.harmonize_countries import harmonize_countries

# --- NOUVEAUX MODULES ---
from transform.integrate_gtfs import integrate_gtfs_france
from transform.audit_data_loss import main as audit_data_loss

def etape(description):
    """Affiche une étape avec timing."""
    def decorator(func):
        def wrapper():
            print(f"\n{'='*60}")
            print(f"▶️  {description}")
            print(f"{'='*60}")
            start = time.time()
            
            try:
                func()
                temps = time.time() - start
                print(f"✅ Terminé ({temps:.1f}s)")
            except Exception as e:
                temps = time.time() - start
                print(f"❌ Erreur ({temps:.1f}s): {e}")
                raise
                
        return wrapper
    return decorator

def check_dossiers():
    """Vérifie que les dossiers existent."""
    import os
    dossiers = [
        "data/raw/back_on_track",
        "data/raw/eurostat",
        "data/raw/gtfs_fr",
        "data/processed/back_on_track",
        "data/processed/eurostat",
        "data/processed/gtfs_fr",
        "data/warehouse"
    ]
    
    for dossier in dossiers:
        os.makedirs(dossier, exist_ok=True)
        print(f"✓ {dossier}")

def run_etl(phases=None, audit=True):
    """
    Exécute le pipeline ETL.
    
    Args:
        phases (list): None pour tout, ou liste de phases ['extraction', 'nettoyage', 'harmonisation']
        audit (bool): Si True, exécute l'audit à la fin
    """
    print("="*60)
    print("🚂 DÉMARRAGE DU PIPELINE ETL – ObRail Europe")
    print(f"🕒 Début: {datetime.now().strftime('%H:%M:%S')}")
    print("="*60)
    
    print("\n📁 Vérification des dossiers...")
    check_dossiers()
    
    start_total = time.time()
    
    # PHASE 1: EXTRACTION
    if phases is None or 'extraction' in phases:
        print("\n" + "="*60)
        print("📥 PHASE 1 - EXTRACTION")
        print("="*60)
        
        @etape("Extraction GTFS France (SNCF)")
        def step1():
            extract_gtfs_fr()
        
        @etape("Extraction Eurostat")
        def step2():
            extract_eurostat()
        
        @etape("Extraction Back-on-Track")
        def step3():
            extract_back_on_track()
        
        step1()
        step2()
        step3()
    
    # PHASE 2: NETTOYAGE
    if phases is None or 'nettoyage' in phases:
        print("\n" + "="*60)
        print("🧹 PHASE 2 - NETTOYAGE")
        print("="*60)
        
        @etape("Nettoyage GTFS France - Agences")
        def step4():
            clean_agency()
        
        @etape("Nettoyage GTFS France - Lignes")
        def step5():
            clean_routes()
        
        @etape("Nettoyage GTFS France - Arrêts")
        def step6():
            clean_stops()
        
        @etape("Nettoyage Eurostat")
        def step7():
            clean_eurostat()
        
        @etape("Nettoyage Back-on-Track")
        def step8():
            clean_back_on_track()
        
        step4()
        step5()
        step6()
        step7()
        step8()
    
    # PHASE 3: HARMONISATION
    if phases is None or 'harmonisation' in phases:
        print("\n" + "="*60)
        print("🔄 PHASE 3 - HARMONISATION")
        print("="*60)
        
        @etape("Harmonisation Back-on-Track (routes)")
        def step9():
            harmonize_back_on_track()
        
        @etape("Harmonisation Back-on-Track (villes)")
        def step10():
            harmonize_back_on_track_cities()
        
        @etape("Harmonisation des opérateurs")
        def step11():
            harmonize_operators()
        
        @etape("Harmonisation des pays")
        def step12():
            harmonize_countries()
        
        @etape("Intégration GTFS France")
        def step13():
            integrate_gtfs_france()
        
        step9()
        step10()
        step11()
        step12()
        step13()
    
    # AUDIT
    if audit:
        print("\n" + "="*60)
        print("🔍 AUDIT FINAL")
        print("="*60)
        
        @etape("Vérification des pertes de données")
        def step14():
            audit_data_loss()
        
        step14()
    
    # RÉSUMÉ
    total_time = time.time() - start_total
    
    print("\n" + "="*60)
    print("🎉 PIPELINE TERMINÉ")
    print("="*60)
    print(f"⏱️  Temps total: {total_time:.1f} secondes")
    print(f"🕒 Fin: {datetime.now().strftime('%H:%M:%S')}")
    print("\n📊 Données disponibles dans:")
    print("   • data/raw/       - Données brutes")
    print("   • data/processed/ - Données nettoyées")
    print("   • data/warehouse/ - Données finales")
    print("="*60)

def run_complet():
    """Exécute tout le pipeline."""
    run_etl()

def run_extraction_seulement():
    """Exécute seulement l'extraction."""
    run_etl(phases=['extraction'], audit=False)

def run_sans_audit():
    """Exécute sans l'audit final."""
    run_etl(audit=False)

if __name__ == "__main__":
    # Exécute tout le pipeline par défaut
    run_complet()
    
    # Pour exécuter seulement certaines parties :
    # run_extraction_seulement()
    # run_sans_audit()
    # run_etl(phases=['extraction', 'nettoyage'])