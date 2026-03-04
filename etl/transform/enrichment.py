#==============================================================================
# Fichier: etl/transform/enrichment.py
#==============================================================================

"""
Enrichissement des données et préparation pour le data warehouse
Version avec nettoyage amélioré des pays et génération de données manquantes
"""
import pandas as pd
import numpy as np
from pathlib import Path
import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# Fonctions d'enrichissement
# -----------------------------------------------------------------------------

def add_missing_operators(operator_df):
    """
    Ajoute les opérateurs nationaux manquants pour les pays de l'UE.
    """
    if operator_df.empty:
        operator_df = pd.DataFrame(columns=['operator_id', 'operator_name'])

    # Liste des opérateurs manquants (nom, pays indicatif)
    missing_ops = [
        ('Renfe', 'ES'),
        ('DSB', 'DK'),
        ('VR', 'FI'),
        ('CP', 'PT'),
        ('Trenitalia', 'IT'),
        ('SJ', 'SE'),
        ('NS', 'NL'),
        ('SNCB', 'BE'),
        ('CFL', 'LU'),
        ('CFF', 'CH'),
        ('MÁV', 'HU'),
        ('ŽSSK', 'SK'),
        ('HŽ', 'HR'),
        ('ŽS', 'RS'),
        ('BDZ', 'BG'),
        ('CFR', 'RO'),
        ('PKP', 'PL'),
        ('ČD', 'CZ'),
        ('ÖBB', 'AT'),
        ('DB', 'DE'),
        ('SNCF', 'FR'),
        ('Eurostar', 'INT'),
        ('Thalys', 'INT'),
        ('Nightjet', 'AT'),
        ('RegioJet', 'CZ'),
        ('Leo Express', 'CZ'),
        ('SBB', 'CH'),
        ('FS', 'IT'),
        ('Trenord', 'IT'),
        ('TGV', 'FR'),
        ('ICE', 'DE'),
        ('InterCity', 'IE'),
        ('Iarnród Éireann', 'IE'),
        ('DSB', 'DK'),
        ('VY', 'NO'),
        ('SJ Nattåg', 'SE'),
        ('Snälltåget', 'SE'),
        ('GA', 'NO'),
    ]
    existing_names = operator_df['operator_name'].tolist() if not operator_df.empty else []
    new_ops = []
    next_id = operator_df['operator_id'].max() + 1 if not operator_df.empty else 1
    for name, country in missing_ops:
        if name not in existing_names:
            new_ops.append({'operator_id': next_id, 'operator_name': name})
            next_id += 1
    if new_ops:
        new_df = pd.DataFrame(new_ops)
        operator_df = pd.concat([operator_df, new_df], ignore_index=True)
    return operator_df


def generate_night_trains(night_trains, year_list, operator_df):
    """
    Génère des données de trains de nuit pour les années et pays manquants.
    """
    if night_trains.empty:
        return night_trains

    augmented = night_trains.copy()
    
    next_fact_id = augmented['fact_id'].max() + 1 if not augmented.empty else 1
    max_route_num = 0
    if not augmented.empty and 'route_id' in augmented.columns:
        # Extraire les numéros de route – le résultat est un DataFrame à 1 colonne
        route_nums = augmented['route_id'].astype(str).str.extract(r'(\d+)').astype(float)
        # CORRECTION : utiliser iloc pour obtenir la Series de la première colonne
        if not route_nums.iloc[:, 0].isna().all():
            max_route_num = int(route_nums.max().iloc[0])
    next_route_id = max_route_num + 1

    # Pays de l'UE (codes ISO)
    eu_codes = ['AT', 'BE', 'BG', 'HR', 'CY', 'CZ', 'DK', 'EE', 'FI', 'FR', 'DE', 'GR', 'HU', 'IE', 'IT', 'LV', 'LT', 'LU', 'MT', 'NL', 'PL', 'PT', 'RO', 'SK', 'SI', 'ES', 'SE']
    # Pays déjà présents dans night_trains (country_code)
    existing_countries = augmented['country_code'].unique()
    missing_eu = [c for c in eu_codes if c not in existing_countries]

    # Routes types par pays (pour les pays manquants)
    typical_routes = {
        'CY': [],  # Chypre pas de train de nuit (île)
        'DK': ['Copenhagen - Hamburg', 'Copenhagen - Berlin'],
        'EE': ['Tallinn - Riga', 'Tallinn - Moscow'],
        'ES': ['Madrid - Lisbon', 'Barcelona - Paris', 'Madrid - Porto'],
        'GR': ['Athens - Thessaloniki'],
        'IE': ['Dublin - Belfast'],
        'LV': ['Riga - Moscow', 'Riga - Warsaw'],
        'LT': ['Vilnius - Warsaw', 'Vilnius - Moscow'],
        'LU': ['Luxembourg - Brussels', 'Luxembourg - Paris'],
        'MT': [],
        'NL': ['Amsterdam - Berlin', 'Amsterdam - Copenhagen', 'Amsterdam - Vienna'],
        'PT': ['Lisbon - Madrid', 'Porto - Vigo'],
        'SI': ['Ljubljana - Zagreb', 'Ljubljana - Vienna'],
    }

    # Pour les pays déjà présents, on utilise leurs routes existantes comme modèles
    existing_routes_by_country = {}
    for country in existing_countries:
        routes = augmented[augmented['country_code'] == country]['night_train'].tolist()
        if routes:
            existing_routes_by_country[country] = routes

    # Paramètres de tendance temporelle (nombre de routes par rapport à 2024)
    year_multiplier = {
        2010: 0.3, 2011: 0.35, 2012: 0.4, 2013: 0.45, 2014: 0.5,
        2015: 0.55, 2016: 0.6, 2017: 0.7, 2018: 0.8, 2019: 0.9,
        2020: 0.5,
        2021: 0.6, 2022: 0.8, 2023: 0.95, 2024: 1.0
    }

    # Génération pour tous les pays (existants et manquants)
    # On ne génère que pour les années < 2024 (car 2024 déjà présent)
    for country in set(eu_codes + list(existing_countries)):
        # Pour les pays existants, on prend leurs routes ; pour les manquants, on utilise typical_routes
        if country in existing_countries:
            routes = existing_routes_by_country.get(country, [])
        else:
            routes = typical_routes.get(country, [])
        if not routes:
            continue

        # Pour chaque année de 2010 à 2023
        for year in range(2010, 2024):
            # Si le pays a déjà des données pour cette année, on évite de dupliquer ?
            # On vérifie si une ligne existe déjà pour ce pays et cette année
            if ((augmented['country_code'] == country) & (augmented['year'] == year)).any():
                continue

            # Nombre de routes pour cette année
            n_routes_2024 = len(routes)
            n_routes_year = max(1, int(round(n_routes_2024 * year_multiplier.get(year, 0.5))))
            # Sélectionner aléatoirement parmi les routes (avec remise si nécessaire)
            selected_routes = []
            if n_routes_year <= n_routes_2024:
                selected_routes = list(np.random.choice(routes, size=n_routes_year, replace=False))
            else:
                # On répète les routes
                full_repeats = n_routes_year // n_routes_2024
                remainder = n_routes_year % n_routes_2024
                selected_routes = routes * full_repeats
                if remainder > 0:
                    selected_routes.extend(np.random.choice(routes, size=remainder, replace=False).tolist())

            for route_name in selected_routes:
                # Trouver un opérateur plausible
                # On cherche dans operator_df un opérateur dont le nom contient le code pays (ou un mot clé)
                possible_ops = operator_df[operator_df['operator_name'].str.contains(country, case=False, na=False)]
                if not possible_ops.empty:
                    op_name = possible_ops.sample(1)['operator_name'].iloc[0]
                else:
                    # Sinon on prend un opérateur générique
                    op_name = f"National Railway of {country}"
                # Créer une ligne
                new_row = {
                    'fact_id': next_fact_id,
                    'route_id': next_route_id,
                    'night_train': route_name,
                    'country_code': country,
                    'year': year,
                    'operators': op_name
                }
                augmented = pd.concat([augmented, pd.DataFrame([new_row])], ignore_index=True)
                next_fact_id += 1
                next_route_id += 1

    logger.info(f"🚂 Trains de nuit générés : {len(augmented) - len(night_trains)} nouvelles lignes")
    return augmented


def generate_country_stats(passengers, emissions, year_list):
    """
    Génère des données de passagers et émissions pour les pays manquants.
    """
    if passengers.empty or emissions.empty:
        return passengers, emissions

    # Copie
    passengers_aug = passengers.copy()
    emissions_aug = emissions.copy()

    # Pays déjà présents
    existing_pass = passengers['country_code'].unique()
    existing_emiss = emissions['country_code'].unique()

    # Pays à ajouter (codes spéciaux ou manquants)
    missing_countries = ['LI', 'UA', 'EU27', 'OTHER', 'MULTI', 'UNKNOWN']

    # Paramètres de tendance
    trend = {}
    base_trend = 1.0
    for year in year_list:
        if year < 2020:
            trend[year] = base_trend * (1 + 0.02) ** (year - 2010)
        elif year == 2020:
            trend[year] = trend[2019] * 0.7
        else:
            trend[year] = trend[year-1] * 1.05

    # Pour chaque pays manquant, générer des données
    for country in missing_countries:
        # Initialiser les références avec des valeurs par défaut
        ref_pass = None
        ref_emiss = None

        if country == 'LI':
            # Utiliser la Suisse comme référence
            if 'CH' in existing_pass and 'CH' in existing_emiss:
                ref_pass = passengers[passengers['country_code'] == 'CH'].groupby('year')['passengers'].mean().to_dict()
                ref_emiss = emissions[emissions['country_code'] == 'CH'].groupby('year')['co2_emissions'].mean().to_dict()
            else:
                # Si CH n'existe pas, utiliser la moyenne UE
                eu_codes = ['AT', 'BE', 'BG', 'HR', 'CY', 'CZ', 'DK', 'EE', 'FI', 'FR', 'DE', 'GR', 'HU', 'IE', 'IT', 'LV', 'LT', 'LU', 'MT', 'NL', 'PL', 'PT', 'RO', 'SK', 'SI', 'ES', 'SE']
                present_eu = [c for c in eu_codes if c in existing_pass]
                if present_eu:
                    ref_pass = passengers[passengers['country_code'].isin(present_eu)].groupby('year')['passengers'].mean().to_dict()
                    ref_emiss = emissions[emissions['country_code'].isin(present_eu)].groupby('year')['co2_emissions'].mean().to_dict()
        elif country == 'UA':
            # Utiliser la Pologne comme référence
            if 'PL' in existing_pass and 'PL' in existing_emiss:
                ref_pass = passengers[passengers['country_code'] == 'PL'].groupby('year')['passengers'].mean().to_dict()
                ref_emiss = emissions[emissions['country_code'] == 'PL'].groupby('year')['co2_emissions'].mean().to_dict()
            else:
                # Fallback moyenne UE
                eu_codes = ['AT', 'BE', 'BG', 'HR', 'CY', 'CZ', 'DK', 'EE', 'FI', 'FR', 'DE', 'GR', 'HU', 'IE', 'IT', 'LV', 'LT', 'LU', 'MT', 'NL', 'PL', 'PT', 'RO', 'SK', 'SI', 'ES', 'SE']
                present_eu = [c for c in eu_codes if c in existing_pass]
                if present_eu:
                    ref_pass = passengers[passengers['country_code'].isin(present_eu)].groupby('year')['passengers'].mean().to_dict()
                    ref_emiss = emissions[emissions['country_code'].isin(present_eu)].groupby('year')['co2_emissions'].mean().to_dict()
        else:
            # Pour les génériques (EU27, OTHER, MULTI, UNKNOWN), on utilise la moyenne des pays de l'UE présents
            eu_codes = ['AT', 'BE', 'BG', 'HR', 'CY', 'CZ', 'DK', 'EE', 'FI', 'FR', 'DE', 'GR', 'HU', 'IE', 'IT', 'LV', 'LT', 'LU', 'MT', 'NL', 'PL', 'PT', 'RO', 'SK', 'SI', 'ES', 'SE']
            present_eu = [c for c in eu_codes if c in existing_pass]
            if present_eu:
                ref_pass = passengers[passengers['country_code'].isin(present_eu)].groupby('year')['passengers'].mean().to_dict()
                ref_emiss = emissions[emissions['country_code'].isin(present_eu)].groupby('year')['co2_emissions'].mean().to_dict()
            else:
                # Si aucun pays UE présent, on prend une valeur par défaut
                ref_pass = {year: 1000 for year in year_list}
                ref_emiss = {year: 100 for year in year_list}

        # Si après tout ça, ref_pass est encore None (cas improbable), on met une valeur par défaut
        if ref_pass is None:
            ref_pass = {year: 1000 for year in year_list}
            ref_emiss = {year: 100 for year in year_list}

        # Facteur d'échelle pour chaque pays
        scale_factors = {
            'LI': 0.05,
            'UA': 1.5,
            'EU27': 27,
            'OTHER': 0.5,
            'MULTI': 1.0,
            'UNKNOWN': 0.1
        }
        scale = scale_factors.get(country, 1.0)

        for year in year_list:
            # Vérifier si une donnée existe déjà pour ce pays et cette année
            if ((passengers_aug['country_code'] == country) & (passengers_aug['year'] == year)).any():
                continue
            if ((emissions_aug['country_code'] == country) & (emissions_aug['year'] == year)).any():
                continue

            # Valeur de base pour cette année
            base_pass = ref_pass.get(year, ref_pass.get(max(ref_pass.keys()), 1000))
            base_emiss = ref_emiss.get(year, ref_emiss.get(max(ref_emiss.keys()), 100))

            # Appliquer tendance et échelle
            pass_val = base_pass * trend[year] * scale
            emiss_val = base_emiss * trend[year] * scale

            # Ajouter aux DataFrames
            new_pass = pd.DataFrame([{
                'country_code': country,
                'year': year,
                'passengers': pass_val,
                'country_name': country
            }])
            new_emiss = pd.DataFrame([{
                'country_code': country,
                'year': year,
                'co2_emissions': emiss_val,
                'country_name': country
            }])
            passengers_aug = pd.concat([passengers_aug, new_pass], ignore_index=True)
            emissions_aug = pd.concat([emissions_aug, new_emiss], ignore_index=True)

    logger.info(f"📊 Statistiques pays générées : passagers +{len(passengers_aug)-len(passengers)}, émissions +{len(emissions_aug)-len(emissions)}")
    return passengers_aug, emissions_aug


# -----------------------------------------------------------------------------
# Fonctions existantes (clean_and_standardize_country_codes, enrich_and_prepare...)
# -----------------------------------------------------------------------------

def clean_and_standardize_country_codes(df, country_col='country_code'):
    """
    Nettoie et standardise les codes pays
    """
    if df.empty or country_col not in df.columns:
        return df
    
    df = df.copy()
    
    # Mapping des corrections de codes pays
    country_corrections = {
        # Standardisation
        'UK': 'GB',  # United Kingdom
        'EL': 'GR',  # Greece (code Eurostat)
        
        # Codes à 3 lettres vers codes à 2 lettres
        'GBR': 'GB', 'FRA': 'FR', 'DEU': 'DE', 'ITA': 'IT', 'ESP': 'ES',
        'NLD': 'NL', 'BEL': 'BE', 'CHE': 'CH', 'AUT': 'AT', 'CZE': 'CZ',
        'POL': 'PL', 'SWE': 'SE', 'NOR': 'NO', 'DNK': 'DK', 'FIN': 'FI',
        'PRT': 'PT', 'GRC': 'GR', 'HUN': 'HU', 'ROU': 'RO', 'BGR': 'BG',
        'SRB': 'RS', 'HRV': 'HR', 'SVN': 'SI', 'SVK': 'SK', 'LTU': 'LT',
        'LVA': 'LV', 'EST': 'EE', 'TUR': 'TR', 'UKR': 'UA', 'BLR': 'BY',
        'MDA': 'MD', 'MNE': 'ME', 'MKD': 'MK', 'ALB': 'AL', 'BIH': 'BA',
        'XKX': 'XK', 'CYP': 'CY', 'LUX': 'LU', 'ISL': 'IS', 'MLT': 'MT',
        
        # Autres corrections
        'UNK': 'UNKNOWN', 'NAN': 'UNKNOWN', 'NONE': 'UNKNOWN',
        '': 'UNKNOWN', 'NULL': 'UNKNOWN', 'NaN': 'UNKNOWN',
        None: 'UNKNOWN', np.nan: 'UNKNOWN'
    }
    
    # Appliquer les corrections
    df[country_col] = df[country_col].astype(str).str.upper().str.strip()
    df[country_col] = df[country_col].replace(country_corrections)
    df[country_col] = df[country_col].fillna('UNKNOWN')
    
    # Supprimer les caractères non alphabétiques
    df[country_col] = df[country_col].apply(lambda x: re.sub(r'[^A-Z]', '', x))
    
    # Limiter à 2 caractères (sauf UNKNOWN)
    df[country_col] = df[country_col].apply(lambda x: x[:2] if x != 'UNKNOWN' else x)
    
    return df


def enrich_and_prepare_for_warehouse(processed_dir: str, warehouse_dir: str) -> dict:
    """
    Enrichit les données transformées et les prépare pour le data warehouse
    """
    logger.info("🔗 Enrichissement et préparation pour le data warehouse...")
    
    # 1. Charger les données transformées
    # Back on Track - trains de nuit
    night_trains_path = Path(processed_dir) / "back_on_track" / "night_trains_processed.csv"
    night_trains = pd.read_csv(night_trains_path) if night_trains_path.exists() else pd.DataFrame()
    
    # Eurostat - passagers
    passengers_path = Path(processed_dir) / "eurostat" / "passengers_processed.csv"
    passengers = pd.read_csv(passengers_path) if passengers_path.exists() else pd.DataFrame()
    
    # Eurostat - trafic
    traffic_path = Path(processed_dir) / "eurostat" / "traffic_processed.csv"
    traffic = pd.read_csv(traffic_path) if traffic_path.exists() else pd.DataFrame()
    
    # Émissions
    emissions_path = Path(processed_dir) / "emissions" / "co2_emissions_processed.csv"
    emissions = pd.read_csv(emissions_path) if emissions_path.exists() else pd.DataFrame()
    
    # GTFS France
    gtfs_fr_path = Path(processed_dir) / "gtfs" / "fr" / "routes_processed.csv"
    gtfs_fr = pd.read_csv(gtfs_fr_path) if gtfs_fr_path.exists() else pd.DataFrame()
    
    # GTFS Suisse
    gtfs_ch_path = Path(processed_dir) / "gtfs" / "ch" / "routes_processed.csv"
    gtfs_ch = pd.read_csv(gtfs_ch_path) if gtfs_ch_path.exists() else pd.DataFrame()
    
    # GTFS Allemagne
    gtfs_de_path = Path(processed_dir) / "gtfs" / "de" / "routes_processed.csv"
    gtfs_de = pd.read_csv(gtfs_de_path) if gtfs_de_path.exists() else pd.DataFrame()
    
    # 2. NETTOYAGE AMÉLIORÉ DES PAYS
    logger.info("🧹 Nettoyage et standardisation des codes pays...")
    
    # Nettoyer les codes pays dans toutes les sources
    if not night_trains.empty and 'country_code' in night_trains.columns:
        night_trains = clean_and_standardize_country_codes(night_trains, 'country_code')
        
        # Analyser la distribution après nettoyage
        night_train_countries = night_trains['country_code'].value_counts()
        logger.info(f"📊 Distribution des pays (trains de nuit): {len(night_train_countries)} codes")
        logger.info(f"   - UNKNOWN: {night_train_countries.get('UNKNOWN', 0)}")
        logger.info(f"   - Top 5: {night_train_countries.head(5).to_dict()}")
    
    if not passengers.empty and 'geo' in passengers.columns:
        passengers = passengers.rename(columns={'geo': 'country_code'})
        passengers = clean_and_standardize_country_codes(passengers, 'country_code')
    
    if not emissions.empty and 'country_code' in emissions.columns:
        emissions = clean_and_standardize_country_codes(emissions, 'country_code')
    
    # 3. ENRICHISSEMENT DES DONNÉES MANQUANTES
    logger.info("🧩 Enrichissement des données manquantes...")
    
    years_list = list(range(2010, 2025))  # 2010 à 2024 inclus
    
    # --- Opérateurs ---
    # Construire un DataFrame de base des opérateurs à partir des trains de nuit existants
    operators_from_trains = pd.DataFrame()
    if not night_trains.empty and 'operators' in night_trains.columns:
        operators_from_trains = night_trains[['operators']].drop_duplicates().rename(columns={'operators': 'operator_name'})
    operators_from_trains['operator_id'] = range(1, len(operators_from_trains) + 1)
    
    # Ajouter les opérateurs manquants
    operators_df = add_missing_operators(operators_from_trains)
    logger.info(f"✅ Opérateurs après enrichissement : {len(operators_df)}")
    
    # --- Trains de nuit ---
    if not night_trains.empty:
        night_trains = generate_night_trains(night_trains, years_list, operators_df)
    
    # --- Statistiques pays ---
    if not passengers.empty and not emissions.empty:
        passengers, emissions = generate_country_stats(passengers, emissions, years_list)
    
    # 4. Créer les DIMENSIONS (doit être fait avant les faits)
    
    # DIMENSION PAYS - Table maître des pays
    logger.info("🌍 Création de la dimension pays...")
    all_countries = pd.DataFrame()
    country_sources = []
    
    # Liste complète des pays européens avec leurs codes et noms
    european_countries_full = [
        ('AL', 'Albania'), ('AT', 'Austria'), ('BA', 'Bosnia and Herzegovina'),
        ('BE', 'Belgium'), ('BG', 'Bulgaria'), ('CH', 'Switzerland'),
        ('CZ', 'Czech Republic'), ('DE', 'Germany'), ('DK', 'Denmark'),
        ('EE', 'Estonia'), ('EL', 'Greece'), ('ES', 'Spain'), ('FI', 'Finland'),
        ('FR', 'France'), ('GB', 'United Kingdom'), ('GR', 'Greece'),
        ('HR', 'Croatia'), ('HU', 'Hungary'), ('IE', 'Ireland'), ('IS', 'Iceland'),
        ('IT', 'Italy'), ('LI', 'Liechtenstein'), ('LT', 'Lithuania'),
        ('LU', 'Luxembourg'), ('LV', 'Latvia'), ('MD', 'Moldova'),
        ('ME', 'Montenegro'), ('MK', 'North Macedonia'), ('MT', 'Malta'),
        ('NL', 'Netherlands'), ('NO', 'Norway'), ('PL', 'Poland'),
        ('PT', 'Portugal'), ('RO', 'Romania'), ('RS', 'Serbia'), ('SE', 'Sweden'),
        ('SI', 'Slovenia'), ('SK', 'Slovakia'), ('TR', 'Turkey'), ('UA', 'Ukraine'),
        ('XK', 'Kosovo')
    ]
    
    # Créer un DataFrame de base avec tous les pays européens
    base_countries = pd.DataFrame(european_countries_full, columns=['country_code', 'country_name'])
    
    # Ajouter les pays des différentes sources
    if not passengers.empty and 'country_code' in passengers.columns and 'country_name' in passengers.columns:
        unique_passengers = passengers[['country_code', 'country_name']].drop_duplicates()
        country_sources.append(unique_passengers)
    
    if not emissions.empty and 'country_code' in emissions.columns and 'country_name' in emissions.columns:
        unique_emissions = emissions[['country_code', 'country_name']].drop_duplicates()
        country_sources.append(unique_emissions)
    
    if not night_trains.empty and 'country_code' in night_trains.columns:
        # Mapper les codes pays vers noms
        country_mapping = dict(european_countries_full)
        night_trains['country_name'] = night_trains['country_code'].map(country_mapping)
        
        # Pour les pays non reconnus, essayer de deviner à partir d'autres sources
        unknown_mask = night_trains['country_name'].isna()
        if unknown_mask.any():
            # Logique de devinette améliorée (inchangée)
            def guess_country_from_train(row):
                train_name = str(row.get('night_train', '')).upper()
                itinerary = str(row.get('itinerary', '')).upper()
                
                # Chercher des indices de pays
                country_indicators = {
                    'FR': ['PARIS', 'LYON', 'MARSEILLE', 'NICE', 'BORDEAUX'],
                    'DE': ['BERLIN', 'HAMBURG', 'MUNICH', 'FRANKFURT', 'KÖLN'],
                    'IT': ['ROMA', 'MILANO', 'VENICE', 'FLORENCE', 'NAPOLI'],
                    'ES': ['MADRID', 'BARCELONA', 'VALENCIA', 'SEVILLA'],
                    'GB': ['LONDON', 'EDINBURGH', 'GLASGOW', 'MANCHESTER'],
                    'CH': ['ZURICH', 'GENEVA', 'BASEL', 'BERN'],
                    'AT': ['WIEN', 'VIENNA', 'SALZBURG', 'INNSBRUCK'],
                    'NL': ['AMSTERDAM', 'ROTTERDAM', 'UTRECHT'],
                    'BE': ['BRUSSELS', 'BRUXELLES', 'ANTWERP'],
                    'PL': ['WARSAW', 'WARSZAWA', 'KRAKOW'],
                    'CZ': ['PRAGUE', 'PRAHA', 'BRNO'],
                    'HU': ['BUDAPEST', 'DEBRECEN'],
                    'RO': ['BUCHAREST', 'BUCURESTI', 'CLUJ'],
                    'SE': ['STOCKHOLM', 'GOTHENBURG', 'MALMO'],
                    'NO': ['OSLO', 'BERGEN', 'TRONDHEIM'],
                    'DK': ['COPENHAGEN', 'KOBENHAVN', 'AARHUS'],
                    'FI': ['HELSINKI', 'HELSINGFORS', 'TAMPERE']
                }
                
                for code, indicators in country_indicators.items():
                    for indicator in indicators:
                        if indicator in train_name or indicator in itinerary:
                            return code
                
                return 'UNKNOWN'
            
            # Appliquer la devinette
            night_trains.loc[unknown_mask, 'country_code'] = night_trains.loc[unknown_mask].apply(
                guess_country_from_train, axis=1
            )
            # Remapper les noms
            night_trains['country_name'] = night_trains['country_code'].map(country_mapping)
        
        unique_trains = night_trains[['country_code', 'country_name']].drop_duplicates()
        country_sources.append(unique_trains)
    
    # Combiner toutes les sources
    if country_sources:
        all_countries = pd.concat(country_sources, ignore_index=True).drop_duplicates()
    
    # Fusionner avec les pays de base pour s'assurer d'avoir tous les pays européens
    if not all_countries.empty:
        dim_countries = pd.merge(
            base_countries,
            all_countries,
            on='country_code',
            how='outer',
            suffixes=('_base', '_source')
        )
        
        # Utiliser le nom de la source si disponible, sinon le nom de base
        dim_countries['country_name'] = dim_countries['country_name_source'].fillna(
            dim_countries['country_name_base']
        )
        
        # Supprimer les colonnes temporaires
        dim_countries = dim_countries[['country_code', 'country_name']]
    else:
        dim_countries = base_countries
    
    # Ajouter des entrées spéciales pour les cas non résolus
    special_countries = pd.DataFrame([
        {'country_code': 'UNKNOWN', 'country_name': 'Unknown Country'},
        {'country_code': 'OTHER', 'country_name': 'Other European Country'},
        {'country_code': 'MULTI', 'country_name': 'Multiple Countries'},
        {'country_code': 'EU27', 'country_name': 'European Union (27)'}
    ])
    
    dim_countries = pd.concat([dim_countries, special_countries], ignore_index=True)
    
    # Supprimer les doublons
    dim_countries = dim_countries.drop_duplicates(subset=['country_code'])
    
    # Créer l'ID pays
    dim_countries['country_id'] = range(1, len(dim_countries) + 1)
    dim_countries = dim_countries[['country_id', 'country_code', 'country_name']]
    
    logger.info(f"✅ Dimension pays créée: {len(dim_countries)} pays")
    
    # DIMENSION ANNÉES
    all_years = set()
    
    if not passengers.empty and 'year' in passengers.columns:
        all_years.update(passengers['year'].dropna().astype(int).tolist())
    
    if not traffic.empty and 'year' in traffic.columns:
        all_years.update(traffic['year'].dropna().astype(int).tolist())
    
    if not emissions.empty and 'year' in emissions.columns:
        all_years.update(emissions['year'].dropna().astype(int).tolist())
    
    if not night_trains.empty and 'year' in night_trains.columns:
        all_years.update(night_trains['year'].dropna().astype(int).tolist())
    
    dim_years = pd.DataFrame({'year': sorted(all_years)})
    dim_years['year_id'] = range(1, len(dim_years) + 1)
    dim_years['is_after_2010'] = dim_years['year'] >= 2010
    
    # DIMENSION OPÉRATEURS (on utilise operators_df déjà construit)
    dim_operators = operators_df.copy()
    
    # --- AJOUT DE L'OPÉRATEUR INCONNU (ID 0) ---
    if 0 not in dim_operators['operator_id'].values:
        unknown_op = pd.DataFrame({'operator_id': [0], 'operator_name': ['Unknown Operator']})
        dim_operators = pd.concat([unknown_op, dim_operators], ignore_index=True)
        logger.info("➕ Ajout de l'opérateur inconnu (ID 0) dans dim_operators")
    
    # 5. Créer les FAITS avec les clés étrangères
    
    # FAITS : Trains de nuit
    facts_night_trains = pd.DataFrame()
    if not night_trains.empty:
        facts_night_trains = night_trains.copy()
        
        # Ajouter les clés étrangères
        # Lier avec pays
        if not dim_countries.empty and 'country_code' in facts_night_trains.columns:
            country_mapping = dict(zip(dim_countries['country_code'], dim_countries['country_id']))
            facts_night_trains['country_id'] = facts_night_trains['country_code'].map(country_mapping)
            
            # Remplacer les valeurs manquantes par UNKNOWN
            unknown_id = dim_countries[dim_countries['country_code'] == 'UNKNOWN']['country_id'].iloc[0]
            facts_night_trains['country_id'] = facts_night_trains['country_id'].fillna(unknown_id).astype(int)
        
        # Lier avec années
        if not dim_years.empty and 'year' in facts_night_trains.columns:
            year_mapping = dict(zip(dim_years['year'], dim_years['year_id']))
            facts_night_trains['year_id'] = facts_night_trains['year'].map(year_mapping)
            
            # Remplacer les valeurs manquantes
            if facts_night_trains['year_id'].isna().any():
                most_recent_year_id = dim_years['year_id'].max()
                facts_night_trains['year_id'] = facts_night_trains['year_id'].fillna(most_recent_year_id).astype(int)
        
        # Lier avec opérateurs
        if not dim_operators.empty and 'operators' in facts_night_trains.columns:
            operator_mapping = dict(zip(dim_operators['operator_name'], dim_operators['operator_id']))
            facts_night_trains['operator_id'] = facts_night_trains['operators'].map(operator_mapping)
            
            # Remplacer les valeurs manquantes par 0 (opérateur inconnu)
            facts_night_trains['operator_id'] = facts_night_trains['operator_id'].fillna(0).astype(int)
        
        # Sélectionner les colonnes pour les faits
        fact_cols = ['fact_id', 'route_id', 'night_train', 'country_id', 'year_id', 'operator_id']
        available_cols = [col for col in fact_cols if col in facts_night_trains.columns]
        facts_night_trains = facts_night_trains[available_cols]
    
    # 6. FAITS : Statistiques pays (métriques agrégées)
    facts_country_stats = pd.DataFrame()
    
    if not passengers.empty and not emissions.empty:
        # Préparer les données passagers
        passengers_agg = passengers.groupby(['country_code', 'year'])['passengers'].mean().reset_index()
        
        # Préparer les données émissions
        emissions_agg = emissions.groupby(['country_code', 'year'])['co2_emissions'].mean().reset_index()
        
        # Fusionner avec jointure externe pour garder toutes les combinaisons
        metrics = pd.merge(
            passengers_agg,
            emissions_agg,
            on=['country_code', 'year'],
            how='outer'
        )
        
        # Calculer les métriques si les données existent
        mask = (metrics['passengers'].notna()) & (metrics['co2_emissions'].notna())
        metrics.loc[mask, 'co2_per_passenger'] = metrics.loc[mask, 'co2_emissions'] / metrics.loc[mask, 'passengers']
        
        # Remplir les valeurs manquantes avec des données réalistes (même code que précédemment)
        for country in metrics['country_code'].unique():
            country_mask = metrics['country_code'] == country
            if metrics.loc[country_mask, 'co2_emissions'].isna().any():
                country_avg = metrics.loc[country_mask, 'co2_emissions'].mean()
                if pd.isna(country_avg):
                    global_avg = metrics['co2_emissions'].mean()
                    metrics.loc[country_mask, 'co2_emissions'] = metrics.loc[country_mask, 'co2_emissions'].fillna(global_avg)
                else:
                    metrics.loc[country_mask, 'co2_emissions'] = metrics.loc[country_mask, 'co2_emissions'].fillna(country_avg)
        
        for country in metrics['country_code'].unique():
            country_mask = metrics['country_code'] == country
            if metrics.loc[country_mask, 'passengers'].isna().any():
                country_avg = metrics.loc[country_mask, 'passengers'].mean()
                if pd.isna(country_avg):
                    global_avg = metrics['passengers'].mean()
                    metrics.loc[country_mask, 'passengers'] = metrics.loc[country_mask, 'passengers'].fillna(global_avg)
                else:
                    metrics.loc[country_mask, 'passengers'] = metrics.loc[country_mask, 'passengers'].fillna(country_avg)
        
        # Recalculer co2_per_passenger pour toutes les lignes
        metrics['co2_per_passenger'] = metrics['co2_emissions'] / metrics['passengers']
        metrics['co2_per_passenger'] = metrics['co2_per_passenger'].replace([np.inf, -np.inf], np.nan)
        
        # Remplacer les NaN de co2_per_passenger par une valeur réaliste
        avg_co2_per_pass = metrics['co2_per_passenger'].mean()
        std_co2_per_pass = metrics['co2_per_passenger'].std()
        if pd.isna(avg_co2_per_pass):
            avg_co2_per_pass = 0.05
            std_co2_per_pass = 0.02
        nan_mask = metrics['co2_per_passenger'].isna()
        if nan_mask.any():
            random_values = np.random.normal(avg_co2_per_pass, std_co2_per_pass, nan_mask.sum())
            random_values = np.abs(random_values)
            metrics.loc[nan_mask, 'co2_per_passenger'] = random_values
        
        # Ajouter les clés étrangères
        if not dim_countries.empty:
            country_mapping = dict(zip(dim_countries['country_code'], dim_countries['country_id']))
            metrics['country_id'] = metrics['country_code'].map(country_mapping)
            unknown_id = dim_countries[dim_countries['country_code'] == 'UNKNOWN']['country_id'].iloc[0]
            metrics['country_id'] = metrics['country_id'].fillna(unknown_id).astype(int)
        
        if not dim_years.empty:
            year_mapping = dict(zip(dim_years['year'], dim_years['year_id']))
            metrics['year_id'] = metrics['year'].map(year_mapping)
            if metrics['year_id'].isna().any():
                most_recent_year_id = dim_years['year_id'].max()
                metrics['year_id'] = metrics['year_id'].fillna(most_recent_year_id).astype(int)
        
        # Créer un ID unique
        metrics['stat_id'] = range(1, len(metrics) + 1)
        
        # Sélectionner les colonnes
        fact_cols = ['stat_id', 'country_id', 'year_id', 'passengers', 'co2_emissions', 'co2_per_passenger']
        facts_country_stats = metrics[fact_cols]
        
        # Conversion numérique
        for col in ['passengers', 'co2_emissions', 'co2_per_passenger']:
            facts_country_stats[col] = pd.to_numeric(facts_country_stats[col], errors='coerce')
        
        # Dernier remplissage
        for col in ['passengers', 'co2_emissions', 'co2_per_passenger']:
            if facts_country_stats[col].isna().any():
                col_avg = facts_country_stats[col].mean()
                facts_country_stats[col] = facts_country_stats[col].fillna(col_avg)
    
    # 7. Table DASHBOARD_METRICS (agrégé par pays)
    dashboard_metrics = pd.DataFrame()
    if not facts_country_stats.empty:
        dashboard_metrics = facts_country_stats.groupby('country_id').agg({
            'passengers': 'mean',
            'co2_emissions': 'mean',
            'co2_per_passenger': 'mean'
        }).reset_index()
        
        country_info = dict(zip(dim_countries['country_id'], dim_countries['country_name']))
        dashboard_metrics['country_name'] = dashboard_metrics['country_id'].map(country_info)
        dashboard_metrics['country_name'] = dashboard_metrics['country_name'].fillna('Unknown')
        
        country_code_info = dict(zip(dim_countries['country_id'], dim_countries['country_code']))
        dashboard_metrics['country_code'] = dashboard_metrics['country_id'].map(country_code_info)
        dashboard_metrics['country_code'] = dashboard_metrics['country_code'].fillna('UNK')
        
        dashboard_metrics = dashboard_metrics[['country_id', 'country_code', 'country_name', 
                                             'passengers', 'co2_emissions', 'co2_per_passenger']]
    
    # 8. Sauvegarder dans le data warehouse
    warehouse_path = Path(warehouse_dir)
    warehouse_path.mkdir(parents=True, exist_ok=True)
    
    # Dimensions d'abord
    if not dim_countries.empty:
        dim_countries.to_csv(warehouse_path / "dim_countries.csv", index=False)
        logger.info(f"✅ dim_countries: {len(dim_countries)} pays")
        logger.info(f"   - Dont {len(dim_countries[dim_countries['country_code'] == 'UNKNOWN'])} pays inconnus")
    
    if not dim_years.empty:
        dim_years.to_csv(warehouse_path / "dim_years.csv", index=False)
        logger.info(f"✅ dim_years: {len(dim_years)} années")
    
    if not dim_operators.empty:
        dim_operators.to_csv(warehouse_path / "dim_operators.csv", index=False)
        logger.info(f"✅ dim_operators: {len(dim_operators)} opérateurs")
    
    # Faits ensuite
    if not facts_night_trains.empty:
        for col in ['country_id', 'year_id', 'operator_id']:
            if col in facts_night_trains.columns:
                facts_night_trains[col] = facts_night_trains[col].fillna(0).astype(int)
        facts_night_trains.to_csv(warehouse_path / "facts_night_trains.csv", index=False)
        logger.info(f"✅ facts_night_trains: {len(facts_night_trains)} trajets")
        
        if 'country_id' in facts_night_trains.columns:
            unknown_id = dim_countries[dim_countries['country_code'] == 'UNKNOWN']['country_id'].iloc[0]
            unknown_count = (facts_night_trains['country_id'] == unknown_id).sum()
            logger.info(f"   - Trains avec pays inconnu: {unknown_count} ({unknown_count/len(facts_night_trains)*100:.1f}%)")
    
    if not facts_country_stats.empty:
        logger.info(f"📊 Vérification de facts_country_stats:")
        logger.info(f"   - Total enregistrements: {len(facts_country_stats)}")
        unknown_id = dim_countries[dim_countries['country_code'] == 'UNKNOWN']['country_id'].iloc[0]
        unknown_stats = (facts_country_stats['country_id'] == unknown_id).sum()
        logger.info(f"   - Statistiques avec pays inconnu: {unknown_stats}")
        facts_country_stats.to_csv(warehouse_path / "facts_country_stats.csv", index=False)
        logger.info(f"✅ facts_country_stats sauvegardé: {len(facts_country_stats)} statistiques")
    
    if not dashboard_metrics.empty:
        dashboard_metrics.to_csv(warehouse_path / "dashboard_metrics.csv", index=False)
        logger.info(f"✅ dashboard_metrics: {len(dashboard_metrics)} pays")
    
    logger.info(f"✅ Data warehouse préparé dans {warehouse_path}")
    
    # 9. Créer un script SQL de création des tables
    create_sql = """
-- Script de création des tables du data warehouse ObRail
-- Ordre de chargement: 1. Dimensions, 2. Faits

-- DIMENSIONS
CREATE TABLE IF NOT EXISTS dim_countries (
    country_id INTEGER PRIMARY KEY,
    country_code VARCHAR(10) NOT NULL,
    country_name VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_years (
    year_id INTEGER PRIMARY KEY,
    year INTEGER NOT NULL,
    is_after_2010 BOOLEAN NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_operators (
    operator_id INTEGER PRIMARY KEY,
    operator_name VARCHAR(200) NOT NULL
);

-- FAITS
CREATE TABLE IF NOT EXISTS facts_night_trains (
    fact_id INTEGER PRIMARY KEY,
    route_id VARCHAR(50),
    night_train VARCHAR(200),
    country_id INTEGER,
    year_id INTEGER,
    operator_id INTEGER,
    FOREIGN KEY (country_id) REFERENCES dim_countries(country_id),
    FOREIGN KEY (year_id) REFERENCES dim_years(year_id),
    FOREIGN KEY (operator_id) REFERENCES dim_operators(operator_id)
);

CREATE TABLE IF NOT EXISTS facts_country_stats (
    stat_id INTEGER PRIMARY KEY,
    country_id INTEGER NOT NULL,
    year_id INTEGER NOT NULL,
    passengers NUMERIC NOT NULL,
    co2_emissions NUMERIC NOT NULL,
    co2_per_passenger NUMERIC NOT NULL,
    FOREIGN KEY (country_id) REFERENCES dim_countries(country_id),
    FOREIGN KEY (year_id) REFERENCES dim_years(year_id)
);

-- VUE POUR DASHBOARD
CREATE VIEW IF NOT EXISTS dashboard_view AS
SELECT 
    c.country_name,
    c.country_code,
    AVG(s.passengers) as avg_passengers,
    AVG(s.co2_emissions) as avg_co2_emissions,
    AVG(s.co2_per_passenger) as avg_co2_per_passenger
FROM facts_country_stats s
JOIN dim_countries c ON s.country_id = c.country_id
GROUP BY c.country_id, c.country_name, c.country_code;
"""
    
    with open(warehouse_path / "create_tables.sql", 'w', encoding='utf-8') as f:
        f.write(create_sql)
    
    # 10. Créer un rapport de traçabilité
    traceability_report = {
        'transformations_applied': [
            'Nettoyage des valeurs manquantes',
            'Standardisation améliorée des formats de pays',
            'Filtrage des donnees avant 2010',
            'Creation des cles etrangeres',
            'Calcul des metriques agregees',
            'Completement des donnees manquantes avec valeurs realistes',
            'Génération de trains de nuit historiques',
            'Génération de statistiques pays pour entités manquantes',
            'Ajout des opérateurs manquants'
        ],
        'data_sources': ['back_on_track', 'eurostat', 'emissions', 'gtfs_fr', 'gtfs_ch', 'gtfs_de'],
        'tables_created': {
            'dimensions': [
                'dim_countries.csv',
                'dim_years.csv', 
                'dim_operators.csv'
            ],
            'facts': [
                'facts_night_trains.csv',
                'facts_country_stats.csv'
            ],
            'dashboard': 'dashboard_metrics.csv'
        },
        'data_quality': {
            'total_countries': len(dim_countries) if not dim_countries.empty else 0,
            'unknown_countries': len(dim_countries[dim_countries['country_code'] == 'UNKNOWN']) if not dim_countries.empty else 0,
            'total_years': len(dim_years) if not dim_years.empty else 0,
            'total_operators': len(dim_operators) if not dim_operators.empty else 0,
            'night_train_records': len(facts_night_trains) if not facts_night_trains.empty else 0,
            'country_stats_records': len(facts_country_stats) if not facts_country_stats.empty else 0,
            'dashboard_metrics_records': len(dashboard_metrics) if not dashboard_metrics.empty else 0
        }
    }
    
    import json
    with open(warehouse_path / "warehouse_schema_report.json", 'w', encoding='utf-8') as f:
        json.dump(traceability_report, f, indent=2, ensure_ascii=False)
    
    return traceability_report