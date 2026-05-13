# server/app/routers/countries.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.dependencies import get_db
from app.models import DimCountries, FactsCountryStats, DimYears
from app.schemas.countries import CountryResponse, CountryStatsResponse, CountryStatsFilter

router = APIRouter()


@router.get("/api/countries", response_model=List[CountryResponse])
def get_countries(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: Optional[int] = Query(None, ge=1)
):
    """Récupère la liste des pays européens référencés."""
    query = db.query(DimCountries).offset(skip)

    if limit is not None:
        query = query.limit(limit)

    return query.all()


@router.get("/api/countries/stats", response_model=List[CountryStatsResponse])
def get_country_stats(
    filter: CountryStatsFilter = Depends(),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: Optional[int] = Query(None, ge=1)
):
    """Récupère les statistiques par pays avec filtrage avancé."""
    query = db.query(
        FactsCountryStats,
        DimCountries.country_name,
        DimCountries.country_code,
        DimYears.year
    ).join(
        DimCountries, FactsCountryStats.country_id == DimCountries.country_id
    ).join(
        DimYears, FactsCountryStats.year_id == DimYears.year_id
    )

    if filter.country_code is not None:
        query = query.filter(DimCountries.country_code == filter.country_code)
    if filter.year is not None:
        query = query.filter(DimYears.year == filter.year)
    if filter.min_passengers is not None:
        query = query.filter(FactsCountryStats.passengers >= filter.min_passengers)
    if filter.max_passengers is not None:
        query = query.filter(FactsCountryStats.passengers <= filter.max_passengers)
    if filter.min_co2_per_passenger is not None:
        query = query.filter(FactsCountryStats.co2_per_passenger >= filter.min_co2_per_passenger)
    if filter.max_co2_per_passenger is not None:
        query = query.filter(FactsCountryStats.co2_per_passenger <= filter.max_co2_per_passenger)

    query = query.offset(skip)

    if limit is not None:
        query = query.limit(limit)

    results = query.all()

    transformed_results = []
    for stats, country_name, country_code, year in results:
        response_item = CountryStatsResponse(
            stats_id=stats.stat_id,      # corrigé : stats.stats_id → stats.stat_id
            country_id=stats.country_id,
            year_id=stats.year_id,
            passengers=float(stats.passengers),
            co2_emissions=float(stats.co2_emissions),
            co2_per_passenger=float(stats.co2_per_passenger),
            country_name=country_name,
            country_code=country_code,
            year=year
        )
        transformed_results.append(response_item)

    return transformed_results
