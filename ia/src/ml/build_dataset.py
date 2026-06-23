# ia/src/ml/build_dataset.py
#
# Nouveau sujet : Prévision de la fréquentation ferroviaire (régression)
#                 + Détection des pays en déclin (classification)
#
# Source principale : facts_country_stats (630 lignes — 42 pays × 15 ans)
#
# Axe 1 — Régression
#   Cible : passengers (année N)
#   Features : year, co2_emissions, co2_per_passenger, passengers_lag1, passengers_lag2
#
# Axe 2 — Classification
#   Cible : en_declin = 1 si passengers_annee_N < passengers_annee_N-2
#   Features : identiques à l'axe régression SANS passengers

import pandas as pd
import numpy as np
from config import (
    STATS_FILE, COUNTRIES_FILE, YEARS_FILE,
    REGRESSION_DATASET_PATH, CLASSIF_DATASET_PATH
)


def load_sources():
    stats    = pd.read_csv(STATS_FILE)
    countries = pd.read_csv(COUNTRIES_FILE)
    years    = pd.read_csv(YEARS_FILE)
    return stats, countries, years


def build_base_df(stats, countries, years):
    """Jointure principale et tri chronologique."""
    df = (stats
          .merge(countries, on='country_id', how='left')
          .merge(years,     on='year_id',    how='left'))
    df = df.sort_values(['country_id', 'year']).reset_index(drop=True)
    return df


def add_lag_features(df):
    """
    Crée les variables lag par pays.
    passengers_lag1 = fréquentation de l'année N-1
    passengers_lag2 = fréquentation de l'année N-2
    Ces variables permettent au modèle d'apprendre la dynamique temporelle
    sans avoir accès à la valeur cible elle-même.
    """
    df = df.copy()
    df['passengers_lag1'] = df.groupby('country_id')['passengers'].shift(1)
    df['passengers_lag2'] = df.groupby('country_id')['passengers'].shift(2)
    df['co2_lag1']        = df.groupby('country_id')['co2_emissions'].shift(1)
    return df


def build_target_classification(df):
    """
    Cible classification : pays en déclin
    en_declin = 1 si la fréquentation de l'année N
                est inférieure à celle de l'année N-2.
    Construit à partir de données historiques réelles → zéro leakage.
    """
    df = df.copy()
    df['en_declin'] = (df['passengers'] < df['passengers_lag2']).astype(int)
    return df


def main():
    print("=" * 55)
    print("CONSTRUCTION DES DATASETS ML — NOUVEAU SUJET")
    print("=" * 55)

    stats, countries, years = load_sources()
    df = build_base_df(stats, countries, years)

    print(f"\n✅ Base construite : {df.shape[0]} lignes, {df.shape[1]} colonnes")
    print(f"   Pays couverts   : {df['country_name'].nunique()}")
    print(f"   Années couvertes: {df['year'].min()} → {df['year'].max()}")

    # ----------------------------------------------------------
    # Features lag
    # ----------------------------------------------------------
    df = add_lag_features(df)
    df = build_target_classification(df)

    # ----------------------------------------------------------
    # Supprimer les lignes sans lag (les 2 premières années
    # par pays n'ont pas de lag2 → non utilisables)
    # ----------------------------------------------------------
    df_clean = df.dropna(subset=['passengers_lag1', 'passengers_lag2']).copy()

    print(f"\n   Lignes après suppression des NaN lag : {len(df_clean)}")
    print(f"   (Années 2010-2011 retirées par pays — pas de lag disponible)")

    # ----------------------------------------------------------
    # Dataset Régression
    # ----------------------------------------------------------
    reg_features = [
        'country_id', 'country_name', 'year', 'year_id',
        'co2_emissions', 'co2_per_passenger', 'co2_lag1',
        'passengers_lag1', 'passengers_lag2',
        'passengers'   # cible régression
    ]
    df_reg = df_clean[reg_features].copy()
    df_reg.to_csv(REGRESSION_DATASET_PATH, index=False)

    print(f"\n✅ Dataset régression sauvegardé : {REGRESSION_DATASET_PATH}")
    print(f"   Shape : {df_reg.shape}")
    print(f"   Cible (passengers) — min: {df_reg['passengers'].min():.0f}"
          f" | max: {df_reg['passengers'].max():.0f}"
          f" | médiane: {df_reg['passengers'].median():.0f}")

    # ----------------------------------------------------------
    # Dataset Classification
    # ----------------------------------------------------------
    clf_features = [
        'country_id', 'country_name', 'year', 'year_id',
        'co2_emissions', 'co2_per_passenger', 'co2_lag1',
        'passengers_lag1', 'passengers_lag2',
        'en_declin'   # cible classification
    ]
    df_clf = df_clean[clf_features].copy()
    df_clf.to_csv(CLASSIF_DATASET_PATH, index=False)

    print(f"\n✅ Dataset classification sauvegardé : {CLASSIF_DATASET_PATH}")
    print(f"   Shape : {df_clf.shape}")
    counts = df_clf['en_declin'].value_counts()
    total  = len(df_clf)
    print(f"   Distribution de en_declin :")
    for val, cnt in counts.items():
        label = "En déclin" if val == 1 else "En croissance"
        print(f"     {val} ({label}) : {cnt} ({cnt/total*100:.1f}%)")

    print("\n" + "=" * 55)
    print("RÉSUMÉ")
    print("=" * 55)
    print(f"  Axe régression    → {REGRESSION_DATASET_PATH.name}")
    print(f"  Axe classification → {CLASSIF_DATASET_PATH.name}")
    print(f"  Aucun leakage : la cible ne dépend pas des features d'entraînement")


if __name__ == "__main__":
    main()