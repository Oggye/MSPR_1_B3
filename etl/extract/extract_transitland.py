# =========================================================
# etl/extract/extract_transitland.py
# =========================================================

import requests
import json
from pathlib import Path

TRANSITLAND_URL = "https://transit.land/api/v2/rest/feeds"
RAW_DIR = Path("data/raw/transitland")


def extract_transitland():
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    params = {"country": "FR"}
    print("Appel API Transit.land…")

    response = requests.get(TRANSITLAND_URL, params=params)
    response.raise_for_status()

    data = response.json()

    output_file = RAW_DIR / "feeds_fr.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print(f"{len(data.get('feeds', []))} feeds Transit.land sauvegardés")
