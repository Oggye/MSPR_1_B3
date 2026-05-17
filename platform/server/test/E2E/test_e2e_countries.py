import pytest

pytestmark = pytest.mark.e2e


def test_get_countries_returns_expected_payload(client, sample_data):
    response = client.get("/api/countries")
    assert response.status_code == 200

    payload = response.json()
    assert isinstance(payload, list)
    assert len(payload) == 5

    for country in payload:
        assert {"country_id", "country_code", "country_name"} <= set(country)
        assert isinstance(country["country_code"], str)
        assert country["country_code"]


@pytest.mark.parametrize(
    "query, expected_size",
    [
        ("?limit=2", 2),
        ("?skip=3", 2),
        ("?skip=100", 0),
    ],
)
def test_get_countries_pagination(client, sample_data, query, expected_size):
    response = client.get(f"/api/countries{query}")
    assert response.status_code == 200
    assert len(response.json()) == expected_size


@pytest.mark.parametrize("query", ["?skip=-1", "?limit=0"])
def test_get_countries_invalid_pagination_returns_422(client, sample_data, query):
    response = client.get(f"/api/countries{query}")
    assert response.status_code == 422


def test_get_countries_contains_known_unique_codes(client, sample_data):
    response = client.get("/api/countries")
    assert response.status_code == 200

    codes = [country["country_code"] for country in response.json()]
    assert "FR" in codes
    assert len(codes) == len(set(codes))


def test_get_country_stats_returns_expected_payload(client, sample_data):
    response = client.get("/api/countries/stats")
    assert response.status_code == 200

    payload = response.json()
    assert isinstance(payload, list)
    assert len(payload) == 3

    expected_keys = {
        "stats_id",
        "country_id",
        "year_id",
        "passengers",
        "co2_emissions",
        "co2_per_passenger",
        "country_name",
        "country_code",
        "year",
    }
    for item in payload:
        assert expected_keys <= set(item)
        assert item["passengers"] > 0


@pytest.mark.parametrize(
    "query, expected_count",
    [
        ("?country_code=FR", 2),
        ("?year=2010", 2),
        ("?min_passengers=150000", 1),
        ("?max_passengers=105000", 1),
        ("?min_passengers=100000&max_passengers=115000", 2),
        ("?min_co2_per_passenger=0.045", 2),
        ("?max_co2_per_passenger=0.045", 1),
        ("?country_code=FR&year=2010", 1),
        ("?country_code=XX", 0),
        ("?limit=1", 1),
        ("?skip=2", 1),
    ],
)
def test_get_country_stats_filters_and_pagination(client, sample_data, query, expected_count):
    response = client.get(f"/api/countries/stats{query}")
    assert response.status_code == 200
    assert len(response.json()) == expected_count


def test_get_country_stats_filter_values_are_respected(client, sample_data):
    filtered = client.get("/api/countries/stats?country_code=FR&year=2010").json()
    assert len(filtered) == 1
    assert filtered[0]["country_code"] == "FR"
    assert filtered[0]["year"] == 2010

    min_filtered = client.get("/api/countries/stats?min_passengers=150000").json()
    assert all(item["passengers"] >= 150000 for item in min_filtered)

    max_filtered = client.get("/api/countries/stats?max_co2_per_passenger=0.045").json()
    assert all(item["co2_per_passenger"] <= 0.045 for item in max_filtered)


@pytest.mark.parametrize("query", ["?skip=-1", "?limit=0"])
def test_get_country_stats_invalid_pagination_returns_422(client, sample_data, query):
    response = client.get(f"/api/countries/stats{query}")
    assert response.status_code == 422
