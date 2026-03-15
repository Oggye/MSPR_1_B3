import pandas as pd
import sys
from pathlib import Path

# Ajouter le répertoire racine au PYTHONPATH
current_dir = Path(__file__).parent
project_root = current_dir.parent
sys.path.insert(0, str(project_root))
from .database import db

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
