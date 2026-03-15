import os
import psycopg2 
import pandas as pd
from psycopg2.extras import execute_values

class DatabaseConnection:
    """Gestion de la connexion à PostgreSQL"""
    
    def __init__(self):
        """Initialisation des attributs de connexion"""
        self.connection = None
        self.cursor = None

        # Paramètres de connexion - à adapter selon votre environnement
        self.config = {
            'host': 'localhost',
            'port': 5432,
            'database': 'obrail',
            'user': 'obrail_user',
            'password': '1234'
        }
    
    def connect(self):
        """Établir la connexion à la base de données"""
        try:
            # Tentative de connexion avec les paramètres configurés
            self.connection = psycopg2.connect(**self.config)
            # On crée un curseur pour pouvoir exécuter des requêtes
            self.cursor = self.connection.cursor()
            return True
        except Exception as e:
            # Si la connexion échoue, on affiche l'erreur
            print(f"Erreur de connexion: {e}")
            return False

    def test_connection(self):
        """Vérifie que tout fonctionne et que les tables sont là"""
        if not self.connect():
            return False
        
        try:
            # Test basique pour voir si PostgreSQL répond
            self.cursor.execute("SELECT 1")
            print("✅ Connexion PostgreSQL établie")
            
            # Vérifier les tables essentielles
            essential_tables = [
                'dim_countries', 
                'dim_years', 
                'dim_operators', 
                'facts_night_trains', 
                'facts_country_stats'
            ]

            missing = []

            print("\n📋 Vérification des tables:")
            # Vérification de chaque table
            for table in essential_tables:
                self.cursor.execute(f"""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = '{table}'
                    )
                """)
                print(f"{table} : existe")
                
                if not self.cursor.fetchone()[0]:
                    missing.append(table)
            
            # On vérifie les tables manquantes
            if missing:
                print(f"❌ Tables manquantes:")
                for table in missing:
                    print(f"   - {table}")
                print("Créer les tables")
                return False
            
            print("✅ Toutes les tables essentielles sont présentes")

            # Vérifier le vue pour le dashboard
            print("\n📋 Vérification de la vue:")
            self.cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.views 
                        WHERE table_schema = 'public' 
                        AND table_name = 'dashboard_metrics'
                    )
                """)

            exists = self.cursor.fetchone()[0]
            if exists:
                    print(f"dashboard_metric: vue présente")
            else:
                    print(f"❌ dashboard_metric: vue absente")

            return True
        except Exception as e:
            print(f"❌ Erreur test: {e}")
            return False
        finally:
            self.close()

    def execute_query(self, query, params=None):
        """Exécute une requête SQL et gère la connexion automatiquement"""
        try:
            # Établir une connexion si nécessaire
            if not self.connection:
                self.connect()
            
            # Exécution avec ou sans paramètres
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            
            # Validation de la transaction
            self.connection.commit()
            return self.cursor
        except Exception as e:
            print(f"❌ Erreur requête: {e}")
            return None
    
    def load_dataframe(self, df, table_name):
        """Charger un DataFrame dans une table"""
        try:
            if not self.connect():
                return False
            
            print(f"📥 Chargement de {table_name}...")
            
            # Vider la table AVEC CASCADE pour les contraintes FK
            self.cursor.execute(f"TRUNCATE TABLE {table_name} CASCADE")
            
            # Insérer les données selon la table
            if table_name == 'dim_years':
                for row in df.itertuples():
                    self.cursor.execute(
                        "INSERT INTO dim_years (year_id, year, is_after_2010) VALUES (%s, %s, %s)",
                        (row.year_id, row.year, row.is_after_2010)
                    )
            
            elif table_name == 'dim_countries':
                for row in df.itertuples():
                    self.cursor.execute(
                        "INSERT INTO dim_countries (country_id, country_code, country_name) VALUES (%s, %s, %s)",
                        (row.country_id, row.country_code, row.country_name)
                    )
            
            elif table_name == 'dim_operators':
                for row in df.itertuples():
                    self.cursor.execute(
                        "INSERT INTO dim_operators (operator_id, operator_name) VALUES (%s, %s)",
                        (row.operator_id, row.operator_name)
                    )

            elif table_name == 'facts_night_trains':
                for row in df.itertuples():
                    self.cursor.execute(
                        """INSERT INTO facts_night_trains 
                        (fact_id, route_id, night_train, operator_id, year_id, country_id) 
                        VALUES (%s, %s, %s, %s, %s, %s)""",
                        (row.fact_id, row.route_id, row.night_train, row.operator_id, row.year_id, row.country_id)
                    )
            
            elif table_name == 'facts_country_stats':
                for row in df.itertuples():
                    self.cursor.execute(
                        """INSERT INTO facts_country_stats 
                        (stats_id, passengers, co2_emissions, co2_per_passenger, country_id, year_id) 
                        VALUES (%s, %s, %s, %s, %s, %s)""",
                        (row.stat_id, row.passengers, row.co2_emissions, row.co2_per_passenger, row.country_id, row.year_id)
                    )
            
            # Validation de toutes les insertions            
            self.connection.commit()
            return True
            
        except Exception as e:
            print(f"❌ Erreur chargement {table_name}: {e}")
            return False
   
    def close(self):
        """Fermer la connexion"""
        if self.cursor:
            self.cursor.close()  # Fermeture du curseur
        if self.connection:
            self.connection.close() # Fermeture de la connexion

# Instance globale
db = DatabaseConnection()