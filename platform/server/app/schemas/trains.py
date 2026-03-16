# app/schemas/trains.py
from pydantic import BaseModel
from typing import Optional
from .base import BaseSchema


class NightTrainBase(BaseSchema):
    """Schéma de base pour un train de nuit."""
    route_id: int
    night_train: str


class NightTrainCreate(NightTrainBase):
    """Schéma pour la création d'un nouvel enregistrement de train de nuit."""
    country_id: int
    year_id: int
    operator_id: int


class NightTrainResponse(NightTrainBase):
    """Schéma de réponse pour un train de nuit."""
    fact_id: int
    country_name: str
    country_code: str
    operator_name: str
    year: int
    is_night: bool


class NightTrainFilter(BaseModel):
    """Schéma pour filtrer les requêtes de trains de nuit."""
    country_code: Optional[str] = None
    operator_id: Optional[int] = None
    year: Optional[int] = None
    operator_name: Optional[str] = None
    is_night: Optional[bool] = None