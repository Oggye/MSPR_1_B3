# ia\src\ml\feature_engineering.py

import numpy as np


def add_features(df):

    df = df.copy()

    df["duration_hours"] = df["duration_min"] / 60

    safe_duration = df["duration_hours"].replace(0, np.nan)

    df["avg_speed_kmh"] = (
        df["distance_km"] / safe_duration
    )

    df["long_night_route"] = (
        (df["is_night"] == 1)
        &
        (df["distance_km"] > 800)
    ).astype(int)

    # ==================================================
    # Catégorie de distance
    # ==================================================
    df["distance_category"] = np.select(
        [
            df["distance_km"] < 500,
            (df["distance_km"] >= 500)
            & (df["distance_km"] < 1000),
            df["distance_km"] >= 1000
        ],
        [
            "short",
            "medium",
            "long"
        ],
        default="unknown"
    )

    # ==================================================
    # Catégorie de durée
    # ==================================================
    df["duration_category"] = np.select(
        [
            df["duration_hours"] < 4,
            (df["duration_hours"] >= 4)
            & (df["duration_hours"] < 8),
            df["duration_hours"] >= 8
        ],
        [
            "fast",
            "medium",
            "slow"
        ],
        default="unknown"
    )

    # ==================================================
    # Ratio nuit / jour exploitable
    # ==================================================
    df["night_bonus"] = (
        df["is_night"] == 1
    ).astype(int)

    # ==================================================
    # Nettoyage des éventuelles valeurs infinies
    # ==================================================
    df.replace(
        [np.inf, -np.inf],
        np.nan,
        inplace=True
    )

    return df