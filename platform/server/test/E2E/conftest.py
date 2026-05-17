import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE_DIR))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.dependencies import get_db
from app.models import Base, DimCountries, DimYears, DimOperators, FactsCountryStats, FactsNightTrains

SQLALCHEMY_DATABASE_URL = 'sqlite:///:memory:'
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={'check_same_thread': False}, poolclass=StaticPool)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope='function')
def db_session():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope='function')
def client():
    return TestClient(app)

@pytest.fixture(scope='function')
def sample_data(db_session):
    years = []
    for y in range(2010, 2025):
        year_obj = DimYears(year_id=y-2009, year=y, is_after_2010=(y >= 2010))
        years.append(year_obj)
        db_session.add(year_obj)

    countries = [
        DimCountries(country_id=1, country_code='FR', country_name='France'),
        DimCountries(country_id=2, country_code='DE', country_name='Germany'),
        DimCountries(country_id=3, country_code='IT', country_name='Italy'),
        DimCountries(country_id=4, country_code='ES', country_name='Spain'),
        DimCountries(country_id=5, country_code='BE', country_name='Belgium'),
    ]
    for c in countries:
        db_session.add(c)

    operators = [
        DimOperators(operator_id=1, operator_name='SNCF'),
        DimOperators(operator_id=2, operator_name='DB'),
        DimOperators(operator_id=3, operator_name='Trenitalia'),
        DimOperators(operator_id=4, operator_name='Renfe'),
        DimOperators(operator_id=5, operator_name='OBB'),
    ]
    for o in operators:
        db_session.add(o)

    stats = [
        FactsCountryStats(stats_id=1, country_id=1, year_id=1, passengers=100000.0, co2_emissions=5000.0, co2_per_passenger=0.05),
        FactsCountryStats(stats_id=2, country_id=1, year_id=2, passengers=110000.0, co2_emissions=5200.0, co2_per_passenger=0.047),
        FactsCountryStats(stats_id=3, country_id=2, year_id=1, passengers=200000.0, co2_emissions=8000.0, co2_per_passenger=0.04),
    ]
    for s in stats:
        db_session.add(s)

    night_trains = []
    for i in range(1, 26):
        train = FactsNightTrains(
            fact_id=i,
            country_id=(i % 5) + 1,
            operator_id=(i % 5) + 1,
            year_id=1,
            route_id=i,
            night_train=f'Train-{i}',
            is_night=(i % 2 == 0),
        )
        night_trains.append(train)
        db_session.add(train)

    db_session.commit()
    return {'years': years, 'countries': countries, 'operators': operators, 'stats': stats, 'night_trains': night_trains}
