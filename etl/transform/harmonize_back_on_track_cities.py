# =========================================================
# ETL/transform/harmonize_back_on_track_cities.py
# Harmonisation des villes Back-on-Track – ObRail Europe
# =========================================================


"""
Harmonisation des villes 'Back-on-Track'.

Ce module lit le fichier traité `view_ontd_cities.csv` (dossier
`data/processed/back_on_track`), sélectionne les colonnes utiles pour la
méthode métier, normalise et nettoie les valeurs puis écrit le résultat
dans `data/warehouse/cities.csv`.
"""

import pandas as pd
from pathlib import Path

# Répertoire contenant les fichiers traités pour 'back_on_track'
PROCESSED_DIR = Path("data/processed/back_on_track")
# Répertoire de sortie (entrepôt). On s'assure qu'il existe.
WAREHOUSE_DIR = Path("data/warehouse")
WAREHOUSE_DIR.mkdir(parents=True, exist_ok=True)


def harmonize_back_on_track_cities():
    """Génère `cities.csv` à partir de `view_ontd_cities.csv`.

    Étapes réalisées :
    - Chargement du CSV source
    - Sélection et renommage des colonnes pertinentes
    - Nettoyage des chaînes (trim + conversion en str pour éviter NaN)
    - Normalisation des codes pays en majuscules
    - Suppression des doublons (par nom de ville + code pays)
    - Écriture du fichier `cities.csv` dans l'entrepôt
    """

    # Message de suivi dans la console
    print("\n HARMONISATION – Villes Back-on-Track")

    file = PROCESSED_DIR / "view_ontd_cities.csv"
    print(f"Traitement : {file.name}")

    # Lecture du fichier source
    df = pd.read_csv(file)

    # Sélection des colonnes utiles et renommage vers le schéma cible
    cities = df[[
        "stop_id",
        "stop_cityname_romanized",
        "stop_country"
    ]].rename(columns={
        "stop_id": "city_id",
        "stop_cityname_romanized": "city_name",
        "stop_country": "country_code"
    })

    # Nettoyage des chaînes : conversion en str (évite les NaN), suppression
    # des espaces en début/fin
    for col in ["city_name", "country_code"]:
        cities[col] = cities[col].astype(str).str.strip()

    # Normalisation du code pays en majuscules pour cohérence
    cities["country_code"] = cities["country_code"].str.upper()

    # Élimination des doublons sur l'association (city_name, country_code)
    cities = cities.drop_duplicates(subset=["city_name", "country_code"])

    # Écriture du fichier harmonisé dans l'entrepôt
    cities.to_csv(WAREHOUSE_DIR / "cities.csv", index=False)

    print("✔ cities.csv généré")


if __name__ == "__main__":
    harmonize_back_on_track_cities()
