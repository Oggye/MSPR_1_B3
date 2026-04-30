# etl/transform/distance.py
import pandas as pd
import numpy as np
import re
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    return R * 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))

def parse_stops_from_itinerary(itinerary):
    """Extrait une liste de noms de gares à partir d'un itinéraire texte."""
    if pd.isna(itinerary) or not itinerary.strip():
        return []
    # Supprimer les balises HTML
    text = re.sub(r'<[^>]+>', ' ', itinerary)
    # Ne garder que la partie après le dernier ':' (nom de train)
    parts = text.split(':')
    if len(parts) > 1:
        text = parts[-1]
    # Séparer sur tiret, tiret long ou slash
    stops = re.split(r'\s*[-–/]\s*', text)
    stops = [s.strip() for s in stops if s.strip()]
    return stops

def compute_route_distance(trains_df, dim_stops):
    """
    Calcule la distance cumulée de chaque trajet à partir de sa colonne 'itinerary'.
    Ajoute une colonne 'distance_km'.
    """
    logger.info("📏 Calcul des distances...")
    if dim_stops.empty:
        trains_df['distance_km'] = 0.0
        return trains_df

    # Lookup rapide : dict {nom_gare: (lat, lon)}
    stops_lookup = {}
    for _, row in dim_stops.iterrows():
        name = row['stop_name']
        stops_lookup[name] = (row['stop_lat'], row['stop_lon'])

    distances = []
    for idx, row in trains_df.iterrows():
        itinerary = row.get('itinerary', '')
        stop_names = parse_stops_from_itinerary(itinerary)
        if not stop_names or len(stop_names) < 2:
            distances.append(0.0)
            continue

        total_km = 0.0
        for i in range(len(stop_names)-1):
            n1 = stop_names[i].strip().lower()
            n2 = stop_names[i+1].strip().lower()
            # Recherche exacte puis partielle
            if n1 in stops_lookup:
                lat1, lon1 = stops_lookup[n1]
                if n2 in stops_lookup:
                    lat2, lon2 = stops_lookup[n2]
                    total_km += haversine(lat1, lon1, lat2, lon2)
                    continue
            # Fallback : recherche approximative
            found1 = [v for k,v in stops_lookup.items() if n1 in k]
            found2 = [v for k,v in stops_lookup.items() if n2 in k]
            if found1 and found2:
                lat1, lon1 = found1[0]
                lat2, lon2 = found2[0]
                total_km += haversine(lat1, lon1, lat2, lon2)
        distances.append(total_km)

    trains_df['distance_km'] = distances
    return trains_df