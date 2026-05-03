# server/app/routers/analysis.py
from fastapi import APIRouter, Depends
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
    Groupé par is_night directement sur facts_night_trains,
    sans jointure avec facts_country_stats pour éviter les duplications.
    """
    REFERENCE_CO2 = 0.05

    results = db.query(
        FactsNightTrains.is_night,
        func.count(FactsNightTrains.fact_id).label("nb_trains"),
        func.avg(FactsNightTrains.distance_km).label("avg_distance"),
        func.avg(FactsNightTrains.duration_min).label("avg_duration"),
    ).group_by(
        FactsNightTrains.is_night
    ).all()

    # Stats CO2/passagers depuis facts_country_stats (global, pas de jointure croisée)
    co2_stats = db.query(
        func.avg(FactsCountryStats.co2_per_passenger).label("avg_co2"),
        func.avg(FactsCountryStats.passengers).label("avg_passengers"),
    ).first()

    avg_co2 = float(co2_stats.avg_co2 or 0)
    avg_passengers = float(co2_stats.avg_passengers or 0)

    comparisons = []
    for row in results:
        train_type = "night" if row.is_night else "day"
        avg_distance = float(row.avg_distance or 0)
        # Score d'efficacité basé sur la distance moyenne normalisée
        efficiency = min(100, (avg_distance / 1000) * 100) if avg_distance > 0 else 0

        comparisons.append(TrainTypeComparison(
            train_type=train_type,
            avg_passengers=avg_passengers,
            avg_co2_per_passenger=avg_co2,
            efficiency_score=efficiency
        ))

    # Si pas de données, retourner des valeurs neutres
    if not comparisons:
        return [
            TrainTypeComparison(train_type="night", avg_passengers=0, avg_co2_per_passenger=0, efficiency_score=0),
            TrainTypeComparison(train_type="day", avg_passengers=0, avg_co2_per_passenger=0, efficiency_score=0),
        ]

    return comparisons


@router.get("/api/analysis/policy-recommendations")
def get_policy_recommendations(db: Session = Depends(get_db)):
    """
    Génère des recommandations politiques basées sur les données.
    Tables: facts_country_stats, facts_night_trains, dim_countries
    """
    recommendations = []

    # Top 5 des pays avec le plus de CO2
    top_emitters = db.query(
        DimCountries.country_name,
        func.avg(FactsCountryStats.co2_per_passenger).label("avg_co2")
    ).join(
        FactsCountryStats,
        DimCountries.country_id == FactsCountryStats.country_id
    ).group_by(
        DimCountries.country_id, DimCountries.country_name
    ).order_by(
        func.avg(FactsCountryStats.co2_per_passenger).desc()
    ).limit(5).all()

    if top_emitters:
        countries_list = [c.country_name for c in top_emitters]
        avg_co2_values = [float(c.avg_co2) for c in top_emitters]
        recommendations.append({
            "title": "Pays prioritaires pour la modernisation",
            "description": f"Ces pays ont les émissions les plus élevées: {', '.join(countries_list)}",
            "suggestion": "Accorder des subventions européennes pour le renouvellement du matériel roulant",
            "avg_co2_per_passenger": avg_co2_values,
        })

    # Pays avec faible CO2 et beaucoup de trains
    success = db.query(
        DimCountries.country_name,
        func.avg(FactsCountryStats.co2_per_passenger).label("avg_co2"),
        func.count(FactsNightTrains.fact_id).label("train_count")
    ).join(
        FactsCountryStats,
        DimCountries.country_id == FactsCountryStats.country_id
    ).outerjoin(
        FactsNightTrains,
        DimCountries.country_id == FactsNightTrains.country_id
    ).group_by(
        DimCountries.country_id, DimCountries.country_name
    ).having(
        func.avg(FactsCountryStats.co2_per_passenger) < 0.03
    ).order_by(
        func.count(FactsNightTrains.fact_id).desc()
    ).first()

    if success:
        recommendations.append({
            "title": "Bonnes pratiques",
            "description": f"{success[0]} combine faible CO2 ({float(success[1]):.3f}) et {success[2]} trains",
            "suggestion": "Étudier et reproduire cette stratégie"
        })

    return {"recommendations": recommendations}