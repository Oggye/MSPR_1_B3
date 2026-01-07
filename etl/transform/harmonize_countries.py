"""
Module d'harmonisation des pays.

Ce module construit la liste unique des codes-pays utilisés dans l'entrepôt
(`data/warehouse`) à partir des fichiers intermédiaires existants :
- `route_countries.csv` (liaisons route <-> pays)
- `cities.csv` (villes avec leur code pays)

Le résultat est persisté dans `data/warehouse/countries.csv` avec une
seule colonne `country_code` contenant les codes triés.
"""

import pandas as pd
from pathlib import Path

# Répertoire local de l'entrepôt de données (input/output pour les CSV intermédiaires)
WAREHOUSE_DIR = Path("data/warehouse")


def harmonize_countries():
    """Harmonise la table des pays.

    Étapes :
    1. Charger `route_countries.csv` et `cities.csv` depuis l'entrepôt.
    2. Extraire les colonnes `country_code` des deux tables.
    3. Concaténer les codes, supprimer les valeurs manquantes (`NaN`), puis garder
       les valeurs uniques afin d'obtenir l'ensemble des pays référencés.
    4. Trier les codes de manière déterministe et écrire le CSV `countries.csv`.
    """

    # Message d'exécution pour le suivi dans les logs/console
    print("\n HARMONISATION – Pays")

    # Chargement des sources depuis l'entrepôt
    rc = pd.read_csv(WAREHOUSE_DIR / "route_countries.csv")
    cities = pd.read_csv(WAREHOUSE_DIR / "cities.csv")

    # On ne conserve que la colonne `country_code` de chaque table, puis on concatène
    # les deux séries. Ensuite on retire les valeurs manquantes et on récupère
    # l'ensemble unique des codes de pays.
    countries = pd.concat([
        rc["country_code"],
        cities["country_code"]
    ]).dropna().unique()

    # Construction d'un DataFrame propre contenant les codes pays triés pour garantir
    # un ordre déterministe dans le fichier de sortie.
    countries_df = pd.DataFrame({
        "country_code": sorted(countries)
    })

    # Écriture du résultat dans l'entrepôt (sans index inutile)
    countries_df.to_csv(WAREHOUSE_DIR / "countries.csv", index=False)

    # Indication que le fichier a bien été généré
    print("✔ countries.csv généré")


if __name__ == "__main__":
    harmonize_countries()
