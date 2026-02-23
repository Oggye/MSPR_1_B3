"""
Orchestrateur principal du chargement PostgreSQL
"""
import sys
import time
from database import db
import os 
import json
# Importer les fonctions de chargement
from load_countries import load_countries
from load_years import load_years
from load_operators import load_operators
from load_night_trains import load_night_trains
from load_country_stats import load_country_stats


def load_reports():
    """Charger quality_reports depuis data/warehouse vers platform/server/app/reports"""
    
    # Créer le dossier
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    report_path = os.path.join(project_root, "platform", "server", "app", "reports")
    os.makedirs(report_path, exist_ok=True)
    
    # Définir les chemins source et destination
    chemin_source = "data/warehouse/quality_reports.json"
    chemin_destination = os.path.join(report_path, "quality_reports.json")
    
    # Vérifier que le fichier source existe
    if not os.path.exists(chemin_source):
        print(f"❌ Fichier source introuvable: {chemin_source}")
        # Créer un fichier vide par défaut
        donnees_source = {"reports": [], "status": "default"}
    else:
        # Lire les données source
        with open(chemin_source, 'r', encoding='utf-8') as f:
            donnees_source = json.load(f)
        print(f"✅ Données lues depuis {chemin_source}")
        
    # Écrire dans le fichier destination
    with open(chemin_destination, 'w', encoding='utf-8') as f:
        json.dump(donnees_source, f, indent=2, ensure_ascii=False)

    return True

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
        ("Chargement de quality reports ", load_reports),
    ]
            
    for step_name, step_func in steps:
        print(f"\n➡️  Étape: {step_name}")
        if not step_func():
            print(f"❌ Échec à l'étape: {step_name}")
            break
            
    return True

if __name__ == "__main__":
    mainload()