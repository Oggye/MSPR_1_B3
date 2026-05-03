# app/schemas/operators.py
from pydantic import BaseModel
from typing import List, Optional
from .base import BaseSchema


class OperatorResponse(BaseSchema):
    """Schéma de réponse pour un opérateur ferroviaire."""
    operator_id: int
    operator_name: str


class OperatorRanking(BaseSchema):
    """Schéma de statistiques détaillées pour un opérateur."""
    operator_id: int
    operator_name: str
    total_trains: int
    night_trains: int
    day_trains: int
    distance_totale_km: float
    duree_moyenne_min: float
    countries_served: List[str]
    countries_count: int