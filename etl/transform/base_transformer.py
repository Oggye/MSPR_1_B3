"""
Classe de base pour toutes les transformations.
Gère les logs, métriques et méthodes communes.
"""
import pandas as pd
import numpy as np
import logging
from pathlib import Path
import json
from datetime import datetime
import hashlib

class BaseTransformer:
    """Classe parente pour toutes les transformations de données."""
    
    def __init__(self, source_name):
        self.source_name = source_name
        self.metrics = {}
        self.setup_logging()
        
    def setup_logging(self):
        """Configure le système de logs."""
        self.logger = logging.getLogger(f'transform_{self.source_name}')
        self.logger.setLevel(logging.INFO)
        
        if not self.logger.handlers:
            handler = logging.FileHandler(f'logs/transform_{self.source_name}.log')
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def log_transform(self, step, df_before, df_after):
        """Log une étape de transformation avec métriques."""
        rows_before = len(df_before)
        rows_after = len(df_after)
        cols_before = len(df_before.columns)
        cols_after = len(df_after.columns)
        
        self.logger.info(f"{step}: {rows_before} → {rows_after} lignes, {cols_before} → {cols_after} colonnes")
        self.metrics[step] = {
            'rows_before': rows_before,
            'rows_after': rows_after,
            'cols_before': cols_before,
            'cols_after': cols_after
        }
    
    def save_metrics(self):
        """Sauvegarde les métriques dans un fichier JSON."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        metrics_file = Path(f'data/processed/metrics/{self.source_name}_{timestamp}.json')
        metrics_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(metrics_file, 'w') as f:
            json.dump(self.metrics, f, indent=2)
    
    def generate_id(self, *args):
        """Génère un ID unique pour une ligne à partir de ses valeurs."""
        combined = '_'.join(str(arg) for arg in args if arg)
        return hashlib.md5(combined.encode()).hexdigest()[:12]
    
    def standardize_country_code(self, country_code):
        """Standardise les codes pays (ISO 3166-1 alpha-2)."""
        country_map = {
            'UK': 'GB',  # Royaume-Uni
            'EL': 'GR',  # Grèce
            'FR': 'FR',
            'DE': 'DE',
            'CH': 'CH',
            'IT': 'IT',
            'ES': 'ES',
            'PT': 'PT',
            'BE': 'BE',
            'NL': 'NL',
            'AT': 'AT',
            # Ajouter d'autres pays selon vos données
        }
        return country_map.get(str(country_code).upper(), str(country_code).upper())
    
    def clean_text(self, text):
        """Nettoie les chaînes de texte."""
        if pd.isna(text):
            return None
        text = str(text)
        # Supprime les espaces multiples
        text = ' '.join(text.split())
        # Standardise la casse
        text = text.title()
        return text.strip()