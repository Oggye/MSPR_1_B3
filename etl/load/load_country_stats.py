# etl/load/load_country_stats.py
import pandas as pd
import sys
from pathlib import Path

current_dir = Path(__file__).parent
project_root = current_dir.parent
sys.path.insert(0, str(project_root))
from .database import db

def load_country_stats():
    """Charger la table facts_country_stats"""
    
    file_path = "data/warehouse/facts_country_stats.csv"
    df = pd.read_csv(file_path)
    
    # Vérifier que la colonne s'appelle bien 'stat_id' (pas 'stats_id')
    if 'stats_id' in df.columns:
        df = df.rename(columns={'stats_id': 'stat_id'})
    
    success = db.load_dataframe(df, 'facts_country_stats')
    
    if success:
        cursor = db.execute_query("SELECT COUNT(*) FROM facts_country_stats")
        if cursor:
            count = cursor.fetchone()[0]
            print(f"✅ {count} statistiques pays chargées avec succès")
    
    return success