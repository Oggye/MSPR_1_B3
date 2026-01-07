# =========================================================
# Nettoyage GTFS France – ObRail Europe
# =========================================================

import pandas as pd
from pathlib import Path

RAW_DIR = Path("data/raw/gtfs_fr")
PROCESSED_DIR = Path("data/processed/gtfs_fr")
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------
# AGENCY
# ---------------------------------------------------------
def clean_agency():
    print("\n Nettoyage agency.csv")

    df = pd.read_csv(RAW_DIR / "agency.csv")

    df = df[[
        "agency_id",
        "agency_name",
        "agency_url"
    ]]

    df.drop_duplicates(inplace=True)

    df.to_csv(PROCESSED_DIR / "agency_clean.csv", index=False)
    print("✔ agency_clean.csv créé")

# ---------------------------------------------------------
# ROUTES
# ---------------------------------------------------------
def clean_routes():
    print("\n Nettoyage routes.csv")

    df = pd.read_csv(RAW_DIR / "routes.csv")

    # garder uniquement les lignes ferroviaires (2 = rail)
    df = df[df["route_type"] == 2]

    df = df[[
        "route_id",
        "agency_id",
        "route_long_name"
    ]]

    df.drop_duplicates(inplace=True)

    df.to_csv(PROCESSED_DIR / "routes_clean.csv", index=False)
    print("✔ routes_clean.csv créé")

# ---------------------------------------------------------
# STOPS
# ---------------------------------------------------------
def clean_stops():
    print("\n Nettoyage stops.csv")

    df = pd.read_csv(RAW_DIR / "stops.csv")

    # garder uniquement les gares
    df = df[df["location_type"] == 0]

    df = df[[
        "stop_id",
        "stop_name",
        "stop_lat",
        "stop_lon"
    ]]

    df.drop_duplicates(inplace=True)

    df.to_csv(PROCESSED_DIR / "stops_clean.csv", index=False)
    print("✔ stops_clean.csv créé")

# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------
if __name__ == "__main__":
    print(" NETTOYAGE GTFS FRANCE")

    clean_agency()
    clean_routes()
    clean_stops()

    print("\n Nettoyage GTFS terminé")
