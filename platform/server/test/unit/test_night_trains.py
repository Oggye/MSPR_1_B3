# Importer les modules nécessaires pour les tests unitaires
from types import SimpleNamespace
from unittest.mock import MagicMock
from app.routers.night_trains import _to_response, _apply_pagination


# Tests unitaires pour les fonctions utilitaires de night_trains.py
def test_to_response_returns_valid_object():
    """
    Vérifie que _to_response construit correctement
    une réponse API.
    """

    train = SimpleNamespace(
        fact_id=1,
        route_id="FR001",
        night_train="Paris → Nice",
        is_night=True,
        distance_km=1200,
        duration_min=720
    )

    response = _to_response(
        train,
        country_name="France",
        country_code="FR",
        operator_name="SNCF",
        year=2024
    )

    assert response.fact_id == 1
    assert response.route_id == "FR001"
    assert response.night_train == "Paris → Nice"
    assert response.country_name == "France"
    assert response.country_code == "FR"
    assert response.operator_name == "SNCF"
    assert response.year == 2024
    assert response.train_type == "night"


# Tests pour vérifier que les fonctions de pagination fonctionnent correctement
def test_apply_pagination_with_limit():
    """
    Vérifie que offset et limit sont appliqués.
    """

    query = MagicMock()
    query.offset.return_value = query
    query.limit.return_value = query

    result = _apply_pagination(
        query,
        skip=10,
        limit=5
    )

    query.offset.assert_called_once_with(10)
    query.limit.assert_called_once_with(5)

    assert result == query


def test_apply_pagination_without_limit():
    """
    Vérifie que limit n'est pas appelé
    quand limit=None.
    """

    query = MagicMock()
    query.offset.return_value = query

    result = _apply_pagination(
        query,
        skip=5,
        limit=None
    )

    query.offset.assert_called_once_with(5)
    query.limit.assert_not_called()

    assert result == query


# Test pour vérifier que les trains de jour ont bien train_type='day'
def test_to_response_day_train():
    """
    Vérifie qu'un train de jour retourne train_type='day'
    """

    train = SimpleNamespace(
        fact_id=2,
        route_id="FR002",
        night_train="Paris → Lyon",
        is_night=False,
        distance_km=500,
        duration_min=120
    )

    response = _to_response(
        train,
        country_name="France",
        country_code="FR",
        operator_name="SNCF",
        year=2024
    )

    assert response.train_type == "day"


# Test pour vérifier que les valeurs None sont correctement gérées
def test_to_response_handles_none_values():
    """
    Vérifie que les valeurs None sont correctement gérées.
    """

    train = SimpleNamespace(
        fact_id=3,
        route_id="FR003",
        night_train="Test Train",
        is_night=True,
        distance_km=None,
        duration_min=None
    )

    response = _to_response(
        train,
        country_name="France",
        country_code="FR",
        operator_name="SNCF",
        year=2024
    )

    assert response.distance_km is None
    assert response.duration_min is None