"""
Tests pour les endpoints d'analyse
"""

import pytest

class TestAnalysisEndpoints:
    """Tests pour /api/analysis/*"""

    def test_get_train_types_comparison(self, client, sample_data):
        """Test comparaison trains jour/nuit"""
        response = client.get("/api/analysis/train-types-comparison")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        if data:  # Si on a des données
            assert "train_type" in data[0]
            assert "avg_passengers" in data[0]
            assert "avg_co2_per_passenger" in data[0]
            assert "efficiency_score" in data[0]
            # Vérifier qu'on a au moins les types night et day
            train_types = [item["train_type"] for item in data]
            assert "night" in train_types or "day" in train_types

    def test_get_policy_recommendations(self, client, sample_data):
        """Test recommandations politiques"""
        response = client.get("/api/analysis/policy-recommendations")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "recommendations" in data
        assert isinstance(data["recommendations"], list)
        if data["recommendations"]:  # Si on a des recommandations
            assert "title" in data["recommendations"][0]
            assert "description" in data["recommendations"][0]
            assert "suggestion" in data["recommendations"][0]
