# =========================================================
# ETL/transform/clean_eurostat.py
# Nettoyage Eurostat – ObRail Europe
# =========================================================

import pandas as pd
from pathlib import Path

RAW_DIR = Path("data/raw/eurostat")
PROCESSED_DIR = Path("data/processed/eurostat")
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def display_raw_data(df, name):
    print(f"\n===== APERÇU : {name} =====")
    print(df.head())

    print(f"\n===== SCHÉMA : {name} =====")
    df.info()

    print(f"\n===== VALEURS MANQUANTES : {name} =====")
    print((df == ":").sum())


def clean_eurostat_file(file_path):
    print(f"\n Traitement : {file_path.name}")
    df = pd.read_csv(file_path)

    # Affichage brut
    display_raw_data(df, file_path.name)

    # Normalisation colonnes
    df.columns = df.columns.str.lower().str.strip()

    # Remplacer ":" par NaN
    df = df.replace(":", pd.NA)

    # Colonnes fixes (métadonnées)
    id_cols = [c for c in df.columns if not c.isdigit()]

    # Colonnes années
    year_cols = [c for c in df.columns if c.isdigit()]

    # Reshape wide -> long
    df_long = df.melt(
        id_vars=id_cols,
        value_vars=year_cols,
        var_name="year",
        value_name="value"
    )

    # Conversion types
    df_long["year"] = df_long["year"].astype(int)
    df_long["value"] = pd.to_numeric(df_long["value"], errors="coerce")

    # Suppression doublons
    df_long = df_long.drop_duplicates()

    return df_long


def clean_eurostat():
    print(" NETTOYAGE & PRÉPARATION – Eurostat")

    for file in RAW_DIR.glob("*.csv"):
        df_clean = clean_eurostat_file(file)

        output = PROCESSED_DIR / file.name.replace(".csv", "_clean.csv")
        df_clean.to_csv(output, index=False)

        print(f" Sauvegardé : {output}")


if __name__ == "__main__":
    clean_eurostat()
