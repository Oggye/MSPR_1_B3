# =========================================================
# ETL/transform/harmonize_back_on_track.py
# harmonisation Back-on-Track – ObRail Europe
# =========================================================

"""
Harmonisation des données Back-on-Track.

Ce module transforme le fichier traité `view_ontd_list.csv` (dossier
`data/processed/back_on_track`) pour produire :
- `routes.csv` : table des liaisons/routes avec les champs métiers sélectionnés
- `route_countries.csv` : association route <-> code pays (une ligne par couple)

Le script normalise les opérateurs, décompose la liste de pays et sauvegarde
les résultats dans `data/warehouse`.
"""

import pandas as pd
from pathlib import Path

# Dossier contenant les fichiers traités Back-on-Track
PROCESSED_DIR = Path("data/processed/back_on_track")
# Dossier de l'entrepôt de données : sortie des tables harmonisées
WAREHOUSE_DIR = Path("data/warehouse")
WAREHOUSE_DIR.mkdir(parents=True, exist_ok=True)


def split_countries(value):
    """Sépare une chaîne de pays séparés par des virgules en liste.

    Renvoie une liste vide si la valeur est manquante.
    On strip() chaque élément pour enlever les espaces résiduels.
    """
    if pd.isna(value):
        return []
    return [c.strip() for c in value.split(",")]


def harmonize_back_on_track():
    """Pipeline principal d'harmonisation pour Back-on-Track.

    Étapes :
    - Lecture du CSV source
    - Normalisation des opérateurs (MAJUSCULES + trim)
    - Décomposition des listes de pays en colonnes utilisables
    - Construction des tables cibles (`routes`, `route_countries`)
    - Export CSV des tables harmonisées
    """
    print("\n HARMONISATION – Back-on-Track")

    file = PROCESSED_DIR / "view_ontd_list.csv"
    print(f"\nTraitement : {file.name}")

    # Lecture du fichier source
    df = pd.read_csv(file)

    # Normalisation des opérateurs : on met en majuscules et on enlève
    # les espaces autour pour assurer la cohérence des valeurs.
    df["operator"] = df["operators"].str.upper().str.strip()

    # Transformation de la colonne 'countries' (chaîne de codes séparés par ',')
    # en une liste de codes (champ 'country_list').
    df["country_list"] = df["countries"].apply(split_countries)

    # Construction de la table 'routes' : sélection des colonnes métier
    routes = df[[
        "route_id",
        "night_train",
        "route_long_name",
        "itinerary",
        "itinerary_long",
        "operator",
        "source"
    ]].copy()

    # Construction de la table d'association route -> pays : on explode la
    # liste 'country_list' pour avoir une ligne par (route_id, country_code)
    route_countries = df[["route_id", "country_list"]].explode("country_list")
    route_countries = route_countries.rename(
        columns={"country_list": "country_code"}
    )

    # Sauvegarde des tables harmonisées dans l'entrepôt (sans index)
    routes.to_csv(WAREHOUSE_DIR / "routes.csv", index=False)
    route_countries.to_csv(WAREHOUSE_DIR / "route_countries.csv", index=False)

    print("✔ routes.csv et route_countries.csv générés")


if __name__ == "__main__":
    harmonize_back_on_track()
