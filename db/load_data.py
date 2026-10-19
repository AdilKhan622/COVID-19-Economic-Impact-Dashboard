"""Load annual policy/mobility and daily OxCGRT data into MySQL.
Usage (from the repository root, with the conda env active):

    1. Set credentials (PowerShell):
           $env:DB_USER="root"
           $env:DB_PASSWORD="your_password"
           # optional: DB_HOST (localhost), DB_PORT (3306), DB_NAME (covid)
    2. Run:                 python db/load_data.py
       Validate CSVs only:  python db/load_data.py --check

The import replaces country_year and upserts country metadata and daily
stringency values in one transaction. Other daily COVID and economic columns
are preserved. Override the CSV locations with the corresponding environment
variables if needed.
"""

import argparse
import os
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

ROOT = Path(__file__).resolve().parent.parent
PROCESSED_DIR = Path(os.getenv(
    "PROCESSED_DATA_DIR",
    str(ROOT / "Data_cleaning" / "data" / "processed"),
))
INTERIM_DIR = Path(os.getenv(
    "INTERIM_DATA_DIR",
    str(ROOT / "Data_cleaning" / "data" / "interim"),
))

COUNTRY_FIELDS = [
    "iso_code", "name", "iso2_code", "region", "income_group",
    "capital_city", "longitude", "latitude",
]
YEAR_FIELDS = [
    "iso_code", "year", "school_closing_avg", "workplace_closing_avg",
    "stay_home_requirements_avg", "international_travel_controls_avg",
    "stringency_index_avg", "government_response_index_avg",
    "containment_health_index_avg", "economic_support_index_avg",
    "policy_days_observed", "policy_period_start", "policy_period_end",
    "mobility_retail_and_recreation_avg",
    "mobility_grocery_and_pharmacy_avg", "mobility_parks_avg",
    "mobility_transit_stations_avg", "mobility_workplaces_avg",
    "mobility_residential_avg", "mobility_rows_observed",
    "mobility_days_with_any_value", "source_period_start",
    "source_period_end", "source_period_days", "mobility_coverage_pct",
    "partial_year", "has_policy_data", "has_mobility_data",
    "has_world_bank_metadata",
]
DATE_FIELDS = [
    "policy_period_start", "policy_period_end", "source_period_start",
    "source_period_end",
]
BOOLEAN_FIELDS = [
    "partial_year", "has_policy_data", "has_mobility_data",
    "has_world_bank_metadata",
]
NUMERIC_FIELDS = [
    field for field in YEAR_FIELDS
    if field not in {"iso_code", "year", *DATE_FIELDS, *BOOLEAN_FIELDS}
]


def get_engine():
    """Build the SQLAlchemy engine from environment variables."""
    url = URL.create(
        "mysql+pymysql",
        username=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "3306")),
        database=os.getenv("DB_NAME", "covid"),
        query={"charset": "utf8mb4"},
    )
    return create_engine(url)


def read_processed(filename, required):
    path = PROCESSED_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Missing file: {path}")
    df = pd.read_csv(path)
    missing = set(required) - set(df.columns)
    if missing:
        raise ValueError(f"{filename}: missing columns {sorted(missing)}")
    return df


def read_interim(filename, required):
    path = INTERIM_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Missing file: {path}")
    df = pd.read_csv(path)
    missing = set(required) - set(df.columns)
    if missing:
        raise ValueError(f"{filename}: missing columns {sorted(missing)}")
    return df


def validate_iso_codes(df, label):
    df["iso_code"] = df["iso_code"].astype("string").str.strip().str.upper()
    valid = df["iso_code"].str.fullmatch(r"[A-Z]{3}").fillna(False)
    if not valid.all():
        raise ValueError(f"{label}: found invalid ISO alpha-3 country codes")


def prepare_data():
    countries = read_processed(
        "country_metadata_clean.csv",
        ["country", "iso_code", "iso2_code", "region", "income_group",
         "capital_city", "longitude", "latitude"],
    ).rename(columns={"country": "name"})
    annual = read_processed(
        "merged_country_year_clean.csv",
        ["country", "iso2_code", "region", "income_group", "capital_city",
         "longitude", "latitude", *YEAR_FIELDS],
    )
    daily = read_interim(
        "oxcgrt_country_day_clean.csv", ["iso_code", "date", "stringency_index"]
    )

    validate_iso_codes(countries, "country metadata")
    validate_iso_codes(annual, "merged country-year data")
    validate_iso_codes(daily, "OxCGRT daily data")
    if countries["iso_code"].duplicated().any():
        raise ValueError("country metadata contains duplicate iso_code values")
    if annual.duplicated(subset=["iso_code", "year"]).any():
        raise ValueError("merged country-year data contains duplicate iso_code/year rows")

    missing_metadata = ~annual["iso_code"].isin(countries["iso_code"])
    if missing_metadata.any():
        fallback = (
            annual.loc[missing_metadata,
                       ["country", "iso_code", "iso2_code", "region",
                        "income_group", "capital_city", "longitude", "latitude"]]
            .drop_duplicates(subset="iso_code")
            .rename(columns={"country": "name"})
        )
        countries = pd.concat([countries, fallback], ignore_index=True)

    unknown_countries = sorted(set(annual["iso_code"]) - set(countries["iso_code"]))
    if unknown_countries:
        raise ValueError(f"country-year data has codes missing from metadata: {unknown_countries}")
    unknown_daily_countries = sorted(set(daily["iso_code"]) - set(countries["iso_code"]))
    if unknown_daily_countries:
        raise ValueError(f"OxCGRT daily data has codes missing from metadata: {unknown_daily_countries}")

    if daily.duplicated(subset=["iso_code", "date"]).any():
        raise ValueError("OxCGRT daily data contains duplicate iso_code/date rows")
    daily["date"] = pd.to_datetime(daily["date"], errors="coerce")
    if daily["date"].isna().any():
        raise ValueError("OxCGRT daily data contains invalid dates")
    daily["date"] = daily["date"].dt.date
    raw_stringency = daily["stringency_index"]
    daily["stringency_index"] = pd.to_numeric(raw_stringency, errors="coerce")
    invalid_stringency = raw_stringency.notna() & daily["stringency_index"].isna()
    if invalid_stringency.any():
        raise ValueError("OxCGRT daily data contains non-numeric stringency values")
    out_of_range = daily["stringency_index"].notna() & ~daily["stringency_index"].between(0, 100)
    if out_of_range.any():
        raise ValueError("OxCGRT daily stringency values must be between 0 and 100")
    daily = daily.dropna(subset=["stringency_index"])

    annual["year"] = pd.to_numeric(annual["year"], errors="raise").astype(int)
    for field in NUMERIC_FIELDS:
        annual[field] = pd.to_numeric(annual[field], errors="raise")
    for field in DATE_FIELDS:
        annual[field] = pd.to_datetime(annual[field], errors="coerce").dt.date
    for field in BOOLEAN_FIELDS:
        if not pd.api.types.is_bool_dtype(annual[field]):
            values = annual[field].astype("string").str.lower()
            parsed = values.map({"true": True, "false": False, "1": True, "0": False})
            invalid = values.notna() & parsed.isna()
            if invalid.any():
                raise ValueError(f"merged country-year data has invalid {field} values")
            annual[field] = parsed

    return countries, annual, daily


def records_without_nulls(df):
    return df.astype(object).where(pd.notna(df), None).to_dict("records")


def insert(conn, table, df):
    """Append a DataFrame to a table (NaN becomes NULL)."""
    if df.empty:
        print(f"  {table}: nothing to insert")
        return
    df.to_sql(table, con=conn, if_exists="append", index=False,
              method="multi", chunksize=5000)
    print(f"  {table}: {len(df):,} rows inserted")


# Main
def main(check_only=False):
    countries, annual, daily = prepare_data()
    print(
        f"Validated {len(countries):,} countries, {len(annual):,} country-year rows, "
        f"and {len(daily):,} daily stringency rows."
    )
    if check_only:
        return

    country_rows = countries[COUNTRY_FIELDS].copy()
    country_rows.insert(2, "continent", None)
    country_rows.insert(5, "population", None)
    country_rows = records_without_nulls(country_rows)
    annual_rows = annual[YEAR_FIELDS].copy()
    annual_rows = annual_rows.astype(object).where(pd.notna(annual_rows), None)
    daily_rows = records_without_nulls(
        daily[["iso_code", "date", "stringency_index"]]
    )

    country_upsert = text("""
        INSERT INTO country
            (iso_code, name, continent, region, income_group, population,
             iso2_code, capital_city, longitude, latitude)
        VALUES
            (:iso_code, :name, :continent, :region, :income_group, :population,
             :iso2_code, :capital_city, :longitude, :latitude)
        ON DUPLICATE KEY UPDATE
            name = VALUES(name), region = VALUES(region),
            income_group = VALUES(income_group), iso2_code = VALUES(iso2_code),
            capital_city = VALUES(capital_city), longitude = VALUES(longitude),
            latitude = VALUES(latitude)
    """)
    daily_upsert = text("""
        INSERT INTO covid_daily (iso_code, date, stringency_index)
        VALUES (:iso_code, :date, :stringency_index)
        ON DUPLICATE KEY UPDATE
            stringency_index = VALUES(stringency_index)
    """)

    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM country_year"))
        conn.execute(country_upsert, country_rows)
        annual_rows.to_sql(
            "country_year", con=conn, if_exists="append", index=False,
            method="multi", chunksize=500,
        )
        for start in range(0, len(daily_rows), 5000):
            conn.execute(daily_upsert, daily_rows[start:start + 5000])

    print("Imported country metadata, country_year rows, and daily stringency values.")
    with engine.connect() as conn:
        for table in ("country", "country_year", "covid_daily"):
            count = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
            print(f"  {table:<15} {count:>10,}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="validate CSVs without connecting to MySQL")
    args = parser.parse_args()
    main(check_only=args.check)