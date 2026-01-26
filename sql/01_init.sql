-- 01_init.sql
-- Script de création des tables du data warehouse ObRail
-- Ordre de chargement: 1. Dimensions, 2. Faits
-- Supression de la vue si elle existe
DROP VIEW IF EXISTS dashboard_metrics;

-- DIMENSIONS
-- Table des pays
CREATE TABLE IF NOT EXISTS dim_countries(
  country_id INTEGER PRIMARY KEY,
  country_code VARCHAR(10) UNIQUE NOT NULL, 
  country_name VARCHAR(100) NOT NULL
);

-- Table des années
CREATE TABLE IF NOT EXISTS dim_years(
  year_id INTEGER PRIMARY KEY,
  year INTEGER NOT NULL,
  is_after_2010 BOOLEAN NOT NULL DEFAULT TRUE
);

-- Table des opérateurs
CREATE TABLE IF NOT EXISTS dim_operators(
  operator_id INTEGER PRIMARY KEY,
  operator_name VARCHAR(200) NOT NULL
);

-- FAITS
-- Table de faits des trajets de nuit
CREATE TABLE IF NOT EXISTS facts_night_trains(
  fact_id INTEGER PRIMARY KEY,
  route_id INTEGER NOT NULL,
  night_train VARCHAR(200) NOT NULL,
  country_id INTEGER NOT NULL,
  year_id INTEGER NOT NULL, 
  operator_id INTEGER NOT NULL,
  FOREIGN KEY (country_id) REFERENCES dim_countries(country_id),
  FOREIGN KEY (year_id) REFERENCES dim_years(year_id),
  FOREIGN KEY (operator_id) REFERENCES dim_operators(operator_id)
);

-- Table de faits pour les statistiques par pays
CREATE TABLE IF NOT EXISTS facts_country_stats (
  stats_id INTEGER PRIMARY KEY,
  passengers DECIMAL NOT NULL,
  co2_emissions DECIMAL NOT NULL,
  co2_per_passenger DECIMAL NOT NULL,
  country_id INTEGER NOT NULL,
  year_id INTEGER NOT NULL,
  FOREIGN KEY (country_id) REFERENCES dim_countries(country_id),
  FOREIGN KEY (year_id) REFERENCES dim_years(year_id)
);

-- VUE POUR DASHBOARD
CREATE VIEW dashboard_metrics AS
SELECT 
  c.country_name,
  c.country_code,
  AVG(s.passengers) as avg_passengers,
  AVG(s.co2_emissions) as avg_co2_emissions,
  AVG(s.co2_per_passenger) as avg_co2_per_passenger
FROM facts_country_stats s
JOIN dim_countries c ON s.country_id = c.country_id
GROUP BY c.country_id, c.country_name, c.country_code;
