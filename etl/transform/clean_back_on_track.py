# =========================================================
#  ETL/transform/clean_back_on_track.py
#  Nettoyage Back-on-Track – ObRail Europe
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
        
        # Log initial
        print(f"  Lignes avant nettoyage: {len(df)}")
        
        # Suppression des doublons
        initial_rows = len(df)
        df = df.drop_duplicates()
        duplicate_removed = initial_rows - len(df)
        if duplicate_removed > 0:
            print(f"  Doublons supprimés: {duplicate_removed}")
        
        # Suppression des lignes entièrement vides
        df = df.dropna(how="all")
        
        # Nettoyage spécifique aux fichiers
        if "cities" in file.name.lower():
            # Pour les villes, traiter les noms manquants
            if "stop_cityname_romanized" in df.columns:
                missing_before = df["stop_cityname_romanized"].isna().sum()
                df["stop_cityname_romanized"] = df["stop_cityname_romanized"].fillna("Inconnu")
                print(f"  Noms de ville manquants traités: {missing_before}")
            
            # Nettoyer les codes pays
            if "stop_country" in df.columns:
                df["stop_country"] = df["stop_country"].str.strip().str.upper()
        
        # Nettoyage des chaînes de caractères
        for col in df.select_dtypes(include="object"):
            df[col] = df[col].astype(str).str.strip()
            # Remplacer les chaînes vides par NaN
            df[col] = df[col].replace(["", "nan", "NaN", "None"], pd.NA)
        
        # Log final
        print(f"  Lignes après nettoyage: {len(df)}")
        
        # Sauvegarde PROCESSED
        out_file = PROCESSED_DIR / file.name
        df.to_csv(out_file, index=False)
        
        print(f"✔ Nettoyé et sauvegardé → {out_file}")

if __name__ == "__main__":
    clean_back_on_track()