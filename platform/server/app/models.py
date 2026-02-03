# app/models.py
from sqlalchemy import Column, Integer, String, ForeignKey, DECIMAL, Boolean, text
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


class FactsCountryStats(Base):
    """Table de faits pour les statistiques par pays"""
    __tablename__ = "facts_country_stats"
    
    stats_id = Column(Integer, primary_key=True, index=True)
    passengers = Column(DECIMAL(15, 6), nullable=False)
    co2_emissions = Column(DECIMAL(15, 6), nullable=False)
    co2_per_passenger = Column(DECIMAL(15, 6), nullable=False)
    
    # Clés étrangères
    country_id = Column(Integer, ForeignKey("dim_countries.country_id"), nullable=False, index=True)
    year_id = Column(Integer, ForeignKey("dim_years.year_id"), nullable=False, index=True)
    
    # Relations
    country = relationship("DimCountries", back_populates="country_stats")
    year_dim = relationship("DimYears", back_populates="country_stats")
    
    def __repr__(self):
        return f"<CountryStats(id={self.stats_id}, country={self.country_id}, year={self.year_id}, passengers={self.passengers})>"


class FactsNightTrains(Base):
    """Table de faits des trains de nuit"""
    __tablename__ = "facts_night_trains"
    
    fact_id = Column(Integer, primary_key=True, index=True)
    route_id = Column(Integer, nullable=False, index=True)
    night_train = Column(String(200), nullable=False, index=True)
    
    # Clés étrangères
    country_id = Column(Integer, ForeignKey("dim_countries.country_id"), nullable=False, index=True)
    year_id = Column(Integer, ForeignKey("dim_years.year_id"), nullable=False, index=True)
    operator_id = Column(Integer, ForeignKey("dim_operators.operator_id"), nullable=False, index=True)
    
    # Relations
    country = relationship("DimCountries", back_populates="night_trains")
    year_dim = relationship("DimYears", back_populates="night_trains")
    operator = relationship("DimOperators", back_populates="night_trains")
    
    def __repr__(self):
        return f"<NightTrain(id={self.fact_id}, route={self.route_id}, train='{self.night_train}')>"


class DashboardMetrics(Base):
    """Vue pour les métriques du dashboard"""
    __tablename__ = "dashboard_metrics"
    
    # Note: Puisque c'est une vue, on utilise declared_attr pour les colonnes
    @declared_attr
    def country_name(cls):
        return Column(String(100), primary_key=True)
    
    @declared_attr
    def country_code(cls):
        return Column(String(10))
    
    @declared_attr
    def avg_passengers(cls):
        return Column(DECIMAL(15, 6))
    
    @declared_attr
    def avg_co2_emissions(cls):
        return Column(DECIMAL(15, 6))
    
    @declared_attr
    def avg_co2_per_passenger(cls):
        return Column(DECIMAL(15, 6))
    
    # Pour indiquer à SQLAlchemy que c'est une vue
    __table_args__ = {'info': {'is_view': True}}
    
    @classmethod
    def create_view(cls, engine):
        """Méthode pour créer la vue si elle n'existe pas"""
        view_sql = """
        CREATE OR REPLACE VIEW dashboard_metrics AS
        SELECT 
          c.country_name,
          c.country_code,
          AVG(s.passengers) as avg_passengers,
          AVG(s.co2_emissions) as avg_co2_emissions,
          AVG(s.co2_per_passenger) as avg_co2_per_passenger
        FROM facts_country_stats s
        JOIN dim_countries c ON s.country_id = c.country_id
        GROUP BY c.country_id, c.country_name, c.country_code
        """
        
        with engine.connect() as conn:
            conn.execute(text(view_sql))
            conn.commit()
    
    def __repr__(self):
        return f"<DashboardMetrics(country='{self.country_name}', avg_passengers={self.avg_passengers})>"


# Modèle pour les données de qualité (à partir du JSON)
class QualityReport(Base):
    """Table pour stocker les rapports de qualité"""
    __tablename__ = "quality_reports"
    
    report_id = Column(Integer, primary_key=True, index=True)
    execution_date = Column(String(50), nullable=False)
    project = Column(String(200), nullable=False)
    report_data = Column(String, nullable=False)  # JSON stocké en texte
    created_at = Column(String(50), nullable=False)
    
    def __repr__(self):
        return f"<QualityReport(id={self.report_id}, project='{self.project}', date='{self.execution_date}')>"


# Fonction utilitaire pour créer toutes les tables et vues
def create_tables_and_views(engine):
    """Crée toutes les tables et vues nécessaires"""
    # Créer les tables de base
    Base.metadata.create_all(bind=engine)
    
    # Créer la vue dashboard_metrics
    DashboardMetrics.create_view(engine)
    
    print("✅ Tables et vues créées avec succès!")


# Si ce fichier est exécuté directement
if __name__ == "__main__":
    from app.database import engine
    
    create_tables_and_views(engine)