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
    print(f"  Routes chargées: {len(routes)} lignes")
    
    # On récupère la colonne 'operator', on supprime les valeurs manquantes
    operators_series = routes["operator"].dropna()
    print(f"  Opérateurs avant nettoyage: {len(operators_series)} valeurs")
    
    # Initialiser la liste des opérateurs
    operator_list = []
    
    # Traiter chaque valeur d'opérateur
    for op in operators_series:
        # Normaliser
        op_clean = str(op).upper().strip()
        
        # Séparer par virgule si nécessaire
        if "," in op_clean:
            separated = [o.strip() for o in op_clean.split(",")]
            operator_list.extend(separated)
        else:
            operator_list.append(op_clean)
    
    # Supprimer les valeurs vides
    operator_list = [op for op in operator_list if op and op not in ["", "NAN", "NONE"]]
    
    # Garder les valeurs uniques et trier
    operators_unique = sorted(set(operator_list))
    
    print(f"  Opérateurs uniques après traitement: {len(operators_unique)}")
    
    # Construction d'un DataFrame
    operators_df = pd.DataFrame({
        "operator_name": operators_unique
    })
    
    # Écriture du fichier de sortie sans index
    output_file = WAREHOUSE_DIR / "operators.csv"
    operators_df.to_csv(output_file, index=False)

    # Confirmation de la génération
    print(f"✔ operators.csv généré → {output_file}")
    
    # Aperçu des opérateurs
    print(f"  Aperçu des 10 premiers opérateurs:")
    print(operators_df.head(10).to_string(index=False))


if __name__ == "__main__":
    harmonize_operators()