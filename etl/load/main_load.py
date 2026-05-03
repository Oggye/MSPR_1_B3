# etl/load/main_load.py
"""Script principal de chargement du data warehouse vers PostgreSQL"""
import sys
from pathlib import Path

current_dir = Path(__file__).parent
project_root = current_dir.parent
sys.path.insert(0, str(project_root))

from .database import db
from .load_countries import load_countries
from .load_years import load_years
from .load_operators import load_operators
from .load_stops import load_stops
from .load_country_stats import load_country_stats
from .load_night_trains import load_night_trains

def init_schema():
    """Initialise le schéma SQL"""
    print("=" * 60)
    print("📐 INITIALISATION DU SCHÉMA")
    print("=" * 60)
    
    sql_path = Path("data/warehouse/create_tables.sql")
    
    if not sql_path.exists():
        print(f"❌ Script SQL introuvable : {sql_path}")
        print("   Place le script create_tables.sql dans data/warehouse/")
        return False
    
    with open(sql_path, 'r', encoding='utf-8') as f:
        sql_script = f.read()
    
    if not db.connect():
        return False
    
    try:
        db.cursor.execute(sql_script)
        db.connection.commit()
        print("✅ Schéma créé avec succès")
        return True
    except Exception as e:
        print(f"❌ Erreur création schéma: {e}")
        return False
    finally:
        db.close()

def mainload():
    """Chargement complet"""
    print("=" * 60)
    print("💾 CHARGEMENT DATA WAREHOUSE → POSTGRESQL")
    print("=" * 60)
    
    # 0. Test connexion
    if not db.test_connection():
        print("\n⚠️  Les tables n'existent pas. Initialisation du schéma...")
        if not init_schema():
            print("❌ Impossible d'initialiser le schéma. Abandon.")
            return
    
    print("\n" + "=" * 60)
    print("📥 CHARGEMENT DES DONNÉES")
    print("=" * 60)
    
    # 1. Dimensions (ordre important pour les FK)
    print("\n📐 DIMENSIONS:")
    load_countries()
    load_years()
    load_operators()
    load_stops()
    
    # 2. Faits (après les dimensions)
    print("\n📊 FAITS:")
    load_country_stats()
    load_night_trains()
    
    # 3. Vues
    print("\n📈 VUES:")
    db.refresh_views()
    
    # 4. Résumé
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ DU CHARGEMENT")
    print("=" * 60)
    
    if db.connect():
        tables = [
            'dim_countries', 'dim_years', 'dim_operators', 'dim_stops',
            'facts_night_trains', 'facts_country_stats'
        ]
        for table in tables:
            db.cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = db.cursor.fetchone()[0]
            print(f"   📄 {table:<25} : {count:>10,} lignes")
        
        db.cursor.execute("SELECT COUNT(*) FROM dashboard_metrics")
        print(f"   📈 dashboard_metrics     : {db.cursor.fetchone()[0]:>10,} lignes")
        
        db.cursor.execute("SELECT COUNT(*) FROM operator_dashboard")
        print(f"   📈 operator_dashboard    : {db.cursor.fetchone()[0]:>10,} lignes")
        
        db.close()
    
    print("\n✅ Chargement terminé avec succès !")

if __name__ == "__main__":
    mainload()