# app/schemas/base.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class BaseSchema(BaseModel):
    """Schéma de base avec configuration commune"""
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class PaginatedResponse(BaseModel):
    """Schéma pour les réponses paginées"""
    items: list
    total: int
    page: int
    page_size: int
    total_pages: int