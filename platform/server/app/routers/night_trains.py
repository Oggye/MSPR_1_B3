# server/app/routers/night_trains.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from app.dependencies import get_db
from app.models import FactsNightTrains, DimCountries, DimOperators, DimYears
from app.schemas.trains import NightTrainResponse, NightTrainFilter

router = APIRouter()

def _build_night_trains_query(db: Session, is_night: Optional[bool] = None):
    """
    Fonction utilitaire pour construire la requête de base avec jointures
    et filtre optionnel sur is_night.
    """
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

    if is_night is not None:
        query = query.filter(FactsNightTrains.is_night == is_night)

    return query


@router.get("/api/night-trains", response_model=List[NightTrainResponse])
def get_all_night_trains(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    country_code: Optional[str] = None,
    operator_name: Optional[str] = None,
    year: Optional[int] = None,
):
    """
    Récupère tous les trains (jour et nuit) avec filtres optionnels.
    """
    query = _build_night_trains_query(db, is_night=None)

    if country_code:
        query = query.filter(DimCountries.country_code == country_code)
    if operator_name:
        query = query.filter(DimOperators.operator_name.ilike(f"%{operator_name}%"))
    if year:
        query = query.filter(DimYears.year == year)

    results = query.offset(skip).limit(limit).all()

    transformed = []
    for train, country_name, country_code, operator_name, year in results:
        transformed.append(NightTrainResponse(
            fact_id=train.fact_id,
            route_id=train.route_id,
            night_train=train.night_train,
            country_name=country_name,
            country_code=country_code,
            operator_name=operator_name,
            year=year,
            is_night=train.is_night
        ))
    return transformed


@router.get("/api/night-trains/night", response_model=List[NightTrainResponse])
def get_night_trains_only(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    country_code: Optional[str] = None,
    operator_name: Optional[str] = None,
    year: Optional[int] = None,
):
    """
    Récupère uniquement les trains de nuit (is_night = true).
    """
    query = _build_night_trains_query(db, is_night=True)

    if country_code:
        query = query.filter(DimCountries.country_code == country_code)
    if operator_name:
        query = query.filter(DimOperators.operator_name.ilike(f"%{operator_name}%"))
    if year:
        query = query.filter(DimYears.year == year)

    results = query.offset(skip).limit(limit).all()

    transformed = []
    for train, country_name, country_code, operator_name, year in results:
        transformed.append(NightTrainResponse(
            fact_id=train.fact_id,
            route_id=train.route_id,
            night_train=train.night_train,
            country_name=country_name,
            country_code=country_code,
            operator_name=operator_name,
            year=year,
            is_night=train.is_night
        ))
    return transformed


@router.get("/api/night-trains/day", response_model=List[NightTrainResponse])
def get_day_trains_only(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    country_code: Optional[str] = None,
    operator_name: Optional[str] = None,
    year: Optional[int] = None,
):
    """
    Récupère uniquement les trains de jour (is_night = false).
    """
    query = _build_night_trains_query(db, is_night=False)

    if country_code:
        query = query.filter(DimCountries.country_code == country_code)
    if operator_name:
        query = query.filter(DimOperators.operator_name.ilike(f"%{operator_name}%"))
    if year:
        query = query.filter(DimYears.year == year)

    results = query.offset(skip).limit(limit).all()

    transformed = []
    for train, country_name, country_code, operator_name, year in results:
        transformed.append(NightTrainResponse(
            fact_id=train.fact_id,
            route_id=train.route_id,
            night_train=train.night_train,
            country_name=country_name,
            country_code=country_code,
            operator_name=operator_name,
            year=year,
            is_night=train.is_night
        ))
    return transformed


@router.get("/api/night-trains/by-operator/{operator_id}", response_model=List[NightTrainResponse])
def get_night_trains_by_operator(
    operator_id: int,
    db: Session = Depends(get_db)
):
    """
    Récupère les trains (jour et nuit) pour un opérateur donné.
    """
    operator = db.query(DimOperators).filter(DimOperators.operator_id == operator_id).first()
    if not operator:
        raise HTTPException(status_code=404, detail="Opérateur non trouvé")

    query = _build_night_trains_query(db, is_night=None).filter(
        FactsNightTrains.operator_id == operator_id
    )

    results = query.all()
    transformed = []
    for train, country_name, country_code, operator_name, year in results:
        transformed.append(NightTrainResponse(
            fact_id=train.fact_id,
            route_id=train.route_id,
            night_train=train.night_train,
            country_name=country_name,
            country_code=country_code,
            operator_name=operator_name,
            year=year,
            is_night=train.is_night
        ))
    return transformed


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

    coverage_list = [
        {
            "country_name": country_name,
            "country_code": country_code,
            "train_count": train_count
        }
        for country_name, country_code, train_count in coverage
    ]

    return {
        "total_countries_covered": len(coverage),
        "coverage_by_country": coverage_list
    }