# server\app\routers\statistics.py
# ROUTER: Endpoints d'analyse statistique avancée
# ===============================================
# Rôle: Fournir des analyses temporelles et comparatives
#       sur les indicateurs clés du transport ferroviaire.

# Tables utilisées:
# - facts_country_stats : Données statistiques historiques
# - dim_years : Dimension temporelle
# - dim_countries : Contexte géographique

# Endpoints implémentés:
# 1. GET /api/statistics/timeline - Évolution temporelle des indicateurs
# 2. GET /api/statistics/co2-ranking - Classement des pays par performance CO2

# Résultats attendus:
# - Identification des tendances 2010-2024
# - Détection des meilleures pratiques nationales
# - Données pour les modèles prédictifs

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from app.dependencies import get_db
from app.models import DashboardMetrics, FactsCountryStats, FactsNightTrains, DimYears
from app.schemas.statistics import TimelineData, CO2RankingItem

router = APIRouter()

@router.get("/api/statistics/timeline", response_model=List[TimelineData])
def get_timeline_data(db: Session = Depends(get_db)):
    """
    Récupère les données d'évolution temporelle pour les graphiques.
    """
    # Récupérer toutes les statistiques
    stats_query = db.query(
        DimYears.year,
        func.sum(FactsCountryStats.passengers).label("passengers"),
        func.sum(FactsCountryStats.co2_emissions).label("co2_emissions"),
        func.avg(FactsCountryStats.co2_per_passenger).label("co2_per_passenger")
    ).join(
        DimYears, FactsCountryStats.year_id == DimYears.year_id
    ).group_by(
        DimYears.year_id, DimYears.year
    ).order_by(
        DimYears.year
    ).all()
    
    # Récupérer les trains de nuit par année
    night_trains_query = db.query(
        DimYears.year,
        func.count(FactsNightTrains.fact_id).label("night_trains_count")
    ).join(
        DimYears, FactsNightTrains.year_id == DimYears.year_id
    ).group_by(
        DimYears.year_id, DimYears.year
    ).order_by(
        DimYears.year
    ).all()

    night_trains_dict = {}
    for year, count in night_trains_query:
        night_trains_dict[year] = count
    
    timeline_data = []
    for year, passengers, co2, co2_per_passenger in stats_query:
        timeline_data.append(
            TimelineData(
                year=year,
                passengers=float(passengers or 0),
                co2_emissions=float(co2 or 0),
                co2_per_passenger=float(co2_per_passenger or 0),
                night_trains_count=night_trains_dict.get(year, 0)
            )
        )
    
    return timeline_data

@router.get("/api/statistics/co2-ranking", response_model=List[CO2RankingItem])
def get_co2_ranking(
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, le=50)
):
    """
    Classe les pays par performance CO2.
    """
    # Récupère les données de la vue dashboard_metrics
    ranking_data = db.query(
        DashboardMetrics.country_name,
        DashboardMetrics.country_code,
        DashboardMetrics.avg_co2_per_passenger
    ).order_by(
        DashboardMetrics.avg_co2_per_passenger.asc()
    ).limit(limit).all()
    
    ranking_items = []
    for i, (country_name, country_code, avg_co2) in enumerate(ranking_data, 1):
        # Détermine la performance
        if avg_co2 < 0.05:
            performance = "good"
        elif avg_co2 < 0.1:
            performance = "medium"
        else:
            performance = "bad"
        
        ranking_items.append(
            CO2RankingItem(
                country_name=country_name,
                country_code=country_code,
                avg_co2_per_passenger=float(avg_co2),
                ranking=i,
                performance=performance
            )
        )
    
    return ranking_items