# =========================================================
# ETL/main_etl.py
# Pipeline ETL principal – ObRail Europe (MSPR E6.1)
# =========================================================

# --- EXTRACTION ---
from etl.extract.extract_gtfs_fr import extract_gtfs_fr
from etl.extract.extract_eurostat import extract_eurostat
from etl.extract.extract_back_on_track_eu import extract_back_on_track

# --- NETTOYAGE ---
from etl.transform.clean_gtfs_fr import clean_agency, clean_routes, clean_stops
from etl.transform.clean_eurostat import clean_eurostat
from etl.transform.clean_back_on_track import clean_back_on_track

# --- HARMONISATION ---
from etl.transform.harmonize_back_on_track import harmonize_back_on_track
from etl.transform.harmonize_back_on_track_cities import harmonize_back_on_track_cities
from etl.transform.harmonize_operators import harmonize_operators
from etl.transform.harmonize_countries import harmonize_countries


def run_etl():
    print("🚆 DÉMARRAGE DU PIPELINE ETL – ObRail Europe")

    # -----------------------------
    print("\n[1/9] Extraction GTFS France (SNCF)")
    extract_gtfs_fr()

    # -----------------------------
    print("\n[2/9] Extraction Eurostat (trafic et passagers)")
    extract_eurostat()

    # -----------------------------
    print("\n[3/9] Extraction Back-on-Track Europe (trains de nuit & villes)")
    extract_back_on_track()

    print("\n✅ EXTRACTION TERMINÉE – Données disponibles dans data/raw/")

    # -----------------------------
    print("\n[4/9] Nettoyage GTFS France")
    clean_agency()
    clean_routes()
    clean_stops()

    # -----------------------------
    print("\n[5/9] Nettoyage Eurostat")
    clean_eurostat()

    # -----------------------------
    print("\n[6/9] Nettoyage Back-on-Track")
    clean_back_on_track()

    print("\n✅ NETTOYAGE TERMINÉ – Données disponibles dans data/processed/")

    # -----------------------------
    print("\n[7/9] Harmonisation Back-on-Track (routes + pays)")
    harmonize_back_on_track()

    # -----------------------------
    print("\n[8/9] Harmonisation Back-on-Track (villes)")
    harmonize_back_on_track_cities()

    # -----------------------------
    print("\n[9/9] Harmonisation référentiels (opérateurs, pays)")
    harmonize_operators()
    harmonize_countries()

    print("\n✅ HARMONISATION TERMINÉE – Données disponibles dans data/warehouse/")

    print("\nPROCESSUS ETL COMPLET – extraction, nettoyage, harmonisation terminés")


if __name__ == "__main__":
    run_etl()
