<<<<<<< HEAD

# COVID-19 and the Global Economy: an Interactive Dashboard

A multi-page Plotly Dash dashboard that explores and illustrates the economic impact of the COVID-19 pandemic.

Project for **CentraleDigitalLab: Data Storytelling and Visualization** (Centrale Méditerranée).

> **Live demo:** _<add the URL here once deployed>_
> **Deadline:** final dashboard and 20-minute group oral presentation, **October 21**.

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

---

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

| Role                                   | Member | Responsibilities                                                                                                                          |
| -------------------------------------- | ------ | ----------------------------------------------------------------------------------------------------------------------------------------- |
| **A: Data and Preprocessing**          | _name_ | Dataset search, collection, cleaning, merging, exploratory analysis, data documentation                                                   |
| **B: Analyst and Storyteller**         | _name_ | Critical analysis (are the data sufficient?), narrative strategy, choice of indicators and chart types, bias review, annotations and text |
| **C: Dashboard Developer**             | _name_ | Dash app architecture, multi-page navigation, callbacks, charts, integration                                                              |
| **D: Design, Deployment and Database** | _name_ | Repo and environment setup, Bootstrap theme and CSS, reusable components, hosting, MySQL schema (bonus)                                   |

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
git clone <repository-url>
cd covid-dashboard

# 2. Create and activate the environment
conda env create -f environment.yml
conda activate covid-dashboard

# 3. Run the dashboard
python app.py
```

Then open **http://127.0.0.1:8050** in your browser.

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
- **Missing data files:** make sure `data/clean/` is populated. If it is not, run the preprocessing script (see [Data](#5-data)).
- **Environment conflicts:** remove and recreate it: `conda env remove -n covid-dashboard`, then repeat step 2.

---

## 4. Project structure

```
covid-dashboard/
├── app.py                  # Dash entry point; exposes `server` for deployment
├── pages/                  # One file per dashboard page (Dash multi-page)
│   ├── home.py
│   ├── timeline.py
│   ├── economy.py
│   ├── countries.py
│   ├── analysis.py
│   └── methodology.py
├── components/             # Reusable UI building blocks
│   ├── cards.py            # kpi_card, chart_card
│   ├── layout.py           # navbar, footer, page_header
│   └── callouts.py         # insight_box
├── assets/                 # Auto-loaded by Dash
│   ├── style.css           # Custom styling
│   ├── favicon.ico
│   └── logo.png
├── data/
│   ├── raw/                # Original downloads (never edited by hand)
│   └── clean/              # Processed datasets used by the app
├── notebooks/              # Exploratory analysis
├── scripts/                # Data download and preprocessing scripts
├── db/                     # Bonus: MySQL
│   ├── schema.sql
│   ├── load_data.py
│   └── covid.sql           # Database dump
├── theme.py                # Shared colors, fonts and chart template
├── environment.yml
├── requirements.txt
└── README.md
```

> Adjust this tree if the final layout differs, so the README stays accurate.

---

## 5. Data

### Sources

| Source            | Content                                                 | Link                                   |
| ----------------- | ------------------------------------------------------- | -------------------------------------- |
| Our World in Data | COVID-19 cases, deaths, vaccinations, policy stringency | https://ourworldindata.org/coronavirus |
| Eurostat          | European economic and COVID-19 indicators               | https://ec.europa.eu/eurostat          |
| INSEE             | French economic and COVID-19 data                       | https://www.insee.fr                   |
| Mendeley Data     | Research datasets on COVID-19                           | https://data.mendeley.com              |

_Update this table with the datasets actually used, including download date and license._

### Pipeline

1. **Collect:** raw files are stored in `data/raw/` and never modified.
2. **Clean:** scripts in `scripts/` handle missing values, type conversion, country-code harmonisation, date alignment and unit consistency.
3. **Merge:** health and economic indicators are joined by country (ISO code) and period.
4. **Explore:** notebooks in `notebooks/` document trends, correlations and anomalies.
5. **Output:** analysis-ready files go to `data/clean/`.

```bash
# Rebuild the clean data from the raw files
python scripts/preprocess.py
```

### Data dictionary

_A fills this in. One row per column used by the dashboard._

| Column              | Description                     | Unit       | Source | Frequency |
| ------------------- | ------------------------------- | ---------- | ------ | --------- |
| `iso_code`          | ISO 3166-1 alpha-3 country code | n/a        | OWID   | n/a       |
| `date`              | Observation date                | YYYY-MM-DD | OWID   | Daily     |
| `new_cases`         | New confirmed cases             | count      | OWID   | Daily     |
| `gdp_growth`        | GDP growth rate                 | %          | _tbd_  | Quarterly |
| `unemployment_rate` | Unemployment rate               | %          | _tbd_  | Monthly   |

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

fig = px.line(df, x="date", y="gdp_growth", color="country")

layout = chart_card(
    title="GDP fell sharply in Q2 2020 across most economies",
    subtitle="Quarterly GDP growth rate, selected countries",
    graph=dcc.Graph(figure=fig),
    source="Source: Eurostat, 2024",
    note="Growth rates are quarter-on-quarter and not seasonally comparable across all countries.",
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
- The deployed version reads from files in `data/clean/`. The MySQL database is included as a dump and can be used locally.
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

**Known limitations** _(complete as the project progresses)_

- _e.g. Under-reporting of cases in some countries._
- _e.g. Economic indicators are published at different frequencies and with delays._
- _e.g. Other events during 2020-2022 also affected the economy._

---

## 12. Evaluation criteria

- Technological innovation
- Development skills
- Project management
- Communication

---

## 13. Sources and credits

- [Our World in Data: Coronavirus](https://ourworldindata.org/coronavirus)
- [Eurostat](https://ec.europa.eu/eurostat)
- [INSEE](https://www.insee.fr)
- [Mendeley Data](https://data.mendeley.com)
- [Plotly Dash documentation](https://dash.plotly.com) and [Dash Gallery](https://plotly.com/examples/)
- # [Dash Bootstrap Components](https://dash-bootstrap-components.opensource.faculty.ai/)

# COVID-19 and the Global Economy: an Interactive Dashboard

A multi-page Plotly Dash dashboard that explores and illustrates the economic impact of the COVID-19 pandemic.

Project for **CentraleDigitalLab: Data Storytelling and Visualization** (Centrale Méditerranée).

> **Live demo:** _<add the URL here once deployed>_
> **Deadline:** final dashboard and 20-minute group oral presentation, **October 21**.

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

| Role                                   | Member | Responsibilities                                                                                                                          |
| -------------------------------------- | ------ | ----------------------------------------------------------------------------------------------------------------------------------------- |
| **A: Data and Preprocessing**          | _name_ | Dataset search, collection, cleaning, merging, exploratory analysis, data documentation                                                   |
| **B: Analyst and Storyteller**         | _name_ | Critical analysis (are the data sufficient?), narrative strategy, choice of indicators and chart types, bias review, annotations and text |
| **C: Dashboard Developer**             | _name_ | Dash app architecture, multi-page navigation, callbacks, charts, integration                                                              |
| **D: Design, Deployment and Database** | _name_ | Repo and environment setup, Bootstrap theme and CSS, reusable components, hosting, MySQL schema (bonus)                                   |

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
git clone <repository-url>
cd covid-dashboard

# 2. Create and activate the environment
conda env create -f environment.yml
conda activate covid-dashboard

# 3. Run the dashboard
python app.py
```

Then open **http://127.0.0.1:8050** in your browser.

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
- **Missing data files:** make sure `data/clean/` is populated. If it is not, run the preprocessing script (see [Data](#5-data)).
- **Environment conflicts:** remove and recreate it: `conda env remove -n covid-dashboard`, then repeat step 2.

---

## 4. Project structure

```
covid-dashboard/
├── app.py                  # Dash entry point; exposes `server` for deployment
├── pages/                  # One file per dashboard page (Dash multi-page)
│   ├── home.py
│   ├── timeline.py
│   ├── economy.py
│   ├── countries.py
│   ├── analysis.py
│   └── methodology.py
├── components/             # Reusable UI building blocks
│   ├── cards.py            # kpi_card, chart_card
│   ├── layout.py           # navbar, footer, page_header
│   └── callouts.py         # insight_box
├── assets/                 # Auto-loaded by Dash
│   ├── style.css           # Custom styling
│   ├── favicon.ico
│   └── logo.png
├── data/
│   ├── raw/                # Original downloads (never edited by hand)
│   └── clean/              # Processed datasets used by the app
├── notebooks/              # Exploratory analysis
├── scripts/                # Data download and preprocessing scripts
├── db/                     # Bonus: MySQL
│   ├── schema.sql
│   ├── load_data.py
│   └── covid.sql           # Database dump
├── theme.py                # Shared colors, fonts and chart template
├── environment.yml
├── requirements.txt
└── README.md
```

> Adjust this tree if the final layout differs, so the README stays accurate.

---

## 5. Data

### Sources

| Source            | Content                                                 | Link                                   |
| ----------------- | ------------------------------------------------------- | -------------------------------------- |
| Our World in Data | COVID-19 cases, deaths, vaccinations, policy stringency | https://ourworldindata.org/coronavirus |
| Eurostat          | European economic and COVID-19 indicators               | https://ec.europa.eu/eurostat          |
| INSEE             | French economic and COVID-19 data                       | https://www.insee.fr                   |
| Mendeley Data     | Research datasets on COVID-19                           | https://data.mendeley.com              |

_Update this table with the datasets actually used, including download date and license._

### Pipeline

1. **Collect:** raw files are stored in `data/raw/` and never modified.
2. **Clean:** scripts in `scripts/` handle missing values, type conversion, country-code harmonisation, date alignment and unit consistency.
3. **Merge:** health and economic indicators are joined by country (ISO code) and period.
4. **Explore:** notebooks in `notebooks/` document trends, correlations and anomalies.
5. **Output:** analysis-ready files go to `data/clean/`.

```bash
# Rebuild the clean data from the raw files
python scripts/preprocess.py
```

### Data dictionary

_A fills this in. One row per column used by the dashboard._

| Column              | Description                     | Unit       | Source | Frequency |
| ------------------- | ------------------------------- | ---------- | ------ | --------- |
| `iso_code`          | ISO 3166-1 alpha-3 country code | n/a        | OWID   | n/a       |
| `date`              | Observation date                | YYYY-MM-DD | OWID   | Daily     |
| `new_cases`         | New confirmed cases             | count      | OWID   | Daily     |
| `gdp_growth`        | GDP growth rate                 | %          | _tbd_  | Quarterly |
| `unemployment_rate` | Unemployment rate               | %          | _tbd_  | Monthly   |

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

fig = px.line(df, x="date", y="gdp_growth", color="country")

layout = chart_card(
    title="GDP fell sharply in Q2 2020 across most economies",
    subtitle="Quarterly GDP growth rate, selected countries",
    graph=dcc.Graph(figure=fig),
    source="Source: Eurostat, 2024",
    note="Growth rates are quarter-on-quarter and not seasonally comparable across all countries.",
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
- The deployed version reads from files in `data/clean/`. The MySQL database is included as a dump and can be used locally.
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

**Known limitations** _(complete as the project progresses)_

- _e.g. Under-reporting of cases in some countries._
- _e.g. Economic indicators are published at different frequencies and with delays._
- _e.g. Other events during 2020-2022 also affected the economy._

---

## 12. Evaluation criteria

- Technological innovation
- Development skills
- Project management
- Communication

---

## 13. Sources and credits

- [Our World in Data: Coronavirus](https://ourworldindata.org/coronavirus)
- [Eurostat](https://ec.europa.eu/eurostat)
- [INSEE](https://www.insee.fr)
- [Mendeley Data](https://data.mendeley.com)
- [Plotly Dash documentation](https://dash.plotly.com) and [Dash Gallery](https://plotly.com/examples/)
- [Dash Bootstrap Components](https://dash-bootstrap-components.opensource.faculty.ai/)

Built at Centrale Méditerranée, Nice, 2026.
