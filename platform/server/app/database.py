# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

# Configuration depuis les variables d'environnement
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "obrail")
DB_USER = os.getenv("DB_USER", "obrail_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "1234")

# URL de connexion PostgreSQL
SQLALCHEMY_DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)