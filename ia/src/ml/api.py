from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from ia.src.ml.predict import predict

app = FastAPI(
    title="ObRail Europe — API de prédiction",
    description="Prédiction de la fréquentation ferroviaire et détection des pays en déclin",
    version="1.0.0"
)

class PredictionInput(BaseModel):
    country: str
    year: int
    co2_emissions: float
    co2_per_passenger: float
    co2_lag1: float
    passengers_lag1: float
    passengers_lag2: float

@app.get("/")
def root():
    return {"message": "ObRail Europe API", "status": "ok"}

@app.post("/predict/classification")
def predict_classification(data: PredictionInput):
    try:
        result = predict(
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

@app.post("/predict/regression")
def predict_regression(data: PredictionInput):
    try:
        result = predict(
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

@app.get("/health")
def health():
    return {"status": "healthy"}