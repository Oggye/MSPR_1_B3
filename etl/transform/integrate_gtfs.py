# =========================================================
# ETL/transform/integrate_gtfs.py
# Intégration GTFS France dans le warehouse – ObRail Europe
# =========================================================

"""
Intégration des données GTFS France dans le warehouse.
Ce script ajoute les données ferroviaires françaises aux tables existantes.
"""

import pandas as pd
from pathlib import Path

PROCESSED_DIR = Path("data/processed/gtfs_fr")
WAREHOUSE_DIR = Path("data/warehouse")

def integrate_gtfs_france():
    """Intègre les données GTFS France dans le warehouse."""
    print("\n" + "="*60)
    print("🚄 INTÉGRATION GTFS FRANCE")
    print("="*60)
    
    # Vérifier que les fichiers existent
    required_files = ["agency_clean.csv", "routes_clean.csv", "stops_clean.csv"]
    missing_files = []
    
    for file in required_files:
        if not (PROCESSED_DIR / file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Fichiers manquants: {missing_files}")
        return
    
    # 1. Ajouter les opérateurs SNCF
    print("\n1. Ajout des opérateurs SNCF...")
    
    # Charger les opérateurs existants
    operators_df = pd.read_csv(WAREHOUSE_DIR / "operators.csv")
    
    # Charger les agences GTFS
    agencies = pd.read_csv(PROCESSED_DIR / "agency_clean.csv")
    
    # Ajouter SNCF aux opérateurs si pas déjà présent
    sncf_operators = ["SNCF VOYAGEURS", "SNCF"]
    existing_operators = set(operators_df["operator_name"].str.upper())
    
    new_operators = []
    for op in sncf_operators:
        if op.upper() not in existing_operators:
            new_operators.append(op)
    
    if new_operators:
        new_operators_df = pd.DataFrame({"operator_name": new_operators})
        operators_updated = pd.concat([operators_df, new_operators_df], ignore_index=True)
        operators_updated = operators_updated.drop_duplicates().sort_values("operator_name")
        operators_updated.to_csv(WAREHOUSE_DIR / "operators.csv", index=False)
        print(f"   {len(new_operators)} nouveaux opérateurs ajoutés")
    else:
        print("   Tous les opérateurs SNCF sont déjà présents")
    
    # 2. Créer une table des gares françaises
    print("\n2. Création de la table des gares françaises...")
    
    stops = pd.read_csv(PROCESSED_DIR / "stops_clean.csv")
    
    # Nettoyer les noms de gares
    stops["clean_stop_name"] = stops["stop_name"].str.replace("StopPoint:OCE", "", regex=False)
    stops["clean_stop_name"] = stops["clean_stop_name"].str.replace(r'^(TGV|ICE|Train TER)-', '', regex=True)
    
    # Créer la table des gares françaises
    french_stations = stops[[
        "stop_id",
        "stop_name",
        "stop_lat",
        "stop_lon"
    ]].copy()
    
    french_stations["country_code"] = "FR"
    french_stations["data_source"] = "GTFS_FR"
    
    # Sauvegarder
    french_stations_file = WAREHOUSE_DIR / "french_stations.csv"
    french_stations.to_csv(french_stations_file, index=False)
    print(f"   {len(french_stations)} gares françaises sauvegardées")
    
    # 3. Créer une table des lignes ferroviaires françaises
    print("\n3. Création de la table des lignes françaises...")
    
    routes = pd.read_csv(PROCESSED_DIR / "routes_clean.csv")
    
    # Associer les noms d'agences
    routes_with_agency = pd.merge(
        routes,
        agencies[["agency_id", "agency_name"]],
        on="agency_id",
        how="left"
    )
    
    # Créer la table des lignes françaises
    french_routes = routes_with_agency[[
        "route_id",
        "agency_name",
        "route_long_name"
    ]].copy()
    
    french_routes["country_code"] = "FR"
    french_routes["data_source"] = "GTFS_FR"
    french_routes = french_routes.rename(columns={
        "agency_name": "operator",
        "route_long_name": "route_name"
    })
    
    # Sauvegarder
    french_routes_file = WAREHOUSE_DIR / "french_routes.csv"
    french_routes.to_csv(french_routes_file, index=False)
    print(f"   {len(french_routes)} lignes ferroviaires françaises sauvegardées")
    
    # 4. Mettre à jour la table des pays
    print("\n4. Mise à jour de la table des pays...")
    
    countries_df = pd.read_csv(WAREHOUSE_DIR / "countries.csv")
    
    # Ajouter FR si pas déjà présent
    if "FR" not in countries_df["country_code"].values:
        new_country = pd.DataFrame({"country_code": ["FR"]})
        countries_updated = pd.concat([countries_df, new_country], ignore_index=True)
        countries_updated = countries_updated.sort_values("country_code")
        countries_updated.to_csv(WAREHOUSE_DIR / "countries.csv", index=False)
        print("   France ajoutée à la table des pays")
    else:
        print("   France déjà présente dans la table des pays")
    
    print("\n" + "="*60)
    print("✅ INTÉGRATION GTFS FRANCE TERMINÉE")
    print("="*60)
    print(f"📁 Fichiers créés:")
    print(f"   - {french_stations_file.name}: {len(french_stations)} gares")
    print(f"   - {french_routes_file.name}: {len(french_routes)} lignes")
    print(f"📊 Opérateurs totaux: {len(operators_updated)}")

if __name__ == "__main__":
    integrate_gtfs_france()