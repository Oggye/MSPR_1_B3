"""
Tests pour les endpoints de statistiques
"""

import pytest

class TestStatisticsEndpoints:
    """Tests pour /api/statistics/*"""

    def test_get_statistics_timeline(self, client, sample_data):
        """Test évolution temporelle des indicateurs"""
        response = client.get("/api/statistics/timeline")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        if data:
            assert "year" in data[0]
            assert "passengers" in data[0]
            assert "co2_emissions" in data[0]

    def test_get_co2_ranking(self, client, sample_data):
        """Test classement par impact CO2"""
        response = client.get("/api/statistics/co2-ranking")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        if data:
            assert "country_name" in data[0]
            assert "co2_per_passenger" in data[0]
            assert "rank" in data[0]
