#==============================================================================
# Fichier: etl/transform/back_on_track.py
#==============================================================================

"""
Transformation des données Back on Track (trains de nuit)
Version améliorée avec meilleure extraction des pays
"""
import pandas as pd
import numpy as np
from pathlib import Path
import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_country_code_enhanced(route_name, itinerary, countries_field, route_long_name=None):
    """
    Extrait le code pays de manière intelligente avec priorité multiple
    """
    if pd.isna(route_name):
        route_name = ''
    if pd.isna(itinerary):
        itinerary = ''
    if pd.isna(countries_field):
        countries_field = ''
    if pd.isna(route_long_name):
        route_long_name = ''
    
    # Concaténer tous les champs pour la recherche
    text_to_search = f" {countries_field} {itinerary} {route_name} {route_long_name} ".upper()
    
    # Liste complète des codes pays européens
    european_countries = {
        'FR': 'France', 'DE': 'Germany', 'CH': 'Switzerland', 'IT': 'Italy',
        'ES': 'Spain', 'GB': 'United Kingdom', 'UK': 'United Kingdom',
        'BE': 'Belgium', 'NL': 'Netherlands', 'AT': 'Austria', 'HU': 'Hungary',
        'CZ': 'Czech Republic', 'PL': 'Poland', 'DK': 'Denmark', 'SE': 'Sweden',
        'NO': 'Norway', 'FI': 'Finland', 'PT': 'Portugal', 'GR': 'Greece',
        'IE': 'Ireland', 'RO': 'Romania', 'BG': 'Bulgaria', 'RS': 'Serbia',
        'HR': 'Croatia', 'SI': 'Slovenia', 'SK': 'Slovakia', 'LT': 'Lithuania',
        'LV': 'Latvia', 'EE': 'Estonia', 'TR': 'Turkey', 'UA': 'Ukraine',
        'BY': 'Belarus', 'MD': 'Moldova', 'ME': 'Montenegro', 'MK': 'North Macedonia',
        'AL': 'Albania', 'BA': 'Bosnia and Herzegovina', 'XK': 'Kosovo', 'CY': 'Cyprus',
        'LU': 'Luxembourg', 'IS': 'Iceland', 'MT': 'Malta'
    }
    
    # 1. PRIORITÉ: chercher dans le champ countries (le plus fiable)
    if countries_field and str(countries_field).strip():
        countries_str = str(countries_field).upper().replace(' ', '')
        # Séparer par virgule
        country_codes = [c.strip() for c in countries_str.split(',') if c.strip()]
        
        # Chercher des codes pays dans la liste
        for code in country_codes:
            # Code à 2 lettres
            if len(code) == 2 and code in european_countries:
                return code
            
            # Code à 3 lettres, essayer de convertir
            if len(code) == 3:
                three_to_two = {
                    'GBR': 'GB', 'FRA': 'FR', 'DEU': 'DE', 'ITA': 'IT', 'ESP': 'ES',
                    'NLD': 'NL', 'BEL': 'BE', 'CHE': 'CH', 'AUT': 'AT', 'CZE': 'CZ',
                    'POL': 'PL', 'SWE': 'SE', 'NOR': 'NO', 'DNK': 'DK', 'FIN': 'FI',
                    'PRT': 'PT', 'GRC': 'GR', 'HUN': 'HU', 'ROU': 'RO', 'BGR': 'BG',
                    'SRB': 'RS', 'HRV': 'HR', 'SVN': 'SI', 'SVK': 'SK', 'LTU': 'LT',
                    'LVA': 'LV', 'EST': 'EE', 'TUR': 'TR', 'UKR': 'UA', 'BLR': 'BY',
                    'MDA': 'MD', 'MNE': 'ME', 'MKD': 'MK', 'ALB': 'AL', 'BIH': 'BA',
                    'XKX': 'XK', 'CYP': 'CY', 'LUX': 'LU', 'ISL': 'IS', 'MLT': 'MT'
                }
                if code in three_to_two:
                    return three_to_two[code]
    
    # 2. Chercher des codes pays dans le texte
    for code in european_countries.keys():
        # Chercher le code pays entouré d'espaces ou de ponctuation
        if re.search(r'[ ,\-]' + code + r'[ ,\-]', text_to_search):
            return code
    
    # 3. Chercher le nom du pays (en anglais)
    for code, country_name in european_countries.items():
        if re.search(r'[ ,\-]' + country_name.upper() + r'[ ,\-]', text_to_search):
            return code
    
    # 4. Chercher les noms de villes connus
    city_country_mapping = {
        'WIEN': 'AT', 'VIENNA': 'AT', 'BERLIN': 'DE', 'PARIS': 'FR', 'ROMA': 'IT',
        'ROME': 'IT', 'MADRID': 'ES', 'BARCELONA': 'ES', 'LONDON': 'GB', 
        'AMSTERDAM': 'NL', 'BRUSSELS': 'BE', 'BRUXELLES': 'BE', 'PRAGUE': 'CZ',
        'PRAHA': 'CZ', 'BUDAPEST': 'HU', 'WARSAW': 'PL', 'WARSZAWA': 'PL',
        'STOCKHOLM': 'SE', 'OSLO': 'NO', 'HELSINKI': 'FI', 'HELSINGFORS': 'FI',
        'COPENHAGEN': 'DK', 'KOBENHAVN': 'DK', 'ZURICH': 'CH', 'GENEVA': 'CH',
        'MILANO': 'IT', 'MILAN': 'IT', 'VENICE': 'IT', 'VENEZIA': 'IT',
        'ATHENS': 'GR', 'LISBON': 'PT', 'LISBOA': 'PT', 'DUBLIN': 'IE',
        'BUCHAREST': 'RO', 'BUCURESTI': 'RO', 'SOFIA': 'BG', 'ZAGREB': 'HR',
        'BELGRADE': 'RS', 'BEOGRAD': 'RS', 'VILNIUS': 'LT', 'RIGA': 'LV',
        'TALLINN': 'EE', 'ISTANBUL': 'TR', 'KYIV': 'UA', 'KIEV': 'UA',
        'BRATISLAVA': 'SK', 'LJUBLJANA': 'SI', 'TIRANA': 'AL', 'PODGORICA': 'ME',
        'SKOPJE': 'MK', 'SARAJEVO': 'BA', 'MINSK': 'BY', 'CHISINAU': 'MD',
        'REYKJAVIK': 'IS', 'VALLETTA': 'MT', 'NICOSIA': 'CY', 'LUXEMBOURG': 'LU'
    }
    
    for city, code in city_country_mapping.items():
        if re.search(r'[ ,\-]' + city + r'[ ,\-]', text_to_search):
            return code
    
    # 5. Chercher les indicatifs téléphoniques (dernier recours)
    phone_country = {
        '+43': 'AT', '+32': 'BE', '+359': 'BG', '+385': 'HR', '+357': 'CY',
        '+420': 'CZ', '+45': 'DK', '+372': 'EE', '+358': 'FI', '+33': 'FR',
        '+49': 'DE', '+30': 'GR', '+36': 'HU', '+354': 'IS', '+353': 'IE',
        '+39': 'IT', '+371': 'LV', '+423': 'LI', '+370': 'LT', '+352': 'LU',
        '+356': 'MT', '+31': 'NL', '+47': 'NO', '+48': 'PL', '+351': 'PT',
        '+40': 'RO', '+421': 'SK', '+386': 'SI', '+34': 'ES', '+46': 'SE',
        '+41': 'CH', '+90': 'TR', '+44': 'GB', '+380': 'UA'
    }
    
    for prefix, code in phone_country.items():
        if prefix in text_to_search:
            return code
    
    return 'UNKNOWN'

def transform_back_on_track(raw_dir: str, processed_dir: str) -> None:
    """
    Transforme les données Back on Track avec amélioration des pays
    """
    logger.info("🚂 Transformation des données Back on Track...")
    
    # 1. Fichier des villes
    cities_path = Path(raw_dir) / "back_on_track" / "view_ontd_cities.csv"
    cities_df = pd.read_csv(cities_path)
    
    # Nettoyage
    cities_df = cities_df.copy()
    cities_df.columns = [col.strip().lower() for col in cities_df.columns]
    
    # Gérer valeurs manquantes
    cities_df['stop_cityname_romanized'] = cities_df['stop_cityname_romanized'].fillna('Inconnu')
    cities_df['stop_country'] = cities_df['stop_country'].fillna('UNKNOWN')
    
    # Standardiser les IDs
    cities_df['stop_id'] = cities_df['stop_id'].astype(str).str.strip()
    
    # Mapper les codes pays vers noms complets
    country_mapping = {
        'FR': 'France', 'DE': 'Germany', 'CH': 'Switzerland',
        'IT': 'Italy', 'ES': 'Spain', 'GB': 'United Kingdom', 'UK': 'United Kingdom',
        'BE': 'Belgium', 'NL': 'Netherlands', 'AT': 'Austria',
        'HU': 'Hungary', 'CZ': 'Czech Republic', 'PL': 'Poland',
        'DK': 'Denmark', 'SE': 'Sweden', 'NO': 'Norway',
        'FI': 'Finland', 'PT': 'Portugal', 'GR': 'Greece', 'EL': 'Greece',
        'IE': 'Ireland', 'RO': 'Romania', 'BG': 'Bulgaria', 'RS': 'Serbia',
        'HR': 'Croatia', 'SI': 'Slovenia', 'SK': 'Slovakia',
        'LT': 'Lithuania', 'LV': 'Latvia', 'EE': 'Estonia',
        'TR': 'Turkey', 'UA': 'Ukraine', 'MD': 'Moldova',
        'ME': 'Montenegro', 'MK': 'North Macedonia', 'AL': 'Albania',
        'BA': 'Bosnia and Herzegovina', 'XK': 'Kosovo', 'CY': 'Cyprus',
        'LU': 'Luxembourg', 'IS': 'Iceland', 'MT': 'Malta'
    }
    
    # Convertir les codes pays (ex: FR, DE) en noms complets
    cities_df['country_name'] = cities_df['stop_country'].map(country_mapping)
    cities_df['country_name'] = cities_df['country_name'].fillna(cities_df['stop_country'])
    
    # Créer un code pays standardisé
    cities_df['country_code'] = cities_df['stop_country'].str[:2].str.upper()
    
    # Correction spécifique pour UK
    cities_df.loc[cities_df['stop_country'].str.upper() == 'UK', 'country_code'] = 'GB'
    cities_df.loc[cities_df['stop_country'].str.upper() == 'UK', 'country_name'] = 'United Kingdom'
    
    # Sauvegarder
    save_path = Path(processed_dir) / "back_on_track" / "cities_processed.csv"
    save_path.parent.mkdir(parents=True, exist_ok=True)
    cities_df.to_csv(save_path, index=False)
    logger.info(f"✅ Villes sauvegardées: {save_path}")
    
    # 2. Fichier des trains de nuit
    trains_path = Path(raw_dir) / "back_on_track" / "view_ontd_list.csv"
    trains_df = pd.read_csv(trains_path)
    
    # Nettoyage
    trains_df = trains_df.copy()
    trains_df.columns = [col.strip().lower() for col in trains_df.columns]
    
    # Extraire l'année du nom du train ou de l'ID
    def extract_year(text):
        if pd.isna(text):
            return 2024
        text = str(text)
        # Chercher un motif d'année
        match = re.search(r'20[0-2][0-9]', text)
        if match:
            return int(match.group())
        return 2024  # Année par défaut
    
    trains_df['year'] = trains_df['night_train'].apply(extract_year)
    
    # Standardiser les noms
    trains_df['night_train'] = trains_df['night_train'].fillna('Train de nuit')
    trains_df['operators'] = trains_df['operators'].fillna('Opérateur inconnu')
    
    # Créer un identifiant unique pour chaque route
    trains_df['route_id'] = trains_df['route_id'].astype(str).str.strip()
    
    # NOUVEAU: Extraction améliorée du code pays
    logger.info("🌍 Extraction des codes pays avec logique améliorée...")
    
    # Appliquer la fonction d'extraction améliorée
    trains_df['country_code'] = trains_df.apply(
        lambda row: extract_country_code_enhanced(
            row['night_train'],
            row.get('itinerary', ''),
            row.get('countries', ''),
            row.get('route_long_name', '')
        ),
        axis=1
    )
    
    # Statistiques sur les codes pays extraits
    country_counts = trains_df['country_code'].value_counts()
    logger.info(f"📊 Distribution des codes pays: {len(country_counts)} codes uniques")
    logger.info(f"   - Trains avec pays reconnus: {(trains_df['country_code'] != 'UNKNOWN').sum()}")
    logger.info(f"   - Trains avec pays inconnu: {(trains_df['country_code'] == 'UNKNOWN').sum()}")
    
    # Afficher les 10 codes pays les plus fréquents
    for code, count in country_counts.head(10).items():
        logger.info(f"   - {code}: {count} trains")
    
    # Sélectionner uniquement les données après 2010
    trains_df = trains_df[trains_df['year'] >= 2010]
    
    # Ajouter un identifiant unique pour les faits
    trains_df['fact_id'] = range(1, len(trains_df) + 1)
    
    # Sauvegarder
    save_path = Path(processed_dir) / "back_on_track" / "night_trains_processed.csv"
    trains_df.to_csv(save_path, index=False)
    logger.info(f"✅ Trains de nuit sauvegardés: {save_path}")
    
    # 3. Créer un rapport de qualité
    quality_report = {
        'source': 'back_on_track',
        'cities_total': len(cities_df),
        'cities_with_names': cities_df['stop_cityname_romanized'].notna().sum(),
        'trains_total': len(trains_df),
        'trains_after_2010': len(trains_df[trains_df['year'] >= 2010]),
        'countries_covered': trains_df['country_code'].nunique(),
        'years_range': (trains_df['year'].min(), trains_df['year'].max()),
        'unknown_countries': (trains_df['country_code'] == 'UNKNOWN').sum(),
        'country_distribution': country_counts.head(20).to_dict()
    }
    
    return quality_report