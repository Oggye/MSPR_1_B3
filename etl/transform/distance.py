import logging
import re
import unicodedata

import numpy as np
import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


REFERENCE_COORDS = {
    "wien": (48.2082, 16.3738), "vienna": (48.2082, 16.3738),
    "bruxelles": (50.8503, 4.3517), "brussels": (50.8503, 4.3517),
    "berlin": (52.5200, 13.4050), "zurich": (47.3769, 8.5417),
    "zuerich": (47.3769, 8.5417), "split": (43.5081, 16.4402),
    "zagreb": (45.8150, 15.9819), "hamburg": (53.5511, 9.9937),
    "paris": (48.8566, 2.3522), "lyon": (45.7640, 4.8357),
    "marseille": (43.2965, 5.3698), "lille": (50.6292, 3.0573),
    "muenchen": (48.1351, 11.5820), "munich": (48.1351, 11.5820),
    "frankfurt": (50.1109, 8.6821), "koeln": (50.9375, 6.9603),
    "cologne": (50.9375, 6.9603), "stuttgart": (48.7758, 9.1829),
    "roma": (41.9028, 12.4964), "rome": (41.9028, 12.4964),
    "milano": (45.4642, 9.1900), "napoli": (40.8518, 14.2681),
    "venezia": (45.4408, 12.3155), "madrid": (40.4168, -3.7038),
    "barcelona": (41.3874, 2.1686), "valencia": (39.4699, -0.3763),
    "sevilla": (37.3891, -5.9845), "amsterdam": (52.3676, 4.9041),
    "rotterdam": (51.9244, 4.4777), "utrecht": (52.0907, 5.1214),
    "salzburg": (47.8095, 13.0550), "innsbruck": (47.2692, 11.4041),
    "antwerp": (51.2194, 4.4025), "liege": (50.6326, 5.5797),
    "sofia": (42.6977, 23.3219), "plovdiv": (42.1354, 24.7453),
    "varna": (43.2141, 27.9147), "praha": (50.0755, 14.4378),
    "prague": (50.0755, 14.4378), "brno": (49.1951, 16.6068),
    "ostrava": (49.8209, 18.2625), "copenhagen": (55.6761, 12.5683),
    "aarhus": (56.1629, 10.2039), "odense": (55.4038, 10.4024),
    "tallinn": (59.4370, 24.7536), "tartu": (58.3776, 26.7290),
    "helsinki": (60.1699, 24.9384), "tampere": (61.4978, 23.7610),
    "turku": (60.4518, 22.2666), "athens": (37.9838, 23.7275),
    "thessaloniki": (40.6401, 22.9444), "budapest": (47.4979, 19.0402),
    "debrecen": (47.5316, 21.6273), "szeged": (46.2530, 20.1414),
    "dublin": (53.3498, -6.2603), "cork": (51.8985, -8.4756),
    "galway": (53.2707, -9.0568), "riga": (56.9496, 24.1052),
    "daugavpils": (55.8747, 26.5362), "vilnius": (54.6872, 25.2797),
    "kaunas": (54.8985, 23.9036), "luxembourg": (49.6116, 6.1319),
    "esch-sur-alzette": (49.4958, 5.9806), "warszawa": (52.2297, 21.0122),
    "warsaw": (52.2297, 21.0122), "krakow": (50.0647, 19.9450),
    "wroclaw": (51.1079, 17.0385), "lisboa": (38.7223, -9.1393),
    "lisbon": (38.7223, -9.1393), "porto": (41.1579, -8.6291),
    "coimbra": (40.2033, -8.4103), "bucuresti": (44.4268, 26.1025),
    "bucharest": (44.4268, 26.1025), "cluj": (46.7712, 23.6236),
    "timisoara": (45.7489, 21.2087), "bratislava": (48.1486, 17.1077),
    "kosice": (48.7164, 21.2611), "ljubljana": (46.0569, 14.5058),
    "maribor": (46.5547, 15.6459), "stockholm": (59.3293, 18.0686),
    "goteborg": (57.7089, 11.9746), "gothenburg": (57.7089, 11.9746),
    "malmo": (55.6050, 13.0038), "london": (51.5072, -0.1276),
    "manchester": (53.4808, -2.2426), "edinburgh": (55.9533, -3.1883),
}

COUNTRY_GROUPS = {
    "AT": "A", "BE": "A", "CH": "A", "DE": "A", "ES": "A", "FR": "A", "IT": "A", "NL": "A",
    "CZ": "B", "DK": "B", "FI": "B", "PL": "B", "SE": "B",
    "HR": "C", "HU": "C", "PT": "C", "RO": "C", "SI": "C", "SK": "C",
    "BG": "D", "EE": "D", "GR": "D", "IE": "D", "LT": "D", "LV": "D",
    "CY": "E", "LU": "E", "MT": "E",
}

COUNTRY_DISTANCE_DEFAULTS = {"A": 420.0, "B": 320.0, "C": 260.0, "D": 180.0, "E": 45.0}


def haversine(lat1, lon1, lat2, lon2):
    radius_km = 6371.0
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    return radius_km * 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))


def normalize_name(value):
    if pd.isna(value):
        return ""
    text = unicodedata.normalize("NFKD", str(value))
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.lower()
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\b(hbf|hb|sbb|ost|sud|nord|midi|zuid|main|saale)\b", " ", text)
    text = re.sub(r"[^a-z0-9\- ]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def parse_stops_from_itinerary(itinerary):
    if pd.isna(itinerary) or not str(itinerary).strip():
        return []
    text = re.sub(r"<br\s*/?>", " - ", str(itinerary), flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\b[A-Z]{0,4}\s*\d{1,5}\s*:", " ", text)
    stops = re.split(r"\s+(?:-|--|–|—|/)\s+", text)
    return [normalize_name(stop) for stop in stops if normalize_name(stop)]


def lookup_reference_coord(stop_name):
    name = normalize_name(stop_name)
    if name in REFERENCE_COORDS:
        return REFERENCE_COORDS[name]
    for key, coords in REFERENCE_COORDS.items():
        if key in name or name in key:
            return coords
    return None


def fallback_distance(row):
    country = str(row.get("country_code", "")).upper()
    group = COUNTRY_GROUPS.get(country)
    base = COUNTRY_DISTANCE_DEFAULTS.get(group, 250.0)
    if bool(row.get("is_night", False)):
        return max(base * 1.8, 120.0)
    return max(base, 25.0)


def compute_route_distance(trains_df, dim_stops):
    logger.info("Calcul des distances ferroviaires...")
    if trains_df.empty:
        return trains_df

    stops_lookup = {}
    if not dim_stops.empty:
        for _, row in dim_stops.iterrows():
            name = normalize_name(row.get("stop_name", ""))
            lat = pd.to_numeric(row.get("stop_lat"), errors="coerce")
            lon = pd.to_numeric(row.get("stop_lon"), errors="coerce")
            if name and pd.notna(lat) and pd.notna(lon):
                stops_lookup[name] = (lat, lon)

    distances = []
    for _, row in trains_df.iterrows():
        stop_names = parse_stops_from_itinerary(row.get("itinerary", ""))
        total_km = 0.0

        for start, end in zip(stop_names, stop_names[1:]):
            coord1 = stops_lookup.get(start)
            coord2 = stops_lookup.get(end)

            if coord1 is None:
                matches = [value for key, value in stops_lookup.items() if start in key or key in start]
                coord1 = matches[0] if matches else lookup_reference_coord(start)
            if coord2 is None:
                matches = [value for key, value in stops_lookup.items() if end in key or key in end]
                coord2 = matches[0] if matches else lookup_reference_coord(end)

            if coord1 and coord2:
                total_km += haversine(coord1[0], coord1[1], coord2[0], coord2[1])

        if total_km <= 0:
            total_km = fallback_distance(row)
        distances.append(float(total_km))

    trains_df = trains_df.copy()
    trains_df["distance_km"] = distances
    return trains_df
