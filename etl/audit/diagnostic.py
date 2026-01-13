# diagnostic.py
import pandas as pd

print("=== DIAGNOSTIC COMPLET ===")

# 1. GTFS routes
df_raw_gtfs = pd.read_csv("data/raw/gtfs_fr/routes.csv")
df_warehouse_gtfs = pd.read_csv("data/warehouse/routes.csv")  # Si existant
print(f"\nGTFS Routes - Raw: {len(df_raw_gtfs)}")

# Identifier les types exclus
for rt in df_raw_gtfs["route_type"].unique():
    count = len(df_raw_gtfs[df_raw_gtfs["route_type"] == rt])
    print(f"  Type {rt}: {count} lignes")

# 2. Villes Back-on-Track
df_raw_cities = pd.read_csv("data/raw/back_on_track/view_ontd_cities.csv")
df_warehouse_cities = pd.read_csv("data/warehouse/cities.csv")

lost_cities = df_raw_cities[~df_raw_cities["stop_id"].isin(df_warehouse_cities["city_id"])]
print(f"\nVilles perdues : {len(lost_cities)}")
print("Exemples :")
print(lost_cities[["stop_id", "stop_cityname_romanized"]].head(10))