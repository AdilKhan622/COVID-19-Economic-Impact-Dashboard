#!/usr/bin/env python3
"""Merge the cleaned country-year datasets without using country names as keys."""

import csv
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED = PROJECT_ROOT / "data" / "processed"
METADATA_PATH = PROCESSED / "country_metadata_clean.csv"
POLICY_PATH = PROCESSED / "oxcgrt_country_year_clean.csv"
MOBILITY_PATH = PROCESSED / "google_mobility_country_year_clean.csv"
OUTPUT_PATH = PROCESSED / "merged_country_year_clean.csv"


def read_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8-sig") as source:
        reader = csv.DictReader(source)
        return list(reader.fieldnames or []), list(reader)


def main() -> None:
    metadata_fields, metadata_rows = read_rows(METADATA_PATH)
    policy_fields, policy_rows = read_rows(POLICY_PATH)
    mobility_fields, mobility_rows = read_rows(MOBILITY_PATH)

    metadata = {row["iso_code"]: row for row in metadata_rows}
    policy = {(row["iso_code"], row["year"]): row for row in policy_rows}
    mobility = {(row["iso_code"], row["year"]): row for row in mobility_rows}
    keys = sorted(set(policy) | set(mobility))

    metadata_payload = [
        field for field in metadata_fields if field not in {"country", "iso_code"}
    ]
    policy_payload = [
        field for field in policy_fields if field not in {"country", "iso_code", "year"}
    ]
    mobility_payload = [
        field
        for field in mobility_fields
        if field not in {"country", "iso_code", "iso2_code", "year"}
    ]
    output_fields = [
        "country",
        "iso_code",
        "year",
        *metadata_payload,
        *policy_payload,
        *mobility_payload,
        "has_policy_data",
        "has_mobility_data",
        "has_world_bank_metadata",
    ]

    with OUTPUT_PATH.open("w", newline="", encoding="utf-8") as destination:
        writer = csv.DictWriter(destination, fieldnames=output_fields)
        writer.writeheader()
        for iso_code, year in keys:
            metadata_row = metadata.get(iso_code, {})
            policy_row = policy.get((iso_code, year), {})
            mobility_row = mobility.get((iso_code, year), {})
            country = (
                metadata_row.get("country")
                or policy_row.get("country")
                or mobility_row.get("country")
                or ""
            )
            row = {"country": country, "iso_code": iso_code, "year": year}
            for field in metadata_payload:
                row[field] = metadata_row.get(field, "")
            for field in policy_payload:
                row[field] = policy_row.get(field, "")
            for field in mobility_payload:
                row[field] = mobility_row.get(field, "")
            row["has_policy_data"] = bool(policy_row)
            row["has_mobility_data"] = bool(mobility_row)
            row["has_world_bank_metadata"] = bool(metadata_row)
            writer.writerow(row)

    print(f"Merged country-year rows: {len(keys)}")
    print(f"Output: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
