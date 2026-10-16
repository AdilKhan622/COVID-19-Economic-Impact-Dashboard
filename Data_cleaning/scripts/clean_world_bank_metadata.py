#!/usr/bin/env python3
"""Clean World Bank country metadata for country-level dataset joins."""

import csv
import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = PROJECT_ROOT / "data" / "raw" / "world_bank" / "countries.json"
OUTPUT_PATH = (
    PROJECT_ROOT / "data" / "processed" / "country_metadata_clean.csv"
)


def main() -> None:
    with INPUT_PATH.open(encoding="utf-8-sig") as source:
        _, records = json.load(source)

    # The API also returns aggregates such as "World" and income groups.
    # Their region id is "NA", so they are not country/economy observations.
    countries = [record for record in records if record["region"]["id"] != "NA"]

    cleaned = []
    for record in countries:
        cleaned.append(
            {
                "country": record["name"].strip(),
                "iso_code": record["id"].strip(),
                "iso2_code": record["iso2Code"].strip(),
                "region": record["region"]["value"].strip(),
                "income_group": record["incomeLevel"]["value"].strip(),
                "capital_city": record["capitalCity"].strip(),
                "longitude": record["longitude"].strip(),
                "latitude": record["latitude"].strip(),
            }
        )

    cleaned.sort(key=lambda row: row["iso_code"])

    iso3_codes = [row["iso_code"] for row in cleaned]
    if any(not code for code in iso3_codes):
        raise ValueError("A country/economy record is missing its ISO-3 code")
    if len(iso3_codes) != len(set(iso3_codes)):
        raise ValueError("Duplicate ISO-3 codes found in country metadata")

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", newline="", encoding="utf-8") as destination:
        writer = csv.DictWriter(destination, fieldnames=list(cleaned[0]))
        writer.writeheader()
        writer.writerows(cleaned)

    print(f"Raw API records: {len(records)}")
    print(f"Removed aggregate records: {len(records) - len(cleaned)}")
    print(f"Clean country/economy records: {len(cleaned)}")
    print(f"Unique ISO-3 codes: {len(set(iso3_codes))}")
    print(f"Output: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
