import pandas as pd
import sys
from pathlib import Path

# Ajouter le répertoire racine au PYTHONPATH
current_dir = Path(__file__).parent
project_root = current_dir.parent
sys.path.insert(0, str(project_root))
from .database import db

def load_country_stats():
    """Charger la table facts_country_stats"""
    
    # Lire le fichier facts_country_stats
    trips_path = "data/warehouse/facts_country_stats.csv"
    df = pd.read_csv(trips_path)

    # Charger dans PostgreSQL
    success = db.load_dataframe(df, 'facts_country_stats')
        
    # Vérification
    if success:
        db.cursor.execute("SELECT COUNT(*) FROM facts_country_stats")
        count = db.cursor.fetchone()[0]
        print(f"✅ {count} statistiques par pays chargés avec succès")
    
    return success