#!/usr/bin/env python3
"""Create clean country-day and country-year OxCGRT datasets."""

import csv
from collections import defaultdict
from datetime import datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = (
    PROJECT_ROOT / "data" / "raw" / "oxcgrt" / "OxCGRT_compact_national_v1.csv"
)
DAILY_OUTPUT = (
    PROJECT_ROOT / "data" / "interim" / "oxcgrt_country_day_clean.csv"
)
ANNUAL_OUTPUT = (
    PROJECT_ROOT / "data" / "processed" / "oxcgrt_country_year_clean.csv"
)

SOURCE_COLUMNS = {
    "C1M_School closing": "school_closing",
    "C2M_Workplace closing": "workplace_closing",
    "C6M_Stay at home requirements": "stay_home_requirements",
    "C8EV_International travel controls": "international_travel_controls",
    "StringencyIndex_Average": "stringency_index",
    "GovernmentResponseIndex_Average": "government_response_index",
    "ContainmentHealthIndex_Average": "containment_health_index",
    "EconomicSupportIndex": "economic_support_index",
}

# OxCGRT uses RKS for Kosovo, while the World Bank metadata uses XKX.
# Canonicalizing it here prevents a false non-match during merging.
COUNTRY_CODE_CROSSWALK = {"RKS": "XKX"}


def to_number(value: str) -> float | None:
    value = value.strip()
    return None if value == "" else float(value)


def main() -> None:
    DAILY_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    ANNUAL_OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    daily_fields = [
        "country",
        "iso_code",
        "date",
        "year",
        *SOURCE_COLUMNS.values(),
    ]
    annual = defaultdict(
        lambda: {
            "country": "",
            "dates": set(),
            "values": {
                cleaned_name: [] for cleaned_name in SOURCE_COLUMNS.values()
            },
        }
    )
    seen_keys = set()
    input_rows = 0
    output_rows = 0

    with INPUT_PATH.open(newline="", encoding="utf-8-sig") as source, DAILY_OUTPUT.open(
        "w", newline="", encoding="utf-8"
    ) as destination:
        reader = csv.DictReader(source)
        writer = csv.DictWriter(destination, fieldnames=daily_fields)
        writer.writeheader()

        for source_row in reader:
            input_rows += 1
            if source_row["Jurisdiction"] != "NAT_TOTAL":
                continue

            parsed_date = datetime.strptime(source_row["Date"], "%Y%m%d").date()
            source_iso_code = source_row["CountryCode"].strip()
            iso_code = COUNTRY_CODE_CROSSWALK.get(source_iso_code, source_iso_code)
            key = (iso_code, parsed_date.isoformat())
            if key in seen_keys:
                raise ValueError(f"Duplicate OxCGRT country-date key: {key}")
            seen_keys.add(key)

            clean_row = {
                "country": source_row["CountryName"].strip(),
                "iso_code": iso_code,
                "date": parsed_date.isoformat(),
                "year": parsed_date.year,
            }
            for source_name, clean_name in SOURCE_COLUMNS.items():
                clean_row[clean_name] = to_number(source_row[source_name])

            writer.writerow(clean_row)
            output_rows += 1

            annual_key = (iso_code, parsed_date.year)
            group = annual[annual_key]
            group["country"] = clean_row["country"]
            group["dates"].add(parsed_date)
            for clean_name in SOURCE_COLUMNS.values():
                value = clean_row[clean_name]
                if value is not None:
                    group["values"][clean_name].append(value)

    annual_fields = [
        "country",
        "iso_code",
        "year",
        *[f"{name}_avg" for name in SOURCE_COLUMNS.values()],
        "policy_days_observed",
        "policy_period_start",
        "policy_period_end",
    ]
    with ANNUAL_OUTPUT.open("w", newline="", encoding="utf-8") as destination:
        writer = csv.DictWriter(destination, fieldnames=annual_fields)
        writer.writeheader()
        for (iso_code, year), group in sorted(annual.items()):
            dates = group["dates"]
            row = {
                "country": group["country"],
                "iso_code": iso_code,
                "year": year,
                "policy_days_observed": len(dates),
                "policy_period_start": min(dates).isoformat(),
                "policy_period_end": max(dates).isoformat(),
            }
            for name, values in group["values"].items():
                row[f"{name}_avg"] = (
                    round(sum(values) / len(values), 4) if values else None
                )
            writer.writerow(row)

    print(f"Raw rows read: {input_rows}")
    print(f"Clean national daily rows: {output_rows}")
    print(f"Country-year rows: {len(annual)}")
    print(f"Daily output: {DAILY_OUTPUT}")
    print(f"Annual output: {ANNUAL_OUTPUT}")


if __name__ == "__main__":
    main()
