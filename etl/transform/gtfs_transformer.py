"""
Transformation non destructive des données GTFS
"""
import pandas as pd
import numpy as np
from pathlib import Path
import logging
from .config import DATA_RAW, DATA_PROCESSED, COUNTRY_CODES, CLEANING_STRATEGY

logger = logging.getLogger(__name__)

class GTFSTransformer:
    """Transforme les données GTFS SANS supprimer de lignes"""
    
    def __init__(self, country_code):
        self.country_code = country_code
        self.raw_path = DATA_RAW / f"gtfs_{country_code.lower()}"
        self.processed_path = DATA_PROCESSED / f"gtfs_{country_code.lower()}"
        self.processed_path.mkdir(exist_ok=True)
        
    def clean_stops(self):
        """Nettoyage du fichier stops.csv SANS suppression"""
        logger.info(f"Nettoyage NON DESTRUCTIF des stops pour {self.country_code}")
        
        file_path = self.raw_path / "stops.csv"
        if not file_path.exists():
            logger.warning(f"Fichier stops.csv introuvable pour {self.country_code}")
            return None
            
        try:
            # Lecture complète
            df = pd.read_csv(file_path, low_memory=False)
            original_rows = len(df)
            
            # Standardisation des noms de colonnes
            df.columns = df.columns.str.lower().str.replace(' ', '_')
            
            # Ajout du code pays
            df['country'] = self.country_code
            
            # 1. FLAG des valeurs manquantes au lieu de les supprimer
            for col in df.columns:
                if col.startswith('stop_'):
                    missing_count = df[col].isnull().sum()
                    if missing_count > 0:
                        # Créer une colonne flag
                        flag_col = f"{col}_missing"
                        df[flag_col] = df[col].isnull()
                        
                        # Remplir avec des valeurs par défaut explicites
                        if col == 'stop_name':
                            df[col] = df[col].fillna(f"Station_Inconnue_{self.country_code}")
                        elif 'lat' in col or 'lon' in col:
                            df[col] = df[col].fillna(0)  # 0 est clairement une valeur invalide
                        else:
                            df[col] = df[col].fillna('N/A')
            
            # 2. Standardisation de l'ID (sans perdre l'original)
            if 'stop_id' in df.columns:
                # Garder l'original
                df['stop_id_original'] = df['stop_id'].astype(str)
                # Créer un ID standardisé
                df['stop_id_standardized'] = self.country_code + '_' + df['stop_id_original']
                # Utiliser le standardisé comme ID principal
                df['stop_id'] = df['stop_id_standardized']
            
            # 3. Vérification des coordonnées (flag au lieu de suppression)
            if 'stop_lat' in df.columns and 'stop_lon' in df.columns:
                # Flag pour coordonnées invalides
                df['coordinates_valid'] = (
                    df['stop_lat'].between(-90, 90) & 
                    df['stop_lon'].between(-180, 180)
                )
                
                # Flag pour coordonnées nulles
                df['coordinates_zero'] = (df['stop_lat'] == 0) & (df['stop_lon'] == 0)
            
            # 4. Gestion des doublons (flag uniquement)
            if 'stop_id' in df.columns:
                df['is_duplicate_id'] = df['stop_id'].duplicated(keep=False)
            
            # Sauvegarde TOUTES les données
            output_path = self.processed_path / "stops_clean.csv"
            df.to_csv(output_path, index=False)
            
            # Rapport
            logger.info(f"Stops nettoyés : {len(df)} lignes (original: {original_rows})")
            logger.info(f"  - Valeurs manquantes flaggées")
            logger.info(f"  - Aucune ligne supprimée")
            
            return df
            
        except Exception as e:
            logger.error(f"Erreur lors du nettoyage des stops {self.country_code}: {e}")
            return None
    
    def clean_routes(self):
        """Nettoyage du fichier routes.csv SANS suppression"""
        logger.info(f"Nettoyage NON DESTRUCTIF des routes pour {self.country_code}")
        
        file_path = self.raw_path / "routes.csv"
        if not file_path.exists():
            logger.warning(f"Fichier routes.csv introuvable pour {self.country_code}")
            return None
            
        try:
            df = pd.read_csv(file_path, low_memory=False)
            original_rows = len(df)
            
            # Standardisation
            df.columns = df.columns.str.lower().str.replace(' ', '_')
            
            # Gestion des valeurs manquantes
            text_cols = ['route_short_name', 'route_long_name', 'route_desc']
            for col in text_cols:
                if col in df.columns:
                    missing_mask = df[col].isnull()
                    if missing_mask.any():
                        df[f"{col}_missing"] = missing_mask
                        df[col] = df[col].fillna('')
            
            # Type de transport standardisé
            if 'route_type' in df.columns:
                route_type_map = {
                    0: 'Tram', 1: 'Metro', 2: 'Train', 3: 'Bus',
                    4: 'Ferry', 5: 'Cable car', 6: 'Gondola',
                    7: 'Funicular', 100: 'Railway', 109: 'Suburban',
                    400: 'Urban rail', -1: 'Unknown'
                }
                df['transport_type'] = df['route_type'].map(route_type_map)
                
                # Flag pour types inconnus
                df['route_type_unknown'] = df['transport_type'].isnull()
                df['transport_type'] = df['transport_type'].fillna('Unknown')
            
            # Standardisation IDs (garder l'original)
            for id_col in ['route_id', 'agency_id']:
                if id_col in df.columns:
                    df[f"{id_col}_original"] = df[id_col].astype(str)
                    df[id_col] = self.country_code + '_' + df[f"{id_col}_original"]
            
            # Sauvegarde
            output_path = self.processed_path / "routes_clean.csv"
            df.to_csv(output_path, index=False)
            
            logger.info(f"Routes nettoyées : {len(df)} lignes (original: {original_rows})")
            
            return df
            
        except Exception as e:
            logger.error(f"Erreur lors du nettoyage des routes {self.country_code}: {e}")
            return None
    
    def clean_stop_times(self, sample_ratio=None):
        """Nettoyage des stop_times SANS suppression"""
        logger.info(f"Nettoyage NON DESTRUCTIF des stop_times pour {self.country_code}")
        
        file_path = self.raw_path / "stop_times.csv"
        if not file_path.exists():
            logger.warning(f"Fichier stop_times.csv introuvable pour {self.country_code}")
            return None
            
        try:
            # Détection de la taille du fichier
            file_size = file_path.stat().st_size
            
            # Pour fichiers TRÈS gros (> 500MB), on prend un échantillon représentatif
            # MAIS on sauvegarde quand même les métadonnées complètes
            if file_size > 500_000_000 and sample_ratio:
                logger.info(f"Fichier très volumineux ({file_size/1e9:.2f}GB), échantillonnage à {sample_ratio*100}%")
                
                # Méthode: lire tous les IDs uniques d'abord
                logger.info("Lecture des IDs uniques...")
                trip_ids = pd.read_csv(file_path, usecols=['trip_id'], low_memory=False)
                unique_trips = trip_ids['trip_id'].unique()
                
                # Échantillonner les trips
                sampled_trips = np.random.choice(
                    unique_trips, 
                    size=int(len(unique_trips) * sample_ratio),
                    replace=False
                )
                
                # Lire seulement les trips échantillonnés
                logger.info("Lecture des données échantillonnées...")
                chunks = []
                for chunk in pd.read_csv(file_path, chunksize=100000, low_memory=False):
                    chunk = chunk[chunk['trip_id'].isin(sampled_trips)]
                    if len(chunk) > 0:
                        chunks.append(chunk)
                
                df = pd.concat(chunks, ignore_index=True)
                
                # Sauvegarde des métadonnées sur l'échantillonnage
                sampling_info = {
                    'original_file_size_gb': file_size / 1e9,
                    'sampling_ratio': sample_ratio,
                    'original_unique_trips': len(unique_trips),
                    'sampled_unique_trips': len(sampled_trips),
                    'sampled_rows': len(df)
                }
                
                # Sauvegarde des infos d'échantillonnage
                info_path = self.processed_path / "stop_times_sampling_info.json"
                import json
                with open(info_path, 'w') as f:
                    json.dump(sampling_info, f, indent=2)
                    
            else:
                # Lecture complète
                df = pd.read_csv(file_path, low_memory=False)
            
            original_rows = len(df)
            
            # Standardisation
            df.columns = df.columns.str.lower().str.replace(' ', '_')
            
            # Standardisation des IDs
            for id_col in ['trip_id', 'stop_id']:
                if id_col in df.columns:
                    # Garder l'original
                    df[f"{id_col}_original"] = df[id_col].astype(str)
                    # Standardiser
                    df[id_col] = self.country_code + '_' + df[f"{id_col}_original"]
            
            # Vérification des heures (flag au lieu de suppression)
            for time_col in ['arrival_time', 'departure_time']:
                if time_col in df.columns:
                    # Flag pour formats invalides
                    df[f"{time_col}_valid"] = df[time_col].astype(str).str.match(r'^\d{2}:\d{2}:\d{2}$', na=False)
                    
                    # Flag pour valeurs manquantes
                    df[f"{time_col}_missing"] = df[time_col].isnull()
                    
                    # Remplissage avec une valeur par défaut
                    df[time_col] = df[time_col].fillna('00:00:00')
            
            # Flag pour stop_sequence invalide
            if 'stop_sequence' in df.columns:
                df['stop_sequence_invalid'] = (
                    df['stop_sequence'].isnull() | 
                    (df['stop_sequence'] < 0)
                )
            
            # Sauvegarde
            output_path = self.processed_path / "stop_times_clean.csv"
            df.to_csv(output_path, index=False)
            
            logger.info(f"Stop times nettoyés : {len(df)} lignes (original: {original_rows})")
            
            return df
            
        except Exception as e:
            logger.error(f"Erreur lors du nettoyage des stop_times {self.country_code}: {e}")
            return None
    
    def clean_trips(self):
        """Nettoyage du fichier trips.csv SANS suppression"""
        logger.info(f"Nettoyage NON DESTRUCTIF des trips pour {self.country_code}")
        
        file_path = self.raw_path / "trips.csv"
        if not file_path.exists():
            logger.warning(f"Fichier trips.csv introuvable pour {self.country_code}")
            return None
            
        try:
            df = pd.read_csv(file_path, low_memory=False)
            original_rows = len(df)
            
            df.columns = df.columns.str.lower().str.replace(' ', '_')
            
            # Standardisation IDs (garder l'original)
            for id_col in ['trip_id', 'route_id', 'service_id']:
                if id_col in df.columns:
                    df[f"{id_col}_original"] = df[id_col].astype(str)
                    df[id_col] = self.country_code + '_' + df[f"{id_col}_original"]
            
            # Ajout du pays
            df['country'] = self.country_code
            
            # Flag pour les champs manquants
            if 'trip_headsign' in df.columns:
                df['trip_headsign_missing'] = df['trip_headsign'].isnull()
                df['trip_headsign'] = df['trip_headsign'].fillna('Destination_Inconnue')
            
            # Sauvegarde
            output_path = self.processed_path / "trips_clean.csv"
            df.to_csv(output_path, index=False)
            
            logger.info(f"Trips nettoyés : {len(df)} lignes (original: {original_rows})")
            
            return df
            
        except Exception as e:
            logger.error(f"Erreur lors du nettoyage des trips {self.country_code}: {e}")
            return None
    
    def transform_all(self):
        """Exécute toutes les transformations SANS suppression"""
        logger.info(f"=== Transformation GTFS NON DESTRUCTIVE pour {self.country_code} ===")
        
        # Pour la Suisse, on échantillonne les gros fichiers mais on garde TOUT le reste
        sample_ratio = 0.05 if self.country_code == 'CH' else None
        
        results = {
            'stops': self.clean_stops(),
            'routes': self.clean_routes(),
            'stop_times': self.clean_stop_times(sample_ratio),
            'trips': self.clean_trips()
        }
        
        # Rapport de qualité détaillé
        self._generate_quality_report(results)
        
        return results
    
    def _generate_quality_report(self, results):
        """Génère un rapport de qualité détaillé"""
        report_path = self.processed_path / "quality_report.txt"
        
        with open(report_path, 'w') as f:
            f.write(f"=== RAPPORT QUALITÉ GTFS {self.country_code} ===\n")
            f.write(f"Stratégie: NON DESTRUCTIVE - Aucune ligne supprimée\n\n")
            
            total_rows = 0
            total_columns = 0
            
            for dataset_name, df in results.items():
                if df is not None:
                    f.write(f"\n{dataset_name.upper()}:\n")
                    f.write(f"  Lignes: {len(df):,}\n")
                    f.write(f"  Colonnes: {len(df.columns)}\n")
                    
                    total_rows += len(df)
                    total_columns += len(df.columns)
                    
                    # Détail des flags de qualité
                    flag_cols = [col for col in df.columns if any(x in col for x in ['missing', 'invalid', 'duplicate', 'valid'])]
                    if flag_cols:
                        f.write(f"  Flags de qualité créés:\n")
                        for flag_col in flag_cols:
                            flag_count = df[flag_col].sum() if df[flag_col].dtype == bool else 'N/A'
                            f.write(f"    - {flag_col}: {flag_count}\n")
                    
                    # Pourcentages de complétude
                    f.write(f"  Complétude des colonnes principales:\n")
                    main_cols = [col for col in df.columns if not any(x in col for x in ['original', 'missing', 'invalid', 'duplicate'])]
                    for col in main_cols[:10]:  # Premières 10 seulement
                        if col in df.columns:
                            completeness = (1 - df[col].isnull().mean()) * 100
                            f.write(f"    - {col}: {completeness:.1f}%\n")
                
                else:
                    f.write(f"\n{dataset_name.upper()}: NON TRAITÉ\n")
            
            f.write(f"\n=== TOTAL {self.country_code} ===\n")
            f.write(f"Lignes totales: {total_rows:,}\n")
            f.write(f"Colonnes totales: {total_columns}\n")
        
        logger.info(f"Rapport qualité généré: {report_path}")