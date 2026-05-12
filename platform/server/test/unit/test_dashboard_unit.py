from types import SimpleNamespace
from unittest.mock import MagicMock

from app.routers.dashboard import get_dashboard_kpis


def test_dashboard_kpis_aggregates_counts_and_totals():
    db = MagicMock()

    countries_query = MagicMock()
    countries_query.count.return_value = 2

    trains_query = MagicMock()
    trains_query.count.return_value = 5
    trains_query.filter.return_value.count.side_effect = [3, 2]

    operators_query = MagicMock()
    operators_query.count.return_value = 4

    years_query = MagicMock()
    years_query.order_by.return_value.all.return_value = [(2010,), (2024,)]

    stats_query = MagicMock()
    stats_query.first.return_value = (0.041, 120000.0, 4500.0)

    db.query.side_effect = [
        countries_query,
        trains_query,
        trains_query,
        trains_query,
        operators_query,
        years_query,
        stats_query,
    ]

    result = get_dashboard_kpis(db)

    assert result.total_countries == 2
    assert result.total_trains == 5
    assert result.total_night_trains == 3
    assert result.total_day_trains == 2
    assert result.total_operators == 4
    assert result.years_covered == "2010-2024"
    assert result.avg_co2_per_passenger == 0.041
    assert result.total_passengers == 120000.0
    assert result.total_co2_emissions == 4500.0


def test_dashboard_kpis_handles_empty_database():
    db = MagicMock()

    empty_count_query = MagicMock()
    empty_count_query.count.return_value = 0
    empty_count_query.filter.return_value.count.return_value = 0

    years_query = MagicMock()
    years_query.order_by.return_value.all.return_value = []

    stats_query = MagicMock()
    stats_query.first.return_value = (None, None, None)

    db.query.side_effect = [
        empty_count_query,
        empty_count_query,
        empty_count_query,
        empty_count_query,
        empty_count_query,
        years_query,
        stats_query,
    ]

    result = get_dashboard_kpis(db)

    assert result.total_countries == 0
    assert result.total_trains == 0
    assert result.total_night_trains == 0
    assert result.total_day_trains == 0
    assert result.total_operators == 0
    assert result.years_covered.startswith("Pas de")
    assert result.avg_co2_per_passenger == 0
    assert result.total_passengers == 0
    assert result.total_co2_emissions == 0
