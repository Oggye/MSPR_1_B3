# =========================================================
# etl/extract/extract_gtfs_de.py
# =========================================================

import requests
import zipfile
import io
from pathlib import Path
import csv
from datetime import datetime

GTFS_DE_URL = "https://download.gtfs.de/germany/fv_free/latest.zip" 
RAW_DIR = Path("data/raw/gtfs_de")
KEEP_FILES = [
    "routes.txt",
    "trips.txt",
    "stop_times.txt",
    "stops.txt",
    "calendar_dates.txt",
    "agency.txt",
]

def extract_gtfs_de():
    """
    Extrait les données GTFS d'Allemagne (Deutsche Bahn)
    Contient les données de tous les opérateurs allemands (DB, etc.)
    """
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    print("Téléchargement du GTFS Allemagne (Deutsche Bahn)…")
    response = requests.get(GTFS_DE_URL)
    response.raise_for_status()

    with zipfile.ZipFile(io.BytesIO(response.content)) as z:
        for file_name in KEEP_FILES:
            if file_name in z.namelist():
                txt_path = Path(z.extract(file_name, RAW_DIR))
                
                # Transformation en CSV
                csv_path = txt_path.with_suffix(".csv")
                with open(txt_path, "r", encoding="utf-8") as txt_file, \
                     open(csv_path, "w", newline="", encoding="utf-8") as csv_file:
                    reader = csv.reader(txt_file)
                    writer = csv.writer(csv_file)
                    for row in reader:
                        writer.writerow(row)
                
                # Suppression du fichier .txt
                txt_path.unlink()

    print("GTFS Allemagne extrait et converti en CSV :")
    for file in RAW_DIR.iterdir():
        if file.suffix == ".csv":
            print(" -", file.name)
    
    # Ajout d'un fichier de métadonnées
    metadata = {
        "source": "Deutsche Bahn GTFS",
        "url": GTFS_DE_URL,
        "date_extraction": datetime.now().isoformat(),
        "description": "Données complètes des transports ferroviaires allemands (trains de jour)",
        "coverage": "Allemagne entière",
        "format": "GTFS standard"
    }
    
    import json
    with open(RAW_DIR / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    extract_gtfs_de()

