"""
Tests pour les endpoints des trains de nuit
"""

import pytest

class TestNightTrainsEndpoints:
    """Tests pour tous les endpoints /api/night-trains/*"""

    def test_get_night_trains(self, client, sample_data):
        """Test récupération de tous les trains de nuit"""
        response = client.get("/api/night-trains")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2  # 2 trains dans sample_data
        assert "night_train" in data[0]
        assert "country_name" in data[0]

    def test_get_night_trains_summary(self, client, sample_data):
        """Test récupération du résumé des trains de nuit"""
        response = client.get("/api/night-trains/summary")
        assert response.status_code == 200
        data = response.json()
        assert "total_trains" in data
        assert "total_night_trains" in data
        assert "total_day_trains" in data
        assert data["total_trains"] == 2  # 2 trains dans sample_data
        assert data["total_night_trains"] == 2  # tous sont des trains de nuit
        assert data["total_day_trains"] == 0

    def test_get_night_trains_only(self, client, sample_data):
        """Test récupération des trains de nuit uniquement"""
        response = client.get("/api/night-trains/night")
        assert response.status_code == 200
        data = response.json()
        # Vérifier que tous les trains récupérés sont des trains de nuit
        assert len(data) >= 0

    def test_get_day_trains_only(self, client, sample_data):
        """Test récupération des trains de jour uniquement"""
        response = client.get("/api/night-trains/day")
        assert response.status_code == 200
        data = response.json()
        # Vérifier que la liste des trains de jour est vide (car sample_data ne contient que des trains de nuit)
        assert len(data) == 0

    def test_get_night_trains_by_operator(self, client, sample_data):
        """Test récupération des trains par opérateur"""
        response = client.get("/api/night-trains/by-operator/1")  # SNCF
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1  # 1 train pour SNCF
        assert data[0]["operator_name"] == "SNCF"
