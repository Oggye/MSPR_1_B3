"""
Transformation NON DESTRUCTIVE des données Eurostat
"""
import pandas as pd
import numpy as np
import logging
from pathlib import Path
from .config import DATA_RAW, DATA_PROCESSED, COUNTRY_CODES

logger = logging.getLogger(__name__)

class EurostatTransformer:
    """Transforme les données Eurostat SANS supprimer"""
    
    def __init__(self):
        self.raw_path = DATA_RAW / "eurostat"
        self.processed_path = DATA_PROCESSED / "eurostat"
        self.processed_path.mkdir(exist_ok=True)
    
    def clean_passenger_data(self):
        """Nettoie les données de passagers SANS supprimer"""
        logger.info("Nettoyage NON DESTRUCTIF des données passagers Eurostat")
        
        file_path = self.raw_path / "rail_passengers.csv"
        if not file_path.exists():
            logger.error("Fichier rail_passengers.csv introuvable")
            return None
        
        try:
            # Lecture COMPLÈTE
            df = pd.read_csv(file_path)
            original_rows = len(df)
            
            # IMPORTANT: On garde TOUTES les données brutes d'abord
            df_raw = df.copy()
            
            # 1. Extraction des métadonnées SANS perte
            # La première colonne contient tout
            df.columns = ['metadata'] + [str(col) for col in df.columns[1:]]
            
            # Séparation en colonnes distinctes
            split_cols = df['metadata'].str.split(',', expand=True)
            
            # Nombre de colonnes peut varier, on s'adapte
            if split_cols.shape[1] >= 4:
                df[['freq', 'unit', 'vehicle', 'geo']] = split_cols.iloc[:, :4]
            else:
                # Si structure différente, on garde tout dans une colonne
                df['full_metadata'] = df['metadata']
                df['geo'] = split_cols.iloc[:, -1] if split_cols.shape[1] > 0 else 'Unknown'
            
            # 2. Conversion en format long POUR TOUTES LES DONNÉES
            # Identifier les colonnes d'années
            year_cols = []
            for col in df.columns:
                if col.strip().isdigit() and len(col.strip()) == 4:
                    year_cols.append(col)
                elif col.strip().replace(' ', '').isdigit():
                    year_cols.append(col)
            
            # Si aucune colonne d'année détectée, utiliser une approche différente
            if not year_cols:
                logger.warning("Aucune colonne d'année détectée, conservation brute")
                # Sauvegarde brute
                df_raw.to_csv(self.processed_path / "passengers_raw_backup.csv", index=False)
                
                # Essayons une autre approche
                # Recherche des valeurs numériques dans toutes les colonnes
                for col in df.columns[1:]:  # Exclure metadata
                    if df[col].astype(str).str.replace(':', '').str.replace(' ', '').str.isdigit().any():
                        year_cols.append(col)
            
            if year_cols:
                logger.info(f"Colonnes d'années identifiées: {len(year_cols)}")
                
                # Conversion en format long
                df_long = pd.melt(
                    df,
                    id_vars=[col for col in df.columns if col not in year_cols],
                    value_vars=year_cols,
                    var_name='year_raw',
                    value_name='passenger_km_raw'
                )
                
                # On garde la valeur brute ET la valeur nettoyée
                df_long['passenger_km_cleaned'] = pd.to_numeric(
                    df_long['passenger_km_raw'].replace([':', '', 'NaN', 'nan', 'NA'], np.nan),
                    errors='coerce'
                )
                
                # Flag pour valeurs originales ':' (manquantes dans Eurostat)
                df_long['value_was_missing'] = df_long['passenger_km_raw'].isin([':', ' :', ': '])
                
                # Conversion de l'année
                df_long['year'] = pd.to_numeric(df_long['year_raw'].astype(str).str.strip(), errors='coerce')
                
                # Flag pour années invalides
                df_long['year_valid'] = df_long['year'].between(1900, 2100)
                
                # Ajout du nom du pays si possible
                if 'geo' in df_long.columns:
                    df_long['country_name'] = df_long['geo'].map(COUNTRY_CODES)
                    df_long['country_name'] = df_long['country_name'].fillna('Unknown')
                    
                    # Flag pour pays non reconnus
                    df_long['country_recognized'] = df_long['geo'].isin(COUNTRY_CODES.keys())
                
                # Garder TOUTES les lignes, même celles sans données numériques
                logger.info(f"Données passagers format long: {len(df_long):,} lignes")
                
                # Sauvegarde COMPLÈTE
                output_path = self.processed_path / "passengers_complete.csv"
                df_long.to_csv(output_path, index=False)
                
                # Créer aussi une version "nettoyée" pour analyse (mais garder l'original)
                if 'passenger_km_cleaned' in df_long.columns:
                    df_clean = df_long[
                        df_long['passenger_km_cleaned'].notna() & 
                        df_long['year_valid']
                    ].copy()
                    
                    # Pour analyse, on peut regrouper par pays et année
                    df_agg = df_clean.groupby(['geo', 'country_name', 'year'], as_index=False).agg({
                        'passenger_km_cleaned': 'mean'
                    })
                    
                    clean_path = self.processed_path / "passengers_for_analysis.csv"
                    df_agg.to_csv(clean_path, index=False)
                    
                    logger.info(f"Données pour analyse: {len(df_agg)} lignes")
                
                return df_long
            else:
                # Sauvegarde brute si transformation impossible
                logger.warning("Impossible de transformer, sauvegarde brute")
                df.to_csv(self.processed_path / "passengers_untransformed.csv", index=False)
                return df
                
        except Exception as e:
            logger.error(f"Erreur lors du nettoyage des données passagers: {e}")
            # Sauvegarde d'urgence
            try:
                emergency_path = self.processed_path / "passengers_ERROR_backup.csv"
                pd.read_csv(file_path).to_csv(emergency_path, index=False)
                logger.info(f"Sauvegarde d'urgence créée: {emergency_path}")
            except:
                pass
            return None
    
    def clean_traffic_data(self):
        """Nettoie les données de trafic SANS supprimer"""
        logger.info("Nettoyage NON DESTRUCTIF des données trafic Eurostat")
        
        file_path = self.raw_path / "rail_traffic.csv"
        if not file_path.exists():
            logger.error("Fichier rail_traffic.csv introuvable")
            return None
        
        try:
            # Lecture COMPLÈTE
            df = pd.read_csv(file_path)
            original_rows = len(df)
            
            # Sauvegarde brute d'abord
            df_raw = df.copy()
            df_raw.to_csv(self.processed_path / "traffic_raw_backup.csv", index=False)
            
            # Standardisation des noms de colonnes
            df.columns = ['metadata'] + [str(col) for col in df.columns[1:]]
            
            # Extraction des métadonnées
            split_result = df['metadata'].str.split(',', expand=True)
            
            # La structure peut varier, on s'adapte
            n_cols = split_result.shape[1]
            if n_cols >= 6:
                df[['freq', 'train', 'vehicle', 'mot_nrg', 'unit', 'geo']] = split_result.iloc[:, :6]
            elif n_cols >= 5:
                df[['freq', 'train', 'vehicle', 'mot_nrg', 'unit']] = split_result.iloc[:, :5]
                df['geo'] = 'Unknown'
            else:
                df['full_metadata'] = df['metadata']
                df['geo'] = 'Unknown' if n_cols == 0 else split_result.iloc[:, -1]
            
            # Identifier les colonnes d'années
            year_cols = []
            for col in df.columns:
                col_str = str(col).strip()
                if col_str.isdigit() and len(col_str) == 4:
                    year_cols.append(col)
            
            if year_cols:
                # Conversion en format long
                id_cols = [col for col in df.columns if col not in year_cols and col != 'metadata']
                
                df_long = pd.melt(
                    df,
                    id_vars=id_cols,
                    value_vars=year_cols,
                    var_name='year_raw',
                    value_name='train_km_raw'
                )
                
                # Nettoyage des valeurs
                df_long['train_km_cleaned'] = pd.to_numeric(
                    df_long['train_km_raw'].astype(str).replace([':', '', 'NaN', 'nan', 'NA', ' :', ': '], np.nan),
                    errors='coerce'
                )
                
                # Flag pour valeurs manquantes originales
                df_long['value_was_missing'] = df_long['train_km_raw'].astype(str).str.contains(':')
                
                # Conversion année
                df_long['year'] = pd.to_numeric(df_long['year_raw'].astype(str).str.strip(), errors='coerce')
                df_long['year_valid'] = df_long['year'].between(2010, 2030)
                
                # Pays
                if 'geo' in df_long.columns:
                    df_long['country_name'] = df_long['geo'].map(COUNTRY_CODES)
                    df_long['country_name'] = df_long['country_name'].fillna('Unknown')
                
                # Sauvegarde COMPLÈTE
                complete_path = self.processed_path / "traffic_complete.csv"
                df_long.to_csv(complete_path, index=False)
                
                logger.info(f"Données trafic format long: {len(df_long):,} lignes")
                
                # Version pour analyse (sans supprimer, juste filtrer)
                if 'train_km_cleaned' in df_long.columns:
                    df_for_analysis = df_long[
                        df_long['train_km_cleaned'].notna() &
                        df_long['year_valid'] &
                        (df_long['train'] == 'TOTAL')  # Filtrer mais garder les autres dans le fichier complet
                    ].copy()
                    
                    analysis_path = self.processed_path / "traffic_for_analysis.csv"
                    df_for_analysis.to_csv(analysis_path, index=False)
                    
                    logger.info(f"Données trafic pour analyse: {len(df_for_analysis)} lignes")
                
                return df_long
                
            else:
                # Sauvegarde sans transformation
                df.to_csv(self.processed_path / "traffic_untransformed.csv", index=False)
                return df
                
        except Exception as e:
            logger.error(f"Erreur lors du nettoyage des données trafic: {e}")
            # Sauvegarde d'urgence
            try:
                emergency_path = self.processed_path / "traffic_ERROR_backup.csv"
                pd.read_csv(file_path).to_csv(emergency_path, index=False)
            except:
                pass
            return None
    
    def generate_eurostat_report(self):
        """Génère un rapport détaillé sur les données Eurostat"""
        report_path = self.processed_path / "eurostat_completeness_report.txt"
        
        with open(report_path, 'w') as f:
            f.write("=== RAPPORT COMPLÉTUDE DONNÉES EUROSTAT ===\n\n")
            
            # Analyser les fichiers transformés
            for file_name in ['passengers_complete.csv', 'traffic_complete.csv']:
                file_path = self.processed_path / file_name
                if file_path.exists():
                    try:
                        df = pd.read_csv(file_path, nrows=100000)  # Limite pour performance
                        
                        f.write(f"\n{file_name}:\n")
                        f.write(f"  Lignes totales: {len(df):,}\n")
                        
                        # Colonnes clés
                        key_cols = ['year', 'geo', 'country_name']
                        for col in key_cols:
                            if col in df.columns:
                                completeness = (1 - df[col].isnull().mean()) * 100
                                unique_count = df[col].nunique()
                                f.write(f"  - {col}: {completeness:.1f}% complet, {unique_count} valeurs uniques\n")
                        
                        # Valeurs numériques
                        value_cols = [col for col in df.columns if 'cleaned' in col or 'km' in col]
                        for col in value_cols[:3]:  # Premières 3 seulement
                            if col in df.columns:
                                data_present = df[col].notna().sum()
                                data_percent = (data_present / len(df)) * 100
                                f.write(f"  - {col}: {data_present:,} valeurs ({data_percent:.1f}%)\n")
                        
                        # Flag pour valeurs manquantes
                        if 'value_was_missing' in df.columns:
                            missing_flags = df['value_was_missing'].sum()
                            f.write(f"  - Valeurs originales manquantes (':'): {missing_flags:,}\n")
                    
                    except Exception as e:
                        f.write(f"  ERREUR lors de l'analyse: {e}\n")