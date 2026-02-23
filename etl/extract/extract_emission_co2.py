# download_direct_updated.py
import pandas as pd
import os
import requests
import time
from io import BytesIO
import zipfile

def download_eurostat_via_api():
    """Télécharge les données depuis l'API SDMX 2.1 d'Eurostat."""
    
    # URL de l'API SDMX pour le dataset ENV_AIR_GGE
    base_url = "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1"
    
    # Option 1: Données au format SDMX-CSV (recommandé)
    url_csv = f"{base_url}/data/ENV_AIR_GGE/?format=SDMX-CSV&compressed=false"
    
    # Option 2: Données au format TSV (similaire à l'ancien format)
    # url_tsv = f"{base_url}/data/ENV_AIR_GGE/?format=TSV&compressed=false"
    
    print(f"Téléchargement depuis l'API Eurostat...")
    print(f"URL : {url_csv}")
    
    try:
        # Télécharger les données
        response = requests.get(url_csv, timeout=30)
        response.raise_for_status()
        
        # Lire les données CSV
        csv_content = response.content.decode('utf-8')
        
        # Créer un DataFrame à partir du contenu CSV
        # Note: SDMX-CSV utilise la première ligne comme en-tête
        df = pd.read_csv(BytesIO(csv_content.encode('utf-8')))
        
        print(f"Dataset chargé : {df.shape}")
        print(f"Colonnes : {df.columns.tolist()[:10]}...")  # Afficher les 10 premières colonnes
        
        # Sauvegarder
        output_dir = 'data/raw/emission_co2'
        os.makedirs(output_dir, exist_ok=True)
        
        # Sauvegarder en CSV
        output_file_csv = os.path.join(output_dir, 'eurostat_env_air_gge_sdmx.csv')
        df.to_csv(output_file_csv, index=False)
        
        # Sauvegarder en TSV (pour compatibilité avec l'ancien format)
        output_file_tsv = os.path.join(output_dir, 'eurostat_env_air_gge_full.tsv')
        df.to_csv(output_file_tsv, sep='\t', index=False)
        
        print(f"\n✅ Fichiers sauvegardés :")
        print(f"   CSV : {output_file_csv}")
        print(f"   TSV : {output_file_tsv}")
        print(f"   Lignes : {len(df)}")
        print(f"   Colonnes : {len(df.columns)}")
        
        # Aperçu
        print("\nAperçu des données (5 premières lignes) :")
        print(df.head())
        
        # Statistiques de base
        print("\nStatistiques de base :")
        print(f"Période de temps : {df['TIME_PERIOD'].min()} à {df['TIME_PERIOD'].max()}")
        
        # Afficher les valeurs uniques pour quelques dimensions clés
        for col in ['freq', 'airpol', 'geo']:
            if col in df.columns:
                unique_vals = df[col].unique()[:5]
                print(f"{col} (exemples) : {', '.join(map(str, unique_vals))}")
                if len(df[col].unique()) > 5:
                    print(f"  (Total: {len(df[col].unique())} valeurs uniques)")
        
    except requests.exceptions.RequestException as e:
        print(f"Erreur HTTP : {e}")
    except Exception as e:
        print(f"Erreur : {e}")
        import traceback
        traceback.print_exc()

def download_filtered_data():
    """Télécharger des données filtrées (exemple : CO2 pour tous les pays)."""
    
    base_url = "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1"
    
    # Filtre : CO2 seulement, tous les pays, tous les secteurs
    # Format: freq.unit.airpol.src_crf.geo
    url = f"{base_url}/data/ENV_AIR_GGE/A..CO2../?format=SDMX-CSV&compressed=false"
    
    print(f"\nTéléchargement des données filtrées (CO2 uniquement)...")
    print(f"URL : {url}")
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        df_co2 = pd.read_csv(BytesIO(response.content))
        
        output_dir = 'data/raw/emission_co2'
        os.makedirs(output_dir, exist_ok=True)
        
        output_file = os.path.join(output_dir, 'eurostat_co2_filtered.csv')
        df_co2.to_csv(output_file, index=False)
        
        print(f"✅ Données CO2 sauvegardées : {output_file}")
        print(f"   Lignes : {len(df_co2)}")
        print(f"   Colonnes : {len(df_co2.columns)}")
        
    except Exception as e:
        print(f"Erreur lors du téléchargement filtré : {e}")

def get_data_structure():
    """Récupérer la structure des données (métadonnées)."""
    
    base_url = "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1"
    
    # Structure du flux de données
    url = f"{base_url}/dataflow/ESTAT/ENV_AIR_GGE/1.0?references=descendants&detail=referencepartial"
    
    print(f"\nRécupération de la structure des données...")
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # Sauvegarder la structure XML
        output_dir = 'data/raw/emission_co2'
        os.makedirs(output_dir, exist_ok=True)
        
        structure_file = os.path.join(output_dir, 'data_structure.xml')
        with open(structure_file, 'wb') as f:
            f.write(response.content)
        
        print(f"✅ Structure sauvegardée : {structure_file}")
        
    except Exception as e:
        print(f"Erreur lors de la récupération de la structure : {e}")
