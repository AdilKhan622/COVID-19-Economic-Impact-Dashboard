-- COVID-19 & the Global Economy: MySQL schema (3NF)
-- Run:  mysql -u <user> -p -e "source db/schema.sql"
-- WARNING: this script DROPS and recreates all tables (safe to re-run
-- during development, but it erases loaded data).
-- Requires MySQL 8.0.16+ (CHECK constraints are enforced from that version).
CREATE DATABASE IF NOT EXISTS covid CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE covid;
DROP TABLE IF EXISTS economic_value;
DROP TABLE IF EXISTS country_year;
DROP TABLE IF EXISTS covid_daily;
DROP TABLE IF EXISTS indicator;
DROP TABLE IF EXISTS source;
DROP TABLE IF EXISTS country;
-- country: one row per country, attributes stored once
-- iso_code is the ISO 3166-1 alpha-3 code (e.g. FRA, DEU, USA).
-- Aggregates such as OWID_WRL (World) are NOT stored here.
CREATE TABLE country (
    iso_code CHAR(3) NOT NULL,
    name VARCHAR(100) NOT NULL,
    continent VARCHAR(50),
    region VARCHAR(100),
    income_group VARCHAR(50),
    population BIGINT UNSIGNED,
    iso2_code CHAR(2),
    capital_city VARCHAR(100),
    longitude DECIMAL(10, 6),
    latitude DECIMAL(10, 6),
    PRIMARY KEY (iso_code)
) ENGINE = InnoDB;
CREATE TABLE country_year (
    iso_code CHAR(3) NOT NULL,
    year SMALLINT UNSIGNED NOT NULL,
    school_closing_avg DECIMAL(8, 4),
    workplace_closing_avg DECIMAL(8, 4),
    stay_home_requirements_avg DECIMAL(8, 4),
    international_travel_controls_avg DECIMAL(8, 4),
    stringency_index_avg DECIMAL(8, 4),
    government_response_index_avg DECIMAL(8, 4),
    containment_health_index_avg DECIMAL(8, 4),
    economic_support_index_avg DECIMAL(8, 4),
    policy_days_observed INT UNSIGNED,
    policy_period_start DATE,
    policy_period_end DATE,
    mobility_retail_and_recreation_avg DECIMAL(9, 4),
    mobility_grocery_and_pharmacy_avg DECIMAL(9, 4),
    mobility_parks_avg DECIMAL(9, 4),
    mobility_transit_stations_avg DECIMAL(9, 4),
    mobility_workplaces_avg DECIMAL(9, 4),
    mobility_residential_avg DECIMAL(9, 4),
    mobility_rows_observed INT UNSIGNED,
    mobility_days_with_any_value INT UNSIGNED,
    source_period_start DATE,
    source_period_end DATE,
    source_period_days INT UNSIGNED,
    mobility_coverage_pct DECIMAL(6, 2),
    partial_year BOOLEAN,
    has_policy_data BOOLEAN NOT NULL DEFAULT FALSE,
    has_mobility_data BOOLEAN NOT NULL DEFAULT FALSE,
    has_world_bank_metadata BOOLEAN NOT NULL DEFAULT FALSE,
    PRIMARY KEY (iso_code, year),
    KEY idx_country_year_year (year),
    CONSTRAINT fk_country_year_country FOREIGN KEY (iso_code) REFERENCES country (iso_code) ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE = InnoDB;
-- source: provenance of every indicator (supports transparency)
CREATE TABLE source (
    source_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    name VARCHAR(150) NOT NULL,
    url VARCHAR(500),
    license VARCHAR(100),
    retrieved_on DATE,
    PRIMARY KEY (source_id),
    UNIQUE KEY uq_source_name (name)
) ENGINE = InnoDB;
-- indicator: describes each economic / policy / health series
-- (e.g. gdp_growth, unemployment_rate, trade_volume, inflation)
CREATE TABLE indicator (
    indicator_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    code VARCHAR(50) NOT NULL,
    name VARCHAR(150) NOT NULL,
    unit VARCHAR(50),
    category ENUM('health', 'economic', 'policy') NOT NULL,
    frequency ENUM('daily', 'monthly', 'quarterly', 'annual') NOT NULL,
    source_id INT UNSIGNED NOT NULL,
    PRIMARY KEY (indicator_id),
    UNIQUE KEY uq_indicator_code (code),
    CONSTRAINT fk_indicator_source FOREIGN KEY (source_id) REFERENCES source (source_id) ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE = InnoDB;
-- covid_daily: daily pandemic and policy measures per country
-- Counts are signed because source data contains negative corrections.
CREATE TABLE covid_daily (
    iso_code CHAR(3) NOT NULL,
    date DATE NOT NULL,
    new_cases BIGINT,
    new_deaths BIGINT,
    people_vaccinated BIGINT UNSIGNED,
    stringency_index DECIMAL(5, 2),
    PRIMARY KEY (iso_code, date),
    KEY idx_covid_date (date),
    CONSTRAINT fk_covid_country FOREIGN KEY (iso_code) REFERENCES country (iso_code) ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT chk_stringency CHECK (
        stringency_index IS NULL
        OR stringency_index BETWEEN 0 AND 100
    )
) ENGINE = InnoDB;
-- economic_value: long-format economic observations
-- period = first day of the observed period (2020-01-01 for Q1 2020,
-- 2020-03-01 for March 2020, 2020-01-01 for year 2020).
CREATE TABLE economic_value (
    iso_code CHAR(3) NOT NULL,
    indicator_id INT UNSIGNED NOT NULL,
    period DATE NOT NULL,
    value DECIMAL(18, 4),
    PRIMARY KEY (iso_code, indicator_id, period),
    KEY idx_econ_indicator_period (indicator_id, period),
    CONSTRAINT fk_econ_country FOREIGN KEY (iso_code) REFERENCES country (iso_code) ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_econ_indicator FOREIGN KEY (indicator_id) REFERENCES indicator (indicator_id) ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE = InnoDB;
-- +++++++++++++++++++++++++++++
-- Example queries to test the database after loading
-- 1) Ten worst GDP growth values in 2020
-- SELECT c.name, e.period, e.value AS gdp_growth
-- FROM economic_value e
-- JOIN country   c ON c.iso_code = e.iso_code
-- JOIN indicator i ON i.indicator_id = e.indicator_id
-- WHERE i.code = 'gdp_growth'
--   AND e.period BETWEEN '2020-01-01' AND '2020-12-31'
-- ORDER BY e.value ASC
-- LIMIT 10;
-- 2) Pandemic severity vs economic outcome per country, 2020
-- SELECT c.name,
--        SUM(d.new_deaths)           AS deaths_2020,
--        ROUND(AVG(d.stringency_index), 1) AS avg_stringency_2020,
--        (SELECT AVG(e.value)
--           FROM economic_value e
--           JOIN indicator i ON i.indicator_id = e.indicator_id
--          WHERE e.iso_code = c.iso_code
--            AND i.code = 'gdp_growth'
--            AND e.period BETWEEN '2020-01-01' AND '2020-12-31') AS avg_gdp_growth_2020
-- FROM country c
-- JOIN covid_daily d ON d.iso_code = c.iso_code
-- WHERE d.date BETWEEN '2020-01-01' AND '2020-12-31'
-- GROUP BY c.iso_code, c.name
-- ORDER BY deaths_2020 DESC
-- LIMIT 10;
-- 3) Row counts per table
-- SELECT 'country' AS tbl, COUNT(*) AS n FROM country
-- UNION ALL SELECT 'source', COUNT(*) FROM source
-- UNION ALL SELECT 'indicator', COUNT(*) FROM indicator
-- UNION ALL SELECT 'covid_daily', COUNT(*) FROM covid_daily
-- UNION ALL SELECT 'economic_value', COUNT(*) FROM economic_value;