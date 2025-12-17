# =========================================================
# etl/extract/extract_eurostat.py
# =========================================================

import requests
from pathlib import Path

EUROSTAT_URL = "https://ec.europa.eu/eurostat/api/dissemination/files"
RAW_DIR = Path("data/raw/eurostat")


def extract_eurostat():
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    print("Téléchargement métadonnées Eurostat…")
    response = requests.get(EUROSTAT_URL)
    response.raise_for_status()

    output_file = RAW_DIR / "eurostat_files.json"
    with open(output_file, "wb") as f:
        f.write(response.content)

    print("Données Eurostat sauvegardées")
