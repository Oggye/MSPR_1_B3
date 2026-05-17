"""
Tests E2E – Night Trains & Geographic Coverage
Dossier cible : platform/server/tests/E2E/test_e2e_night_trains.py

Ces tests utilisent les fixtures du conftest.py existant (client + sample_data).
Ils testent les endpoints de bout en bout : HTTP → logique métier → SQLite in-memory.
"""

import pytest


# ──────────────────────────────────────────────
# /api/night-trains/summary
# ──────────────────────────────────────────────

class TestNightTrainsSummary:

    def test_summary_status_200(self, client, sample_data):
        """Le endpoint summary répond bien en 200."""
        response = client.get("/api/night-trains/summary")
        assert response.status_code == 200

    def test_summary_structure(self, client, sample_data):
        """La réponse contient bien les trois champs attendus."""
        data = client.get("/api/night-trains/summary").json()
        assert "total_trains" in data
        assert "total_night_trains" in data
        assert "total_day_trains" in data

    def test_summary_coherence(self, client, sample_data):
        """total_trains == total_night_trains + total_day_trains."""
        data = client.get("/api/night-trains/summary").json()
        assert data["total_trains"] == data["total_night_trains"] + data["total_day_trains"]

    def test_summary_counts(self, client, sample_data):
        """
        25 trains insérés dans sample_data.
        Les pairs (i % 2 == 0) sont is_night=True → 12 trains de nuit (2,4,...,24)
        Les impairs → 13 trains de jour.
        """
        data = client.get("/api/night-trains/summary").json()
        assert data["total_trains"] == 25
        assert data["total_night_trains"] == 12
        assert data["total_day_trains"] == 13


# ──────────────────────────────────────────────
# /api/night-trains  (tous les trains)
# ──────────────────────────────────────────────

class TestGetAllNightTrains:

    def test_returns_all_trains(self, client, sample_data):
        """Sans filtre, retourne les 25 trains."""
        response = client.get("/api/night-trains")
        assert response.status_code == 200
        assert len(response.json()) == 25

    def test_response_fields(self, client, sample_data):
        """Chaque item possède les champs obligatoires du schéma NightTrainResponse."""
        item = client.get("/api/night-trains").json()[0]
        for field in ["fact_id", "route_id", "night_train", "country_name",
                      "country_code", "operator_name", "year", "is_night", "is_night"]:
            assert field in item, f"Champ manquant : {field}"

    def test_train_type_values(self, client, sample_data):
        """train_type vaut uniquement 'night' ou 'day'."""
        items = client.get("/api/night-trains").json()
        for item in items:
            assert item["is_night"] in ("night", "day")

    def test_filter_by_country_code(self, client, sample_data):
        """Filtre country_code=FR ne retourne que des trains français."""
        response = client.get("/api/night-trains?country_code=FR")
        assert response.status_code == 200
        for item in response.json():
            assert item["country_code"] == "FR"

    def test_filter_by_operator_name(self, client, sample_data):
        """Filtre operator_name=SNCF (insensible à la casse) ne retourne que SNCF."""
        response = client.get("/api/night-trains?operator_name=sncf")
        assert response.status_code == 200
        for item in response.json():
            assert item["operator_name"].lower() == "sncf"

    def test_filter_by_year(self, client, sample_data):
        """Filtre year=2010 ne retourne que des trains de l'année 2010."""
        response = client.get("/api/night-trains?year=2010")
        assert response.status_code == 200
        for item in response.json():
            assert item["year"] == 2010

    def test_pagination_limit(self, client, sample_data):
        """limit=5 retourne exactement 5 résultats."""
        response = client.get("/api/night-trains?limit=5")
        assert response.status_code == 200
        assert len(response.json()) == 5

    def test_pagination_skip(self, client, sample_data):
        """skip=20 sur 25 trains retourne 5 résultats."""
        response = client.get("/api/night-trains?skip=20")
        assert response.status_code == 200
        assert len(response.json()) == 5

    def test_pagination_skip_and_limit(self, client, sample_data):
        """skip=10&limit=3 retourne exactement 3 résultats."""
        response = client.get("/api/night-trains?skip=10&limit=3")
        assert response.status_code == 200
        assert len(response.json()) == 3

    def test_invalid_skip_returns_422(self, client, sample_data):
        """skip négatif → 422 Unprocessable Entity."""
        response = client.get("/api/night-trains?skip=-1")
        assert response.status_code == 422

    def test_invalid_limit_returns_422(self, client, sample_data):
        """limit=0 → 422 Unprocessable Entity."""
        response = client.get("/api/night-trains?limit=0")
        assert response.status_code == 422

    def test_unknown_country_returns_empty(self, client, sample_data):
        """Filtre sur un pays inexistant retourne une liste vide."""
        response = client.get("/api/night-trains?country_code=XX")
        assert response.status_code == 200
        assert response.json() == []


# ──────────────────────────────────────────────
# /api/night-trains/night
# ──────────────────────────────────────────────

class TestNightTrainsOnly:

    def test_returns_only_night_trains(self, client, sample_data):
        """Tous les résultats ont is_night=True et train_type='night'."""
        response = client.get("/api/night-trains/night")
        assert response.status_code == 200
        items = response.json()
        assert len(items) > 0
        for item in items:
            assert item["is_night"] is True
            

    def test_night_count_matches_summary(self, client, sample_data):
        """Le nombre de trains de nuit correspond au summary."""
        summary = client.get("/api/night-trains/summary").json()
        night_list = client.get("/api/night-trains/night").json()
        assert len(night_list) == summary["total_night_trains"]

    def test_filter_country_on_night(self, client, sample_data):
        """Filtre country_code sur /night fonctionne correctement."""
        response = client.get("/api/night-trains/night?country_code=FR")
        assert response.status_code == 200
        for item in response.json():
            assert item["country_code"] == "FR"
            assert item["is_night"] is True

    def test_limit_on_night(self, client, sample_data):
        """limit=3 sur /night retourne exactement 3 résultats."""
        response = client.get("/api/night-trains/night?limit=3")
        assert response.status_code == 200
        assert len(response.json()) == 3


# ──────────────────────────────────────────────
# /api/night-trains/day
# ──────────────────────────────────────────────

class TestDayTrainsOnly:

    def test_returns_only_day_trains(self, client, sample_data):
        """Tous les résultats ont is_night=False et train_type='day'."""
        response = client.get("/api/night-trains/day")
        assert response.status_code == 200
        items = response.json()
        assert len(items) > 0
        for item in items:
            assert item["is_night"] is False
            

    def test_day_count_matches_summary(self, client, sample_data):
        """Le nombre de trains de jour correspond au summary."""
        summary = client.get("/api/night-trains/summary").json()
        day_list = client.get("/api/night-trains/day").json()
        assert len(day_list) == summary["total_day_trains"]

    def test_filter_operator_on_day(self, client, sample_data):
        """Filtre operator_name sur /day ne retourne que le bon opérateur."""
        response = client.get("/api/night-trains/day?operator_name=DB")
        assert response.status_code == 200
        for item in response.json():
            assert "db" in item["operator_name"].lower()
            assert item["is_night"] is False


# ──────────────────────────────────────────────
# /api/night-trains/by-operator/{operator_id}
# ──────────────────────────────────────────────

class TestNightTrainsByOperator:

    def test_valid_operator_returns_trains(self, client, sample_data):
        """Opérateur existant (id=1 = SNCF) retourne des trains."""
        response = client.get("/api/night-trains/by-operator/1")
        assert response.status_code == 200
        items = response.json()
        assert len(items) > 0
        for item in items:
            assert item["operator_name"] == "SNCF"

    def test_all_trains_belong_to_operator(self, client, sample_data):
        """Tous les trains retournés appartiennent bien à l'opérateur demandé."""
        response = client.get("/api/night-trains/by-operator/2")
        assert response.status_code == 200
        for item in response.json():
            assert item["operator_name"] == "DB"

    def test_invalid_operator_returns_404(self, client, sample_data):
        """Opérateur inexistant → 404."""
        response = client.get("/api/night-trains/by-operator/9999")
        assert response.status_code == 404
        assert "detail" in response.json()

    def test_404_message_content(self, client, sample_data):
        """Le message d'erreur 404 mentionne 'Opérateur non trouvé'."""
        response = client.get("/api/night-trains/by-operator/9999")
        assert response.json()["detail"] == "Opérateur non trouvé"


# ──────────────────────────────────────────────
# /api/geographic/coverage
# ──────────────────────────────────────────────

class TestGeographicCoverage:

    def test_coverage_status_200(self, client, sample_data):
        """Le endpoint geographic/coverage répond en 200."""
        response = client.get("/api/geographic/coverage")
        assert response.status_code == 200

    def test_coverage_structure(self, client, sample_data):
        """La réponse contient total_countries_covered et coverage_by_country."""
        data = client.get("/api/geographic/coverage").json()
        assert "total_countries_covered" in data
        assert "coverage_by_country" in data

    def test_coverage_country_fields(self, client, sample_data):
        """Chaque entrée de coverage_by_country a country_name, country_code, train_count."""
        data = client.get("/api/geographic/coverage").json()
        for entry in data["coverage_by_country"]:
            assert "country_name" in entry
            assert "country_code" in entry
            assert "train_count" in entry

    def test_coverage_train_count_positive(self, client, sample_data):
        """Chaque pays a au moins 1 train."""
        data = client.get("/api/geographic/coverage").json()
        for entry in data["coverage_by_country"]:
            assert entry["train_count"] > 0

    def test_coverage_sorted_desc(self, client, sample_data):
        """Les pays sont triés par train_count décroissant."""
        data = client.get("/api/geographic/coverage").json()
        counts = [e["train_count"] for e in data["coverage_by_country"]]
        assert counts == sorted(counts, reverse=True)

    def test_total_countries_matches_list(self, client, sample_data):
        """total_countries_covered == len(coverage_by_country)."""
        data = client.get("/api/geographic/coverage").json()
        assert data["total_countries_covered"] == len(data["coverage_by_country"])
