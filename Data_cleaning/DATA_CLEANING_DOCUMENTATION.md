# Nour's Data-Cleaning Documentation

## 1. Scope of Nour's assignment

Based on the group's allocation, Nour is responsible for cleaning:

1. Oxford COVID-19 Government Response Tracker (OxCGRT)
2. Google COVID-19 Community Mobility data
3. World Bank country metadata

The World Bank economic indicators, IMF WEO, OWID COVID-19 data, and Mendeley dataset are assigned to Anushka and are not processed here.

## 2. What these datasets contribute

- **OxCGRT** describes government responses, including school closures, workplace closures, stay-at-home requirements, travel controls, and policy indices.
- **Google Mobility** describes changes in visits to workplaces, retail locations, transit stations, grocery stores, parks, and residential locations relative to Google's pre-pandemic baseline.
- **World Bank metadata** supplies standardized country/economy names, codes, regions, income groups, capitals, and coordinates.

These data do not contain the main economic outcomes. They provide policy, behaviour, and country-context variables that can later be joined to Anushka's economic data.

## 3. Reproducible folder structure

```text
data/
├── raw/          Original downloads; never edited
├── interim/      Clean country-day files
└── processed/    Final country-level and country-year files

scripts/          Reproducible Python cleaning programs
reports/          Automatically generated validation report
```

The separation is intentional:

```text
official source
      ↓
raw file preserved unchanged
      ↓
country-level daily cleaning
      ↓
country-year aggregation
      ↓
validation and documented handoff
```

## 4. Raw sources

The files were downloaded on October 15, 2026.

| Source | Official location | Local raw file | Raw shape |
|---|---|---|---|
| OxCGRT | <https://github.com/OxCGRT/covid-policy-dataset> | `data/raw/oxcgrt/OxCGRT_compact_national_v1.csv` | 202,760 rows, 56 columns |
| Google Mobility | <https://storage.googleapis.com/covid19-open-data/v3/mobility.csv> | `data/raw/google_mobility/mobility.csv` | 6,321,226 rows, 8 columns |
| Google location index | <https://storage.googleapis.com/covid19-open-data/v3/index.csv> | `data/raw/google_mobility/index.csv` | 22,963 rows, 15 columns |
| World Bank country API | <https://api.worldbank.org/v2/country?format=json&per_page=400> | `data/raw/world_bank/countries.json` | 296 API records |

The raw files are not overwritten by any cleaning script. Their SHA-256 fingerprints are recorded in `reports/cleaning_validation.md`.

## 5. Step A - World Bank metadata cleaning

Script: `scripts/clean_world_bank_metadata.py`

### Raw structure

The API returned 296 records. It mixes countries/economies with aggregates such as "World" and regional or income-level totals.

### Cleaning operations

1. Loaded the JSON response.
2. Removed records whose World Bank region identifier was `NA`; these are aggregate entities rather than country/economy observations.
3. Extracted and renamed the required fields.
4. Trimmed surrounding whitespace.
5. Sorted records by the three-letter country/economy code.
6. Confirmed that every retained code was non-empty and unique.

### Result

- 296 raw records
- 79 aggregate records removed
- 217 clean country/economy records
- 217 unique three-letter codes

Output: `data/processed/country_metadata_clean.csv`

Columns:

```text
country
iso_code
iso2_code
region
income_group
capital_city
longitude
latitude
```

No interim daily file is needed because metadata are static rather than time-series observations.

## 6. Step B - OxCGRT cleaning

Script: `scripts/clean_oxcgrt.py`

### Raw structure

- 202,760 daily rows
- 185 countries/territories
- January 1, 2020 through December 31, 2022
- Every raw row is marked `NAT_TOTAL`, meaning national-level total policy data
- No duplicate country-date keys

### Cleaning operations

1. Retained national-total records only.
2. Converted `Date` from `YYYYMMDD` text to ISO `YYYY-MM-DD` format.
3. Created a numeric `year` column.
4. Renamed selected columns to consistent lowercase snake-case names.
5. Converted policy values and indices to numeric values.
6. Preserved missing values as missing; no zero filling or interpolation was performed.
7. Converted Kosovo's OxCGRT code `RKS` to the World Bank code `XKX` using an explicit crosswalk.
8. Verified uniqueness of `iso_code + date`.
9. Wrote the cleaned daily data.
10. Calculated country-year means using available non-missing daily values.
11. Recorded the number of observed policy days and the first and last date in each annual group.

### Daily output

`data/interim/oxcgrt_country_day_clean.csv`

- 202,760 rows
- 185 country/economy codes
- Primary key: `iso_code + date`

Selected variables:

```text
school_closing
workplace_closing
stay_home_requirements
international_travel_controls
stringency_index
government_response_index
containment_health_index
economic_support_index
```

### Country-year output

`data/processed/oxcgrt_country_year_clean.csv`

- 555 rows: 185 countries/economies multiplied by 3 years
- Primary key: `iso_code + year`
- Annual values use a simple arithmetic mean of the available daily observations

The four selected policy indices and four selected individual policies have 0% missingness in the source used here.

## 7. Step C - Google Mobility cleaning

Script: `scripts/clean_google_mobility.py`

### Raw structure

- 6,321,226 daily rows across 7,351 geographic location keys
- February 15, 2020 through September 12, 2022 in the downloaded file
- The file contains a mixture of country, state/province, and smaller geographic levels

### Why the Google index is required

The mobility file contains a `location_key`, not a complete country classification. The accompanying Google index maps each key to:

- Country name
- ISO-2 code
- Three-letter code
- Geographic aggregation level

An aggregation level of `0` identifies country-level records.

### Cleaning operations

1. Loaded the Google location index.
2. Retained index entries where `aggregation_level == 0`.
3. Streamed the large mobility file rather than loading all 6.3 million rows into memory.
4. Retained mobility rows whose location key matched a country-level index entry.
5. Attached country name, ISO-2, and three-letter codes.
6. Parsed dates and created a `year` column.
7. Converted the six mobility measures to numeric values.
8. Preserved missing values; no zero filling or interpolation was performed.
9. Verified uniqueness of `iso_code + date`.
10. Wrote the clean country-day data.
11. Calculated country-year means from available non-missing daily values.
12. Added coverage fields showing observed days, source-period dates, coverage percentage, and whether the calendar year is partial.

### Daily output

`data/interim/google_mobility_country_day_clean.csv`

- 120,826 rows retained from 6,321,226 raw rows
- 129 countries/territories with country-level mobility data
- Primary key: `iso_code + date`

Variables:

```text
mobility_retail_and_recreation
mobility_grocery_and_pharmacy
mobility_parks
mobility_transit_stations
mobility_workplaces
mobility_residential
```

### Country-year output

`data/processed/google_mobility_country_year_clean.csv`

- 387 rows: 129 countries/territories multiplied by 3 years
- Primary key: `iso_code + year`
- 2020 is partial because the source begins on February 15
- 2022 is partial because the downloaded source ends on September 12

Missing daily mobility values were retained. Missingness ranges from 0.79% for workplace mobility to 2.24% for residential mobility. Exact values are recorded in the validation report.

## 8. Step D - Merge of Nour's cleaned datasets

Script: `scripts/merge_nour_datasets.py`

The processed policy and mobility tables are merged using `iso_code + year`. Country names are labels only and are never used as join keys. World Bank metadata are added using `iso_code`.

The merge uses the union of policy and mobility country-year keys so that a record is not silently discarded merely because one source does not cover it.

Output: `data/processed/nour_country_year_clean.csv`

- 564 country-year rows
- 36 columns
- Primary key: `iso_code + year`

Three traceability flags are included:

```text
has_policy_data
has_mobility_data
has_world_bank_metadata
```

## 9. Step E - Validation

Script: `scripts/validate_cleaned_data.py`

Generated report: `reports/cleaning_validation.md`

The validation checks:

- Every required output can be read
- Metadata codes are unique
- Daily country-date keys are unique
- Annual country-year keys are unique
- Missing-value counts are reported
- Country codes absent from World Bank metadata are reported
- Raw-file SHA-256 fingerprints are recorded

The current pipeline passes all uniqueness checks.

After the Kosovo crosswalk, the country-level observations still lacking World Bank metadata are:

- `TWN` - Taiwan
- `REU` - Réunion

These records are retained and flagged rather than deleted. This allows the group to decide later whether to supplement their metadata or exclude them from a particular comparison.

## 10. Missing-value policy

The pipeline follows these rules:

- Blank source values remain blank.
- Missing values are not converted to zero because zero has a real meaning in both policy and mobility data.
- Missing mobility days are not interpolated.
- Annual averages use only available non-missing observations for that variable.
- Coverage columns allow incomplete country-years to be identified before visualization.

## 11. Important interpretation limitations

1. Google mobility values are percentage changes from a pre-pandemic baseline, not absolute numbers of visits.
2. Google mobility data represent users who opted into Location History and may not represent the entire population.
3. Google cautions against treating cross-country mobility values as perfectly comparable because coverage and place categorization differ.
4. The downloaded mobility data do not cover full calendar years in 2020 or 2022.
5. OxCGRT indices measure the presence and strictness of government policies, not whether those policies were effective or properly enforced.
6. Annual averages simplify daily variation and can hide brief periods of very strict policy or extreme mobility decline. The cleaned daily files are retained for time-series charts.
7. World Bank income groups in the downloaded metadata reflect the API response at download time and may not represent each country's historical classification in every pandemic year.
8. Relationships between policy, mobility, and economic indicators are associations; a dashboard alone does not prove causation.

## 12. How to reproduce everything

The scripts use only Python's standard library.

From the project directory, run:

```bash
python3 scripts/run_all_cleaning.py
```

This executes, in order:

1. World Bank metadata cleaning
2. OxCGRT cleaning and annual aggregation
3. Google Mobility cleaning and annual aggregation
4. Merge of Nour's three outputs
5. Validation and report generation

Running the pipeline recreates all files under `data/interim`, `data/processed`, and `reports` while leaving `data/raw` unchanged.

## 13. Plain-English summary for the group

> I preserved the original source files, filtered the time-series datasets to country-level observations, standardized the dates and country codes, converted the selected measures to numeric values, retained missing values rather than treating them as zero, produced both daily and annual files, and checked that every country-date and country-year key is unique. I also documented source coverage and unmatched country codes so the cleaned data can be merged safely with the economic datasets.
