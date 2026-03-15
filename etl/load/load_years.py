import pandas as pd
import sys
from pathlib import Path

# Ajouter le répertoire racine au PYTHONPATH
current_dir = Path(__file__).parent
project_root = current_dir.parent
sys.path.insert(0, str(project_root))
from .database import db

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
