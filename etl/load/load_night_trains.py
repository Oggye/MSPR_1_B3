import pandas as pd
import sys
from pathlib import Path

# Ajouter le répertoire racine au PYTHONPATH
current_dir = Path(__file__).parent
project_root = current_dir.parent
sys.path.insert(0, str(project_root))
from .database import db

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
        

