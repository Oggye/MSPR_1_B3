# server\app\routers\analysis.py
# ROUTER: Endpoints d'analyse avancée et recommandations
# =======================================================
# Rôle: Produire des analyses comparatives et des recommandations
#       basées sur les données pour soutenir les politiques publiques.

# Tables utilisées:
# - facts_night_trains + facts_country_stats : Données combinées
# - dim_countries : Contexte national
# - dim_operators : Acteurs ferroviaires

# Endpoints implémentés:
# 1. GET /api/analysis/train-types-comparison - Comparaison jour/nuit
# 2. GET /api/analysis/policy-recommendations - Recommandations politiques

# Résultats attendus:
# - Preuves data-driven pour le Green Deal européen
# - Arguments pour le développement du ferroviaire nocturne
# - Base pour les décisions d'investissement

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from app.dependencies import get_db
from app.models import FactsCountryStats, FactsNightTrains, DimCountries
from app.schemas.statistics import TrainTypeComparison

router = APIRouter()

@router.get("/api/analysis/train-types-comparison")
def compare_train_types(db: Session = Depends(get_db)):
    """
    Compare les indicateurs entre trains de jour et trains de nuit.
    Tables: facts_night_trains + données statistiques extrapolées
    """
    # Données pour les trains de nuit
    night_stats = db.query(
        func.avg(FactsCountryStats.passengers).label("avg_passengers"),
        func.avg(FactsCountryStats.co2_per_passenger).label("avg_co2")
    ).join(
        FactsNightTrains,
        FactsCountryStats.country_id == FactsNightTrains.country_id
    ).first()
    
    # Récupère les pays qui ont des trains de nuit
    night_countries = db.query(FactsNightTrains.country_id).distinct().subquery()
    
    # Moyennes des trains de jour 
    day_stats = db.query(
        func.avg(FactsCountryStats.passengers).label("avg_passengers"),
        func.avg(FactsCountryStats.co2_per_passenger).label("avg_co2")
    ).filter(
        ~FactsCountryStats.country_id.in_(night_countries)
    ).first()
    
    night_avg_co2 = 0
    night_avg_passengers = 0
    day_avg_co2 = 0
    day_avg_passengers = 0
    
    if night_stats and night_stats.avg_co2:
        night_avg_co2 = float(night_stats.avg_co2)
        night_avg_passengers = float(night_stats.avg_passengers)
    
    if day_stats and day_stats.avg_co2:
        day_avg_co2 = float(day_stats.avg_co2)
        day_avg_passengers = float(day_stats.avg_passengers)
    
    # Score d'efficacité
    REFERENCE_CO2 = 0.05
    
    night_efficiency = 0
    if night_avg_co2 > 0:
        night_efficiency = min(100, (REFERENCE_CO2 / night_avg_co2) * 100)
    
    day_efficiency = 0
    if day_avg_co2 > 10:
        day_avg_co2 = day_avg_co2 / 1000 
        day_efficiency = min(100, (REFERENCE_CO2 / day_avg_co2) * 100)
    
    return [
        TrainTypeComparison(
            train_type="night",
            avg_passengers=night_avg_passengers,
            avg_co2_per_passenger=night_avg_co2,
            efficiency_score=night_efficiency
        ),
        TrainTypeComparison(
            train_type="day",
            avg_passengers=day_avg_passengers,
            avg_co2_per_passenger=day_avg_co2,
            efficiency_score=day_efficiency
        )
    ]

@router.get("/api/analysis/policy-recommendations")
def get_policy_recommendations(db: Session = Depends(get_db)):
    """
    Génère des recommandations politiques basées sur les données.
    """
    recommendations = []
    
    # Top 5 des pays avec le plus de CO2
    top_emitters = db.query(
        DimCountries.country_name,
        func.avg(FactsCountryStats.co2_per_passenger).label("avg_co2")
    ).join(
        FactsCountryStats
    ).group_by(
        DimCountries.country_id
    ).order_by(
        func.avg(FactsCountryStats.co2_per_passenger).desc()
    ).limit(5).all()
        
    if top_emitters:
        # Liste avec juste les noms des pays et de leurs valeurs CO2 associée
        countries_list = []
        avg_co2_values = []
        for c in top_emitters:
            countries_list.append(c.country_name)
            avg_co2_values.append(float(c.avg_co2))

        recommendations.append({
            "title": "Pays prioritaires pour la modernisation",
            "description": f"Ces pays ont les émissions les plus élevées: {', '.join(countries_list)}",
            "suggestion": "Accorder des subventions européennes pour le renouvellement du matériel roulant",
            "avg_co2_per_passenger": avg_co2_values,
        })
        
    # Pays avec succès (CO2 bas et trains de nuit)
    success = db.query(
        DimCountries.country_name,
        func.avg(FactsCountryStats.co2_per_passenger).label("avg_co2"),
        func.count(FactsNightTrains.fact_id).label("train_count")
    ).join(
        FactsCountryStats
    ).outerjoin(
        FactsNightTrains
    ).group_by(
        DimCountries.country_id
    ).having(
        func.avg(FactsCountryStats.co2_per_passenger) < 0.03
    ).order_by(
        func.count(FactsNightTrains.fact_id).desc()
    ).first()
        
    if success:
        recommendations.append({
            "title": "Bonnes pratiques",
            "description": f"{success[0]} combine faible CO2 ({success[1]:.3f}) et {success[2]} trains de nuit",
            "suggestion": "Étudier et reproduire cette stratégie"
        })
    
    return {"recommendations": recommendations}