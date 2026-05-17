import pytest

pytestmark = pytest.mark.e2e


def test_night_train_summary_is_consistent(client, sample_data):
    response = client.get("/api/night-trains/summary")
    assert response.status_code == 200

    payload = response.json()
    assert payload["total_trains"] == 25
    assert payload["total_night_trains"] == 12
    assert payload["total_day_trains"] == 13
    assert payload["total_trains"] == payload["total_night_trains"] + payload["total_day_trains"]


def test_get_all_night_trains_returns_expected_schema(client, sample_data):
    response = client.get("/api/night-trains")
    assert response.status_code == 200

    payload = response.json()
    assert len(payload) == 25

    required_keys = {
        "fact_id",
        "route_id",
        "night_train",
        "country_name",
        "country_code",
        "operator_name",
        "year",
        "is_night",
        "distance_km",
        "duration_min",
        "train_type",
    }
    for item in payload:
        assert required_keys <= set(item)
        assert isinstance(item["is_night"], bool)
        assert item["train_type"] in {"night", "day"}
        assert item["train_type"] == ("night" if item["is_night"] else "day")


@pytest.mark.parametrize(
    "query, expected_count",
    [
        ("?country_code=FR", 5),
        ("?operator_name=sncf", 5),
        ("?year=2010", 25),
        ("?limit=5", 5),
        ("?skip=20", 5),
        ("?skip=10&limit=3", 3),
        ("?country_code=XX", 0),
    ],
)
def test_get_all_night_trains_filters_and_pagination(client, sample_data, query, expected_count):
    response = client.get(f"/api/night-trains{query}")
    assert response.status_code == 200
    assert len(response.json()) == expected_count


@pytest.mark.parametrize("query", ["?skip=-1", "?limit=0"])
def test_get_all_night_trains_invalid_pagination_returns_422(client, sample_data, query):
    response = client.get(f"/api/night-trains{query}")
    assert response.status_code == 422


def test_night_only_endpoint(client, sample_data):
    response = client.get("/api/night-trains/night")
    assert response.status_code == 200

    payload = response.json()
    assert len(payload) == 12
    assert all(item["is_night"] is True for item in payload)
    assert all(item["train_type"] == "night" for item in payload)

    summary = client.get("/api/night-trains/summary").json()
    assert len(payload) == summary["total_night_trains"]


def test_day_only_endpoint(client, sample_data):
    response = client.get("/api/night-trains/day")
    assert response.status_code == 200

    payload = response.json()
    assert len(payload) == 13
    assert all(item["is_night"] is False for item in payload)
    assert all(item["train_type"] == "day" for item in payload)

    summary = client.get("/api/night-trains/summary").json()
    assert len(payload) == summary["total_day_trains"]


def test_night_and_day_filters_are_respected(client, sample_data):
    night_fr = client.get("/api/night-trains/night?country_code=FR")
    assert night_fr.status_code == 200
    assert all(item["country_code"] == "FR" and item["is_night"] is True for item in night_fr.json())

    day_db = client.get("/api/night-trains/day?operator_name=DB")
    assert day_db.status_code == 200
    assert all("db" in item["operator_name"].lower() and item["is_night"] is False for item in day_db.json())


def test_get_night_trains_by_operator(client, sample_data):
    response = client.get("/api/night-trains/by-operator/1")
    assert response.status_code == 200

    payload = response.json()
    assert len(payload) == 5
    assert all(item["operator_name"] == "SNCF" for item in payload)


def test_get_night_trains_by_operator_invalid_id_returns_404(client, sample_data):
    response = client.get("/api/night-trains/by-operator/9999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Opérateur non trouvé"


def test_geographic_coverage_endpoint(client, sample_data):
    response = client.get("/api/geographic/coverage")
    assert response.status_code == 200

    payload = response.json()
    assert payload["total_countries_covered"] == 5
    assert len(payload["coverage_by_country"]) == 5

    counts = [row["train_count"] for row in payload["coverage_by_country"]]
    assert counts == sorted(counts, reverse=True)
    assert all(count == 5 for count in counts)

    returned_codes = {row["country_code"] for row in payload["coverage_by_country"]}
    assert returned_codes == {"FR", "DE", "IT", "ES", "BE"}
