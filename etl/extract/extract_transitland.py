# =========================================================
# etl/extract/extract_transitland.py
# =========================================================

import requests
import json
import os
from pathlib import Path


TRANSITLAND_URL = "https://transit.land/api/v2/rest/feeds"
RAW_DIR = Path("data/raw/transitland")


# Transit.land nécessite une clé API
# Clé à définir dans le fichier .env : TRANSITLAND_API_KEY=xxxxx


def extract_transitland():
RAW_DIR.mkdir(parents=True, exist_ok=True)


api_key = os.getenv("TRANSITLAND_API_KEY")


if not api_key:
print("⚠️ Transit.land API KEY manquante → extraction ignorée")
print("➡️ Ajoute TRANSITLAND_API_KEY dans ton fichier .env")
return


headers = {
"Authorization": f"Bearer {api_key}"
}


params = {"country": "FR"}

print("Appel API Transit.land avec authentification…")
response = requests.get(TRANSITLAND_URL, headers=headers, params=params)
response.raise_for_status()


data = response.json()


output_file = RAW_DIR / "feeds_fr.json"
with open(output_file, "w", encoding="utf-8") as f:
json.dump(data, f, indent=2)


print(f"{len(data.get('feeds', []))} feeds Transit.land sauvegardés")

