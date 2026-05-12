from pathlib import Path

import pandas as pd
import pytest

from transform.distance import haversine, parse_stops_from_itinerary
from transform.duration import (
    compute_night_train_durations,
    estimate_duration_from_distance,
    extract_duration_from_text,
)
from transform.emissions import transform_emissions


def test_extract_duration_from_text_handles_overnight_trip():
    assert extract_duration_from_text("Depart 22:30 - Arrivee 08:15") == 585


def test_extract_duration_from_text_returns_none_without_two_times():
    assert extract_duration_from_text("Depart dans la soiree") is None
    assert extract_duration_from_text(None) is None


def test_estimate_duration_from_distance_uses_speed():
    assert estimate_duration_from_distance(140, speed_kmh=70) == 120
    assert estimate_duration_from_distance(0) == 0


def test_compute_night_train_durations_prefers_text_then_distance():
    trains = pd.DataFrame(
        [
            {"itinerary_long": "20:00 - 06:00", "distance_km": 800, "is_night": True},
            {"itinerary_long": "", "distance_km": 200, "is_night": False},
            {"itinerary_long": "", "distance_km": 0, "is_night": True},
        ]
    )

    result = compute_night_train_durations(trains)

    assert result.loc[0, "duration_min"] == 600
    assert result.loc[1, "duration_min"] == 120
    assert result.loc[2, "duration_min"] == 0


def test_parse_stops_from_itinerary_cleans_html_and_separators():
    result = parse_stops_from_itinerary("<b>Nightjet:</b> Paris - Strasbourg / Munich")

    assert result == ["Paris", "Strasbourg", "Munich"]


def test_haversine_returns_expected_distance_between_paris_and_lyon():
    distance = haversine(48.8566, 2.3522, 45.7640, 4.8357)

    assert distance == pytest.approx(391, rel=0.03)


def test_transform_emissions_filters_co2_after_2010_and_fills_missing_values(tmp_path):
    raw_dir = tmp_path / "raw"
    source_dir = raw_dir / "emission_co2"
    processed_dir = tmp_path / "processed"
    source_dir.mkdir(parents=True)

    pd.DataFrame(
        [
            {"airpol": "CO2", "geo": "FR", "TIME_PERIOD": 2009, "OBS_VALUE": 10},
            {"airpol": "CO2", "geo": "FR", "TIME_PERIOD": 2010, "OBS_VALUE": 20},
            {"airpol": "CO2", "geo": "FR", "TIME_PERIOD": 2011, "OBS_VALUE": None},
            {"airpol": "CH4", "geo": "FR", "TIME_PERIOD": 2011, "OBS_VALUE": 999},
            {"airpol": "CO2", "geo": "XX", "TIME_PERIOD": 2012, "OBS_VALUE": 5},
        ]
    ).to_csv(source_dir / "eurostat_env_air_gge_sdmx.csv", index=False)

    report = transform_emissions(str(raw_dir), str(processed_dir))
    output = pd.read_csv(processed_dir / "emissions" / "co2_emissions_processed.csv")

    assert report["source"] == "emissions"
    assert report["total_records"] == 3
    assert report["missing_values_after"] == 0
    assert set(output["year"]) == {2010, 2011, 2012}
    assert set(output["airpol"]) == {"CO2"}
    assert output.loc[output["year"] == 2011, "co2_emissions"].iloc[0] == 20
    assert output.loc[output["country_code"] == "XX", "country_name"].iloc[0] == "Unknown"
