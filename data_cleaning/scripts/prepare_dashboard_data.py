#!/usr/bin/env python3
"""Integrate the three downloaded WDI indicators with the existing annual master.

Raw World Bank downloads are kept unchanged in ``data/raw``. The original
``merged_master_annual.csv`` is read-only input; this script writes a separate
dashboard dataset and a coverage/quality report.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED = PROJECT_ROOT / "data" / "processed"
RAW_WDI = PROJECT_ROOT / "data" / "raw" / "world_bank" / "economic_indicators"
MASTER_PATH = PROCESSED / "merged_master_annual.csv"
METADATA_PATH = PROCESSED / "country_metadata_clean.csv"
OUTPUT_PATH = PROCESSED / "dashboard_master_annual.csv"
REPORT_PATH = PROJECT_ROOT / "reports" / "dashboard_data_integration.md"

INDICATORS = {
    "NY.GDP.MKTP.KD.ZG": ("real_gdp_growth_pct", "API_NY.GDP.MKTP.KD.ZG_*.csv"),
    "SL.UEM.TOTL.ZS": ("unemployment_rate_pct", "API_SL.UEM.TOTL.ZS_*.csv"),
    "FP.CPI.TOTL.ZG": ("inflation_rate_pct", "API_FP.CPI.TOTL.ZG_*.csv"),
}
KEYS = ["country_code", "year"]


def _only_file(directory: Path, pattern: str) -> Path:
    matches = sorted(directory.glob(pattern))
    if len(matches) != 1:
        raise FileNotFoundError(
            f"Expected exactly one source matching {pattern!r} in {directory}; "
            f"found {len(matches)}."
        )
    return matches[0]


def _read_wdi_long(path: Path, indicator_code: str, value_name: str,
                   valid_country_codes: set[str]) -> tuple[pd.DataFrame, int]:
    # WDI downloads have four preamble lines followed by a wide country/year table.
    raw = pd.read_csv(path, skiprows=4, encoding="utf-8-sig", low_memory=False)
    raw = raw.loc[:, ~raw.columns.astype(str).str.startswith("Unnamed:")]
    required = {"Country Name", "Country Code", "Indicator Code"}
    if not required.issubset(raw.columns):
        raise ValueError(f"Unexpected WDI schema in {path}: missing {required - set(raw.columns)}")
    found_codes = set(raw["Indicator Code"].dropna().astype(str))
    if found_codes != {indicator_code}:
        raise ValueError(f"Expected indicator {indicator_code} in {path}, found {sorted(found_codes)}")

    year_columns = [c for c in raw.columns if re.fullmatch(r"\d{4}", str(c))]
    if not year_columns:
        raise ValueError(f"No annual year columns found in {path}")
    raw_codes = raw["Country Code"].fillna("").astype(str).str.strip().str.upper()
    raw = raw.assign(_country_code=raw_codes)
    aggregate_rows = int((~raw["_country_code"].isin(valid_country_codes)).sum())
    countries = raw.loc[raw["_country_code"].isin(valid_country_codes)]
    long = countries.melt(
        id_vars=["Country Name", "_country_code"],
        value_vars=year_columns,
        var_name="year",
        value_name=value_name,
    )
    long = long.rename(columns={"_country_code": "country_code", "Country Name": "wdi_country_name"})
    long["country_code"] = long["country_code"].str.upper()
    long["year"] = pd.to_numeric(long["year"], errors="raise").astype("int64")
    long[value_name] = pd.to_numeric(long[value_name], errors="coerce")
    long = long.dropna(subset=[value_name])
    if long.duplicated(KEYS).any():
        raise ValueError(f"Duplicate {KEYS} records in {path}")
    return long[[*KEYS, "wdi_country_name", value_name]], aggregate_rows


def _markdown_table(headers: list[str], rows: list[list[object]]) -> list[str]:
    out = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(headers)) + "|"]
    out.extend("| " + " | ".join(str(x) for x in row) + " |" for row in rows)
    return out


def prepare(master_path: Path = MASTER_PATH, metadata_path: Path = METADATA_PATH,
            raw_dir: Path = RAW_WDI, output_path: Path = OUTPUT_PATH,
            report_path: Path = REPORT_PATH) -> tuple[pd.DataFrame, str]:
    master = pd.read_csv(master_path, low_memory=False)
    metadata = pd.read_csv(metadata_path, dtype={"iso_code": str}, low_memory=False)
    if "isocode" not in master or "year" not in master:
        raise ValueError("Master dataset must contain `isocode` and `year` keys.")
    if "iso_code" not in metadata:
        raise ValueError("Country metadata must contain `iso_code`.")

    master = master.rename(columns={"isocode": "country_code"})
    master["country_code"] = master["country_code"].astype(str).str.strip().str.upper()
    master["year"] = pd.to_numeric(master["year"], errors="raise").astype("int64")
    if master.duplicated(KEYS).any():
        raise ValueError("Original master contains duplicate country-year keys.")

    metadata["iso_code"] = metadata["iso_code"].astype(str).str.strip().str.upper()
    valid_country_codes = set(metadata["iso_code"].dropna())
    if metadata["iso_code"].duplicated().any():
        raise ValueError("Country metadata contains duplicate ISO3 codes.")

    indicator_frames: list[pd.DataFrame] = []
    aggregate_counts: dict[str, int] = {}
    source_paths: dict[str, Path] = {}
    for code, (column, pattern) in INDICATORS.items():
        source = _only_file(raw_dir, pattern)
        source_paths[code] = source
        values, aggregate_counts[code] = _read_wdi_long(source, code, column, valid_country_codes)
        values = values.drop(columns="wdi_country_name")
        indicator_frames.append(values)

    economic = indicator_frames[0]
    for values in indicator_frames[1:]:
        economic = economic.merge(values, on=KEYS, how="outer", validate="one_to_one")
    if economic.duplicated(KEYS).any():
        raise ValueError("Integrated World Bank indicators have duplicate country-year keys.")

    original_keys = master[KEYS].copy()
    # Keep the full union so historical World Bank observations remain available,
    # while the policy/COVID fields naturally stay missing outside their source years.
    merged = master.merge(economic, on=KEYS, how="outer", validate="one_to_one", indicator="_master_match")
    code_meta = metadata[[c for c in ["iso_code", "country", "region", "income_group"] if c in metadata.columns]].copy()
    code_meta = code_meta.rename(columns={
        "iso_code": "country_code", "country": "_wdi_country",
        "region": "_wdi_region", "income_group": "_wdi_income_group",
    })
    merged = merged.merge(code_meta, on="country_code", how="left", validate="many_to_one")
    if "country" not in merged:
        merged["country"] = merged["_wdi_country"]
    else:
        merged["country"] = merged["country"].fillna(merged["_wdi_country"])
    for column, fallback in [("region", "_wdi_region"), ("income_group", "_wdi_income_group")]:
        if column in merged:
            merged[column] = merged[column].fillna(merged[fallback])
        elif fallback in merged:
            merged[column] = merged[fallback]
    merged = merged.drop(columns=[c for c in ["_wdi_country", "_wdi_region", "_wdi_income_group"] if c in merged])

    indicator_columns = [value[0] for value in INDICATORS.values()]
    baselines = merged.loc[merged["year"].eq(2019), [*KEYS, *indicator_columns]].copy()
    baselines = baselines.rename(columns={
        "real_gdp_growth_pct": "_gdp_growth_2019",
        "unemployment_rate_pct": "_unemployment_2019",
        "inflation_rate_pct": "_inflation_2019",
    }).drop(columns="year")
    merged = merged.merge(baselines, on="country_code", how="left", validate="many_to_one")
    merged["gdp_growth_deterioration_vs_2019_pp"] = merged["_gdp_growth_2019"] - merged["real_gdp_growth_pct"]
    merged["unemployment_change_vs_2019_pp"] = merged["unemployment_rate_pct"] - merged["_unemployment_2019"]
    merged["inflation_change_vs_2019_pp"] = merged["inflation_rate_pct"] - merged["_inflation_2019"]
    merged = merged.drop(columns=["_gdp_growth_2019", "_unemployment_2019", "_inflation_2019", "_master_match"])
    merged = merged.sort_values(KEYS, kind="stable").reset_index(drop=True)
    if merged.duplicated(KEYS).any():
        raise ValueError("Final dashboard data contains duplicate country-year keys.")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    merged.to_csv(output_path, index=False, na_rep="")

    matched_original = merged.merge(original_keys.assign(_original=True), on=KEYS, how="inner")
    any_indicator = matched_original[indicator_columns].notna().any(axis=1)
    matched_records = int(any_indicator.sum())
    report: list[str] = [
        "# Dashboard Data Integration Report", "",
        "Generated by `Data_cleaning/scripts/prepare_dashboard_data.py`.",
        "The original master and raw World Bank downloads are inputs only and are not overwritten.", "",
        "## Dataset shape and keys", "",
    ]
    report += _markdown_table(["Measure", "Original master", "Dashboard output"], [
        ["Rows", f"{len(master):,}", f"{len(merged):,}"],
        ["Columns", f"{len(master.columns):,}", f"{len(merged.columns):,}"],
        ["Unique ISO3 codes", f"{master['country_code'].nunique():,}", f"{merged['country_code'].nunique():,}"],
        ["Year range", f"{master.year.min()}–{master.year.max()}", f"{merged.year.min()}–{merged.year.max()}"],
        ["Duplicate country-year keys", "0", f"{int(merged.duplicated(KEYS).sum()):,}"],
        ["Original records with ≥1 new indicator", f"{matched_records:,} / {len(master):,} ({matched_records / len(master) * 100:.1f}%)", "n/a"],
    ])
    report += ["", "## Indicator availability", "", "Missing values include years outside the relevant source coverage; no economic values were imputed.", ""]
    availability = []
    for column in indicator_columns:
        present = int(merged[column].notna().sum())
        availability.append([column, f"{present:,}", f"{len(merged) - present:,} ({(len(merged)-present)/len(merged)*100:.1f}%)"])
    report += _markdown_table(["Indicator column", "Non-missing observations", "Missing in final panel"], availability)
    report += ["", "### Coverage by indicator and year", ""]
    for column in indicator_columns:
        counts = merged.loc[merged[column].notna()].groupby("year")["country_code"].nunique()
        report.append(f"**{column}:** " + (", ".join(f"{year}: {count} countries" for year, count in counts.items()) or "no observations"))
    report += ["", "### Country codes in each download not present in the original master", ""]
    master_codes = set(master["country_code"])
    for code, frame in zip(INDICATORS, indicator_frames):
        unmatched = sorted(set(frame["country_code"]) - master_codes)
        report.append(f"- `{code}`: {', '.join(unmatched) if unmatched else 'None'}")
    report += ["", "## Aggregate handling", "", "World Bank rows whose codes are not in the cleaned World Bank country metadata were excluded from the indicator series. This removes regional, income-group, and global aggregates before country rankings.", ""]
    report += _markdown_table(["Indicator", "Aggregate/non-country rows excluded"], [[code, f"{aggregate_counts[code]:,}"] for code in INDICATORS])
    report += ["", "## Derived measures", "",
        "- `gdp_growth_deterioration_vs_2019_pp` = 2019 real GDP growth minus selected-year real GDP growth. A positive value means growth slowed relative to 2019; it is not a fall in GDP level.",
        "- `unemployment_change_vs_2019_pp` = selected-year unemployment rate minus 2019 rate, in percentage points.",
        "- `inflation_change_vs_2019_pp` = selected-year inflation rate minus 2019 rate, in percentage points.",
        "- Where a country lacks a 2019 observation for an indicator, its baseline comparison remains missing.",
        "- Existing `wdi_gdp` is retained as the project's nominal GDP level series and is not used as real GDP growth.", "",
        "## Input files", ""]
    report.extend(f"- `{path.relative_to(PROJECT_ROOT) if path.is_relative_to(PROJECT_ROOT) else path}`" for path in source_paths.values())
    report += ["", f"Final output: `{output_path.relative_to(PROJECT_ROOT) if output_path.is_relative_to(PROJECT_ROOT) else output_path}`.", ""]
    report_text = "\n".join(report)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report_text, encoding="utf-8")
    return merged, report_text


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--master", type=Path, default=MASTER_PATH)
    parser.add_argument("--metadata", type=Path, default=METADATA_PATH)
    parser.add_argument("--raw-dir", type=Path, default=RAW_WDI)
    parser.add_argument("--output", type=Path, default=OUTPUT_PATH)
    parser.add_argument("--report", type=Path, default=REPORT_PATH)
    args = parser.parse_args()
    data, _ = prepare(args.master, args.metadata, args.raw_dir, args.output, args.report)
    print(f"Wrote dashboard data: {args.output} ({len(data):,} rows, {len(data.columns)} columns)")
    print(f"Wrote integration report: {args.report}")


if __name__ == "__main__":
    main()
