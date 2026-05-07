"""
Tests pour les endpoints de métadonnées
"""

import pytest

class TestMetadataEndpoints:
    """Tests pour /api/metadata/*"""

    def test_get_metadata_quality(self, client, sample_data):
        """Test rapport de qualité des données"""
        response = client.get("/api/metadata/quality")
        assert response.status_code == 200
        data = response.json()
        assert "execution_date" in data
        assert "project" in data
        assert "reports" in data
        assert "summary" in data
        assert isinstance(data["reports"], list)
        assert "success" in data["summary"]

    def test_get_metadata_sources(self, client, sample_data):
        """Test sources de données"""
        response = client.get("/api/metadata/sources")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "sources" in data
        assert isinstance(data["sources"], list)
        if data["sources"]:
            assert "name" in data["sources"][0]
            assert "description" in data["sources"][0]
            assert "datasets" in data["sources"][0]
