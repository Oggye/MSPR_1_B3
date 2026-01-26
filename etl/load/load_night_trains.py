import pandas as pd
from database import db

def load_night_trains():
    """Charger la table facts_night_trains"""
    
    # Lire le fichier facts_night_trains
    trips_path = "data/warehouse/facts_night_trains.csv"
    df = pd.read_csv(trips_path)

    # Charger dans PostgreSQL
    success = db.load_dataframe(df, 'facts_night_trains')
        
    # Vérification
    if success:
        db.cursor.execute("SELECT COUNT(*) FROM facts_night_trains")
        count = db.cursor.fetchone()[0]
        print(f"✅ {count} trajets chargés avec succès")
    
    return success
        

