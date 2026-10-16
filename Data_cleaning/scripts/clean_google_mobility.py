#!/usr/bin/env python3
"""Create clean country-day and country-year Google Mobility datasets."""

import csv
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MOBILITY_INPUT = (
    PROJECT_ROOT / "data" / "raw" / "google_mobility" / "mobility.csv"
)
INDEX_INPUT = PROJECT_ROOT / "data" / "raw" / "google_mobility" / "index.csv"
DAILY_OUTPUT = (
    PROJECT_ROOT / "data" / "interim" / "google_mobility_country_day_clean.csv"
)
ANNUAL_OUTPUT = (
    PROJECT_ROOT / "data" / "processed" / "google_mobility_country_year_clean.csv"
)

MOBILITY_COLUMNS = [
    "mobility_retail_and_recreation",
    "mobility_grocery_and_pharmacy",
    "mobility_parks",
    "mobility_transit_stations",
    "mobility_workplaces",
    "mobility_residential",
]

# Google uses RKS for Kosovo, while the World Bank metadata uses XKX.
COUNTRY_CODE_CROSSWALK = {"RKS": "XKX"}


def to_number(value: str) -> float | None:
    value = value.strip()
    return None if value == "" else float(value)


def inclusive_days(start: date, end: date) -> int:
    return (end - start).days + 1


def main() -> None:
    DAILY_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    ANNUAL_OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    country_index = {}
    with INDEX_INPUT.open(newline="", encoding="utf-8-sig") as source:
        for row in csv.DictReader(source):
            if row["aggregation_level"] == "0":
                source_iso_code = row["iso_3166_1_alpha_3"].strip()
                country_index[row["location_key"]] = {
                    "country": row["country_name"].strip(),
                    "iso2_code": row["iso_3166_1_alpha_2"].strip(),
                    "iso_code": COUNTRY_CODE_CROSSWALK.get(
                        source_iso_code, source_iso_code
                    ),
                }

    daily_fields = [
        "country",
        "iso_code",
        "iso2_code",
        "date",
        "year",
        *MOBILITY_COLUMNS,
    ]
    annual = defaultdict(
        lambda: {
            "country": "",
            "iso2_code": "",
            "dates": set(),
            "dates_with_any_value": set(),
            "values": {column: [] for column in MOBILITY_COLUMNS},
        }
    )
    source_year_bounds = {}
    seen_keys = set()
    raw_rows = 0
    country_rows = 0

    with MOBILITY_INPUT.open(newline="", encoding="utf-8-sig") as source, DAILY_OUTPUT.open(
        "w", newline="", encoding="utf-8"
    ) as destination:
        reader = csv.DictReader(source)
        writer = csv.DictWriter(destination, fieldnames=daily_fields)
        writer.writeheader()

        for source_row in reader:
            raw_rows += 1
            metadata = country_index.get(source_row["location_key"])
            if metadata is None:
                continue
            if not metadata["iso_code"]:
                raise ValueError(
                    f"Country-level Google key lacks ISO-3: {source_row['location_key']}"
                )

            parsed_date = datetime.strptime(source_row["date"], "%Y-%m-%d").date()
            key = (metadata["iso_code"], parsed_date.isoformat())
            if key in seen_keys:
                raise ValueError(f"Duplicate mobility country-date key: {key}")
            seen_keys.add(key)

            clean_row = {
                **metadata,
                "date": parsed_date.isoformat(),
                "year": parsed_date.year,
            }
            for column in MOBILITY_COLUMNS:
                clean_row[column] = to_number(source_row[column])
            writer.writerow(clean_row)
            country_rows += 1

            bounds = source_year_bounds.setdefault(
                parsed_date.year, [parsed_date, parsed_date]
            )
            bounds[0] = min(bounds[0], parsed_date)
            bounds[1] = max(bounds[1], parsed_date)

            annual_key = (metadata["iso_code"], parsed_date.year)
            group = annual[annual_key]
            group["country"] = metadata["country"]
            group["iso2_code"] = metadata["iso2_code"]
            group["dates"].add(parsed_date)
            has_value = False
            for column in MOBILITY_COLUMNS:
                value = clean_row[column]
                if value is not None:
                    group["values"][column].append(value)
                    has_value = True
            if has_value:
                group["dates_with_any_value"].add(parsed_date)

    annual_fields = [
        "country",
        "iso_code",
        "iso2_code",
        "year",
        *[f"{column}_avg" for column in MOBILITY_COLUMNS],
        "mobility_rows_observed",
        "mobility_days_with_any_value",
        "source_period_start",
        "source_period_end",
        "source_period_days",
        "mobility_coverage_pct",
        "partial_year",
    ]
    with ANNUAL_OUTPUT.open("w", newline="", encoding="utf-8") as destination:
        writer = csv.DictWriter(destination, fieldnames=annual_fields)
        writer.writeheader()
        for (iso_code, year), group in sorted(annual.items()):
            source_start, source_end = source_year_bounds[year]
            source_days = inclusive_days(source_start, source_end)
            days_with_values = len(group["dates_with_any_value"])
            row = {
                "country": group["country"],
                "iso_code": iso_code,
                "iso2_code": group["iso2_code"],
                "year": year,
                "mobility_rows_observed": len(group["dates"]),
                "mobility_days_with_any_value": days_with_values,
                "source_period_start": source_start.isoformat(),
                "source_period_end": source_end.isoformat(),
                "source_period_days": source_days,
                "mobility_coverage_pct": round(days_with_values / source_days * 100, 2),
                "partial_year": year in {2020, 2022},
            }
            for column, values in group["values"].items():
                row[f"{column}_avg"] = (
                    round(sum(values) / len(values), 4) if values else None
                )
            writer.writerow(row)

    print(f"Raw rows read: {raw_rows}")
    print(f"Country-level daily rows: {country_rows}")
    print(f"Country-year rows: {len(annual)}")
    print(f"Daily output: {DAILY_OUTPUT}")
    print(f"Annual output: {ANNUAL_OUTPUT}")


if __name__ == "__main__":
    main()
