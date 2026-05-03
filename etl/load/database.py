# etl/load/database.py
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
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', 5432)),
            'database': os.getenv('DB_NAME', 'obrail'),
            'user': os.getenv('DB_USER', 'obrail_user'),
            'password': os.getenv('DB_PASSWORD', '1234')
        }
    
    def connect(self):
        """Établir la connexion à la base de données"""
        try:
            self.connection = psycopg2.connect(**self.config)
            self.cursor = self.connection.cursor()
            return True
        except Exception as e:
            print(f"Erreur de connexion: {e}")
            return False

    def test_connection(self):
        """Vérifie que tout fonctionne et que les tables sont là"""
        if not self.connect():
            return False
        
        try:
            self.cursor.execute("SELECT 1")
            print("✅ Connexion PostgreSQL établie")
            
            essential_tables = [
                'dim_countries', 
                'dim_years', 
                'dim_operators',
                'dim_stops',
                'facts_night_trains', 
                'facts_country_stats'
            ]

            print("\n📋 Vérification des tables:")
            missing = []
            for table in essential_tables:
                self.cursor.execute(f"""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = '{table}'
                    )
                """)
                exists = self.cursor.fetchone()[0]
                status = "✅" if exists else "❌"
                print(f"   {status} {table}")
                if not exists:
                    missing.append(table)
            
            if missing:
                print(f"\n❌ {len(missing)} table(s) manquante(s). Exécutez d'abord le script SQL d'initialisation.")
                return False
            
            print("\n✅ Toutes les tables essentielles sont présentes")

            # Vérifier les vues
            print("\n📋 Vérification des vues:")
            for view in ['dashboard_metrics', 'operator_dashboard']:
                self.cursor.execute(f"""
                    SELECT EXISTS (
                        SELECT FROM information_schema.views 
                        WHERE table_schema = 'public' 
                        AND table_name = '{view}'
                    )
                """)
                exists = self.cursor.fetchone()[0]
                status = "✅" if exists else "⚠️"
                print(f"   {status} {view}")

            return True
        except Exception as e:
            print(f"❌ Erreur test: {e}")
            return False
        finally:
            self.close()

    def execute_query(self, query, params=None):
        """Exécute une requête SQL et gère la connexion automatiquement"""
        try:
            if not self.connection:
                self.connect()
            
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            
            self.connection.commit()
            return self.cursor
        except Exception as e:
            print(f"❌ Erreur requête: {e}")
            if self.connection:
                self.connection.rollback()
            return None
    
    def load_dataframe(self, df, table_name):
        """Charger un DataFrame dans une table - version corrigée et complète"""
        try:
            if not self.connect():
                return False
            
            print(f"📥 Chargement de {table_name}... ({len(df)} lignes)")
            
            # Vider la table AVEC CASCADE pour les contraintes FK
            self.cursor.execute(f"TRUNCATE TABLE {table_name} CASCADE")
            
            # Insérer les données selon la table
            if table_name == 'dim_stops':
                for row in df.itertuples():
                    self.cursor.execute(
                        """INSERT INTO dim_stops (stop_id_dim, stop_name, stop_lat, stop_lon, stop_id, source_country) 
                        VALUES (%s, %s, %s, %s, %s, %s)""",
                        (row.stop_id_dim, row.stop_name, row.stop_lat, row.stop_lon, 
                         row.stop_id if hasattr(row, 'stop_id') else None, 
                         row.source_country)
                    )
            
            elif table_name == 'dim_years':
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
                        (fact_id, route_id, night_train, country_id, year_id, operator_id, is_night, distance_km, duration_min) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                        (row.fact_id, row.route_id, row.night_train, row.country_id, 
                         row.year_id, row.operator_id, row.is_night, row.distance_km, row.duration_min)
                    )
            
            elif table_name == 'facts_country_stats':
                for row in df.itertuples():
                    self.cursor.execute(
                        """INSERT INTO facts_country_stats 
                        (stat_id, country_id, year_id, passengers, co2_emissions, co2_per_passenger) 
                        VALUES (%s, %s, %s, %s, %s, %s)""",
                        (row.stat_id, row.country_id, row.year_id, row.passengers, row.co2_emissions, row.co2_per_passenger)
                    )
            
            # Validation de toutes les insertions            
            self.connection.commit()
            print(f"   ✅ {table_name} chargé avec succès")
            return True
            
        except Exception as e:
            print(f"❌ Erreur chargement {table_name}: {e}")
            if self.connection:
                self.connection.rollback()
            import traceback
            traceback.print_exc()
            return False
   
    def refresh_views(self):
        """Recréer les vues dashboard"""
        if not self.connect():
            return False
        
        try:
            print("🔄 Recréation des vues...")
            
            self.cursor.execute("DROP VIEW IF EXISTS dashboard_metrics CASCADE")
            self.cursor.execute("DROP VIEW IF EXISTS operator_dashboard CASCADE")
            
            self.cursor.execute("""
                CREATE VIEW dashboard_metrics AS
                SELECT 
                    c.country_id,
                    c.country_name,
                    c.country_code,
                    AVG(s.passengers)::NUMERIC(15, 2) as avg_passengers,
                    AVG(s.co2_emissions)::NUMERIC(15, 4) as avg_co2_emissions,
                    AVG(s.co2_per_passenger)::NUMERIC(15, 6) as avg_co2_per_passenger
                FROM facts_country_stats s
                JOIN dim_countries c ON s.country_id = c.country_id
                GROUP BY c.country_id, c.country_name, c.country_code
            """)
            
            self.cursor.execute("""
                CREATE VIEW operator_dashboard AS
                SELECT 
                    o.operator_id,
                    o.operator_name,
                    COUNT(f.fact_id) as nb_trains,
                    SUM(CASE WHEN f.is_night = TRUE THEN 1 ELSE 0 END) as nb_trains_nuit,
                    SUM(CASE WHEN f.is_night = FALSE THEN 1 ELSE 0 END) as nb_trains_jour,
                    COALESCE(SUM(f.distance_km), 0)::NUMERIC(15, 2) as distance_totale_km,
                    COALESCE(AVG(f.duration_min), 0)::NUMERIC(10, 1) as duree_moyenne_min
                FROM dim_operators o
                LEFT JOIN facts_night_trains f ON o.operator_id = f.operator_id
                GROUP BY o.operator_id, o.operator_name
                ORDER BY nb_trains DESC
            """)
            
            self.connection.commit()
            print("   ✅ Vues créées avec succès")
            return True
        except Exception as e:
            print(f"❌ Erreur création vues: {e}")
            return False

    def close(self):
        """Fermer la connexion"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

# Instance globale
db = DatabaseConnection()