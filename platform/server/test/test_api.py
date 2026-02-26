"""
Tests unitaires pour l'API ObRail - Observatoire Européen du Rail
Couvre tous les endpoints définis dans la documentation
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app.database import Base, get_db
from app.models import (
    DimCountry, DimYear, DimOperator,
    FactCountryStat, FactNightTrain, DashboardMetric
)

# Configuration de la base de données de test
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    """Override de la dépendance get_db pour utiliser la DB de test"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

class TestObRailAPI:
    """Classe de tests pour l'API ObRail"""

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """Setup et teardown pour chaque test"""
        # Création des tables
        Base.metadata.create_all(bind=engine)
        
        # Création d'une session
        db = TestingSessionLocal()
        
        # Données de test - DimYears
        years = []
        for year in range(2010, 2025):
            year_obj = DimYear(year_id=year-2009, year=year, is_after_2010=(year >= 2010))
            years.append(year_obj)
            db.add(year_obj)
        
        # Données de test - DimCountries
        countries = [
            DimCountry(country_id=1, country_code="FR", country_name="France"),
            DimCountry(country_id=2, country_code="DE", country_name="Germany"),
            DimCountry(country_id=3, country_code="IT", country_name="Italy"),
            DimCountry(country_id=4, country_code="ES", country_name="Spain"),
            DimCountry(country_id=5, country_code="BE", country_name="Belgium"),
        ]
        for country in countries:
            db.add(country)
        
        # Données de test - DimOperators
        operators = [
            DimOperator(operator_id=1, operator_name="SNCF"),
            DimOperator(operator_id=2, operator_name="DB"),
            DimOperator(operator_id=3, operator_name="Trenitalia"),
            DimOperator(operator_id=4, operator_name="Renfe"),
            DimOperator(operator_id=5, operator_name="ÖBB"),
        ]
        for operator in operators:
            db.add(operator)
        
        # Données de test - FactCountryStats
        stats = [
            FactCountryStat(
                stat_id=1, country_id=1, year_id=1,
                passengers=100000.0, co2_emissions=5000.0, co2_per_passenger=0.05
            ),
            FactCountryStat(
                stat_id=2, country_id=1, year_id=2,
                passengers=110000.0, co2_emissions=5200.0, co2_per_passenger=0.047
            ),
            FactCountryStat(
                stat_id=3, country_id=2, year_id=1,
                passengers=200000.0, co2_emissions=8000.0, co2_per_passenger=0.04
            ),
            FactCountryStat(
                stat_id=4, country_id=2, year_id=2,
                passengers=210000.0, co2_emissions=8200.0, co2_per_passenger=0.039
            ),
            FactCountryStat(
                stat_id=5, country_id=3, year_id=1,
                passengers=150000.0, co2_emissions=6000.0, co2_per_passenger=0.04
            ),
        ]
        for stat in stats:
            db.add(stat)
        
        # Données de test - FactNightTrains
        night_trains = [
            FactNightTrain(
                fact_id=1, route_id=101, night_train="Train de Nuit Paris-Venise",
                country_id=1, year_id=15, operator_id=1
            ),
            FactNightTrain(
                fact_id=2, route_id=102, night_train="NightJet Munich-Rome",
                country_id=2, year_id=15, operator_id=5
            ),
            FactNightTrain(
                fact_id=3, route_id=103, night_train="Trenhotel Barcelone-Milan",
                country_id=3, year_id=15, operator_id=3
            ),
        ]
        for train in night_trains:
            db.add(train)
        
        # Données de test - DashboardMetrics
        dashboard_metrics = [
            DashboardMetric(
                country_name="France", country_code="FR",
                avg_passengers=105000.0, avg_co2_emissions=5100.0,
                avg_co2_per_passenger=0.0485
            ),
            DashboardMetric(
                country_name="Germany", country_code="DE",
                avg_passengers=205000.0, avg_co2_emissions=8100.0,
                avg_co2_per_passenger=0.0395
            ),
        ]
        for metric in dashboard_metrics:
            db.add(metric)
        
        db.commit()
        
        yield
        
        # Teardown : suppression des tables
        Base.metadata.drop_all(bind=engine)

    # ==================== TESTS DES ENDPOINTS OBLIGATOIRES ====================

    def test_get_countries(self):
        """Test GET /api/countries"""
        response = client.get("/api/countries")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 5
        assert data[0]["country_code"] in ["FR", "DE", "IT", "ES", "BE"]
        assert "country_name" in data[0]

    def test_get_countries_with_pagination(self):
        """Test GET /api/countries avec pagination"""
        response = client.get("/api/countries?skip=1&limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_get_country_stats(self):
        """Test GET /api/countries/stats"""
        response = client.get("/api/countries/stats")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert "passengers" in data[0]
        assert "co2_emissions" in data[0]
        assert "country_name" in data[0]

    def test_get_country_stats_with_filters(self):
        """Test GET /api/countries/stats avec filtres"""
        # Filtre par année
        response = client.get("/api/countries/stats?year=2010")
        assert response.status_code == 200
        data = response.json()
        for item in data:
            assert item["year"] == 2010

        # Filtre par pays
        response = client.get("/api/countries/stats?country_code=FR")
        assert response.status_code == 200
        data = response.json()
        for item in data:
            assert item["country_code"] == "FR"

        # Filtre par seuil d'émissions
        response = client.get("/api/countries/stats?min_co2_per_passenger=0.04&max_co2_per_passenger=0.05")
        assert response.status_code == 200

    def test_get_night_trains(self):
        """Test GET /api/night-trains"""
        response = client.get("/api/night-trains")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 3
        assert "night_train" in data[0]
        assert "operator_name" in data[0]

    def test_get_night_trains_with_filters(self):
        """Test GET /api/night-trains avec filtres"""
        # Filtre par pays
        response = client.get("/api/night-trains?country_code=FR")
        assert response.status_code == 200
        data = response.json()
        for item in data:
            assert item["country_code"] == "FR"

        # Filtre par opérateur
        response = client.get("/api/night-trains?operator_name=ÖBB")
        assert response.status_code == 200

        # Filtre par année
        response = client.get("/api/night-trains?year=2024")
        assert response.status_code == 200

    def test_get_dashboard_metrics(self):
        """Test GET /api/dashboard/metrics"""
        response = client.get("/api/dashboard/metrics")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2
        assert "avg_passengers" in data[0]
        assert "avg_co2_emissions" in data[0]

    # ==================== TESTS DES ENDPOINTS D'ANALYSE COMPARATIVE ====================

    def test_train_types_comparison(self):
        """Test GET /api/analysis/train-types-comparison"""
        response = client.get("/api/analysis/train-types-comparison")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2  # Au moins jour et nuit
        train_types = [item["train_type"] for item in data]
        assert "night" in train_types or "day" in train_types

    def test_co2_ranking(self):
        """Test GET /api/statistics/co2-ranking"""
        response = client.get("/api/statistics/co2-ranking")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        if len(data) > 0:
            assert "ranking" in data[0]
            assert "performance" in data[0]
            assert "avg_co2_per_passenger" in data[0]

    def test_co2_ranking_with_limit(self):
        """Test GET /api/statistics/co2-ranking avec limite"""
        response = client.get("/api/statistics/co2-ranking?limit=5")
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 5

    # ==================== TESTS DES ENDPOINTS DE RECHERCHE ====================

    def test_operator_stats(self):
        """Test GET /api/operators/{operator_id}/stats"""
        # Test avec un opérateur existant
        response = client.get("/api/operators/1/stats")
        assert response.status_code == 200
        data = response.json()
        assert data["operator_id"] == 1
        assert "total_trains" in data
        assert "countries_served" in data

        # Test avec un opérateur inexistant
        response = client.get("/api/operators/999/stats")
        assert response.status_code == 404

    def test_operator_stats_with_night_trains(self):
        """Test GET /api/night-trains/by-operator/{operator_id}"""
        response = client.get("/api/night-trains/by-operator/5")  # ÖBB
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_timeline_data(self):
        """Test GET /api/statistics/timeline"""
        response = client.get("/api/statistics/timeline")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert "year" in data[0]
        assert "passengers" in data[0]
        assert "co2_emissions" in data[0]

    # ==================== TESTS DES ENDPOINTS DE MÉTADONNÉES ====================

    def test_metadata_quality(self):
        """Test GET /api/metadata/quality"""
        response = client.get("/api/metadata/quality")
        assert response.status_code == 200
        data = response.json()
        assert "reports" in data or "execution_date" in data or "traceability" in data

    def test_metadata_sources(self):
        """Test GET /api/metadata/sources"""
        response = client.get("/api/metadata/sources")
        assert response.status_code == 200
        data = response.json()
        assert "sources" in data
        assert isinstance(data["sources"], list)

    # ==================== TESTS DES ENDPOINTS POUR TABLEAU DE BORD ====================

    def test_dashboard_kpis(self):
        """Test GET /api/dashboard/kpis"""
        response = client.get("/api/dashboard/kpis")
        assert response.status_code == 200
        data = response.json()
        assert "total_countries" in data
        assert "total_night_trains" in data
        assert "total_operators" in data
        assert "years_covered" in data
        assert isinstance(data["total_countries"], (int, float))
        assert isinstance(data["total_night_trains"], (int, float))

    def test_geographic_coverage(self):
        """Test GET /api/geographic/coverage"""
        response = client.get("/api/geographic/coverage")
        assert response.status_code == 200
        data = response.json()
        assert "total_countries_covered" in data or "coverage_by_country" in data

    # ==================== TESTS DES ENDPOINTS AVANCÉS ====================

    def test_policy_recommendations(self):
        """Test GET /api/analysis/policy-recommendations"""
        response = client.get("/api/analysis/policy-recommendations")
        assert response.status_code == 200
        data = response.json()
        assert "recommendations" in data or isinstance(data, list)

    def test_predictions_trends(self):
        """Test GET /api/predictions/trends (si implémenté)"""
        response = client.get("/api/predictions/trends")
        # Ce test peut échouer si l'endpoint n'est pas implémenté
        if response.status_code != 404:
            assert response.status_code == 200

    def test_export_formats(self):
        """Test GET /api/export/{format} (si implémenté)"""
        formats = ["csv", "json", "excel"]
        for fmt in formats:
            response = client.get(f"/api/export/{fmt}")
            if response.status_code != 404:
                assert response.status_code == 200

    def test_documentation(self):
        """Test GET /api/docs"""
        response = client.get("/api/docs")
        # Peut être redirigé vers /docs
        assert response.status_code in [200, 307]

    # ==================== TESTS DES ENDPOINTS DE L'API OPENAPI ====================

    def test_openapi_json(self):
        """Test GET /api/openapi.json"""
        response = client.get("/api/openapi.json")
        assert response.status_code in [200, 404]

    def test_root_endpoint(self):
        """Test GET /"""
        response = client.get("/")
        assert response.status_code == 200

    # ==================== TESTS DES CAS D'ERREUR ====================

    def test_invalid_country_code(self):
        """Test avec un code pays invalide"""
        response = client.get("/api/countries/stats?country_code=INVALID")
        assert response.status_code == 200  # Doit retourner une liste vide ou 200
        data = response.json()
        assert isinstance(data, list)

    def test_invalid_operator_id(self):
        """Test avec un ID opérateur invalide"""
        response = client.get("/api/operators/999/stats")
        assert response.status_code == 404

    def test_invalid_pagination_parameters(self):
        """Test avec des paramètres de pagination invalides"""
        # skip négatif
        response = client.get("/api/countries?skip=-1")
        assert response.status_code == 422  # Validation error

        # limit trop grand
        response = client.get("/api/countries?limit=1000")
        assert response.status_code == 422  # Validation error

    def test_missing_operator_id(self):
        """Test sans l'ID opérateur requis"""
        response = client.get("/api/operators//stats")
        assert response.status_code == 404

    # ==================== TESTS DE PERFORMANCE DES FILTRES ====================

    def test_filters_combination(self):
        """Test avec combinaison de filtres"""
        response = client.get(
            "/api/countries/stats",
            params={
                "country_code": "FR",
                "year": 2010,
                "min_passengers": 50000,
                "max_passengers": 200000
            }
        )
        assert response.status_code == 200

        response = client.get(
            "/api/night-trains",
            params={
                "country_code": "FR",
                "operator_name": "SNCF",
                "year": 2024
            }
        )
        assert response.status_code == 200

    # ==================== TESTS DE STRUCTURE DES DONNÉES ====================

    def test_data_structure_country_stats(self):
        """Test de la structure des données pour /api/countries/stats"""
        response = client.get("/api/countries/stats?limit=1")
        assert response.status_code == 200
        data = response.json()
        if len(data) > 0:
            item = data[0]
            expected_fields = [
                "passengers", "co2_emissions", "co2_per_passenger",
                "year", "country_name", "country_code"
            ]
            for field in expected_fields:
                assert field in item, f"Champ manquant : {field}"

    def test_data_structure_night_trains(self):
        """Test de la structure des données pour /api/night-trains"""
        response = client.get("/api/night-trains?limit=1")
        assert response.status_code == 200
        data = response.json()
        if len(data) > 0:
            item = data[0]
            expected_fields = [
                "night_train", "country_name", "country_code",
                "operator_name", "year"
            ]
            for field in expected_fields:
                assert field in item, f"Champ manquant : {field}"

    def test_data_structure_dashboard_kpis(self):
        """Test de la structure des données pour /api/dashboard/kpis"""
        response = client.get("/api/dashboard/kpis")
        assert response.status_code == 200
        data = response.json()
        expected_fields = [
            "total_countries", "total_night_trains", "total_operators",
            "years_covered", "avg_co2_per_passenger"
        ]
        for field in expected_fields:
            assert field in data, f"Champ manquant : {field}"

    # ==================== TESTS DES ENDPOINTS NON IMPLÉMENTÉS ====================

    def test_unimplemented_endpoints_return_404(self):
        """Test que les endpoints non implémentés retournent 404"""
        endpoints = [
            "/api/nonexistent",
            "/api/countries/nonexistent",
            "/api/invalid/endpoint/with/many/segments"
        ]
        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.status_code == 404


if __name__ == "__main__":
    pytest.main(["-v", __file__])