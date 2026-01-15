"""
Enrichit les données transformées avec des calculs et jointures.
"""
from .base_transformer import BaseTransformer
import pandas as pd
import numpy as np
from pathlib import Path
from geopy.distance import geodesic
import logging

class DataEnricher(BaseTransformer):
    """Enrichit les données avec des métriques calculées."""
    
    def __init__(self):
        super().__init__('enricher')
    
    def create_star_schema(self, processed_path, warehouse_path):
        """Crée le schéma en étoile pour la BDD."""
        try:
            # Chargement des données transformées
            stops_fr = pd.read_parquet(Path(processed_path) / 'stops_fr.parquet')
            stops_ch = pd.read_parquet(Path(processed_path) / 'stops_ch.parquet')
            stops_de = pd.read_parquet(Path(processed_path) / 'stops_de.parquet')
            
            # Concaténation des stops
            all_stops = pd.concat([stops_fr, stops_ch, stops_de], ignore_index=True)
            
            # Création de la dimension GARE
            dim_gare = self.create_dim_gare(all_stops)
            
            # Création de la dimension TEMPS
            dim_temps = self.create_dim_temps()
            
            # Création de la dimension OPERATEUR
            dim_operateur = self.create_dim_operateur(processed_path)
            
            # Création de la dimension TRAJET
            dim_trajet = self.create_dim_trajet(processed_path)
            
            # Création de la table de fait TRAFIC
            fact_trafic = self.create_fact_trafic(processed_path, dim_gare, dim_temps, dim_operateur, dim_trajet)
            
            # Création de la table de fait EMISSIONS
            fact_emissions = self.create_fact_emissions(processed_path, dim_temps)
            
            # Sauvegarde du schéma en étoile
            self.save_star_schema(warehouse_path, {
                'dim_gare': dim_gare,
                'dim_temps': dim_temps,
                'dim_operateur': dim_operateur,
                'dim_trajet': dim_trajet,
                'fact_trafic': fact_trafic,
                'fact_emissions': fact_emissions
            })
            
            self.logger.info("Schéma en étoile créé avec succès")
            
        except Exception as e:
            self.logger.error(f"Erreur création schéma étoile: {e}")
            raise
    
    def create_dim_gare(self, stops_df):
        """Crée la dimension GARE."""
        dim_gare = stops_df[[
            'stop_uid', 'stop_name', 'stop_lat', 'stop_lon',
            'country_code', 'stop_type', 'parent_station'
        ]].copy()
        
        # Renommage pour la BDD
        dim_gare = dim_gare.rename(columns={
            'stop_uid': 'id_gare',
            'stop_name': 'nom_gare',
            'stop_lat': 'latitude',
            'stop_lon': 'longitude',
            'country_code': 'code_pays',
            'stop_type': 'type_gare'
        })
        
        # Ajout d'informations de région (simplifié)
        dim_gare['region'] = dim_gare.apply(self.determine_region, axis=1)
        
        # Indexation
        dim_gare = dim_gare.drop_duplicates('id_gare')
        dim_gare['id_gare'] = range(1, len(dim_gare) + 1)
        
        return dim_gare
    
    def determine_region(self, row):
        """Détermine la région à partir des coordonnées."""
        # Cette fonction devrait utiliser une API de géocodage inverse
        # Version simplifiée:
        lat, lon = row['latitude'], row['longitude']
        
        # Zones approximatives
        if 48.5 <= lat <= 51.5 and -0.5 <= lon <= 3.0:
            return 'Île-de-France'
        elif 45.0 <= lat <= 47.0 and 5.0 <= lon <= 7.0:
            return 'Suisse Romande'
        elif 47.0 <= lat <= 55.0 and 6.0 <= lon <= 15.0:
            return 'Allemagne'
        else:
            return 'Autre'
    
    def create_dim_temps(self):
        """Crée la dimension TEMPS (années 1970-2024)."""
        years = range(1970, 2025)
        months = range(1, 13)
        
        dates = []
        for year in years:
            for month in months:
                dates.append({
                    'id_temps': f"{year}{month:02d}",
                    'annee': year,
                    'mois': month,
                    'trimestre': (month - 1) // 3 + 1,
                    'semestre': 1 if month <= 6 else 2,
                    'saison': self.get_season(month)
                })
        
        return pd.DataFrame(dates)
    
    def get_season(self, month):
        """Retourne la saison."""
        if month in [12, 1, 2]:
            return 'Hiver'
        elif month in [3, 4, 5]:
            return 'Printemps'
        elif month in [6, 7, 8]:
            return 'Été'
        else:
            return 'Automne'
    
    def create_dim_operateur(self, processed_path):
        """Crée la dimension OPÉRATEUR."""
        # Charger les agences de tous les pays
        agencies = []
        for country in ['fr', 'ch', 'de']:
            try:
                df = pd.read_parquet(Path(processed_path) / f'agencies_{country}.parquet')
                agencies.append(df)
            except:
                continue
        
        if agencies:
            all_agencies = pd.concat(agencies, ignore_index=True)
        else:
            all_agencies = pd.DataFrame()
        
        # Charger les opérateurs de nuit
        try:
            night_routes = pd.read_parquet(Path(processed_path) / 'night_routes.parquet')
            night_operators = night_routes.explode('operators_standardized')
            night_operators = night_operators[['operators_standardized']].dropna()
            night_operators = night_operators.rename(columns={'operators_standardized': 'agency_name'})
            night_operators['country_code'] = 'MULTI'
        except:
            night_operators = pd.DataFrame()
        
        # Fusion
        if not all_agencies.empty:
            dim_operateur = all_agencies[['agency_uid', 'agency_name', 'country_code']].copy()
        else:
            dim_operateur = pd.DataFrame(columns=['agency_uid', 'agency_name', 'country_code'])
        
        # Ajout des opérateurs de nuit
        if not night_operators.empty:
            for _, row in night_operators.iterrows():
                if not dim_operateur[dim_operateur['agency_name'] == row['agency_name']].any().any():
                    new_uid = self.generate_id(row['agency_name'], 'operator')
                    new_row = pd.DataFrame([{
                        'agency_uid': new_uid,
                        'agency_name': row['agency_name'],
                        'country_code': row['country_code']
                    }])
                    dim_operateur = pd.concat([dim_operateur, new_row], ignore_index=True)
        
        # Standardisation
        dim_operateur = dim_operateur.rename(columns={
            'agency_uid': 'id_operateur',
            'agency_name': 'nom_operateur'
        })
        
        # Indexation
        dim_operateur = dim_operateur.drop_duplicates('id_operateur')
        dim_operateur['id_operateur'] = range(1, len(dim_operateur) + 1)
        
        return dim_operateur
    
    def create_fact_trafic(self, processed_path, dim_gare, dim_temps, dim_operateur, dim_trajet):
        """Crée la table de fait TRAFIC."""
        # Cette fonction fusionnerait les données de trafic réelles
        # Pour l'instant, retourne un DataFrame vide
        fact_trafic = pd.DataFrame(columns=[
            'id_fact', 'id_gare', 'id_temps', 'id_operateur', 'id_trajet',
            'nb_passagers', 'nb_trains', 'passagers_km'
        ])
        
        return fact_trafic