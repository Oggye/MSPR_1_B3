# =========================================================
# diagnostic.py
# Affiche les 20 premières lignes de chaque fichier extrait
# =========================================================

import pandas as pd
from pathlib import Path
import glob

# Répertoires des données extraites
DATA_DIRECTORIES = {
    "back_on_track": "data/raw/back_on_track/*.csv",
    "eurostat": "data/raw/eurostat/*.csv",
    "emission_co2": "data/raw/emission_co2/*.csv",
    "gtfs_fr": "data/raw/gtfs_fr/*.csv",
    "gtfs_ch": "data/raw/gtfs_ch/*.csv",
    "gtfs_de": "data/raw/gtfs_de/*.csv",
}

def diagnose_files():
    print("🔍 DIAGNOSTIC DES FICHIERS EXTRACTS")
    print("=" * 60)
    
    for dataset_name, pattern in DATA_DIRECTORIES.items():
        print(f"\n📁 {dataset_name.upper()}")
        print("-" * 40)
        
        files = glob.glob(pattern)
        
        if not files:
            print(f"Aucun fichier trouvé pour {dataset_name}")
            continue
        
        for file_path in files:
            try:
                # Essayer de lire le fichier
                file_name = Path(file_path).name
                print(f"\n📄 Fichier : {file_name}")
                print(f"📊 Chemin : {file_path}")
                
                # Lire le fichier (gérer les différents formats)
                if file_name.endswith('.tsv'):
                    df = pd.read_csv(file_path, sep='\t', nrows=20)
                else:
                    df = pd.read_csv(file_path, nrows=20)
                
                # Informations de base
                print(f"   Lignes totales : {len(pd.read_csv(file_path)) if file_name.endswith('.tsv') else len(pd.read_csv(file_path))}")
                print(f"   Colonnes : {len(df.columns)}")
                print(f"   Colonnes : {', '.join(df.columns.tolist())}")
                
                # Afficher les 20 premières lignes
                print(f"\n   {'='*40}")
                print("   20 PREMIÈRES LIGNES :")
                print(f"   {'='*40}")
                
                # Afficher avec un formatage lisible
                pd.set_option('display.max_columns', None)
                pd.set_option('display.width', 1000)
                pd.set_option('display.max_rows', 25)
                
                print(df.to_string())
                print(f"   {'='*40}")
                
                # Statistiques de base pour les colonnes numériques
                numeric_cols = df.select_dtypes(include=['number']).columns
                if len(numeric_cols) > 0:
                    print(f"\n   📈 Statistiques numériques :")
                    print(df[numeric_cols].describe().round(2).to_string())
                
                # Informations sur les types de données
                print(f"\n   🗂️  Types de données :")
                dtypes = df.dtypes
                for col in df.columns:
                    print(f"      {col}: {dtypes[col]}")
                
                # Vérifier les valeurs nulles
                null_counts = df.isnull().sum()
                if null_counts.sum() > 0:
                    print(f"\n   ⚠️  Valeurs nulles détectées :")
                    for col, count in null_counts.items():
                        if count > 0:
                            print(f"      {col}: {count} valeurs nulles")
                
            except Exception as e:
                print(f"   ❌ Erreur lors de la lecture de {file_name}: {e}")
                print(f"   Type d'erreur : {type(e).__name__}")
                
                # Essayer de lire en texte brut pour voir le contenu
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = [next(f) for _ in range(5)]
                        print(f"   📝 Contenu (5 premières lignes) :")
                        for i, line in enumerate(lines, 1):
                            print(f"      Ligne {i}: {line[:100]}...")
                except:
                    print("   Impossible de lire le fichier en texte brut")
    
    print("\n" + "=" * 60)
    print("✅ DIAGNOSTIC TERMINÉ")

def quick_summary():
    """Affiche un résumé rapide de tous les fichiers"""
    print("\n📋 RÉSUMÉ RAPIDE")
    print("=" * 60)
    
    total_files = 0
    total_rows = 0
    total_columns = 0
    
    for dataset_name, pattern in DATA_DIRECTORIES.items():
        files = glob.glob(pattern)
        if files:
            print(f"\n📁 {dataset_name.upper()}:")
            for file_path in files:
                try:
                    file_name = Path(file_path).name
                    # Lire juste la première ligne pour compter les colonnes
                    if file_name.endswith('.tsv'):
                        df_sample = pd.read_csv(file_path, sep='\t', nrows=1)
                        df_full = pd.read_csv(file_path, sep='\t')
                    else:
                        df_sample = pd.read_csv(file_path, nrows=1)
                        df_full = pd.read_csv(file_path)
                    
                    rows = len(df_full)
                    cols = len(df_sample.columns)
                    
                    print(f"   📄 {file_name}")
                    print(f"      → Lignes: {rows:,}")
                    print(f"      → Colonnes: {cols}")
                    print(f"      → Taille: {Path(file_path).stat().st_size / 1024:.1f} KB")
                    
                    total_files += 1
                    total_rows += rows
                    total_columns += cols
                    
                except Exception as e:
                    print(f"   📄 {Path(file_path).name}")
                    print(f"      → ERREUR: {str(e)[:50]}...")
    
    print("\n" + "=" * 60)
    print("📊 TOTAUX :")
    print(f"   📁 Fichiers analysés: {total_files}")
    print(f"   📈 Lignes totales: {total_rows:,}")
    print(f"   🗂️  Colonnes totales: {total_columns}")
    print("=" * 60)

if __name__ == "__main__":
    print("🔧 UTILISATION :")
    print("   python diagnostic.py          # Diagnostic complet")
    print("   python diagnostic.py --quick  # Résumé rapide")
    
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        quick_summary()
    else:
        diagnose_files()
        quick_summary()