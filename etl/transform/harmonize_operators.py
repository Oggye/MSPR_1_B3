
# =========================================================
# ETL/transform/harmonize_operators.py
# Harmonisation des opérateurs – ObRail Europe
# =========================================================


"""
Module d'harmonisation des opérateurs.

Ce script extrait la liste unique des opérateurs depuis `data/warehouse/routes.csv`
et écrit un fichier `operators.csv` contenant une colonne `operator_name`.
"""

import pandas as pd
from pathlib import Path

# Répertoire de l'entrepôt de données
WAREHOUSE_DIR = Path("data/warehouse")


def harmonize_operators():
    """Génère `operators.csv` à partir des opérateurs présents dans `routes.csv`."""
    # Message de suivi pour l'utilisateur/les logs
    print("\n HARMONISATION – Opérateurs")

    # Chargement des routes depuis l'entrepôt
    routes = pd.read_csv(WAREHOUSE_DIR / "routes.csv")

    # On récupère la colonne 'operator', on supprime les valeurs manquantes,
    # on normalise le texte (majuscules + suppression des espaces autour),
    # puis on garde les valeurs uniques.
    operators = (
        routes["operator"]
        .dropna()
        .str.upper()
        .str.strip()
        .unique()
    )

    # Construction d'un DataFrame trié pour un ordre déterministe
    operators_df = pd.DataFrame({
        "operator_name": sorted(operators)
    })

    # Écriture du fichier de sortie sans index
    operators_df.to_csv(WAREHOUSE_DIR / "operators.csv", index=False)

    # Confirmation de la génération
    print("✔ operators.csv généré")


if __name__ == "__main__":
    harmonize_operators()
