import numpy as np


def add_features(df):
    """
    Création des variables métiers pour le modèle
    de substitution avion -> train.

    Entrée :
        df : DataFrame contenant au minimum :
            - distance_km
            - duration_min
            - is_night

    Sortie :
        DataFrame enrichi de nouvelles features.
    """

    # ==================================================
    # Durée en heures
    # ==================================================
    df["duration_hours"] = df["duration_min"] / 60

    # Éviter les divisions par zéro
    safe_duration = df["duration_hours"].replace(0, np.nan)

    # ==================================================
    # Vitesse moyenne (km/h)
    # ==================================================
    df["avg_speed_kmh"] = (
        df["distance_km"] / safe_duration
    )

    # ==================================================
    # Distance parcourue par heure
    # ==================================================
    df["distance_per_hour"] = (
        df["distance_km"] / safe_duration
    )

    # ==================================================
    # Long trajet de nuit
    # ==================================================
    df["long_night_route"] = (
        (
            df["is_night"] == 1
        )
        &
        (
            df["distance_km"] > 800
        )
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