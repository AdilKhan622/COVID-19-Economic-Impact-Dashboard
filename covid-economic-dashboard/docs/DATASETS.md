# Initial dataset inventory

Retrieval date: **2026-10-12** (Europe/Paris)

This bundle deliberately separates observed data from modelled estimates.
Observed epidemiological and economic series should drive the core dashboard.
The Mendeley scenario results can support a clearly labelled counterfactual or
methodology page, but must not be presented as observed economic outcomes.

## 1. Our World in Data — pandemic conditions

- Official page: <https://ourworldindata.org/coronavirus>
- Download used: <https://catalog.ourworldindata.org/garden/covid/latest/compact/compact.csv>
- Local files: `data/raw/owid/compact.csv` and `compact.meta.json`
- Shape at retrieval: 617,667 rows, 61 columns
- Coverage at retrieval: 2020-01-01 to 2026-08-30
- Unit of observation: country or aggregate region by date
- Main fields: confirmed cases and deaths, hospital/ICU occupancy, vaccination,
  testing, policy stringency, population, and selected socio-economic controls
- Dashboard role: pandemic timing, severity, health-system pressure, policy
  intensity, and normalization per population

Important limitations:

- Confirmed cases depend on testing and reporting capacity and are not fully
  comparable across countries or periods.
- Death attribution and reporting delays differ by country.
- Several testing and policy fields stop earlier than the cases/deaths series.
- Rows include aggregate regions as well as countries; country-only analyses
  must filter on the ISO-like `code` field and explicitly handle OWID aggregates.
- The former OWID GitHub CSV stopped being updated in August 2024; this project
  uses the current OWID catalog endpoint instead.

## 2. Eurostat — observed European economic outcomes

Official COVID-19 economy hub:
<https://ec.europa.eu/eurostat/en/web/covid-19/economy>

### Quarterly real GDP growth

- Dataset code: `namq_10_gdp`
- Local file: `data/raw/eurostat/gdp_quarterly_namq_10_gdp.json`
- Coverage requested: 2015-Q1 to 2026-Q2
- Coverage returned: 46 quarters and 45 geographies
- Filters: GDP at market prices (`B1GQ`), chain-linked volume percentage change
  from the previous quarter (`CLV_PCH_PRE`), seasonally and calendar adjusted
  (`SCA`)
- Dashboard role: compare the pre-pandemic baseline, the 2020 contraction, and
  subsequent recovery across European countries

`gdp_quarterly_teina011.json` is also retained as the small derived Eurostat
view linked from the COVID-19 hub. It only contains the latest 12 quarters at
retrieval, so the full source extract above is the analytical file.

### Monthly unemployment rate

- Dataset code: `une_rt_m`
- Local file: `data/raw/eurostat/unemployment_monthly_une_rt_m.json`
- Coverage: 2015-01 to 2026-08 (140 months)
- Geography subset: EU-27, France, Germany, Italy, Spain, Netherlands, Sweden,
  Poland, Greece, and Portugal
- Filters: total sex, total age, percentage of active population
- The response retains Eurostat's three seasonal-adjustment categories. The
  processing step should select `SA` for the main comparison and retain flags.
- Dashboard role: labour-market response and recovery

Important limitations:

- GDP and unemployment use different frequencies and must not be joined as if
  they were synchronous daily observations.
- Eurostat values can be provisional or revised. Observation-status flags must
  remain attached to values.
- A change in unemployment can be muted by furlough/short-time work schemes;
  it is not a complete measure of labour-market damage.

## 3. INSEE — French business-level impact survey

- Official page: <https://www.insee.fr/fr/statistiques/5356431>
- Local archive: `data/raw/insee/impact_crise_csv.zip`
- Extracted files: `data/raw/insee/impact_crise_tables/table1.csv` through
  `table33.csv`
- Variable metadata: `data/raw/insee/impact_crise_metadata.csv`
- Scope: the 2020 survey on the impact of the health crisis on business activity
  and organization in France
- Breakdowns: company size, activity sector, and region
- Dashboard role: explain heterogeneity hidden by national GDP aggregates —
  activity loss, closures, telework, investment, supply disruption, public aid,
  and direct/indirect costs

Especially useful tables:

- `table5.csv`: activity change by sector, including first- and second-half 2020
  turnover changes versus 2019
- `table8.csv`: factors affecting activity by sector
- `table11.csv`: on-site work, telework, partial unemployment, and other labour
  situations by sector
- `table20.csv`: investment during and after the first lockdown by sector
- `table29.csv`: use of public-support measures by sector
- `table32.csv`: direct and indirect crisis costs by sector

Important limitations:

- This is a one-country, survey-based snapshot rather than a global time series.
- Results are aggregated estimates; denominators and survey weighting must be
  preserved in interpretation.
- Sector classifications are French aggregates and need labels from the metadata
  file before presentation.

## 4. Mendeley Data — global macroeconomic scenarios

- Dataset: *The Global Economic Impacts of the COVID-19 Pandemic*, version 2
- DOI: <https://doi.org/10.17632/4d7rfm4s77.2>
- Repository page: <https://data.mendeley.com/datasets/4d7rfm4s77/2>
- Licence: CC BY 4.0
- Local folder: `data/raw/mendeley/`
- Contents: data for published tables/figures, epidemiological assumptions,
  model shocks, G-Cubed simulation results, a one-page readme, and the authors'
  R plotting script
- Dashboard role: optional counterfactual/scenario page and methodological
  comparison with observed outcomes

Important limitations:

- These are model inputs and simulation results, not measurements of realised
  GDP, employment, or welfare loss.
- Scenario names, assumptions, country aggregation, and model horizon must be
  shown whenever the results are visualized.
- This dataset should not be merged directly into the observed-data fact table.

## Integrity checks

Selected SHA-256 checksums from the retrieval:

```text
7481c676492771e8425b118eaa983e987dd7312989ddcf7c67de09e635c53abc  owid/compact.csv
eaf8023484394a990d21d83b88e1af5c541ea806401b082f16577d1307282bac  owid/compact.meta.json
591cd6569c4dcaf48f9519251ea166a52257fd78247a84c40c6c9a94489ddf9d  eurostat/gdp_quarterly_namq_10_gdp.json
703521f6d98bf927e73f5ba69724343d30b05982d5da1fd04ba6a231648903cb  eurostat/unemployment_monthly_une_rt_m.json
c92234b8ee6abca084ffec095acf04c2873dd8c6fe52d51fa2a1c8f7a0273e50  insee/impact_crise_csv.zip
1b07d94b72e8da9e662eb226a5ab701778fd6e0879b873dcdd1e05184b631e2c  mendeley/data_tables_figures_annexures.xlsx
f75f484d947168a063678f9a2399ba5ba0efd127eb327457fec06668b7453799  mendeley/simulation_results.xlsx
```

The OWID and Eurostat endpoints are live and revision-prone, so re-running the
download script later can legitimately produce different checksums.

## Recommended first analytical scope

Use 2015-2019 as the European economic baseline, 2020-2021 as the acute shock,
and 2022-2024 as the recovery window. Use later observations only in a clearly
labelled post-pandemic context. This avoids implying that every later movement
was caused by COVID-19 and leaves room to discuss the energy-price shock,
inflation, the war in Ukraine, and country-specific policy responses as
confounders.
