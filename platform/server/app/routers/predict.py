# app/routers/predict.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import sys
from pathlib import Path

# Chemin vers la racine du projet pour accéder aux modèles IA
sys.path.append(str(Path(__file__).resolve().parents[4]))

from ia.src.ml.predict import predict as ml_predict

router = APIRouter()

class PredictionInput(BaseModel):
    country: str
    year: int
    co2_emissions: float
    co2_per_passenger: float
    co2_lag1: float
    passengers_lag1: float
    passengers_lag2: float

@router.post("/api/predict/classification")
def predict_classification(data: PredictionInput):
    """Prédit si un pays est en déclin ferroviaire."""
    try:
        result = ml_predict(
            axis="classification",
            country=data.country,
            year=data.year,
            co2_emissions=data.co2_emissions,
            co2_per_passenger=data.co2_per_passenger,
            co2_lag1=data.co2_lag1,
            passengers_lag1=data.passengers_lag1,
            passengers_lag2=data.passengers_lag2,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/predict/regression")
def predict_regression(data: PredictionInput):
    """Prédit le volume de passagers ferroviaires."""
    try:
        result = ml_predict(
            axis="regression",
            country=data.country,
            year=data.year,
            co2_emissions=data.co2_emissions,
            co2_per_passenger=data.co2_per_passenger,
            co2_lag1=data.co2_lag1,
            passengers_lag1=data.passengers_lag1,
            passengers_lag2=data.passengers_lag2,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))