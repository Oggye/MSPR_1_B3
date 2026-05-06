"""
Configuration partagée pour les tests unitaires de l'API ObRail 
"""

import sys
import os

# Ajouter les chemins pour accéder à app/ depuis test/unitest_api/
test_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
server_dir = os.path.dirname(test_dir)
sys.path.insert(0, server_dir)

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.dependencies import get_db
from app.models import Base
from app.models import (
    DimCountries, DimYears, DimOperators,
    FactsCountryStats, FactsNightTrains, DashboardMetrics, OperatorDashboard
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

@pytest.fixture(scope="session")
def test_engine():
    """Moteur de base de données de test"""
    return engine

@pytest.fixture(scope="function")
def db_session(test_engine):
    """Session de base de données pour chaque test"""
    Base.metadata.create_all(bind=test_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)

@pytest.fixture(scope="function")
def client():
    """Client de test FastAPI"""
    return TestClient(app)

@pytest.fixture(scope="function")
def sample_data(db_session):
    """Données d'exemple pour les tests"""
    # Création des années
    years = []
    for year in range(2010, 2025):
        year_obj = DimYears(year_id=year-2009, year=year, is_after_2010=(year >= 2010))
        years.append(year_obj)
        db_session.add(year_obj)

    # Création des pays
    countries = [
        DimCountries(country_id=1, country_code="FR", country_name="France"),
        DimCountries(country_id=2, country_code="DE", country_name="Germany"),
        DimCountries(country_id=3, country_code="IT", country_name="Italy"),
        DimCountries(country_id=4, country_code="ES", country_name="Spain"),
        DimCountries(country_id=5, country_code="BE", country_name="Belgium"),
    ]
    for country in countries:
        db_session.add(country)

    # Création des opérateurs
    operators = [
        DimOperators(operator_id=1, operator_name="SNCF"),
        DimOperators(operator_id=2, operator_name="DB"),
        DimOperators(operator_id=3, operator_name="Trenitalia"),
        DimOperators(operator_id=4, operator_name="Renfe"),
        DimOperators(operator_id=5, operator_name="ÖBB"),
    ]
    for operator in operators:
        db_session.add(operator)

    # Création des statistiques pays
    stats = [
        FactsCountryStats(
            stat_id=1, country_id=1, year_id=1,
            passengers=100000.0, co2_emissions=5000.0, co2_per_passenger=0.05
        ),
        FactsCountryStats(
            stat_id=2, country_id=1, year_id=2,
            passengers=110000.0, co2_emissions=5200.0, co2_per_passenger=0.047
        ),
        FactsCountryStats(
            stat_id=3, country_id=2, year_id=1,
            passengers=200000.0, co2_emissions=8000.0, co2_per_passenger=0.04
        ),
    ]
    for stat in stats:
        db_session.add(stat)

    # Création des trains de nuit (exemple)
    night_trains = [
        FactsNightTrains(
            fact_id=1, country_id=1, operator_id=1, year_id=1,
            route_id="FR-DE-001", night_train="Paris-Berlin", is_night=True, distance_km=1000.0, duration_min=480.0
        ),
        FactsNightTrains(
            fact_id=2, country_id=2, operator_id=2, year_id=1,
            route_id="DE-AT-001", night_train="Berlin-Munich", is_night=True, distance_km=600.0, duration_min=300.0
        ),
    ]
    for train in night_trains:
        db_session.add(train)

    # Création des données operator_dashboard (vue)
    operator_dashboards = [
        OperatorDashboard(
            operator_id=1, operator_name="SNCF",
            nb_trains=1, nb_trains_nuit=1, nb_trains_jour=0,
            distance_totale_km=1000.0, duree_moyenne_min=480.0
        ),
        OperatorDashboard(
            operator_id=2, operator_name="DB",
            nb_trains=1, nb_trains_nuit=1, nb_trains_jour=0,
            distance_totale_km=600.0, duree_moyenne_min=300.0
        ),
    ]
    for dashboard in operator_dashboards:
        db_session.add(dashboard)

    db_session.commit()

    return {
        "years": years,
        "countries": countries,
        "operators": operators,
        "stats": stats,
        "night_trains": night_trains,
        "operator_dashboards": operator_dashboards
    }
