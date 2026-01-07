# =========================================================
# Nettoyage Back-on-Track – ObRail Europe
# =========================================================

import pandas as pd
from pathlib import Path

RAW_DIR = Path("data/raw/back_on_track")
PROCESSED_DIR = Path("data/processed/back_on_track")
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

def clean_back_on_track():
    print("\n NETTOYAGE – Back-on-Track")

    for file in RAW_DIR.glob("*.csv"):
        print(f"\nTraitement : {file.name}")

        df = pd.read_csv(file)

        # Suppression des doublons
        df = df.drop_duplicates()

        # Suppression des lignes entièrement vides
        df = df.dropna(how="all")

        # Nettoyage des chaînes de caractères
        for col in df.select_dtypes(include="object"):
            df[col] = df[col].str.strip()

        # Sauvegarde PROCESSED
        out_file = PROCESSED_DIR / file.name
        df.to_csv(out_file, index=False)

        print(f"✔ Nettoyé et sauvegardé → {out_file}")

if __name__ == "__main__":
    clean_back_on_track()
