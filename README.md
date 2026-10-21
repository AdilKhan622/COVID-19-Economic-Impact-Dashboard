# COVID-19 and the Global Economy: an Interactive Dashboard

A multi-page Plotly Dash dashboard that explores and illustrates the economic impact of the COVID-19 pandemic.

Project for **CentraleDigitalLab: Data Storytelling and Visualization** (Centrale Méditerranée).

> **Live demo:** _<add the URL here once deployed>_
> **Deadline:** final dashboard and 20-minute group oral presentation, **October 21**.

> **Current status (2026-10-21):** both data tracks are in [`Data_cleaning/`](Data_cleaning/). Track 1 (OxCGRT policy, Google Mobility, World Bank country metadata) is cleaned, merged and validated by a reproducible pipeline; full method and caveats are in [`Data_cleaning/DATA_CLEANING_DOCUMENTATION.md`](Data_cleaning/DATA_CLEANING_DOCUMENTATION.md). Track 2 (OWID COVID-19, World Bank GDP, OxCGRT vaccine policy) was cleaned in a Colab notebook exported as [`Data_cleaning/scripts/data_cleaning_set2.py`](Data_cleaning/scripts/data_cleaning_set2.py); its outputs are in `Data_cleaning/data/processed/`. World Bank GDP growth, unemployment and inflation are joined into the dashboard table by `prepare_dashboard_data.py`. The Dash app (`app.py`, `pages/`, `components/`) is in the repo.

---

## Table of contents

1. [Project overview](#1-project-overview)
2. [Team and roles](#2-team-and-roles)
3. [Quick start](#3-quick-start)
4. [Project structure](#4-project-structure)
5. [Data](#5-data)
6. [Dashboard pages](#6-dashboard-pages)
7. [Design system and reusable components](#7-design-system-and-reusable-components)
8. [Database (bonus)](#8-database-bonus)
9. [Deployment](#9-deployment)
10. [Team workflow](#10-team-workflow)
11. [Methodology, limitations and ethics](#11-methodology-limitations-and-ethics)
12. [Evaluation criteria](#12-evaluation-criteria)
13. [Sources and credits](#13-sources-and-credits)

## 1. Project overview

Opinions about how COVID-19 affected the global economy vary widely. This project replaces opinions with evidence: we collect real-world data, clean it, analyse it, and present the findings through an interactive, multi-page dashboard.

**Central question:** _How did the COVID-19 pandemic affect the global economy, and can the available data support that conclusion?_

**Learning objectives**

- Understand the role and ethical responsibilities of data visualization in modern data science.
- Collect, clean and analyse real-world socio-economic datasets.
- Design and deploy interactive dashboards with Plotly Dash.
- Critically evaluate data quality, sampling and context to avoid biased storytelling.
- Communicate findings through visual narratives that support decision-making.

---

## 2. Team and roles

| Role                                   | Member         | Responsibilities                                                                                                                          |
| -------------------------------------- | -------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| **A: Data and Preprocessing**          | Anushka, Nour | Dataset search, collection, cleaning, merging, exploratory analysis, data documentation                                                   |
| **B: Dashboard Developer**             | Sahasri | Dash app architecture, multi-page navigation, callbacks, charts, integration                                                              |
| **C: Design, Deployment and Database** | Adil, Sahasri        | Repo and environment setup, Bootstrap theme and CSS, reusable components, hosting, MySQL schema (bonus)                                   |

Role A is split by dataset track: one member cleans OxCGRT, Google Mobility, and World Bank country metadata (track 1, `Data_cleaning/scripts/clean_*.py`); the other covers OWID COVID-19, World Bank GDP and the Mendeley/Oxford COVID-19 policy tracker (track 2, `Data_cleaning/scripts/data_cleaning_set2.py`).


---

## 3. Quick start

### Prerequisites

- [Anaconda](https://www.anaconda.com/) or Miniconda
- Python 3.12
- Git
- _(Bonus only)_ MySQL 8.x

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/AdilKhan622/COVID-19-Economic-Impact-Dashboard.git
cd COVID-19-Economic-Impact-Dashboard

# 2. Create and activate the environment
conda env create -f environment.yml
conda activate covid-dashboard

# 3. Run the dashboard
python app.py
```

Then open **http://127.0.0.1:8050** in your browser.

> The track 1 cleaning pipeline can also be run on its own with `python3 Data_cleaning/scripts/run_all_cleaning.py` (stdlib only, no extra install needed).

### Alternative: pip

```bash
conda create -n covid-dashboard python=3.12
conda activate covid-dashboard
pip install -r requirements.txt
python app.py
```

### Main dependencies

| Package                     | Purpose                                  |
| --------------------------- | ---------------------------------------- |
| `dash`                      | Dashboard framework (multi-page support) |
| `plotly`                    | Interactive charts                       |
| `pandas`                    | Data manipulation                        |
| `dash-bootstrap-components` | Bootstrap layout and components          |
| `dash-bootstrap-templates`  | Matching Plotly figure themes            |
| `gunicorn`                  | Production server for deployment         |
| `sqlalchemy`, `pymysql`     | Database access (bonus)                  |

### Troubleshooting

- **Port already in use:** change the port with `app.run(debug=True, port=8051)`.
- **Missing data files:** `Data_cleaning/data/raw/` is committed except `google_mobility/mobility.csv` (224MB, over GitHub's 100MB limit) — re-download that one file from the URL in [Data](#5-data), then re-run `python3 Data_cleaning/scripts/run_all_cleaning.py` to regenerate `data/interim/` and `data/processed/`.
- **Environment conflicts:** remove and recreate it: `conda env remove -n covid-dashboard`, then repeat step 2.

---

## 4. Project structure

```
COVID-19-Economic-Impact-Dashboard/
├── environment.yml                     # Conda environment (covid-dashboard)
├── requirements.txt                    # Same dependencies, for pip/venv
├── README.md                           # This file
├── app.py                              # Dash entry point
├── pages/                              # One file per dashboard page (Dash multi-page)
│   ├── overview.py
│   ├── pandemic_policy.py
│   ├── economic_shock.py
│   ├── jobs_inflation.py
│   ├── country_lab.py
│   └── methodology.py
├── components/                         # Reusable building blocks
│   ├── layout.py
│   ├── data_utils.py
│   ├── impact_index.py
│   └── counterfactual.py
├── assets/                             # Auto-loaded by Dash
│   ├── style.css
│   └── theme.py
├── db/                                 # Bonus: MySQL
│   ├── schema.sql
│   ├── load_data.py
│   ├── migrate_processed_data.sql
│   └── covid.sql                       # Database dump
├── tests/
│   └── test_dashboard_data.py
└── Data_cleaning/
    ├── .gitignore                      # Only google_mobility/mobility.csv is excluded (224MB, over GitHub's 100MB limit)
    ├── DATA_CLEANING_DOCUMENTATION.md  # Track 1: method, sources, cleaning steps, limitations
    ├── data/
    │   ├── raw/                        # Original downloads, never edited by hand
    │   │   ├── oxcgrt/                 # OxCGRT government-response policy tracker
    │   │   ├── google_mobility/        # Mobility + location index (mobility.csv not committed, see above)
    │   │   └── world_bank/             # Country metadata (API JSON) + economic_indicators/ (GDP growth, unemployment, CPI)
    │   ├── interim/                    # Track 1 cleaned country-day tables
    │   └── processed/                  # Track 1 country-year tables, track 2 outputs, dashboard master table
    ├── scripts/
    │   ├── clean_world_bank_metadata.py   # Track 1
    │   ├── clean_oxcgrt.py                # Track 1
    │   ├── clean_google_mobility.py       # Track 1
    │   ├── merge_cleaned_datasets.py      # Track 1
    │   ├── validate_cleaned_data.py       # Track 1
    │   ├── run_all_cleaning.py            # Runs the five track 1 scripts above, in order
    │   ├── data_cleaning_set2.py          # Track 2: Colab notebook export (OWID, World Bank GDP, OxCGRT vaccines)
    │   └── prepare_dashboard_data.py      # Joins World Bank economic indicators into dashboard_master_annual.csv
    └── reports/
        ├── cleaning_validation.md         # Track 1 row/column counts, uniqueness checks, missing-value rates
        └── dashboard_data_integration.md  # Coverage report for the dashboard master table
```

---

## 5. Data

All paths below are relative to `Data_cleaning/`. Full provenance, cleaning steps, and known limitations are kept in [`DATA_CLEANING_DOCUMENTATION.md`](Data_cleaning/DATA_CLEANING_DOCUMENTATION.md); row/column counts and uniqueness checks are in [`reports/cleaning_validation.md`](Data_cleaning/reports/cleaning_validation.md) — read both before building a chart on top of these files.

### Track 1 sources (retrieved 2026-10-15)

| Source                                                                                       | Content                                                                                                  | Local files                 |
| -------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------- | --------------------------- |
| [OxCGRT](https://github.com/OxCGRT/covid-policy-dataset)                                     | Government-response policy indices (school/workplace closing, stringency, etc.), Jan 2020 – Dec 2022     | `data/raw/oxcgrt/`          |
| [Google COVID-19 Mobility](https://storage.googleapis.com/covid19-open-data/v3/mobility.csv) | % change in visits to retail, grocery, transit, workplaces, parks, residential vs. pre-pandemic baseline | `data/raw/google_mobility/` |
| [World Bank country API](https://api.worldbank.org/v2/country?format=json&per_page=400)      | Country/economy names, ISO codes, region, income group, capital, coordinates                             | `data/raw/world_bank/`      |

> `google_mobility/mobility.csv` (224MB) is **not committed** — it's over GitHub's 100MB hard limit. Re-download it from the URL above and drop it in `data/raw/google_mobility/` before running the pipeline. Everything else in `data/raw/` **is** committed and visible on GitHub.

### Track 1 pipeline

1. **Collect:** raw files in `data/raw/<source>/`, never edited by hand. ✅ done
2. **Clean:** each source gets its own script (`clean_oxcgrt.py`, `clean_google_mobility.py`, `clean_world_bank_metadata.py`) — country-level filtering, date parsing, numeric conversion, ISO-code harmonisation (including a Kosovo `RKS` → `XKX` crosswalk). Missing values are kept as missing, never zero-filled. ✅ done
3. **Merge:** `merge_cleaned_datasets.py` joins the three cleaned country-year tables on `iso_code` + `year`, using the union of keys so no record is dropped just because one source doesn't cover it. ✅ done
4. **Validate:** `validate_cleaned_data.py` checks primary-key uniqueness, reports missing-value rates and unmatched country codes, and records raw-file SHA-256 fingerprints. ✅ done, currently **PASS**
5. **Output:** `data/interim/` (country-day) and `data/processed/` (country-year + the merged `merged_country_year_clean.csv`).

```bash
# Re-run the whole pipeline (stdlib only, no extra packages needed)
python3 Data_cleaning/scripts/run_all_cleaning.py
```

### Track 2 sources (cleaned 2026-10-16)

Cleaned in a Colab notebook, exported to `scripts/data_cleaning_set2.py`. The notebook downloads its raw files at run time, so there is no track 2 folder under `data/raw/`.

| Source | Content | Output file in `data/processed/` | Shape | Coverage |
|---|---|---|---|---|
| [OWID COVID-19 (GitHub CSV)](https://github.com/owid/covid-19-data) | Cases, deaths, testing, vaccinations, stringency, population and country controls | `covid_clean_daily.csv` | 409,909 rows × 42 columns | 2020-01-01 to 2024-08-14; 248 entities |
| [Mendeley/Oxford COVID-19 policy tracker](https://github.com/OxCGRT/covid-policy-tracker) | Vaccine prioritisation, availability, financial support and mandates by population group | `mendeley_policy_clean_daily.csv` | 202,819 rows × 76 columns | 2020-01-01 to 2023-02-28; 185 countries |
| [World Bank GDP (datahub mirror)](https://github.com/datasets/gdp) | GDP in current US$, one value per country-year | `wdi_gdp_clean_annual.csv` | 13,979 rows × 4 columns | 1960–2023; 262 entities |

`mendeley_policy_clean_daily.csv` was downloaded from the Oxford tracker's GitHub repository (`OxCGRT/covid-policy-tracker`, file `OxCGRT_vaccines_full.csv`).

- **Primary keys:** `isocode` + `date` for the two daily files; `countrycode` + `year` for GDP.
- **Duplicate codes removed:** ISO codes that produced duplicate `isocode` + `date` rows in OWID were removed from the main table.
- **Column names:** normalised to lowercase with spaces and underscores removed (e.g. `new_cases` → `newcases`). Mendeley/Oxford policy columns keep the tracker's `v1`–`v4` prefixes (`v1` prioritisation, `v2` availability, `v3` financial support, `v4` mandate).
- **No missing values:** both daily files were gap-filled during cleaning, so they contain no empty cells (unlike track 1, which keeps gaps as missing).

### Data dictionary

Selected columns from `data/processed/merged_country_year_clean.csv` (primary key `iso_code` + `year`):

| Column                                                            | Description                                          | Unit    | Source       | Frequency (source) |
| ----------------------------------------------------------------- | ---------------------------------------------------- | ------- | ------------ | ------------------ |
| `iso_code`                                                        | ISO 3166-1 alpha-3 country/economy code              | n/a     | all          | n/a                |
| `year`                                                            | Calendar year (2020–2022)                            | n/a     | n/a          | n/a                |
| `stringency_index`                                                | Overall government-response stringency, annual mean  | 0–100   | OxCGRT       | Daily              |
| `school_closing`                                                  | School-closure policy level, annual mean             | ordinal | OxCGRT       | Daily              |
| `mobility_workplaces`                                             | Change in workplace visits vs. baseline, annual mean | %       | Google       | Daily              |
| `mobility_retail_and_recreation`                                  | Change in retail/recreation visits vs. baseline      | %       | Google       | Daily              |
| `region`, `income_group`                                          | World Bank country classification                    | n/a     | World Bank   | Static             |
| `has_policy_data`, `has_mobility_data`, `has_world_bank_metadata` | Traceability flags for which sources cover this row  | boolean | merge script | n/a                |

Economic columns (`real_gdp_growth_pct`, `unemployment_rate_pct`, `inflation_rate_pct`, from the World Bank files in `data/raw/world_bank/economic_indicators/`) are added to `data/processed/dashboard_master_annual.csv` by `prepare_dashboard_data.py`. Their coverage by year is in [`reports/dashboard_data_integration.md`](Data_cleaning/reports/dashboard_data_integration.md).

---

## 6. Dashboard pages

| Page                            | Purpose                                                                      | Key visuals                                   |
| ------------------------------- | ---------------------------------------------------------------------------- | --------------------------------------------- |
| **Overview**                    | Headline findings in one screen                                              | KPI cards, main storyline chart               |
| **Pandemic timeline**           | Evolution of cases, deaths and restrictions                                  | Time series, stringency index                 |
| **Economic indicators**         | GDP, unemployment, trade and inflation before and during the pandemic        | Line and bar charts, before/after comparisons |
| **Country comparison**          | Differences between countries and regions                                    | Choropleth map, ranking charts, filters       |
| **Analysis**                    | Relationship between pandemic severity or restrictions and economic outcomes | Scatter plots, correlation views with caveats |
| **Methodology and limitations** | Data sources, cleaning decisions, biases, sufficiency of the data            | Text, tables                                  |

_Update this table to reflect the final page list._

---

## 7. Design system and reusable components

All pages share one visual identity, defined in `theme.py` and `assets/style.css`.

**Principles**

- One Bootstrap theme and one font family across the whole app.
- One color means one thing everywhere (for example, the same color always represents unemployment).
- Colorblind-safe palette for multi-series charts.
- Every chart has a **finding-style title**, labelled axes with units, a one-sentence context note and a source line.
- Honest scales: no truncated axes that exaggerate effects. Avoid pie charts for many categories.

**Components** (in `components/`)

| Function                                           | Description                                                |
| -------------------------------------------------- | ---------------------------------------------------------- |
| `kpi_card(title, value, delta, color)`             | Headline number with change indicator                      |
| `chart_card(title, subtitle, graph, source, note)` | Card wrapping a chart with title, context, source and note |
| `page_header(title, intro)`                        | Consistent page opening with narrative text                |
| `insight_box(text)`                                | Highlighted callout for annotations and caveats            |
| `navbar()` / `footer()`                            | Global navigation and sources/credits footer               |

**Example**

```python
from components.cards import chart_card
from dash import dcc
import plotly.express as px

fig = px.line(df, x="year", y="stringency_index", color="country")

layout = chart_card(
    title="Government response peaked in 2020 and eased through 2022",
    subtitle="Annual mean stringency index, selected countries",
    graph=dcc.Graph(figure=fig),
    source="Source: OxCGRT, via Data_cleaning/data/processed/",
    note="Annual means smooth out short, strict policy periods — see the daily file in data/interim/ for that detail.",
)
```

---

## 8. Database (bonus)

A MySQL relational database hosts the datasets used in the study.

### Schema

| Table            | Primary key                            | Main attributes                                              | Foreign keys                                         |
| ---------------- | -------------------------------------- | ------------------------------------------------------------ | ---------------------------------------------------- |
| `country`        | `iso_code`                             | name, continent, region, income_group, population            | none                                                 |
| `source`         | `source_id`                            | name, url, license, retrieved_on                             | none                                                 |
| `indicator`      | `indicator_id`                         | name, unit, category (health / economic / policy), frequency | `source_id` → `source`                               |
| `covid_daily`    | (`iso_code`, `date`)                   | new_cases, new_deaths, vaccinations, stringency_index        | `iso_code` → `country`                               |
| `economic_value` | (`iso_code`, `indicator_id`, `period`) | value                                                        | `iso_code` → `country`, `indicator_id` → `indicator` |

> Update this table to match the final schema.

### Design justification

- **Normalisation (3NF):** country attributes are stored once, not repeated on every observation.
- **Flexible indicators:** quarterly GDP and monthly unemployment share one `economic_value` table, without wide tables full of empty cells.
- **Integrity:** composite primary keys prevent duplicate observations; foreign keys guarantee every row points to a valid country, indicator and source.
- **Transparency:** the `source` table keeps provenance for every indicator.
- **Performance:** indexes on `iso_code` and `date`.

### Setup

```bash
# Create the database and tables
mysql -u <user> -p -e "CREATE DATABASE covid CHARACTER SET utf8mb4;"
mysql -u <user> -p covid < db/schema.sql

# Load the cleaned data
python db/load_data.py
```

Database credentials are read from environment variables. **Never commit them.**

```bash
export DB_HOST=localhost
export DB_USER=<user>
export DB_PASSWORD=<password>
export DB_NAME=covid
```

An ER diagram is available in `docs/er_diagram.png` _(add after generating it)_. A full dump is provided in `db/covid.sql`.

---

## 9. Deployment

The app exposes a WSGI server in `app.py`:

```python
app = Dash(__name__, use_pages=True)
server = app.server
```

**Production command**

```bash
gunicorn app:server
```

**Steps (generic)**

1. Push the repository to GitHub.
2. Create a web service on your hosting platform (for example Render, Railway, PythonAnywhere or the school's server).
3. Set the build command to `pip install -r requirements.txt` and the start command to `gunicorn app:server`.
4. Add any environment variables in the platform's settings.
5. Open the generated URL and test every page.

**Notes**

- Free instances may sleep when idle and take about 30 seconds to wake up. Open the app before the presentation.
- Keep datasets small to stay within memory limits.
- The deployed version reads from files in `Data_cleaning/data/processed/` and, once merged, the economic-indicators data from the other dataset track. The MySQL database is included as a dump and can be used locally.
- **Fallback:** the app always runs locally with `python app.py`, and screenshots are stored in `docs/screenshots/`.

---

## 10. Team workflow

**Branching**

- `main`: stable, presentable version only.
- `feature/<name>`: one branch per task (for example `feature/economy-page`).
- Open a pull request and get one review before merging.

**Commits:** short and descriptive, in the imperative (`Add unemployment chart`, `Fix country code mapping`).

**Task tracking:** use the project board (GitHub Projects or Trello). Each task has an owner and a status: To do, In progress, Review, Done.

**Rules**

- Do not commit large raw datasets or credentials.
- Run the app before every pull request.
- Agree on the data contract (column names, formats, countries and period covered) before building on it.

**Timeline**

| Dates      | Milestone                                                                      |
| ---------- | ------------------------------------------------------------------------------ |
| Oct 12-14  | Datasets chosen, storyline agreed, repo and environment ready                  |
| Oct 15-18  | Clean data delivered, pages and charts built, styling, database and deployment |
| Oct 19-20  | Integration, testing, bias review, presentation rehearsal                      |
| **Oct 21** | **Final dashboard and oral presentation (20 min per group)**                   |

---

## 11. Methodology, limitations and ethics

Visualization can clarify reality or distort it. We follow these principles:

- **Transparency:** every chart states its source, period and units.
- **Representativeness:** we check which countries and periods are covered, and flag gaps in the data.
- **Comparability:** differences in how countries report cases and economic statistics are noted.
- **Correlation is not causation:** analysis pages include explicit caveats.
- **Honest design:** consistent scales, no misleading truncation, and no decoration that adds no meaning.
- **Context:** results are read within their geopolitical, socio-economic and temporal setting (lockdown timing, policy support, economic structure).

**Is the data sufficient to measure the economic impact?** _Answer yes or no, with justification, once the analysis is done. See the Methodology page of the dashboard._

**Known limitations, track 1** (from `Data_cleaning/DATA_CLEANING_DOCUMENTATION.md`)

- Google Mobility values are % change from a pre-pandemic baseline, not absolute visit counts, and only reflect users who opted into Location History.
- Mobility data don't cover full calendar years in 2020 (starts Feb 15) or 2022 (ends Sep 12).
- OxCGRT indices measure the presence/strictness of policy, not whether it was enforced or effective.
- Annual averages smooth over brief periods of extreme policy or mobility change; the daily files in `data/interim/` are kept for time-series charts.
- World Bank income groups reflect the API response at download time, not necessarily each country's historical classification in every pandemic year.
- Two country codes (`TWN`, `REU`) have policy/mobility data but no World Bank metadata match — retained and flagged (`has_world_bank_metadata = false`), not dropped.

**Known limitations, track 2**

- **Missing daily counts were set to 0.** In `covid_clean_daily.csv`, empty `newcases`/`newdeaths` values were filled with 0, and 90.2% of rows now have `newcases = 0`. A 0 can mean "not reported that day" as well as "no new cases". Weekly or yearly totals are safer than single days.
- **Other gaps were filled with 0 as a last resort.** In `covid_clean_daily.csv`, remaining columns were filled from the same country's nearby values, and set to 0 where a country had no value at all. In `mendeley_policy_clean_daily.csv`, policy values were carried forward and set to 0 before a country's first record. A 0 in these files can mean "no data" as well as "none" (e.g. `extremepoverty = 0`).
- **OWID data ends on 2024-08-14.** The notebook used OWID's GitHub CSV, which stopped being updated in August 2024; later pandemic years are not covered by `covid_clean_daily.csv`.

---

## 12. Evaluation criteria

- Technological innovation
- Development skills
- Project management
- Communication

---

## 13. Sources and credits

**In this repo:**

- [OxCGRT: COVID-19 Government Response Tracker](https://github.com/OxCGRT/covid-policy-dataset)
- [Google COVID-19 Community Mobility Reports](https://storage.googleapis.com/covid19-open-data/v3/mobility.csv)
- [World Bank country/economy API](https://api.worldbank.org/v2/country?format=json&per_page=400)
- [Our World in Data: COVID-19 dataset](https://github.com/owid/covid-19-data)
- [Mendeley/Oxford COVID-19 policy tracker](https://github.com/OxCGRT/covid-policy-tracker)
- [World Bank GDP, current US$ (datahub mirror)](https://github.com/datasets/gdp)
- World Bank World Development Indicators: GDP growth (`NY.GDP.MKTP.KD.ZG`), unemployment (`SL.UEM.TOTL.ZS`), inflation (`FP.CPI.TOTL.ZG`)

**Discarded:** IMF World Economic Outlook. It was downloaded and compared in the cleaning notebook, but it turned out identical to the World Bank GDP table, so it was dropped to avoid duplication.

**Tooling:**

- [Plotly Dash documentation](https://dash.plotly.com) and [Dash Gallery](https://plotly.com/examples/)
- [Dash Bootstrap Components](https://dash-bootstrap-components.opensource.faculty.ai/)

Built at Centrale Méditerranée, Nice, 2026.
