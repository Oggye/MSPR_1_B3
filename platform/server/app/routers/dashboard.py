# server\app\routers\dashboard.py
# ROUTER: Endpoints pour le tableau de bord ObRail
# ================================================
# Rôle: Alimenter le dashboard interactif avec des indicateurs synthétiques
#       et des métriques agrégées pour la prise de décision.

# Tables/vues utilisées:
# - dashboard_metrics : Vue SQL des indicateurs agrégés
# - facts_country_stats : Données sources
# - dim_countries : Contexte géographique

# Endpoints implémentés:
# 1. GET /api/dashboard/metrics - Métriques pour visualisations
# 2. GET /api/dashboard/kpis - Indicateurs clés de performance

# Résultats attendus:
# - Dashboard temps réel pour décideurs politiques
# - Monitoring de la mobilité durable européenne
# - Support visuel pour les présentations institutionnelles

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from app.dependencies import get_db
from app.models import DashboardMetrics, FactsCountryStats, FactsNightTrains, DimCountries, DimOperators, DimYears
from app.schemas.statistics import DashboardMetricsResponse, KPIsResponse


router = APIRouter()

@router.get("/api/dashboard/metrics", response_model=List[DashboardMetricsResponse])
def get_dashboard_metrics(db: Session = Depends(get_db)):
    """
    Récupère les métriques agrégées pour le dashboard.
    """
    metrics = db.query(DashboardMetrics).all()

    return metrics

@router.get("/api/dashboard/kpis", response_model=KPIsResponse)
def get_dashboard_kpis(db: Session = Depends(get_db)):
    """
    Récupère les indicateurs clés de performance pour le dashboard.
    """
    # Comptages
    total_countries = len(db.query(DimCountries).all())
    total_night_trains = len(db.query(FactsNightTrains).all())
    total_operators = len(db.query(DimOperators).all())
    
    # Période couverte
    years = db.query(DimYears.year).order_by(DimYears.year).all()
    if len(years) > 0:
        min_year = years[0][0]      # La première de la liste
        max_year = years[-1][0]     # La dernière de la liste
        years_covered = f"{min_year}-{max_year}"
    else:
        years_covered = "Pas de données"
        print("Aucune année trouvée")
    
    # Agrégation des statistiques
    stats = db.query(FactsCountryStats).all()
    
    total_co2_per_passenger = 0
    total_passengers = 0
    total_co2_emissions = 0
    nb_stats = 0
    
    for stat in stats:
        total_co2_per_passenger += float(stat.co2_per_passenger)
        total_passengers += float(stat.passengers)
        total_co2_emissions += float(stat.co2_emissions)
        nb_stats += 1
    
    # Moyenne du CO2 par passager
    if nb_stats > 0:
        avg_co2_per_passenger = total_co2_per_passenger / nb_stats
    else:
        avg_co2_per_passenger = 0
    
    return KPIsResponse(
        total_countries=total_countries,
        total_night_trains=total_night_trains,
        total_operators=total_operators,
        years_covered=years_covered,
        avg_co2_per_passenger=avg_co2_per_passenger,
        total_passengers=total_passengers,
        total_co2_emissions=total_co2_emissions
    )