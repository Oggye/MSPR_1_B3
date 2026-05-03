# server/app/routers/night_trains.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from app.dependencies import get_db
from app.models import FactsNightTrains, DimCountries, DimOperators, DimYears
from app.schemas.trains import NightTrainResponse, NightTrainFilter, NightTrainSummary

router = APIRouter()


def _build_night_trains_query(db: Session, is_night: Optional[bool] = None):
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


def _apply_pagination(query, skip: int, limit: Optional[int]):
    """Applique offset et limit uniquement si limit est fourni."""
    query = query.offset(skip)
    if limit is not None:
        query = query.limit(limit)
    return query


def _to_response(train, country_name, country_code, operator_name, year) -> NightTrainResponse:
    return NightTrainResponse(
        fact_id=train.fact_id,
        route_id=train.route_id,
        night_train=train.night_train,
        country_name=country_name,
        country_code=country_code,
        operator_name=operator_name,
        year=year,
        is_night=train.is_night,
        distance_km=float(train.distance_km) if train.distance_km is not None else None,
        duration_min=float(train.duration_min) if train.duration_min is not None else None,
        train_type="night" if train.is_night else "day",
    )


@router.get("/api/night-trains/summary", response_model=NightTrainSummary)
def get_night_trains_summary(db: Session = Depends(get_db)):
    """
    Retourne le nombre total de trains, de trains de nuit et de trains de jour.
    """
    total = db.query(FactsNightTrains).count()
    total_night = db.query(FactsNightTrains).filter(FactsNightTrains.is_night.is_(True)).count()
    total_day = db.query(FactsNightTrains).filter(FactsNightTrains.is_night.is_(False)).count()

    return NightTrainSummary(
        total_trains=total,
        total_night_trains=total_night,
        total_day_trains=total_day,
    )


@router.get("/api/night-trains", response_model=List[NightTrainResponse])
def get_all_night_trains(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: Optional[int] = Query(None, ge=1),
    country_code: Optional[str] = None,
    operator_name: Optional[str] = None,
    year: Optional[int] = None,
):
    """Récupère tous les trains (jour et nuit)."""
    query = _build_night_trains_query(db, is_night=None)

    if country_code:
        query = query.filter(DimCountries.country_code == country_code)
    if operator_name:
        query = query.filter(DimOperators.operator_name.ilike(f"%{operator_name}%"))
    if year:
        query = query.filter(DimYears.year == year)

    results = _apply_pagination(query, skip, limit).all()
    return [_to_response(*row) for row in results]


@router.get("/api/night-trains/night", response_model=List[NightTrainResponse])
def get_night_trains_only(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: Optional[int] = Query(None, ge=1),
    country_code: Optional[str] = None,
    operator_name: Optional[str] = None,
    year: Optional[int] = None,
):
    """Récupère uniquement les trains de nuit (is_night = true)."""
    query = _build_night_trains_query(db, is_night=True)

    if country_code:
        query = query.filter(DimCountries.country_code == country_code)
    if operator_name:
        query = query.filter(DimOperators.operator_name.ilike(f"%{operator_name}%"))
    if year:
        query = query.filter(DimYears.year == year)

    results = _apply_pagination(query, skip, limit).all()
    return [_to_response(*row) for row in results]


@router.get("/api/night-trains/day", response_model=List[NightTrainResponse])
def get_day_trains_only(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: Optional[int] = Query(None, ge=1),
    country_code: Optional[str] = None,
    operator_name: Optional[str] = None,
    year: Optional[int] = None,
):
    """Récupère uniquement les trains de jour (is_night = false)."""
    query = _build_night_trains_query(db, is_night=False)

    if country_code:
        query = query.filter(DimCountries.country_code == country_code)
    if operator_name:
        query = query.filter(DimOperators.operator_name.ilike(f"%{operator_name}%"))
    if year:
        query = query.filter(DimYears.year == year)

    results = _apply_pagination(query, skip, limit).all()
    return [_to_response(*row) for row in results]


@router.get("/api/night-trains/by-operator/{operator_id}", response_model=List[NightTrainResponse])
def get_night_trains_by_operator(
    operator_id: int,
    db: Session = Depends(get_db)
):
    """Récupère tous les trains pour un opérateur donné."""
    operator = db.query(DimOperators).filter(DimOperators.operator_id == operator_id).first()
    if not operator:
        raise HTTPException(status_code=404, detail="Opérateur non trouvé")

    results = _build_night_trains_query(db, is_night=None).filter(
        FactsNightTrains.operator_id == operator_id
    ).all()

    return [_to_response(*row) for row in results]


@router.get("/api/geographic/coverage")
def get_geographic_coverage(db: Session = Depends(get_db)):
    """Récupère la couverture géographique des trains."""
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

    return {
        "total_countries_covered": len(coverage),
        "coverage_by_country": [
            {"country_name": r.country_name, "country_code": r.country_code, "train_count": r.train_count}
            for r in coverage
        ]
    }