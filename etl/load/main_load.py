"""
Orchestrateur principal du chargement PostgreSQL
"""
import sys
import time
from database import db

# Importer les fonctions de chargement
from load_countries import load_countries
from load_years import load_years
from load_operators import load_operators
from load_night_trains import load_night_trains
from load_country_stats import load_country_stats

def mainload():
    """Fonction principale"""
        
    print("\n🔌 Test de connexion à PostgreSQL...")

    # Tester la connexion via la classe db
    if not db.test_connection():
        print("❌ Échec de la connexion à PostgreSQL")
        print("   Vérifiez que:")
        print("   1. PostgreSQL est en cours d'exécution")
        print("   2. La base 'obrail' existe")
        print("   3. L'utilisateur 'obrail_user' a les bons droits")
        print("   4. Les tables sont créées (exécutez 01_init.sql)")
        return False

    # Chargement complet
    print("\n🚀 Démarrage du chargement...")
    steps = [
        ("Années", load_years),
        ("Opérateurs", load_operators),
        ("Pays", load_countries),
        ("Trajets par pays ", load_country_stats),
        ("Trajets de nuit ", load_night_trains),
    ]
            
    for step_name, step_func in steps:
        print(f"\n➡️  Étape: {step_name}")
        if not step_func():
            print(f"❌ Échec à l'étape: {step_name}")
            break
            
    return True

if __name__ == "__main__":
    mainload()