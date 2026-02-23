# app/schemas/operators.py
from pydantic import BaseModel
from typing import List
from datetime import datetime
from .base import BaseSchema


class OperatorResponse(BaseSchema):
    operator_id: int
    operator_name: str


class OperatorRanking(BaseSchema):
    operator_id: int
    operator_name: str
    total_trains: int
    countries_served: List[str]
    countries_count: int