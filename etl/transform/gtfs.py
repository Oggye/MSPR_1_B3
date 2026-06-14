#==============================================================================
# Fichier: etl/transform/gtfs.py
#==============================================================================

"""
Transformation des données GTFS (France, Suisse, Allemagne)
"""

import pandas as pd
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def transform_gtfs_country(raw_dir: str, processed_dir: str, country: str) -> dict:
    """
    Transforme les données GTFS d'un pays spécifique
    """

    logger.info(f"🚉 Transformation GTFS pour {country.upper()}...")

    country_dir = Path(raw_dir) / f"gtfs_{country.lower()}"

    try:
        agency_df = pd.read_csv(
            country_dir / "agency.csv",
            low_memory=False
        )

        routes_df = pd.read_csv(
            country_dir / "routes.csv",
            low_memory=False
        )

        stops_df = pd.read_csv(
            country_dir / "stops.csv",
            low_memory=False
        )

        # CORRECTION : suppression du nrows=10000
        trips_df = pd.read_csv(
            country_dir / "trips.csv",
            low_memory=False
        )

        # NOUVEAU : chargement stop_times
        stop_times_df = pd.read_csv(
            country_dir / "stop_times.csv",
            low_memory=False
        )

    except FileNotFoundError as e:
        logger.error(f"❌ Fichier manquant pour {country}: {e}")
        return None

    # ------------------------------------------------------------------
    # Standardisation des colonnes
    # ------------------------------------------------------------------

    for df in [
        agency_df,
        routes_df,
        stops_df,
        trips_df,
        stop_times_df
    ]:
        df.columns = [
            str(col).strip().lower()
            for col in df.columns
        ]

    # ------------------------------------------------------------------
    # AGENCY
    # ------------------------------------------------------------------

    if "agency_name" in agency_df.columns:
        agency_df["agency_name"] = agency_df["agency_name"].fillna(
            f"Opérateur {country.upper()}"
        )

    if "agency_url" in agency_df.columns:
        agency_df["agency_url"] = agency_df["agency_url"].fillna("")

    agency_df["country"] = country.upper()

    # ------------------------------------------------------------------
    # ROUTES
    # ------------------------------------------------------------------

    if "route_short_name" in routes_df.columns:
        routes_df["route_short_name"] = (
            routes_df["route_short_name"]
            .fillna("")
            .astype(str)
        )

    if "route_long_name" in routes_df.columns:
        routes_df["route_long_name"] = (
            routes_df["route_long_name"]
            .fillna("")
            .astype(str)
        )
    else:
        routes_df["route_long_name"] = ""

    routes_df["is_night_train"] = routes_df[
        "route_long_name"
    ].str.contains(
        r"night|nacht|nocturne|nightjet|nuit",
        case=False,
        na=False,
        regex=True
    )

    # ------------------------------------------------------------------
    # STOPS
    # ------------------------------------------------------------------

    if "stop_name" in stops_df.columns:
        stops_df["stop_name"] = stops_df[
            "stop_name"
        ].fillna("Gare inconnue")

    for col in ["stop_lat", "stop_lon"]:

        if col not in stops_df.columns:
            continue

        stops_df[col] = pd.to_numeric(
            stops_df[col],
            errors="coerce"
        )

        moyenne = stops_df[col].mean()

        stops_df[col] = stops_df[col].fillna(
            moyenne
        )

    # ------------------------------------------------------------------
    # TRIPS
    # ------------------------------------------------------------------

    if "trip_id" in trips_df.columns:
        trips_df = trips_df.dropna(
            subset=["trip_id"]
        )

    trips_df = trips_df.drop_duplicates()

    # ------------------------------------------------------------------
    # STOP_TIMES
    # ------------------------------------------------------------------

    required_cols = [
        col
        for col in ["trip_id", "stop_id"]
        if col in stop_times_df.columns
    ]

    if required_cols:
        stop_times_df = stop_times_df.dropna(
            subset=required_cols
        )

    if "stop_sequence" in stop_times_df.columns:

        stop_times_df["stop_sequence"] = pd.to_numeric(
            stop_times_df["stop_sequence"],
            errors="coerce"
        )

        stop_times_df = stop_times_df.dropna(
            subset=["stop_sequence"]
        )

        stop_times_df["stop_sequence"] = (
            stop_times_df["stop_sequence"]
            .astype(int)
        )

    stop_times_df = stop_times_df.drop_duplicates()

    # ------------------------------------------------------------------
    # Sauvegarde
    # ------------------------------------------------------------------

    save_dir = (
        Path(processed_dir)
        / "gtfs"
        / country.lower()
    )

    save_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    agency_df.to_csv(
        save_dir / "agency_processed.csv",
        index=False
    )

    routes_df.to_csv(
        save_dir / "routes_processed.csv",
        index=False
    )

    stops_df.to_csv(
        save_dir / "stops_processed.csv",
        index=False
    )

    trips_df.to_csv(
        save_dir / "trips_processed.csv",
        index=False
    )

    stop_times_df.to_csv(
        save_dir / "stop_times_processed.csv",
        index=False
    )

    logger.info(
        f"✅ GTFS {country.upper()} sauvegardé dans {save_dir}"
    )

    # ------------------------------------------------------------------
    # Rapport qualité
    # ------------------------------------------------------------------

    missing_coords = {}

    if (
        "stop_lat" in stops_df.columns
        and "stop_lon" in stops_df.columns
    ):
        missing_coords = (
            stops_df[
                ["stop_lat", "stop_lon"]
            ]
            .isna()
            .sum()
            .to_dict()
        )

    quality_report = {
        "source": f"gtfs_{country.lower()}",
        "agencies": len(agency_df),
        "routes": len(routes_df),
        "stops": len(stops_df),
        "trips": len(trips_df),
        "stop_times": len(stop_times_df),
        "night_trains": int(
            routes_df["is_night_train"].sum()
        ),
        "missing_coords": missing_coords
    }

    logger.info(
        f"📊 {country.upper()} : "
        f"{len(trips_df):,} trips | "
        f"{len(stop_times_df):,} stop_times"
    )

    return quality_report


def transform_all_gtfs(
    raw_dir: str,
    processed_dir: str
) -> list:
    """
    Transforme tous les jeux GTFS
    """

    countries = ["fr", "ch", "de"]

    reports = []

    for country in countries:

        report = transform_gtfs_country(
            raw_dir,
            processed_dir,
            country
        )

        if report:
            reports.append(report)

    return reports