import pandas as pd
from database import db

def load_years():
    """Charger la table dim_years"""
    
    # Lire le fichier CSV
    file_path = "data/warehouse/dim_years.csv"
    df = pd.read_csv(file_path)

    # Charger dans PostgreSQL
    success = db.load_dataframe(df, 'dim_years')
    
    # Vérification
    if success:
        cursor = db.execute_query("SELECT MIN(year), MAX(year) FROM dim_years")
        if cursor:
            min_year, max_year = cursor.fetchone()
            print(f"✅ Années chargées: de {min_year} à {max_year}")
    
    return success
