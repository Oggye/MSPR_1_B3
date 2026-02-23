# server\app\routers\operators.py
# ROUTER: Endpoints pour les opérateurs ferroviaires
# ==================================================
# Rôle: Analyser la performance et la contribution des différents
#       opérateurs ferroviaires européens.

# Tables utilisées:
# - dim_operators : Catalogue des opérateurs
# - facts_night_trains : Trains opérés
# - facts_country_stats : Contexte statistique

# Endpoints implémentés:
# 1. GET /api/operators/ - Liste des opérateurs
# 2. GET /api/operators/{id}/stats - Statistiques par opérateur

# Résultats attendus:
# - Évaluation comparative des opérateurs
# - Identification des leaders du secteur
# - Données pour les partenariats public-privé

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from app.dependencies import get_db
from app.models import DimOperators, FactsNightTrains, DimCountries
from app.schemas.operators import OperatorResponse, OperatorRanking

router = APIRouter()

@router.get("/api/operators", response_model=List[OperatorResponse])
def get_operators(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500)
):
    """
    Récupère la liste des opérateurs ferroviaires.
    """
    query = db.query(DimOperators)
    
    operators = query.offset(skip).limit(limit).all()
    
    # Transformation en format de réponse
    transformed_results = []

    for op in operators:
        response_item = OperatorResponse(
            operator_id=op.operator_id,
            operator_name=op.operator_name
        )
        transformed_results.append(response_item)

    return transformed_results

@router.get("/api/operators/{operator_id}/stats", response_model=OperatorRanking)
def get_operator_stats(
    operator_id: int, 
    db: Session = Depends(get_db)
):
    """
    Statistiques détaillées par opérateur ferroviaire.
    """
    operator = db.query(DimOperators).filter(
        DimOperators.operator_id == operator_id
    ).first()
    
    if not operator:
        raise HTTPException(status_code=404, detail="Opérateur non trouvé")
    
    # Nombre de trains de nuit
    night_trains = db.query(FactsNightTrains).filter(
        FactsNightTrains.operator_id == operator_id
    ).count()
    
    # Pays desservis
    countries = db.query(DimCountries).join(
        FactsNightTrains
    ).filter(
        FactsNightTrains.operator_id == operator_id
    ).distinct().all()
    
    return OperatorRanking(
        operator_id=operator.operator_id,
        operator_name=operator.operator_name,
        total_trains=night_trains,
        countries_served=[c.country_name for c in countries],
        countries_count=len(countries)
    )