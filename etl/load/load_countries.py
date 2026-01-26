import pandas as pd
from database import db

def load_countries():
    """Charger la table dim_countries"""

    # Lire le fichier CSV
    file_path = "data/warehouse/dim_countries.csv"
    df = pd.read_csv(file_path)

    # Charger dans PostgreSQL
    success = db.load_dataframe(df, 'dim_countries')
    
    # Vérification
    if success:
        cursor = db.execute_query("SELECT COUNT(*) FROM dim_countries")
        if cursor:
            count = cursor.fetchone()[0]
            print(f"✅ {count} pays chargés avec succès")
    
    return success