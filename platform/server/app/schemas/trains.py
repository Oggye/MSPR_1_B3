# app/schemas/trains.py
from pydantic import BaseModel
from typing import Optional
from .base import BaseSchema


class NightTrainBase(BaseSchema):
    """Schéma de base pour un train."""
    route_id: str          # corrigé : str au lieu de int
    night_train: str


class NightTrainCreate(NightTrainBase):
    """Schéma pour la création d'un enregistrement."""
    country_id: int
    year_id: int
    operator_id: int


class NightTrainResponse(NightTrainBase):
    """Schéma de réponse pour un train."""
    fact_id: int
    country_name: str
    country_code: str
    operator_name: str
    year: int
    is_night: bool
    distance_km: Optional[float] = None   # ajouté
    duration_min: Optional[float] = None  # ajouté
    train_type: Optional[str] = None      # "night" ou "day", calculé dans la route


class NightTrainFilter(BaseModel):
    """Schéma pour filtrer les requêtes de trains."""
    country_code: Optional[str] = None
    operator_id: Optional[int] = None
    year: Optional[int] = None
    operator_name: Optional[str] = None
    is_night: Optional[bool] = None


class NightTrainSummary(BaseModel):
    """Schéma de réponse pour le résumé des trains."""
    total_trains: int
    total_night_trains: int
    total_day_trains: int