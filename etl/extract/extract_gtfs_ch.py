# =========================================================
# ETL / extract / extract_gtfs_ch.py
# Extraction du GTFS Suisse (sans conversion inutile)
# =========================================================

import requests
import zipfile
import io
from pathlib import Path

GTFS_CH_URL = (
    "https://data.opentransportdata.swiss/dataset/6cca1dfb-e53d-4da8-8d49-4797b3e768e3/"
    "resource/d5d9aac1-8251-4dda-9537-ae97cbb810c6/download/gtfs_fp2025_20251211.zip"
)

RAW_DIR = Path("data/raw/gtfs_ch")

KEEP_FILES = {
    "routes.txt",
    "trips.txt",
    "stop_times.txt",
    "stops.txt",
    "calendar_dates.txt",
    "agency.txt",
}

def extract_gtfs_ch():
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    print("📥 Téléchargement du GTFS Suisse...")
    response = requests.get(GTFS_CH_URL, stream=True)
    response.raise_for_status()

    print("📦 Ouverture de l’archive ZIP...")
    with zipfile.ZipFile(io.BytesIO(response.content)) as zip_file:
        for file_name in zip_file.namelist():
            if file_name in KEEP_FILES:
                print(f"➡️  Extraction de {file_name}")
                zip_file.extract(file_name, RAW_DIR)

    print("\n✅ GTFS Suisse extrait avec succès :")
    for file in RAW_DIR.iterdir():
        print(" -", file.name)

    for file in RAW_DIR.glob("*.txt"):
        file.rename(file.with_suffix(".csv"))
        print("\nFichiers .txt convertis en .csv")

