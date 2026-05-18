# app/schemas/base.py
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    """Schema de base avec configuration commune."""

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={datetime: lambda v: v.isoformat()},
    )


class PaginatedResponse(BaseModel):
    """Schema pour les reponses paginees."""

    items: list
    total: int
    page: int
    page_size: int
    total_pages: int
