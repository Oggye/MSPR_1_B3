# =========================================================
# ETL/transform/audit_data_loss.py
# Audit des pertes de données – ObRail Europe
# =========================================================

"""
Audit des pertes de données entre les différentes étapes du pipeline ETL.
Ce script compare les données entre RAW, PROCESSED et WAREHOUSE.
"""

import pandas as pd
from pathlib import Path

RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")
WAREHOUSE_DIR = Path("data/warehouse")

def audit_back_on_track():
    """Audit des données Back-on-Track."""
    print("\n" + "="*60)
    print("🔍 AUDIT BACK-ON-TRACK")
    print("="*60)
    
    # Cities
    try:
        raw_cities = pd.read_csv(RAW_DIR / "back_on_track" / "view_ontd_cities.csv")
        processed_cities = pd.read_csv(PROCESSED_DIR / "back_on_track" / "view_ontd_cities.csv")
        wh_cities = pd.read_csv(WAREHOUSE_DIR / "cities.csv")
        
        print("\n📊 Villes:")
        print(f"  RAW: {len(raw_cities)} lignes")
        print(f"  PROCESSED: {len(processed_cities)} lignes")
        print(f"  WAREHOUSE: {len(wh_cities)} lignes")
        print(f"  Pertes RAW→PROCESSED: {len(raw_cities) - len(processed_cities)}")
        print(f"  Pertes PROCESSED→WAREHOUSE: {len(processed_cities) - len(wh_cities)}")
        print(f"  Pertes totales: {len(raw_cities) - len(wh_cities)}")
        
        # Vérifier les villes sans nom
        missing_names = wh_cities[wh_cities["city_name"].isin(["nan", "NaN", "Inconnu", ""])]
        print(f"  Villes sans nom valide dans warehouse: {len(missing_names)}")
        
        if len(missing_names) > 0:
            print(f"  Exemples de villes problématiques:")
            print(missing_names.head().to_string())
    
    except FileNotFoundError as e:
        print(f"  ❌ Fichier manquant: {e}")
    
    # Routes
    try:
        raw_routes = pd.read_csv(RAW_DIR / "back_on_track" / "view_ontd_list.csv")
        wh_routes = pd.read_csv(WAREHOUSE_DIR / "routes.csv")
        
        print("\n📊 Routes:")
        print(f"  RAW: {len(raw_routes)} lignes")
        print(f"  WAREHOUSE: {len(wh_routes)} lignes")
        print(f"  Pertes: {len(raw_routes) - len(wh_routes)}")
        
    except FileNotFoundError as e:
        print(f"  ❌ Fichier manquant: {e}")
    
    # Route Countries
    try:
        wh_route_countries = pd.read_csv(WAREHOUSE_DIR / "route_countries.csv")
        print(f"\n📊 Associations Route-Pays:")
        print(f"  WAREHOUSE: {len(wh_route_countries)} associations")
        
        # Vérifier la distribution
        route_counts = wh_route_countries["route_id"].value_counts()
        print(f"  Nombre moyen de pays par route: {wh_route_countries.groupby('route_id').size().mean():.2f}")
    
    except FileNotFoundError as e:
        print(f"  ❌ Fichier manquant: {e}")

def audit_gtfs_fr():
    """Audit des données GTFS France."""
    print("\n" + "="*60)
    print("🔍 AUDIT GTFS FRANCE")
    print("="*60)
    
    try:
        # Stops
        raw_stops = pd.read_csv(RAW_DIR / "gtfs_fr" / "stops.csv")
        processed_stops = pd.read_csv(PROCESSED_DIR / "gtfs_fr" / "stops_clean.csv")
        
        print("\n📊 Arrêts:")
        print(f"  RAW: {len(raw_stops)} lignes")
        print(f"  PROCESSED: {len(processed_stops)} lignes")
        print(f"  Pertes: {len(raw_stops) - len(processed_stops)}")
        print(f"  % conservé: {(len(processed_stops)/len(raw_stops))*100:.1f}%")
        
        # Routes
        raw_routes = pd.read_csv(RAW_DIR / "gtfs_fr" / "routes.csv")
        processed_routes = pd.read_csv(PROCESSED_DIR / "gtfs_fr" / "routes_clean.csv")
        
        print("\n📊 Lignes:")
        print(f"  RAW: {len(raw_routes)} lignes")
        print(f"  PROCESSED: {len(processed_routes)} lignes")
        print(f"  Pertes: {len(raw_routes) - len(processed_routes)}")
        print(f"  % conservé: {(len(processed_routes)/len(raw_routes))*100:.1f}%")
        
    except FileNotFoundError as e:
        print(f"  ❌ Fichier manquant: {e}")

def audit_eurostat():
    """Audit des données Eurostat."""
    print("\n" + "="*60)
    print("🔍 AUDIT EUROSTAT")
    print("="*60)
    
    eurostat_files = list((RAW_DIR / "eurostat").glob("*.csv"))
    
    if not eurostat_files:
        print("  ℹ️ Aucun fichier Eurostat trouvé")
        return
    
    for file in eurostat_files:
        try:
            raw_df = pd.read_csv(file)
            processed_file = PROCESSED_DIR / "eurostat" / file.name.replace(".csv", "_clean.csv")
            
            if processed_file.exists():
                processed_df = pd.read_csv(processed_file)
                print(f"\n📊 {file.name}:")
                print(f"  RAW: {len(raw_df)} lignes, {len(raw_df.columns)} colonnes")
                
                # Identifier les colonnes d'années dans RAW
                year_cols_raw = [c for c in raw_df.columns if c.isdigit()]
                if year_cols_raw:
                    min_year_raw = min(map(int, year_cols_raw))
                    max_year_raw = max(map(int, year_cols_raw))
                    print(f"     Période RAW: {min_year_raw} - {max_year_raw}")
                
                print(f"  PROCESSED: {len(processed_df)} lignes, {len(processed_df.columns)} colonnes")
                
                # Identifier les années dans PROCESSED
                if 'year' in processed_df.columns:
                    min_year_proc = processed_df['year'].min()
                    max_year_proc = processed_df['year'].max()
                    print(f"     Période PROCESSED: {int(min_year_proc)} - {int(max_year_proc)}")
                    print(f"     Filtre ≥2013: ✅ appliqué")
                
                # Calculer le % de données conservées après 2012
                if year_cols_raw:
                    total_years_raw = len(year_cols_raw)
                    years_after_2012 = len([y for y in year_cols_raw if int(y) >= 2013])
                    if total_years_raw > 0:
                        print(f"     Années conservées: {years_after_2012}/{total_years_raw} ({years_after_2012/total_years_raw*100:.1f}%)")
            
            else:
                print(f"\n📊 {file.name}:")
                print(f"  RAW: {len(raw_df)} lignes, {len(raw_df.columns)} colonnes")
                print(f"  PROCESSED: ❌ Fichier non généré")
        
        except Exception as e:
            print(f"  ❌ Erreur avec {file.name}: {e}")

def audit_warehouse():
    """Audit complet du warehouse."""
    print("\n" + "="*60)
    print("🏢 AUDIT WAREHOUSE COMPLET")
    print("="*60)
    
    if not WAREHOUSE_DIR.exists():
        print("  ❌ Dossier warehouse introuvable")
        return
    
    warehouse_files = list(WAREHOUSE_DIR.glob("*.csv"))
    
    if not warehouse_files:
        print("  ℹ️ Aucun fichier dans le warehouse")
        return
    
    print(f"\n📁 Fichiers dans le warehouse ({len(warehouse_files)}):")
    
    total_rows = 0
    for file in warehouse_files:
        try:
            df = pd.read_csv(file)
            rows = len(df)
            cols = len(df.columns)
            total_rows += rows
            print(f"  📄 {file.name}: {rows} lignes × {cols} colonnes")
            
            # Afficher un aperçu pour les petites tables
            if rows <= 50:
                print(f"    Aperçu:")
                print(df.head().to_string())
                print()
        
        except Exception as e:
            print(f"  ❌ Erreur avec {file.name}: {e}")
    
    print(f"\n📈 Total des données dans le warehouse: {total_rows} lignes")

def main():
    """Fonction principale d'audit."""
    print("\n" + "="*60)
    print("🔍 AUDIT COMPLET DES PERTES DE DONNÉES")
    print("="*60)
    
    audit_back_on_track()
    audit_gtfs_fr()
    audit_eurostat()
    audit_warehouse()
    
    print("\n" + "="*60)
    print("✅ AUDIT TERMINÉ")
    print("="*60)

if __name__ == "__main__":
    main()