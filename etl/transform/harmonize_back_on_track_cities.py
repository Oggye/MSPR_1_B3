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
    print(f"  Lignes dans le fichier source: {len(df)}")
    
    # Traitement des valeurs manquantes avant sélection
    if "stop_cityname_romanized" in df.columns:
        df["stop_cityname_romanized"] = df["stop_cityname_romanized"].fillna("Inconnu")
    
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
    
    # Nettoyage des chaînes
    cities["city_name"] = cities["city_name"].astype(str).str.strip()
    cities["country_code"] = cities["country_code"].astype(str).str.strip()
    
    # Remplacer les chaînes vides par NaN
    cities["city_name"] = cities["city_name"].replace(["", "nan", "NaN"], pd.NA)
    cities["country_code"] = cities["country_code"].replace(["", "nan", "NaN"], pd.NA)
    
    # Supprimer les lignes où le nom de ville est NaN ou "Inconnu"
    cities = cities[~cities["city_name"].isna()]
    cities = cities[cities["city_name"] != "Inconnu"]
    
    # Normalisation du code pays en majuscules pour cohérence
    cities["country_code"] = cities["country_code"].str.upper()
    
    # Élimination des doublons sur l'association (city_name, country_code)
    initial_count = len(cities)
    cities = cities.drop_duplicates(subset=["city_name", "country_code"])
    duplicate_removed = initial_count - len(cities)
    if duplicate_removed > 0:
        print(f"  Doublons supprimés: {duplicate_removed}")
    
    # Écriture du fichier harmonisé dans l'entrepôt
    output_file = WAREHOUSE_DIR / "cities.csv"
    cities.to_csv(output_file, index=False)
    
    print(f"  Lignes finales: {len(cities)}")
    print(f"✔ cities.csv généré → {output_file}")


if __name__ == "__main__":
    harmonize_back_on_track_cities()