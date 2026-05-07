"""
Tests pour les endpoints géographiques
"""

import pytest

class TestGeographicEndpoints:
    """Tests pour /api/geographic/*"""

    def test_get_geographic_coverage(self, client, sample_data):
        """Test données pour carte interactive"""
        response = client.get("/api/geographic/coverage")
        assert response.status_code == 200
        data = response.json()
        assert "coverage_by_country" in data
        assert "total_countries_covered" in data
        assert isinstance(data["coverage_by_country"], list)
        if data["coverage_by_country"]:
            assert "country_name" in data["coverage_by_country"][0]
            assert "country_code" in data["coverage_by_country"][0]
            assert "train_count" in data["coverage_by_country"][0]
