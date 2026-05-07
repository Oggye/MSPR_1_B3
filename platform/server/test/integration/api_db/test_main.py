"""
Tests pour les endpoints de base
"""

import pytest

class TestMainEndpoints:
    """Tests pour les endpoints de base (/ , /health, /api/docs)"""

    def test_root_endpoint(self, client):
        """Test endpoint racine"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["message"] == "API"

    def test_health_check(self, client):
        """Test vérification de santé"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"

    def test_api_docs(self, client):
        """Test documentation API"""
        response = client.get("/api/docs")
        assert response.status_code == 200
        # Vérifier que c'est du HTML (Swagger UI)
        assert "html" in response.headers.get("content-type", "").lower()

    def test_openapi_json(self, client):
        """Test spécification OpenAPI"""
        response = client.get("/api/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data
        assert "paths" in data
