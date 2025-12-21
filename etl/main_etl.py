# =========================================================
# etl/main_etl.py
# Pipeline ETL principal – ObRail Europe (MSPR E6.1)
# =========================================================

from extract.extract_gtfs_fr import extract_gtfs_fr


def run_etl():
    print("🚆 DÉMARRAGE DU PIPELINE ETL – ObRail Europe")

    print("\n[1/3] Extraction GTFS France (SNCF)")
    extract_gtfs_fr()


    print("\n✅ EXTRACTION TERMINÉE – Données disponibles dans data/raw/")


if __name__ == "__main__":
    run_etl()


