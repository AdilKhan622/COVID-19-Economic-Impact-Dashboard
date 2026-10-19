"""Historical benchmark for a cautious no-pandemic GDP growth scenario."""

import pandas as pd


PANDEMIC_YEARS = (2020, 2021, 2022)


def build_growth_counterfactual(data: pd.DataFrame) -> pd.DataFrame:
    """Compare pandemic-year GDP growth with country-specific pre-COVID means.

    Primary benchmark: each country's mean annual real GDP growth in 2015–2019,
    requiring at least four observed years. Sensitivity benchmark: mean growth
    in 2010–2019, requiring at least eight observed years. This is a historical
    scenario, not an identified causal effect or a GDP-level loss estimate.
    """
    required = {"country_code", "year", "real_gdp_growth_pct"}
    missing = required - set(data.columns)
    if missing:
        raise ValueError(f"Missing required counterfactual columns: {sorted(missing)}")

    source = data.copy()
    source["year"] = pd.to_numeric(source["year"], errors="coerce")
    source["real_gdp_growth_pct"] = pd.to_numeric(source["real_gdp_growth_pct"], errors="coerce")
    if source.duplicated(["country_code", "year"]).any():
        raise ValueError("Counterfactual input has duplicate country-year keys")
    # Country-only WDI rows carry World Bank region and income-group metadata;
    # aggregate rows do not and must not enter country comparisons.
    if "region" in source.columns:
        source = source.loc[source["region"].notna()]
    if "income_group" in source.columns:
        source = source.loc[source["income_group"].notna()]

    primary = source.loc[source["year"].between(2015, 2019)].groupby("country_code")["real_gdp_growth_pct"].agg(
        baseline_2015_19_pct="mean", baseline_2015_19_years="count"
    )
    sensitivity = source.loc[source["year"].between(2010, 2019)].groupby("country_code")["real_gdp_growth_pct"].agg(
        baseline_2010_19_pct="mean", baseline_2010_19_years="count"
    )
    pandemic = source.loc[source["year"].isin(PANDEMIC_YEARS), ["country_code", "year", "real_gdp_growth_pct"]].copy()
    result = pandemic.merge(primary, on="country_code", how="left", validate="many_to_one")
    result = result.merge(sensitivity, on="country_code", how="left", validate="many_to_one")
    result = result.rename(columns={"real_gdp_growth_pct": "actual_growth_pct"})
    result = result.loc[
        result["baseline_2015_19_years"].ge(4)
        & result["actual_growth_pct"].notna()
    ].copy()
    result["growth_gap_vs_2015_19_baseline_pp"] = result["actual_growth_pct"] - result["baseline_2015_19_pct"]
    result["growth_gap_vs_2010_19_baseline_pp"] = result["actual_growth_pct"] - result["baseline_2010_19_pct"]
    return result.sort_values(["year", "country_code"]).reset_index(drop=True)
