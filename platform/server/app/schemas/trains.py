# app/schemas/trains.py
from pydantic import BaseModel
from typing import Optional
from .base import BaseSchema


class NightTrainBase(BaseSchema):
    route_id: int
    night_train: str


class NightTrainCreate(NightTrainBase):
    country_id: int
    year_id: int
    operator_id: int


class NightTrainResponse(NightTrainBase):
    fact_id: int
    country_name: str
    country_code: str
    operator_name: str
    year: int


class NightTrainFilter(BaseModel):
    country_code: Optional[str] = None
    operator_id: Optional[int] = None
    year: Optional[int] = None
    operator_name: Optional[str] = None