# app/models.py
from sqlalchemy import Column, Integer, String, ForeignKey, DECIMAL, Boolean, Float, text
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.ext.declarative import declared_attr

Base = declarative_base()


class DimCountries(Base):
    """Table dimension des pays"""
    __tablename__ = "dim_countries"

    country_id = Column(Integer, primary_key=True, index=True)
    country_code = Column(String(10), unique=True, nullable=False, index=True)
    country_name = Column(String(100), nullable=False)

    # Relations
    country_stats = relationship("FactsCountryStats", back_populates="country")
    night_trains = relationship("FactsNightTrains", back_populates="country")

    def __repr__(self):
        return f"<Country(id={self.country_id}, code='{self.country_code}', name='{self.country_name}')>"


class DimYears(Base):
    """Table dimension des années"""
    __tablename__ = "dim_years"

    year_id = Column(Integer, primary_key=True, index=True)
    year = Column(Integer, nullable=False, unique=True, index=True)
    is_after_2010 = Column(Boolean, nullable=False, default=True)

    # Relations
    country_stats = relationship("FactsCountryStats", back_populates="year_dim")
    night_trains = relationship("FactsNightTrains", back_populates="year_dim")

    def __repr__(self):
        return f"<Year(id={self.year_id}, year={self.year}, after_2010={self.is_after_2010})>"


class DimOperators(Base):
    """Table dimension des opérateurs ferroviaires"""
    __tablename__ = "dim_operators"

    operator_id = Column(Integer, primary_key=True, index=True)
    operator_name = Column(String(200), nullable=False, index=True)

    # Relations
    night_trains = relationship("FactsNightTrains", back_populates="operator")

    def __repr__(self):
        return f"<Operator(id={self.operator_id}, name='{self.operator_name}')>"


class DimStops(Base):
    """Table dimension des arrêts"""
    __tablename__ = "dim_stops"

    stop_id_dim = Column(Integer, primary_key=True, index=True)
    stop_name = Column(String(200), nullable=False)
    stop_lat = Column(DECIMAL(10, 6), nullable=True)
    stop_lon = Column(DECIMAL(10, 6), nullable=True)
    stop_id = Column(String(100), nullable=True)
    source_country = Column(String(2), nullable=True)

    def __repr__(self):
        return f"<Stop(id={self.stop_id_dim}, name='{self.stop_name}')>"


class FactsCountryStats(Base):
    """Table de faits pour les statistiques par pays"""
    __tablename__ = "facts_country_stats"

    stat_id = Column(Integer, primary_key=True, index=True)  # corrigé : était stats_id
    passengers = Column(DECIMAL(15, 2), nullable=False)
    co2_emissions = Column(DECIMAL(15, 4), nullable=False)
    co2_per_passenger = Column(DECIMAL(15, 6), nullable=False)

    # Clés étrangères
    country_id = Column(Integer, ForeignKey("dim_countries.country_id"), nullable=False, index=True)
    year_id = Column(Integer, ForeignKey("dim_years.year_id"), nullable=False, index=True)

    # Relations
    country = relationship("DimCountries", back_populates="country_stats")
    year_dim = relationship("DimYears", back_populates="country_stats")

    def __repr__(self):
        return f"<CountryStats(id={self.stat_id}, country={self.country_id}, year={self.year_id}, passengers={self.passengers})>"


class FactsNightTrains(Base):
    """Table de faits des trajets (nuit + jour)"""
    __tablename__ = "facts_night_trains"

    fact_id = Column(Integer, primary_key=True, index=True)
    route_id = Column(String(50), nullable=False)        # corrigé : String(50), pas Integer
    night_train = Column(String(200), nullable=False, index=True)
    is_night = Column(Boolean, nullable=False, default=True)
    distance_km = Column(DECIMAL(10, 2), default=0)      # ajouté
    duration_min = Column(DECIMAL(10, 1), default=0)     # ajouté

    # Clés étrangères
    country_id = Column(Integer, ForeignKey("dim_countries.country_id"), nullable=False, index=True)
    year_id = Column(Integer, ForeignKey("dim_years.year_id"), nullable=False, index=True)
    operator_id = Column(Integer, ForeignKey("dim_operators.operator_id"), nullable=False, index=True)

    # Relations
    country = relationship("DimCountries", back_populates="night_trains")
    year_dim = relationship("DimYears", back_populates="night_trains")
    operator = relationship("DimOperators", back_populates="night_trains")

    def __repr__(self):
        return f"<NightTrain(id={self.fact_id}, route={self.route_id}, train='{self.night_train}', night={self.is_night})>"


class DashboardMetrics(Base):
    """Vue pour les métriques du dashboard (lecture seule)"""
    __tablename__ = "dashboard_metrics"

    country_id = Column(Integer, primary_key=True)       # ajouté : la vue le retourne maintenant
    country_name = Column(String(100))
    country_code = Column(String(10))
    avg_passengers = Column(DECIMAL(15, 2))
    avg_co2_emissions = Column(DECIMAL(15, 4))
    avg_co2_per_passenger = Column(DECIMAL(15, 6))

    __table_args__ = {'info': {'is_view': True}}

    def __repr__(self):
        return f"<DashboardMetrics(country='{self.country_name}', avg_passengers={self.avg_passengers})>"


class OperatorDashboard(Base):
    """Vue pour les statistiques par opérateur (lecture seule)"""
    __tablename__ = "operator_dashboard"

    operator_id = Column(Integer, primary_key=True)
    operator_name = Column(String(200))
    nb_trains = Column(Integer)
    nb_trains_nuit = Column(Integer)
    nb_trains_jour = Column(Integer)
    distance_totale_km = Column(DECIMAL(15, 2))
    duree_moyenne_min = Column(DECIMAL(10, 1))

    __table_args__ = {'info': {'is_view': True}}

    def __repr__(self):
        return f"<OperatorDashboard(id={self.operator_id}, name='{self.operator_name}', nb_trains={self.nb_trains})>"


class QualityReport(Base):
    """Table pour stocker les rapports de qualité"""
    __tablename__ = "quality_reports"

    report_id = Column(Integer, primary_key=True, index=True)
    execution_date = Column(String(50), nullable=False)
    project = Column(String(200), nullable=False)
    report_data = Column(String, nullable=False)
    created_at = Column(String(50), nullable=False)

    def __repr__(self):
        return f"<QualityReport(id={self.report_id}, project='{self.project}', date='{self.execution_date}')>"


def create_tables_and_views(engine):
    """Crée toutes les tables (les vues sont créées par le SQL init)"""
    Base.metadata.create_all(bind=engine)
    print("✅ Tables créées avec succès!")


if __name__ == "__main__":
    from app.database import engine
    create_tables_and_views(engine)