# app/main.py
from fastapi import FastAPI
from app.routers import countries, night_trains, dashboard, analysis, operators, metadata, statistics

app = FastAPI(
    title="ObRail API - Observatoire Européen du Rail",
    description="""
    API de données ferroviaires européennes
    
    Cette API fournit des données sur les transports ferroviaires en Europe, incluant:
    
    Statistiques par pays : Passagers, émissions CO2, indicateurs de performance
    Trains de nuit : Catalogue des liaisons nocturnes européennes
    Analyses comparatives : Impact environnemental, classements
    Projections : Tendances et prévisions
    Recommandations politiques : Suggestions basées sur les données
    """,
    version="1.0.0",
    docs_url="/api/docs",  # Documentation Swagger UI
    openapi_url="/api/openapi.json",  # Documentation OpenAPI

)

# Tous les routeurs
app.include_router(countries.router)
app.include_router(night_trains.router)
app.include_router(dashboard.router)
app.include_router(analysis.router)
app.include_router(operators.router)
app.include_router(metadata.router)
app.include_router(statistics.router)

@app.get("/")
def read_root():
    return {"message": "API"}

