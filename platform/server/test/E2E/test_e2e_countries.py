"""
Tests E2E – Countries & Country Stats
Dossier cible : platform/server/tests/E2E/test_e2e_countries.py

Ces tests utilisent les fixtures du conftest.py existant (client + sample_data).
"""

import pytest


# ──────────────────────────────────────────────
# /api/countries
# ──────────────────────────────────────────────

class TestGetCountries:

    def test_returns_200(self, client, sample_data):
        """Le endpoint /api/countries répond en 200."""
        response = client.get("/api/countries")
        assert response.status_code == 200

    def test_returns_list(self, client, sample_data):
        """La réponse est une liste."""
        response = client.get("/api/countries")
        assert isinstance(response.json(), list)

    def test_returns_all_countries(self, client, sample_data):
        """Sans filtre, retourne les 5 pays de sample_data."""
        response = client.get("/api/countries")
        assert len(response.json()) == 5

    def test_country_fields(self, client, sample_data):
        """Chaque pays possède country_id, country_code, country_name."""
        item = client.get("/api/countries").json()[0]
        assert "country_id" in item
        assert "country_code" in item
        assert "country_name" in item

    def test_country_codes_are_strings(self, client, sample_data):
        """Les codes pays sont des chaînes non vides."""
        items = client.get("/api/countries").json()
        for item in items:
            assert isinstance(item["country_code"], str)
            assert len(item["country_code"]) > 0

    def test_pagination_limit(self, client, sample_data):
        """limit=2 retourne exactement 2 pays."""
        response = client.get("/api/countries?limit=2")
        assert response.status_code == 200
        assert len(response.json()) == 2

    def test_pagination_skip(self, client, sample_data):
        """skip=3 sur 5 pays retourne 2 résultats."""
        response = client.get("/api/countries?skip=3")
        assert response.status_code == 200
        assert len(response.json()) == 2

    def test_skip_beyond_total_returns_empty(self, client, sample_data):
        """skip=100 sur 5 pays retourne une liste vide."""
        response = client.get("/api/countries?skip=100")
        assert response.status_code == 200
        assert response.json() == []

    def test_invalid_skip_returns_422(self, client, sample_data):
        """skip négatif → 422."""
        response = client.get("/api/countries?skip=-1")
        assert response.status_code == 422

    def test_invalid_limit_returns_422(self, client, sample_data):
        """limit=0 → 422."""
        response = client.get("/api/countries?limit=0")
        assert response.status_code == 422

    def test_known_country_present(self, client, sample_data):
        """La France (FR) est présente dans la liste."""
        items = client.get("/api/countries").json()
        codes = [item["country_code"] for item in items]
        assert "FR" in codes

    def test_no_duplicate_country_codes(self, client, sample_data):
        """Pas de doublons sur country_code."""
        items = client.get("/api/countries").json()
        codes = [item["country_code"] for item in items]
        assert len(codes) == len(set(codes))


# ──────────────────────────────────────────────
# /api/countries/stats
# ──────────────────────────────────────────────

class TestGetCountryStats:

    def test_returns_200(self, client, sample_data):
        """Le endpoint /api/countries/stats répond en 200."""
        response = client.get("/api/countries/stats")
        assert response.status_code == 200

    def test_returns_list(self, client, sample_data):
        """La réponse est une liste."""
        assert isinstance(client.get("/api/countries/stats").json(), list)

    def test_returns_all_stats(self, client, sample_data):
        """Sans filtre, retourne les 3 entrées de sample_data."""
        response = client.get("/api/countries/stats")
        assert len(response.json()) == 3

    def test_stats_fields(self, client, sample_data):
        """Chaque item contient les champs attendus du schéma CountryStatsResponse."""
        item = client.get("/api/countries/stats").json()[0]
        for field in ["stats_id", "country_id", "year_id", "passengers",
                      "co2_emissions", "co2_per_passenger", "country_name",
                      "country_code", "year"]:
            assert field in item, f"Champ manquant : {field}"

    def test_passengers_are_positive(self, client, sample_data):
        """Les valeurs de passengers sont positives."""
        items = client.get("/api/countries/stats").json()
        for item in items:
            assert item["passengers"] > 0

    def test_filter_by_country_code(self, client, sample_data):
        """Filtre country_code=FR retourne uniquement les stats françaises."""
        response = client.get("/api/countries/stats?country_code=FR")
        assert response.status_code == 200
        items = response.json()
        assert len(items) > 0
        for item in items:
            assert item["country_code"] == "FR"

    def test_filter_by_year(self, client, sample_data):
        """Filtre year=2010 retourne uniquement les stats de 2010."""
        response = client.get("/api/countries/stats?year=2010")
        assert response.status_code == 200
        for item in response.json():
            assert item["year"] == 2010

    def test_filter_min_passengers(self, client, sample_data):
        """Filtre min_passengers=150000 exclut les entrées en dessous."""
        response = client.get("/api/countries/stats?min_passengers=150000")
        assert response.status_code == 200
        for item in response.json():
            assert item["passengers"] >= 150000

    def test_filter_max_passengers(self, client, sample_data):
        """Filtre max_passengers=105000 exclut les entrées au dessus."""
        response = client.get("/api/countries/stats?max_passengers=105000")
        assert response.status_code == 200
        for item in response.json():
            assert item["passengers"] <= 105000

    def test_filter_min_and_max_passengers(self, client, sample_data):
        """Combinaison min + max retourne uniquement ce qui est dans la plage."""
        response = client.get("/api/countries/stats?min_passengers=100000&max_passengers=115000")
        assert response.status_code == 200
        for item in response.json():
            assert 100000 <= item["passengers"] <= 115000

    def test_filter_min_co2_per_passenger(self, client, sample_data):
        """Filtre min_co2_per_passenger=0.045 exclut les valeurs inférieures."""
        response = client.get("/api/countries/stats?min_co2_per_passenger=0.045")
        assert response.status_code == 200
        for item in response.json():
            assert item["co2_per_passenger"] >= 0.045

    def test_filter_max_co2_per_passenger(self, client, sample_data):
        """Filtre max_co2_per_passenger=0.045 exclut les valeurs supérieures."""
        response = client.get("/api/countries/stats?max_co2_per_passenger=0.045")
        assert response.status_code == 200
        for item in response.json():
            assert item["co2_per_passenger"] <= 0.045

    def test_combined_filters(self, client, sample_data):
        """Filtres combinés country_code + year fonctionnent ensemble."""
        response = client.get("/api/countries/stats?country_code=FR&year=2010")
        assert response.status_code == 200
        for item in response.json():
            assert item["country_code"] == "FR"
            assert item["year"] == 2010

    def test_unknown_country_returns_empty(self, client, sample_data):
        """Filtre sur pays inexistant retourne liste vide."""
        response = client.get("/api/countries/stats?country_code=XX")
        assert response.status_code == 200
        assert response.json() == []

    def test_pagination_limit(self, client, sample_data):
        """limit=1 retourne exactement 1 résultat."""
        response = client.get("/api/countries/stats?limit=1")
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_pagination_skip(self, client, sample_data):
        """skip=2 sur 3 stats retourne 1 résultat."""
        response = client.get("/api/countries/stats?skip=2")
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_invalid_limit_returns_422(self, client, sample_data):
        """limit=0 → 422."""
        response = client.get("/api/countries/stats?limit=0")
        assert response.status_code == 422