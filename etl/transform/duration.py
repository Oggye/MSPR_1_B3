import logging
import re

import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


COUNTRY_GROUPS = {
    "AT": "A", "BE": "A", "CH": "A", "DE": "A", "ES": "A", "FR": "A", "IT": "A", "NL": "A",
    "CZ": "B", "DK": "B", "FI": "B", "PL": "B", "SE": "B",
    "HR": "C", "HU": "C", "PT": "C", "RO": "C", "SI": "C", "SK": "C",
    "BG": "D", "EE": "D", "GR": "D", "IE": "D", "LT": "D", "LV": "D",
    "CY": "E", "LU": "E", "MT": "E",
}


def extract_duration_from_text(text):
    if pd.isna(text):
        return None
    times = re.findall(r"(\d{1,2}:\d{2})", str(text))
    if len(times) < 2:
        return None

    def to_minutes(value):
        hour, minute = map(int, value.split(":"))
        if hour > 47 or minute > 59:
            raise ValueError("invalid GTFS time")
        return hour * 60 + minute

    try:
        start = to_minutes(times[0])
        end = to_minutes(times[-1])
        if end <= start:
            end += 24 * 60
        duration = end - start
        return duration if duration > 0 else None
    except ValueError:
        return None


def estimate_duration_from_distance(distance_km, speed_kmh=70):
    distance = pd.to_numeric(distance_km, errors="coerce")
    if pd.notna(distance) and distance > 0 and speed_kmh > 0:
        return (float(distance) / speed_kmh) * 60
    return None


def commercial_speed(row):
    country = str(row.get("country_code", "")).upper()
    group = COUNTRY_GROUPS.get(country, "C")
    text = " ".join(str(row.get(col, "")) for col in ["night_train", "route_long_name", "itinerary"])
    text = text.lower()

    if any(token in text for token in ["tgv", "ice", "frecciarossa", "ave", "high speed"]):
        return 240
    if bool(row.get("is_night", False)):
        return {"A": 95, "B": 85, "C": 75, "D": 65, "E": 60}.get(group, 75)
    if any(token in text for token in ["intercity", "ic ", "ec ", "eurocity"]):
        return {"A": 125, "B": 115, "C": 100, "D": 85, "E": 80}.get(group, 100)
    return {"A": 100, "B": 90, "C": 75, "D": 60, "E": 45}.get(group, 75)


def minimum_duration(row):
    if bool(row.get("is_night", False)):
        return 90.0
    country = str(row.get("country_code", "")).upper()
    if COUNTRY_GROUPS.get(country) == "E":
        return 25.0
    return 30.0


def compute_night_train_durations(trains_df):
    logger.info("Calcul des durees ferroviaires...")
    if trains_df.empty:
        return trains_df

    durations = []
    for _, row in trains_df.iterrows():
        duration = extract_duration_from_text(row.get("itinerary_long", ""))
        if duration is None:
            duration = estimate_duration_from_distance(
                row.get("distance_km", 0),
                speed_kmh=commercial_speed(row),
            )
        if duration is None or duration <= 0:
            duration = minimum_duration(row)
        durations.append(float(max(duration, minimum_duration(row))))

    trains_df = trains_df.copy()
    trains_df["duration_min"] = durations
    return trains_df
