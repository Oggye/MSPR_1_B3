# server\app\routers\countries.py
# ROUTER: Endpoints pour les données pays et statistiques nationales
# ==================================================================
# Rôle: Fournir l'accès aux données statistiques par pays (passagers, CO2)
#       avec filtrage avancé pour les analyses comparatives.

# Tables utilisées:
# - facts_country_stats : Statistiques annuelles par pays
# - dim_countries : Référentiel des pays européens  
# - dim_years : Dimension temporelle (2010-2024)

# Endpoints implémentés:
# 1. GET /api/countries/stats - Statistiques complètes avec filtres
# 2. GET /api/countries/ - Liste des pays référencés

# Résultats attendus:
# - Interface pour le tableau de bord ObRail
# - Données pour les rapports institutionnels
# - Base pour les analyses environnementales comparatives

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from app.dependencies import get_db
from app.models import DimCountries, FactsCountryStats, DimYears
from app.schemas.countries import CountryResponse, CountryStatsResponse, CountryStatsFilter

router = APIRouter()

@router.get("/api/countries", response_model=List[CountryResponse])
def get_countries(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500)
):
    """
    Récupère la liste des pays européens référencés.
    """
    countries = db.query(DimCountries).offset(skip).limit(limit).all()
    return countries

@router.get("/api/countries/stats", response_model=List[CountryStatsResponse])
def get_country_stats(
    filter: CountryStatsFilter = Depends(),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500)
):
    """
    Récupère les statistiques par pays avec filtrage avancé.
    """
    # Construction de la requête de base avec jointures
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
    
    # Application des filtres
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
    
    # Exécution de la requête avec pagination
    results = query.offset(skip).limit(limit).all()
    
    # Transformation en format de réponse
    transformed_results = []

    for stats, country_name, country_code, year in results:
        response_item = CountryStatsResponse(
            stats_id=stats.stats_id,
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