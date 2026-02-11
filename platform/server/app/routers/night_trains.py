# server\app\routers\night_trains.py
# ROUTER: Endpoints pour les trains de nuit européens
# ====================================================
# Rôle: Exposer le catalogue des trains de nuit avec leurs caractéristiques
#       et permettre l'analyse de leur couverture géographique.

# Tables utilisées:
# - facts_night_trains : Inventaire des trains de nuit
# - dim_countries : Pays desservis
# - dim_operators : Opérateurs ferroviaires
# - dim_years : Période de fonctionnement

# Endpoints implémentés:
# 1. GET /api/night-trains/ - Liste avec filtres pays/opérateur/année
# 2. GET /api/night-trains/by-operator/{id} - Trains par opérateur
# 3. GET /api/geographic/coverage - Visualisation géographique

# Résultats attendus:
# - Visualisation du réseau de trains de nuit
# - Support pour les études de mobilité durable
# - Données pour les comparaisons modales (train vs avion)

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from app.dependencies import get_db
from app.models import FactsNightTrains, DimCountries, DimOperators, DimYears
from app.schemas.trains import NightTrainResponse, NightTrainFilter

router = APIRouter()

@router.get("/api/night-trains", response_model=List[NightTrainResponse])
def get_night_trains(
    filter: NightTrainFilter = Depends(),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500)
):
    """
    Récupère la liste des trains de nuit avec filtres.
    """
    # Construction de la requête avec jointures
    query = db.query(
        FactsNightTrains,
        DimCountries.country_name,
        DimCountries.country_code,
        DimOperators.operator_name,
        DimYears.year
    ).join(
        DimCountries, FactsNightTrains.country_id == DimCountries.country_id
    ).join(
        DimOperators, FactsNightTrains.operator_id == DimOperators.operator_id
    ).join(
        DimYears, FactsNightTrains.year_id == DimYears.year_id
    )
    
    # Application des filtres
    if filter.country_code:
        query = query.filter(DimCountries.country_code == filter.country_code)
    
    if filter.operator_name:
        query = query.filter(DimOperators.operator_name.ilike(f"%{filter.operator_name}%"))
    
    if filter.year:
        query = query.filter(DimYears.year == filter.year)
    
    # Exécution avec pagination
    results = query.offset(skip).limit(limit).all()
    
    # Transformation en format de réponse
    transformed_results = []

    for train, country_name, country_code, operator_name, year in results:
        response_item = NightTrainResponse(
            fact_id=train.fact_id,
            route_id=train.route_id,
            night_train=train.night_train,
            country_name=country_name,
            country_code=country_code,
            operator_name=operator_name,
            year=year
        )
        transformed_results.append(response_item)
        
    return transformed_results

@router.get("/api/night-trains/by-operator/{operator_id}", response_model=List[NightTrainResponse])
def get_night_trains_by_operator(
    operator_id: int,
    db: Session = Depends(get_db)
):
    """
    Récupère les trains de nuit par opérateur.
    """
    # Vérifier d'abord que l'opérateur existe
    operator = db.query(DimOperators).filter(DimOperators.operator_id == operator_id).first()
    
    if not operator:
        raise HTTPException(status_code=404, detail="Opérateur non trouvé")
    
    # Construction de la requête avec jointures
    query = db.query(
        FactsNightTrains,
        DimCountries.country_name,
        DimCountries.country_code,
        DimOperators.operator_name,
        DimYears.year
    ).join(
        DimCountries, FactsNightTrains.country_id == DimCountries.country_id
    ).join(
        DimOperators, FactsNightTrains.operator_id == DimOperators.operator_id
    ).join(
        DimYears, FactsNightTrains.year_id == DimYears.year_id
    ).filter(
        FactsNightTrains.operator_id == operator_id
    )
    
    results = query.all()
    
    # Transformation en format de réponse
    transformed_results = []
    for train, country_name, country_code, operator_name, year in results:
        response_item = NightTrainResponse(
            fact_id=train.fact_id,
            route_id=train.route_id,
            night_train=train.night_train,
            country_name=country_name,
            country_code=country_code,
            operator_name=operator_name,
            year=year
        )
        transformed_results.append(response_item)
    
    return transformed_results

@router.get("/api/geographic/coverage")
def get_geographic_coverage(db: Session = Depends(get_db)):
    """
    Récupère la couverture géographique des trains de nuit.
    """
    coverage = db.query(
        DimCountries.country_name,
        DimCountries.country_code,
        func.count(FactsNightTrains.fact_id).label("train_count")
    ).join(
        FactsNightTrains, DimCountries.country_id == FactsNightTrains.country_id
    ).group_by(
        DimCountries.country_id,
        DimCountries.country_name,
        DimCountries.country_code
    ).order_by(
        func.count(FactsNightTrains.fact_id).desc()
    ).all()

    coverage_list = []
    for country_name, country_code, train_count in coverage:
        coverage_list.append({
            "country_name": country_name,
            "country_code": country_code,
            "train_count": train_count
        })

    return {
        "total_countries_covered": len(coverage),
        "coverage_by_country": coverage_list
    }