"""
Tests pour les endpoints du dashboard
"""

import pytest

class TestDashboardEndpoints:
    """Tests pour /api/dashboard/*"""

    def test_get_dashboard_metrics(self, client, sample_data):
        """Test récupération des métriques du dashboard"""
        response = client.get("/api/dashboard/metrics")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Vérifier la structure des données
        if data:
            assert "metric_name" in data[0]
            assert "value" in data[0]

    def test_get_dashboard_kpis(self, client, sample_data):
        """Test récupération des KPIs du dashboard"""
        response = client.get("/api/dashboard/kpis")
        assert response.status_code == 200
        data = response.json()
        assert "total_passengers" in data
        assert "total_co2_emissions" in data
        assert "total_countries" in data
        assert "total_trains" in data
        assert "total_night_trains" in data
        assert "total_day_trains" in data
        assert "total_operators" in data
        assert "years_covered" in data
        assert "avg_co2_per_passenger" in data
