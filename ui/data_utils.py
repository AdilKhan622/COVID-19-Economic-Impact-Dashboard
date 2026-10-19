"""Small shared data helpers used by the Dash pages."""

from functools import lru_cache
from pathlib import Path

import pandas as pd
from impact_index import build_economic_strain_index


DATA_PATH = Path(__file__).resolve().parent / "Data_cleaning" / "data" / "processed" / "dashboard_master_annual.csv"
VALUE_COLUMNS = [
    "real_gdp_growth_pct", "unemployment_rate_pct", "inflation_rate_pct",
    "totalcases", "totaldeaths", "newcases", "newdeaths", "population",
    "stringency_index_avg", "economic_support_index_avg", "mobility_workplaces_avg",
    "gdp_growth_deterioration_vs_2019_pp", "unemployment_change_vs_2019_pp",
    "inflation_change_vs_2019_pp",
]


@lru_cache(maxsize=1)
def load_data() -> pd.DataFrame:
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Dashboard data is missing at {DATA_PATH}. Run "
            "python Data_cleaning/scripts/prepare_dashboard_data.py first."
        )
    data = pd.read_csv(DATA_PATH, low_memory=False)
    data["country_code"] = data["country_code"].astype(str).str.upper()
    data["year"] = pd.to_numeric(data["year"], errors="coerce").astype("Int64")
    for column in VALUE_COLUMNS:
        if column in data:
            data[column] = pd.to_numeric(data[column], errors="coerce")
    return data


@lru_cache(maxsize=1)
def load_impact_index() -> pd.DataFrame:
    """Cache scores calculated once against the full 2020–2022 sample."""
    return build_economic_strain_index(load_data())


def filtered_data(year=None, region=None, income_group=None) -> pd.DataFrame:
    data = load_data()
    if year not in (None, "all", ""):
        data = data.loc[data["year"].eq(int(year))]
    if region not in (None, "all", "") and "region" in data:
        data = data.loc[data["region"].eq(region)]
    if income_group not in (None, "all", "") and "income_group" in data:
        data = data.loc[data["income_group"].eq(income_group)]
    return data


def country_label(row) -> str:
    return str(row.get("country") or row.get("countryname") or row.get("country_code"))


def country_options() -> list[dict[str, str]]:
    data = load_data()
    latest = data.sort_values("year").drop_duplicates("country_code", keep="last")
    return [
        {"label": f"{country_label(row)} ({row['country_code']})", "value": row["country_code"]}
        for _, row in latest.sort_values("country_code").iterrows()
        if pd.notna(row.get("country_code"))
    ]


def empty_message(message: str) -> str:
    return message
