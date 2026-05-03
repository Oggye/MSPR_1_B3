# server/app/routers/operators.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from app.dependencies import get_db
from app.models import DimOperators, FactsNightTrains, DimCountries, OperatorDashboard
from app.schemas.operators import OperatorResponse, OperatorRanking

router = APIRouter()


@router.get("/api/operators", response_model=List[OperatorResponse])
def get_operators(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500)
):
    """Récupère la liste des opérateurs ferroviaires."""
    operators = db.query(DimOperators).offset(skip).limit(limit).all()
    return [
        OperatorResponse(
            operator_id=op.operator_id,
            operator_name=op.operator_name
        )
        for op in operators
    ]


@router.get("/api/operators/{operator_id}/stats", response_model=OperatorRanking)
def get_operator_stats(
    operator_id: int,
    db: Session = Depends(get_db)
):
    """
    Statistiques détaillées par opérateur.
    Utilise la vue operator_dashboard + dim_countries pour les pays desservis.
    """
    # Récupération depuis la vue operator_dashboard
    dashboard = db.query(OperatorDashboard).filter(
        OperatorDashboard.operator_id == operator_id
    ).first()

    if not dashboard:
        raise HTTPException(status_code=404, detail="Opérateur non trouvé")

    # Pays desservis par cet opérateur
    countries = db.query(DimCountries).join(
        FactsNightTrains,
        DimCountries.country_id == FactsNightTrains.country_id
    ).filter(
        FactsNightTrains.operator_id == operator_id
    ).distinct().all()

    return OperatorRanking(
        operator_id=dashboard.operator_id,
        operator_name=dashboard.operator_name,
        total_trains=dashboard.nb_trains or 0,
        night_trains=dashboard.nb_trains_nuit or 0,
        day_trains=dashboard.nb_trains_jour or 0,
        distance_totale_km=float(dashboard.distance_totale_km or 0),
        duree_moyenne_min=float(dashboard.duree_moyenne_min or 0),
        countries_served=[c.country_name for c in countries],
        countries_count=len(countries)
    )