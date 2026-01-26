import pandas as pd
from database import db

def load_operators():
    """Charger la table dim_operators"""
    
    # Lire le fichier CSV
    file_path = "data/warehouse/dim_operators.csv"
    df = pd.read_csv(file_path)
    
    # Nettoyer les noms d'opérateurs
    df['operator_name'] = df['operator_name'].str.strip()
    
    # Charger dans PostgreSQL
    success = db.load_dataframe(df, 'dim_operators')
    
    # Vérification
    if success:
        cursor = db.execute_query("SELECT COUNT(*) FROM dim_operators")
        if cursor:
            count = cursor.fetchone()[0]
            print(f"✅ {count} opérateurs chargés avec succès")
    
    return success
