# app/schemas/statistics.py
from pydantic import BaseModel
from typing import List, Optional
from .base import BaseSchema


class DashboardMetricsResponse(BaseSchema):
    """Schéma de réponse pour les métriques agrégées du dashboard."""
    country_name: str
    country_code: str
    avg_passengers: float
    avg_co2_emissions: float
    avg_co2_per_passenger: float


class KPIsResponse(BaseSchema):
    """Schéma de réponse pour les indicateurs clés de performance (KPI)."""
    total_countries: int
    total_night_trains: int
    total_operators: int
    years_covered: str
    avg_co2_per_passenger: float
    total_passengers: float
    total_co2_emissions: float


class TimelineData(BaseSchema):
    """Schéma pour les données d'évolution temporelle."""
    year: int
    passengers: Optional[float] = None
    co2_emissions: Optional[float] = None
    co2_per_passenger: Optional[float] = None
    night_trains_count: Optional[int] = None


class CO2RankingItem(BaseSchema):
    """Schéma pour le classement des pays par performance CO2."""
    country_name: str
    country_code: str
    avg_co2_per_passenger: float
    ranking: int
    performance: str  # "good", "medium", "bad"


class TrainTypeComparison(BaseSchema):
    """Schéma pour la comparaison entre trains de jour et de nuit."""
    train_type: str  # "night", "day" (à extrapoler)
    avg_passengers: float
    avg_co2_per_passenger: float
    efficiency_score: float