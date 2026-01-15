"""
Configuration pour les transformations.
"""
from pathlib import Path

# Chemins
BASE_DIR = Path(__file__).parent.parent.parent
RAW_DATA_DIR = BASE_DIR / 'data' / 'raw'
PROCESSED_DATA_DIR = BASE_DIR / 'data' / 'processed'
WAREHOUSE_DATA_DIR = BASE_DIR / 'data' / 'warehouse'
LOGS_DIR = BASE_DIR / 'logs'

# Paramètres de transformation
GTFS_SETTINGS = {
    'chunk_size': 100000,
    'time_format': '%H:%M:%S',
    'default_timezone': 'Europe/Paris'
}

# Mappings de pays
COUNTRY_MAPPINGS = {
    'UK': 'GB',
    'EL': 'GR', 
    'FR': 'FR',
    'DE': 'DE',
    'CH': 'CH',
    'IT': 'IT',
    'ES': 'ES',
    'PT': 'PT',
    'BE': 'BE',
    'NL': 'NL',
    'AT': 'AT',
    'HU': 'HU',
    'RO': 'RO',
    'CZ': 'CZ',
    'SK': 'SK',
    'PL': 'PL',
    'HR': 'HR',
    'SI': 'SI',
    'BG': 'BG',
    'RS': 'RS',
    'MD': 'MD',
    'UA': 'UA',
    'FI': 'FI',
    'SE': 'SE',
    'NO': 'NO',
    'DK': 'DK',
    'IE': 'IE',
    'EE': 'EE',
    'LV': 'LV',
    'LT': 'LT',
    'AL': 'AL',
    'BA': 'BA',
    'MK': 'MK',
    'ME': 'ME',
    'XK': 'XK'
}

# Types de trains GTFS
ROUTE_TYPES = {
    0: 'Tram',
    1: 'Metro', 
    2: 'Rail',
    3: 'Bus',
    4: 'Ferry',
    5: 'Cable',
    6: 'Gondola',
    7: 'Funicular',
    100: 'Railway',
    109: 'Suburban',
    400: 'Urban',
    401: 'Metro',
    402: 'Bus',
    405: 'Trolleybus',
    700: 'Bus',
    900: 'Tram',
    1000: 'Water',
    1100: 'Air',
    1200: 'Ferry',
    1300: 'Aerial',
    1400: 'Bus',
    1500: 'Telecabin',
    1700: 'Rail'
}