-- 01_init.sql
-- Script de création des tables du data warehouse ObRail
-- Ordre de chargement: 1. Dimensions, 2. Faits, 3. Vues

-- Suppression de la vue si elle existe
DROP VIEW IF EXISTS dashboard_metrics;

-- ============================================================
-- DIMENSIONS
-- ============================================================

-- Table des pays
DROP TABLE IF EXISTS dim_countries CASCADE;
CREATE TABLE dim_countries (
    country_id INTEGER PRIMARY KEY,
    country_code VARCHAR(10) UNIQUE NOT NULL,
    country_name VARCHAR(100) NOT NULL
);

-- Table des années
DROP TABLE IF EXISTS dim_years CASCADE;
CREATE TABLE dim_years (
    year_id INTEGER PRIMARY KEY,
    year INTEGER NOT NULL,
    is_after_2010 BOOLEAN NOT NULL DEFAULT TRUE
);

-- Table des opérateurs
DROP TABLE IF EXISTS dim_operators CASCADE;
CREATE TABLE dim_operators (
    operator_id INTEGER PRIMARY KEY,
    operator_name VARCHAR(200) NOT NULL
);

-- Table des arrêts (NOUVELLE)
DROP TABLE IF EXISTS dim_stops CASCADE;
CREATE TABLE dim_stops (
    stop_id_dim INTEGER PRIMARY KEY,
    stop_name VARCHAR(200) NOT NULL,
    stop_lat NUMERIC(10, 6),
    stop_lon NUMERIC(10, 6),
    stop_id VARCHAR(100),
    source_country VARCHAR(2)
);

-- ============================================================
-- FAITS
-- ============================================================

-- Table de faits des trajets (nuit + jour)
DROP TABLE IF EXISTS facts_night_trains CASCADE;
CREATE TABLE facts_night_trains (
    fact_id INTEGER PRIMARY KEY,
    route_id VARCHAR(50) NOT NULL,
    night_train VARCHAR(200) NOT NULL,
    country_id INTEGER NOT NULL,
    year_id INTEGER NOT NULL,
    operator_id INTEGER NOT NULL,
    is_night BOOLEAN NOT NULL DEFAULT TRUE,
    distance_km NUMERIC(10, 2) DEFAULT 0,
    duration_min NUMERIC(10, 1) DEFAULT 0,
    FOREIGN KEY (country_id) REFERENCES dim_countries(country_id),
    FOREIGN KEY (year_id) REFERENCES dim_years(year_id),
    FOREIGN KEY (operator_id) REFERENCES dim_operators(operator_id)
);

-- Table de faits pour les statistiques par pays
DROP TABLE IF EXISTS facts_country_stats CASCADE;
CREATE TABLE facts_country_stats (
    stat_id INTEGER PRIMARY KEY,
    country_id INTEGER NOT NULL,
    year_id INTEGER NOT NULL,
    passengers NUMERIC(15, 2) NOT NULL,
    co2_emissions NUMERIC(15, 4) NOT NULL,
    co2_per_passenger NUMERIC(15, 6) NOT NULL,
    FOREIGN KEY (country_id) REFERENCES dim_countries(country_id),
    FOREIGN KEY (year_id) REFERENCES dim_years(year_id)
);

-- ============================================================
-- VUES
-- ============================================================

-- Vue dashboard pays
CREATE VIEW dashboard_metrics AS
SELECT 
    c.country_id,
    c.country_name,
    c.country_code,
    AVG(s.passengers)::NUMERIC(15, 2) as avg_passengers,
    AVG(s.co2_emissions)::NUMERIC(15, 4) as avg_co2_emissions,
    AVG(s.co2_per_passenger)::NUMERIC(15, 6) as avg_co2_per_passenger
FROM facts_country_stats s
JOIN dim_countries c ON s.country_id = c.country_id
GROUP BY c.country_id, c.country_name, c.country_code;

-- Vue dashboard opérateurs (NOUVELLE)
CREATE VIEW operator_dashboard AS
SELECT 
    o.operator_id,
    o.operator_name,
    COUNT(f.fact_id) as nb_trains,
    SUM(CASE WHEN f.is_night = TRUE THEN 1 ELSE 0 END) as nb_trains_nuit,
    SUM(CASE WHEN f.is_night = FALSE THEN 1 ELSE 0 END) as nb_trains_jour,
    COALESCE(SUM(f.distance_km), 0)::NUMERIC(15, 2) as distance_totale_km,
    COALESCE(AVG(f.duration_min), 0)::NUMERIC(10, 1) as duree_moyenne_min
FROM dim_operators o
LEFT JOIN facts_night_trains f ON o.operator_id = f.operator_id
GROUP BY o.operator_id, o.operator_name
ORDER BY nb_trains DESC;