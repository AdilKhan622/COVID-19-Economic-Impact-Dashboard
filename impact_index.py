"""Exploratory, equal-weight economic strain index for pandemic years."""

import pandas as pd


INDEX_YEARS = (2020, 2021, 2022)
COMPONENT_COLUMNS = (
    "gdp_growth_deterioration_vs_2019_pp",
    "unemployment_change_vs_2019_pp",
    "inflation_change_vs_2019_pp",
)
STANDARDIZED_COLUMNS = (
    "gdp_deterioration_z",
    "unemployment_increase_z",
    "inflation_pressure_z",
)


def build_economic_strain_index(data: pd.DataFrame) -> pd.DataFrame:
    """Build a complete-case, pooled-standardized index for 2020–2022.

    Components are: GDP growth deterioration versus 2019; unemployment change
    versus 2019; and positive inflation increase versus 2019 (negative inflation
    changes contribute zero inflation pressure). All are oriented so higher
    values represent a larger adverse change. Each component is z-scored over
    the same complete country-year sample pooled across 2020–2022, then given
    equal weight. This is an exploratory summary, not a causal effect or an
    official measure of total economic cost.
    """
    required = {"country_code", "year", *COMPONENT_COLUMNS}
    missing = required - set(data.columns)
    if missing:
        raise ValueError(f"Missing required impact-index columns: {sorted(missing)}")

    frame = data.copy()
    frame["year"] = pd.to_numeric(frame["year"], errors="coerce")
    for column in COMPONENT_COLUMNS:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
    if frame.duplicated(["country_code", "year"]).any():
        raise ValueError("Impact-index input has duplicate country-year keys")

    frame = frame.loc[frame["year"].isin(INDEX_YEARS)].copy()
    # Only country observations with World Bank geographic and income metadata
    # are eligible, which prevents aggregate rows entering the country index.
    if "region" in frame:
        frame = frame.loc[frame["region"].notna()]
    if "income_group" in frame:
        frame = frame.loc[frame["income_group"].notna()]

    inflation_pressure = frame["inflation_change_vs_2019_pp"].clip(lower=0)
    oriented = {
        "gdp_deterioration_pp": frame["gdp_growth_deterioration_vs_2019_pp"],
        "unemployment_increase_pp": frame["unemployment_change_vs_2019_pp"],
        "inflation_pressure_pp": inflation_pressure,
    }
    values = pd.DataFrame(oriented, index=frame.index)
    complete = values.notna().all(axis=1)
    frame = frame.loc[complete].copy()
    values = values.loc[complete]
    if frame.empty:
        return pd.DataFrame(columns=[
            "country_code", "year", *oriented.keys(), *STANDARDIZED_COLUMNS,
            "economic_strain_index", "index_sample_n",
        ])

    means = values.mean()
    standard_deviations = values.std(ddof=0)
    zero_variance = standard_deviations.index[standard_deviations.eq(0)].tolist()
    if zero_variance:
        raise ValueError(f"Cannot standardize zero-variance index components: {zero_variance}")
    z_scores = (values - means) / standard_deviations
    z_scores.columns = STANDARDIZED_COLUMNS
    frame = pd.concat([frame, values, z_scores], axis=1)
    frame["economic_strain_index"] = frame.loc[:, STANDARDIZED_COLUMNS].mean(axis=1)
    frame["index_sample_n"] = len(frame)
    return frame.sort_values(["year", "country_code"]).reset_index(drop=True)
