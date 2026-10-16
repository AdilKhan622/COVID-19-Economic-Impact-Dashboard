# COVID-19 and the Global Economy: an Interactive Dashboard

A multi-page Plotly Dash dashboard that explores and illustrates the economic impact of the COVID-19 pandemic.

Project for **CentraleDigitalLab: Data Storytelling and Visualization** (Centrale Méditerranée).

> **Live demo:** _<add the URL here once deployed>_
> **Deadline:** final dashboard and 20-minute group oral presentation, **October 21**.

> **Current status (2026-10-16):** one half of the data — OxCGRT government-response policy, Google Mobility, and World Bank country metadata — is collected, cleaned, merged, and validated under [`Data_cleaning/`](Data_cleaning/). Full method and caveats are in [`Data_cleaning/DATA_CLEANING_DOCUMENTATION.md`](Data_cleaning/DATA_CLEANING_DOCUMENTATION.md). The other half (World Bank economic indicators, IMF WEO, OWID, Mendeley) is not in this repo yet. The Dash app itself (`app.py`, pages, components) has not been written yet.

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

| Role                                   | Member   | Responsibilities                                                                                                                          |
| -------------------------------------- | -------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| **A: Data and Preprocessing**          | _name_, _name_ | Dataset search, collection, cleaning, merging, exploratory analysis, data documentation                                       |
| **B: Analyst and Storyteller**         | _name_   | Critical analysis (are the data sufficient?), narrative strategy, choice of indicators and chart types, bias review, annotations and text |
| **C: Dashboard Developer**             | _name_   | Dash app architecture, multi-page navigation, callbacks, charts, integration                                                              |
| **D: Design, Deployment and Database** | _name_   | Repo and environment setup, Bootstrap theme and CSS, reusable components, hosting, MySQL schema (bonus)                                   |

Role A is split by dataset track: one member cleans OxCGRT, Google Mobility, and World Bank country metadata (`Data_cleaning/`); the other covers World Bank economic indicators, IMF WEO, OWID, and Mendeley (not yet in this repo).

Everyone contributes to the oral presentation and to code reviews.

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

> `app.py` does not exist yet (see the status note at the top of this README). Until it does, you can still run the data-cleaning pipeline with `python3 Data_cleaning/scripts/run_all_cleaning.py` (stdlib only, no extra install needed).

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
├── app.py                              # Dash entry point; exposes `server`            [to be added]
├── pages/                              # One file per dashboard page (Dash multi-page) [to be added]
│   ├── home.py
│   ├── timeline.py
│   ├── economy.py
│   ├── countries.py
│   ├── analysis.py
│   └── methodology.py
├── components/                         # Reusable UI building blocks                  [to be added]
│   ├── cards.py                         # kpi_card, chart_card
│   ├── layout.py                        # navbar, footer, page_header
│   └── callouts.py                     # insight_box
├── assets/                             # Auto-loaded by Dash                          [to be added]
│   ├── style.css
│   ├── favicon.ico
│   └── logo.png
├── theme.py                            # Shared colors, fonts and chart template      [to be added]
├── notebooks/                          # Exploratory analysis                        [to be added]
├── docs/                               # ER diagram, screenshots for the fallback     [to be added]
│   ├── er_diagram.png
│   └── screenshots/
├── db/                                 # Bonus: MySQL                                [to be added]
│   ├── schema.sql
│   ├── load_data.py
│   └── covid.sql                       # Database dump
└── Data_cleaning/                      # Policy/mobility/metadata cleaning pipeline    [done]
    ├── .gitignore                      # Only google_mobility/mobility.csv is excluded (224MB, over GitHub's 100MB limit)
    ├── DATA_CLEANING_DOCUMENTATION.md  # Method, sources, cleaning steps, limitations
    ├── data/
    │   ├── raw/                        # Original downloads, never edited by hand
    │   │   ├── oxcgrt/                  # OxCGRT government-response policy tracker
    │   │   ├── google_mobility/        # Mobility + location index (mobility.csv not committed, see above)
    │   │   └── world_bank/             # Country/economy metadata (API JSON)
    │   ├── interim/                    # Cleaned country-day tables
    │   └── processed/                  # Country-year tables + merged dataset
    ├── scripts/
    │   ├── clean_world_bank_metadata.py
    │   ├── clean_oxcgrt.py
    │   ├── clean_google_mobility.py
    │   ├── merge_cleaned_datasets.py
    │   ├── validate_cleaned_data.py
    │   └── run_all_cleaning.py         # Runs all five scripts above, in order
    └── reports/
        └── cleaning_validation.md      # Row/column counts, uniqueness checks, missing-value rates
```

> Items marked `[to be added]` are planned but don't exist yet. Adjust this tree as the real layout evolves, so the README stays accurate.

---

## 5. Data

All paths below are relative to `Data_cleaning/`. Full provenance, cleaning steps, and known limitations are kept in [`DATA_CLEANING_DOCUMENTATION.md`](Data_cleaning/DATA_CLEANING_DOCUMENTATION.md); row/column counts and uniqueness checks are in [`reports/cleaning_validation.md`](Data_cleaning/reports/cleaning_validation.md) — read both before building a chart on top of these files.

### Sources in this repo (retrieved 2026-10-15)

| Source                                                                                        | Content                                                                                                   | Local files                 |
| ------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------- | ------------------------------ |
| [OxCGRT](https://github.com/OxCGRT/covid-policy-dataset)                                         | Government-response policy indices (school/workplace closing, stringency, etc.), Jan 2020 – Dec 2022         | `data/raw/oxcgrt/`             |
| [Google COVID-19 Mobility](https://storage.googleapis.com/covid19-open-data/v3/mobility.csv)     | % change in visits to retail, grocery, transit, workplaces, parks, residential vs. pre-pandemic baseline     | `data/raw/google_mobility/`    |
| [World Bank country API](https://api.worldbank.org/v2/country?format=json&per_page=400)          | Country/economy names, ISO codes, region, income group, capital, coordinates                                  | `data/raw/world_bank/`         |

> `google_mobility/mobility.csv` (224MB) is **not committed** — it's over GitHub's 100MB hard limit. Re-download it from the URL above and drop it in `data/raw/google_mobility/` before running the pipeline. Everything else in `data/raw/` **is** committed and visible on GitHub.

### Sources not yet in this repo

World Bank economic indicators, IMF WEO, OWID COVID-19 data, and the Mendeley dataset are assigned to the other dataset track and will land in a separate part of the project once ready.

### Pipeline

1. **Collect:** raw files in `data/raw/<source>/`, never edited by hand. ✅ done
2. **Clean:** each source gets its own script (`clean_oxcgrt.py`, `clean_google_mobility.py`, `clean_world_bank_metadata.py`) — country-level filtering, date parsing, numeric conversion, ISO-code harmonisation (including a Kosovo `RKS` → `XKX` crosswalk). Missing values are kept as missing, never zero-filled. ✅ done
3. **Merge:** `merge_cleaned_datasets.py` joins the three cleaned country-year tables on `iso_code` + `year`, using the union of keys so no record is dropped just because one source doesn't cover it. ✅ done
4. **Validate:** `validate_cleaned_data.py` checks primary-key uniqueness, reports missing-value rates and unmatched country codes, and records raw-file SHA-256 fingerprints. ✅ done, currently **PASS**
5. **Output:** `data/interim/` (country-day) and `data/processed/` (country-year + the merged `merged_country_year_clean.csv`).

```bash
# Re-run the whole pipeline (stdlib only, no extra packages needed)
python3 Data_cleaning/scripts/run_all_cleaning.py
```

### Data dictionary

Selected columns from `data/processed/merged_country_year_clean.csv` (primary key `iso_code` + `year`):

| Column                            | Description                                                       | Unit    | Source     | Frequency (source) |
| ----------------------------------- | --------------------------------------------------------------------- | ------- | ---------- | --------------------- |
| `iso_code`                          | ISO 3166-1 alpha-3 country/economy code                               | n/a     | all        | n/a                    |
| `year`                               | Calendar year (2020–2022)                                              | n/a     | n/a        | n/a                    |
| `stringency_index`                  | Overall government-response stringency, annual mean                   | 0–100   | OxCGRT     | Daily                  |
| `school_closing`                    | School-closure policy level, annual mean                              | ordinal | OxCGRT     | Daily                  |
| `mobility_workplaces`               | Change in workplace visits vs. baseline, annual mean                  | %       | Google     | Daily                  |
| `mobility_retail_and_recreation`    | Change in retail/recreation visits vs. baseline                       | %       | Google     | Daily                  |
| `region`, `income_group`            | World Bank country classification                                     | n/a     | World Bank | Static                 |
| `has_policy_data`, `has_mobility_data`, `has_world_bank_metadata` | Traceability flags for which sources cover this row | boolean | merge script | n/a                  |

The economic columns (GDP growth, unemployment, etc.) from the other dataset track are `_tbd_` until that part is merged in.

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

**Known limitations** (from `Data_cleaning/DATA_CLEANING_DOCUMENTATION.md`; more will be added as the other dataset track lands)

- Google Mobility values are % change from a pre-pandemic baseline, not absolute visit counts, and only reflect users who opted into Location History.
- Mobility data don't cover full calendar years in 2020 (starts Feb 15) or 2022 (ends Sep 12).
- OxCGRT indices measure the presence/strictness of policy, not whether it was enforced or effective.
- Annual averages smooth over brief periods of extreme policy or mobility change; the daily files in `data/interim/` are kept for time-series charts.
- World Bank income groups reflect the API response at download time, not necessarily each country's historical classification in every pandemic year.
- Two country codes (`TWN`, `REU`) have policy/mobility data but no World Bank metadata match — retained and flagged (`has_world_bank_metadata = false`), not dropped.

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

**Not yet in this repo:**

- [Our World in Data: Coronavirus](https://ourworldindata.org/coronavirus)
- World Bank economic indicators and IMF World Economic Outlook
- Mendeley Data (specific dataset TBD)

**Tooling:**

- [Plotly Dash documentation](https://dash.plotly.com) and [Dash Gallery](https://plotly.com/examples/)
- [Dash Bootstrap Components](https://dash-bootstrap-components.opensource.faculty.ai/)

Built at Centrale Méditerranée, Nice, 2026.

