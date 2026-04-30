# =========================================================
# etl/transform/duration.py
# Calcule la durée estimée/minimale des trajets
# =========================================================
import pandas as pd
import numpy as np
import re
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_duration_from_text(text):
    """
    Cherche des horaires dans itinerary_long (ex: départ 20:30, arrivée 08:15).
    Retourne durée en minutes ou None.
    """
    if pd.isna(text):
        return None
    # Patterns possibles : "depart 22:30" ou "22:30 - 08:45"
    times = re.findall(r'(\d{1,2}:\d{2})', text)
    if len(times) >= 2:
        # Prendre le premier et le dernier
        def to_minutes(t):
            h, m = map(int, t.split(':'))
            return h*60 + m
        try:
            start = to_minutes(times[0])
            end = to_minutes(times[-1])
            if end < start:
                end += 24*60  # voyage de nuit
            return end - start
        except:
            pass
    return None

def estimate_duration_from_distance(distance_km, speed_kmh=70):
    """Estimation grossière de la durée en minutes à partir de la distance et d'une vitesse commerciale."""
    if distance_km > 0:
        return (distance_km / speed_kmh) * 60
    return 0

def compute_night_train_durations(trains_df):
    logger.info("⏱️ Calcul des durées pour tous les trains...")
    durations = []
    for idx, row in trains_df.iterrows():
        itinerary_long = row.get('itinerary_long', '')
        duration = extract_duration_from_text(itinerary_long)
        if duration is None:
            distance = row.get('distance_km', 0)
            if pd.notna(distance) and distance > 0:
                # Si c'est un train de nuit, vitesse plus faible
                speed = 70 if row.get('is_night', False) else 100
                duration = estimate_duration_from_distance(distance, speed_kmh=speed)
            else:
                duration = 0
        durations.append(duration)
    trains_df['duration_min'] = durations
    return trains_df