"""
Tests pour les endpoints des pays
"""

import pytest

class TestCountriesEndpoints:
    """Tests pour /api/countries et /api/countries/stats"""

    def test_get_countries(self, client, sample_data):
        """Test récupération de la liste des pays"""
        response = client.get("/api/countries")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5  # 5 pays dans sample_data
        assert data[0]["country_code"] == "FR"
        assert data[0]["country_name"] == "France"

    def test_get_countries_with_pagination(self, client, sample_data):
        """Test pagination pour les pays"""
        response = client.get("/api/countries?skip=2&limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["country_code"] == "IT"

    def test_get_country_stats(self, client, sample_data):
        """Test récupération des statistiques par pays"""
        response = client.get("/api/countries/stats")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3  # 3 stats dans sample_data
        assert "country_name" in data[0]
        assert "passengers" in data[0]
        assert "co2_per_passenger" in data[0]

    def test_get_country_stats_filtered_by_country(self, client, sample_data):
        """Test filtrage des stats par pays"""
        response = client.get("/api/countries/stats?country_code=FR")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2  # 2 stats pour la France
        assert all(item["country_code"] == "FR" for item in data)

    def test_get_country_stats_filtered_by_year(self, client, sample_data):
        """Test filtrage des stats par année"""
        response = client.get("/api/countries/stats?year=2010")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2  # 2 stats pour 2010
        assert all(item["year"] == 2010 for item in data)
