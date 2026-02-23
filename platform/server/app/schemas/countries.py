# app/schemas/countries.py
from pydantic import BaseModel
from typing import Optional
from .base import BaseSchema


class CountryBase(BaseSchema):
    country_code: str
    country_name: str


class CountryCreate(CountryBase):
    pass


class CountryResponse(CountryBase):
    country_id: int


class CountryStatsBase(BaseSchema):
    passengers: float
    co2_emissions: float
    co2_per_passenger: float
    year: Optional[int] = None


class CountryStatsResponse(CountryStatsBase):
    stats_id: int
    country_name: str
    country_code: str
    country_id: int
    year_id: int


class CountryStatsFilter(BaseModel):
    country_code: Optional[str] = None
    year: Optional[int] = None
    min_passengers: Optional[float] = None
    max_passengers: Optional[float] = None
    min_co2_per_passenger: Optional[float] = None
    max_co2_per_passenger: Optional[float] = None