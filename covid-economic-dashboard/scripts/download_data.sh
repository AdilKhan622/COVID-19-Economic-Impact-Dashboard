#!/usr/bin/env bash

set -euo pipefail

project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
raw_dir="${project_dir}/data/raw"

mkdir -p \
  "${raw_dir}/owid" \
  "${raw_dir}/eurostat" \
  "${raw_dir}/insee/impact_crise_tables" \
  "${raw_dir}/mendeley"

download() {
  local url="$1"
  local destination="$2"
  curl -L --fail --retry 3 --output "${destination}" "${url}"
}

# -----------------------------------------------------------------------------
# Our World in Data: observed global pandemic conditions
# -----------------------------------------------------------------------------
# compact.csv
#   Format: CSV. One row represents one country or OWID aggregate on one date.
#   Contents: 61 fields at the initial retrieval covering confirmed cases and
#   deaths; excess mortality; hospital and ICU occupancy/admissions; policy
#   stringency and reproduction rate; testing and positivity; vaccinations;
#   country code and continent; population, GDP per capita, age, life
#   expectancy, poverty, health-risk, health-system, and development controls.
#   Important: the file contains aggregate regions as well as countries, and
#   missing coverage differs by indicator. It is the current OWID catalog
#   export, not the frozen legacy GitHub megafile.
#   Dashboard use: pandemic timing, severity, policy response, vaccination,
#   health-system pressure, and population-normalized comparisons.
download \
  "https://catalog.ourworldindata.org/garden/covid/latest/compact/compact.csv" \
  "${raw_dir}/owid/compact.csv"

# compact.meta.json
#   Format: JSON metadata companion to compact.csv.
#   Contents: table and column definitions, titles, descriptions, units,
#   original data producers, licences, citations, update information, and
#   source notes for the indicators in compact.csv.
#   Dashboard use: data dictionary, labels, units, provenance, and limitations.
download \
  "https://catalog.ourworldindata.org/garden/covid/latest/compact/compact.meta.json" \
  "${raw_dir}/owid/compact.meta.json"

# -----------------------------------------------------------------------------
# Eurostat: observed and harmonized European economic outcomes
# -----------------------------------------------------------------------------
# gdp_quarterly_namq_10_gdp.json
#   Format: JSON-stat 2.0 API response.
#   Grain: geography x quarter for 2015-Q1 through 2026-Q2.
#   Contents: GDP at market prices (B1GQ), chain-linked real-volume percentage
#   change from the previous quarter (CLV_PCH_PRE), seasonally and calendar
#   adjusted (SCA). The initial response contains 45 European geographies,
#   46 quarters, 1,953 reported values, dimensions, labels, and status flags.
#   Dashboard use: main observed measure of the 2020 contraction and recovery.
download \
  "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/namq_10_gdp?lang=en&sinceTimePeriod=2015-Q1&untilTimePeriod=2026-Q2&na_item=B1GQ&unit=CLV_PCH_PRE&s_adj=SCA" \
  "${raw_dir}/eurostat/gdp_quarterly_namq_10_gdp.json"

# gdp_quarterly_teina011.json
#   Format: JSON-stat 2.0 API response.
#   Grain: geography x quarter x GDP-growth measure.
#   Contents: the compact Eurostat "GDP, volumes" view for GDP at market
#   prices. It includes quarter-on-quarter seasonally adjusted growth,
#   year-on-year seasonally adjusted growth, and year-on-year unadjusted
#   growth. Eurostat returns only the latest 12 quarters for this view, even
#   though a longer period is requested.
#   Dashboard use: recent-GDP cross-check/reference; not the main history file.
download \
  "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/teina011?lang=en&sinceTimePeriod=2015-Q1&untilTimePeriod=2026-Q2" \
  "${raw_dir}/eurostat/gdp_quarterly_teina011.json"

# unemployment_monthly_une_rt_m.json
#   Format: JSON-stat 2.0 API response.
#   Grain: geography x month x seasonal-adjustment category.
#   Contents: monthly unemployment rate from 2015-01 through 2026-08 for the
#   EU-27, France, Germany, Italy, Spain, the Netherlands, Sweden, Poland,
#   Greece, and Portugal. Sex and age are totals; the unit is percentage of
#   the labour force. The response retains unadjusted (NSA), seasonally
#   adjusted (SA), and trend-cycle (TC) values, plus Eurostat status flags.
#   Dashboard use: observed labour-market shock and recovery; use SA for the
#   main chart and retain the flags when preparing the data.
download \
  "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/une_rt_m?lang=en&sinceTimePeriod=2015-01&untilTimePeriod=2026-08&sex=T&age=TOTAL&unit=PC_ACT&geo=EU27_2020&geo=FR&geo=DE&geo=IT&geo=ES&geo=NL&geo=SE&geo=PL&geo=EL&geo=PT" \
  "${raw_dir}/eurostat/unemployment_monthly_une_rt_m.json"

# -----------------------------------------------------------------------------
# INSEE: observed French business survey on the 2020 health crisis
# -----------------------------------------------------------------------------
# impact_crise_csv.zip
#   Format: ZIP containing 33 semicolon-delimited CSV tables.
#   Grain: aggregated survey estimates by company-size class, activity sector,
#   or French region, depending on the table.
#   Contents: 11 subjects, each supplied in three breakdowns (size, sector,
#   region): activity closure; activity/turnover change; factors affecting
#   activity; on-site work, telework and partial unemployment; commercial
#   logistics; product/service changes; investment; research and development;
#   partners and suppliers; public-support measures; direct/indirect costs.
#   Dashboard use: France sector case study explaining heterogeneity hidden by
#   national GDP and unemployment aggregates.
download \
  "https://www.insee.fr/fr/statistiques/fichier/5356431/impact_crise_csv.zip" \
  "${raw_dir}/insee/impact_crise_csv.zip"

# impact_crise_metadata.csv
#   Format: semicolon-delimited CSV data dictionary in French.
#   Contents: variable families, variable codes, modality/category codes, and
#   their human-readable labels. Examples include activity-loss bands,
#   turnover change, telework shares, investment, supply difficulties, public
#   aid, and crisis-cost definitions.
#   Dashboard use: decode the abbreviated headers in tables 1-33 and provide
#   correct French/English labels during preparation.
download \
  "https://www.insee.fr/fr/statistiques/fichier/5356431/impact_crise_meta.csv" \
  "${raw_dir}/insee/impact_crise_metadata.csv"

# Extraction preserves the original CSV files. Table groups are:
#   01-03 activity maintained/closed, by size/sector/region
#   04-06 activity and turnover change, by size/sector/region
#   07-09 factors affecting activity, by size/sector/region
#   10-12 workforce location/status and telework, by size/sector/region
#   13-15 commercial/logistics adaptation, by size/sector/region
#   16-18 product/service offering changes, by size/sector/region
#   19-21 investment during/after lockdown, by size/sector/region
#   22-24 research and development, by size/sector/region
#   25-27 partnerships and suppliers, by size/sector/region
#   28-30 public-support measures, by size/sector/region
#   31-33 direct and indirect crisis costs, by size/sector/region
unzip -o \
  "${raw_dir}/insee/impact_crise_csv.zip" \
  -d "${raw_dir}/insee/impact_crise_tables"

# -----------------------------------------------------------------------------
# Mendeley Data: model assumptions and simulations, not observed outcomes
# Version-pinned repository for DOI 10.17632/4d7rfm4s77.2.
# -----------------------------------------------------------------------------
# files_v2.json
#   Format: JSON repository manifest.
#   Contents: the six version-2 files with their immutable file IDs, original
#   filenames, MIME types, byte sizes, SHA-256 hashes, creation dates, and
#   official download/view URLs.
#   Dashboard use: provenance and integrity verification for the model files.
download \
  "https://data.mendeley.com/public-api/datasets/4d7rfm4s77/files?folder_id=root&version=2" \
  "${raw_dir}/mendeley/files_v2.json"

# data_tables_figures_annexures.xlsx
#   Format: Excel workbook with 31 analytical sheets.
#   Contents: scenario tables for 24 countries/regions covering 2020 real-GDP
#   loss in USD and percent, cumulative 2020-2025 GDP loss, employment,
#   consumption, investment, fiscal deficit, trade balance, exchange rate,
#   inflation, and interest rates. It also contains dynamic results used in
#   Figures 1-5 and annex data on institutional GDP forecasts, infections,
#   deaths, morbidity/caregiving, lockdown duration, sector productivity,
#   consumption and risk shocks, government spending, and wage subsidies.
#   Dashboard use: ready-made scenario summaries and observed-versus-projected
#   comparison from the paper. Values are primarily model results, not actuals.
download \
  "https://data.mendeley.com/public-files/datasets/4d7rfm4s77/files/6746f14e-3915-4632-adce-4a6e61f3a609/file_downloaded" \
  "${raw_dir}/mendeley/data_tables_figures_annexures.xlsx"

# epidemiological_assumptions.xlsx
#   Format: Excel workbook with one legend plus 24 country/model-region sheets.
#   Contents: country/model-region code mapping and daily cumulative COVID-19
#   case paths used as the epidemiological assumptions for 2020 in Scenario 1.
#   Each region sheet contains Day and Cumulative Number of Cases.
#   Dashboard use: document how the authors constructed the model scenarios;
#   do not substitute these assumed paths for observed OWID case data.
download \
  "https://data.mendeley.com/public-files/datasets/4d7rfm4s77/files/bef3b868-5af5-42f1-9a94-e554881df021/file_downloaded" \
  "${raw_dir}/mendeley/epidemiological_assumptions.xlsx"

# readme.pdf
#   Format: one-page PDF.
#   Contents: repository inventory, graph-reproduction instructions, G-Cubed
#   hybrid DSGE-CGE model description and references, and the warning that the
#   model itself is proprietary although the shocks can be reused after
#   suitable country/sector aggregation.
#   Dashboard use: methodology and interpretation notes for the scenario page.
download \
  "https://data.mendeley.com/public-files/datasets/4d7rfm4s77/files/23ff0141-e9ce-488d-8674-e905b7124895/file_downloaded" \
  "${raw_dir}/mendeley/readme.pdf"

# produce_graphs.R
#   Format: R source script.
#   Contents: package setup, shared chart theme/colour definitions, workbook
#   imports, reshaping steps, and ggplot code that reproduces the paper's
#   figures and annex charts as PNG files.
#   Dashboard use: reference implementation for variable interpretation and a
#   reproducibility check when translating the authors' plots to Plotly.
download \
  "https://data.mendeley.com/public-files/datasets/4d7rfm4s77/files/45b9e31e-f920-47f0-808b-235a53d9d5d5/file_downloaded" \
  "${raw_dir}/mendeley/produce_graphs.R"

# shocks.xlsx
#   Format: Excel workbook with a legend, Scenario 1-5 sheets, and a wage-
#   subsidies/transfers sheet.
#   Contents: model-region codes and first-year shocks for mortality,
#   morbidity/lost working days, lockdown-driven productivity in six sectors,
#   consumption and sector consumption preferences, human-wealth and country
#   risk premia, six sector risk premia, government spending, wage subsidies,
#   and transfers. Units include percent of population, working days, sector
#   closure, GDP, and percentage points as defined in the legend.
#   Dashboard use: explain the assumptions driving each simulated scenario.
download \
  "https://data.mendeley.com/public-files/datasets/4d7rfm4s77/files/847e45b1-ce9b-47de-814e-f182b04b6185/file_downloaded" \
  "${raw_dir}/mendeley/shocks.xlsx"

# simulation_results.xlsx
#   Format: long-form Excel table with columns Variable, Scenario, Region,
#   Sector, Year, and Value.
#   Contents: 20,118 model-result rows spanning 10 variable codes, six
#   scenarios (S01-S06), 24 countries/model regions, seven periods (Y0-Y6),
#   and aggregate plus six sector categories. Variables cover real GDP,
#   consumption, investment, trade balance, exchange rate, inflation, interest
#   rates, labour/employment, and sector output.
#   Dashboard use: interactive scenario comparison by geography, variable,
#   sector, scenario, and model year. These are simulated deviations from a
#   baseline and must remain separate from observed Eurostat/OWID data.
download \
  "https://data.mendeley.com/public-files/datasets/4d7rfm4s77/files/6a5053d1-2060-4df3-8cca-93f3aa475caf/file_downloaded" \
  "${raw_dir}/mendeley/simulation_results.xlsx"

printf 'Raw datasets downloaded to %s\n' "${raw_dir}"
