# etl/load/load_stops.py
import pandas as pd
import sys
from pathlib import Path

current_dir = Path(__file__).parent
project_root = current_dir.parent
sys.path.insert(0, str(project_root))
from .database import db

def load_stops():
    """Charger la table dim_stops"""
    
    file_path = "data/warehouse/dim_stops.csv"
    df = pd.read_csv(file_path)
    
    success = db.load_dataframe(df, 'dim_stops')
    
    if success:
        cursor = db.execute_query("SELECT COUNT(*) FROM dim_stops")
        if cursor:
            count = cursor.fetchone()[0]
            print(f"✅ {count:,} arrêts chargés avec succès")
    
    return success