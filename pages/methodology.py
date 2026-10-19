"""Sources, indicator definitions, coverage, and interpretation limits."""

import pandas as pd
from dash import html, register_page

from components.layout import page_header, source_note
from components.data_utils import load_data


register_page(__name__, path="/methodology", name="Data & method", order=5)

_data = load_data()
_indicator_columns = ["real_gdp_growth_pct", "unemployment_rate_pct", "inflation_rate_pct"]
_coverage_rows = []
for column in _indicator_columns:
    observed = int(_data[column].notna().sum())
    annual = _data.loc[_data[column].notna()].groupby("year")["country_code"].nunique()
    _coverage_rows.append(html.Tr([
        html.Td(column), html.Td(f"{observed:,}"), html.Td(f"{annual.index.min()}–{annual.index.max()}" if len(annual) else "—"), html.Td(f"{annual.max():,}" if len(annual) else "—"),
    ]))

layout = html.Div([
    page_header("Transparent methods make comparison possible.", "DATA & METHODOLOGY", "The dashboard brings together the existing annual COVID/policy/mobility master and three World Bank indicators. Historical economic data remain available outside the 2020–2022 pandemic-data window."),
    html.Div([
        html.Section([html.H2("Sources and definitions"), html.Dl([
            html.Dt("Real GDP growth"), html.Dd(["Annual percentage growth in real GDP (World Bank NY.GDP.MKTP.KD.ZG). Used for economic performance comparisons; the existing wdi_gdp field is a nominal GDP level and is not treated as real growth. ", html.A("Indicator source", href="https://data.worldbank.org/indicator/NY.GDP.MKTP.KD.ZG", target="_blank")]),
            html.Dt("Unemployment"), html.Dd(["Modeled ILO estimate: unemployment as a percentage of the labor force (SL.UEM.TOTL.ZS). ", html.A("Indicator source", href="https://data.worldbank.org/indicator/SL.UEM.TOTL.ZS", target="_blank")]),
            html.Dt("Inflation"), html.Dd(["Annual consumer-price inflation (FP.CPI.TOTL.ZG), percent change in consumer prices. ", html.A("Indicator source", href="https://data.worldbank.org/indicator/FP.CPI.TOTL.ZG", target="_blank")]),
            html.Dt("Pandemic and policy"), html.Dd("Project COVID annual totals, OxCGRT policy indices, Google mobility, and World Bank region/income metadata, as documented in Data_cleaning/DATA_CLEANING_DOCUMENTATION.md. The overview reports annual new cases and deaths per 100,000 people using population as the denominator."),
        ])], className="method-card"),
        html.Section([html.H2("Coverage in the dashboard panel"), html.P(f"{_data['country_code'].nunique()} country/economy codes · {_data['year'].min()}–{_data['year'].max()} · {_data.shape[0]:,} country-year keys. The original COVID/policy/mobility master covers 2020–2022; the new economic indicators extend the panel to their available World Bank years."), html.Table([
            html.Thead(html.Tr([html.Th("Indicator"), html.Th("Observed rows"), html.Th("Available years"), html.Th("Peak countries in a year")])) , html.Tbody(_coverage_rows),
        ], className="data-table"), html.P("Rows with unavailable indicators remain in the panel as missing. No zero fills, interpolation or forward/backward fills were applied.", className="small-note")], className="method-card"),
    ], className="method-grid"),
    html.Section([html.H2("Derived comparisons"), html.Ul([
        html.Li("GDP growth deterioration = 2019 real GDP growth minus selected-year real GDP growth. Positive values indicate a slower growth rate than 2019, not a fall in GDP level."),
        html.Li("Unemployment and inflation changes are percentage-point differences from each country’s own 2019 observation."),
        html.Li("Exploratory no-COVID growth benchmark: for countries with at least four of five observations, expected 2020–2022 real GDP growth is set to that country's mean annual growth in 2015–2019. The actual-minus-benchmark gap is in percentage points. A 2010–2019 mean is shown as a sensitivity check, requiring at least eight observations."),
        html.Li("Exploratory Economic Strain Index = (GDP slowdown z-score + unemployment-increase z-score + inflation-pressure z-score) / 3. Each of the three components has equal weight."),
        html.Li("A z-score puts a component on a common scale: it expresses how many standard deviations a country-year is above or below the average of the pooled 2020–2022 reference sample. Higher index values indicate more strain relative to that reference; negative values do not mean there was no impact."),
        html.Li("GDP slowdown = 2019 real GDP growth minus current-year real GDP growth. Unemployment increase = current-year rate minus the 2019 rate. Inflation pressure = max(current-year inflation minus 2019 inflation, 0); an inflation decrease is assigned zero pressure and is not counted as a benefit."),
        html.Li("Scores use the same complete-case country-year sample pooled over 2020–2022 to calculate standardization values, so a region or income filter does not change a country's score. Rows missing any of the three components and World Bank aggregates are excluded."),
        html.Li("A comparison is missing when its country lacks the relevant 2019 baseline."),
        html.Li("Country rankings omit World Bank aggregate entities; regional and income-group comparisons use country observations."),
        html.Li("Global headline values are shown as country medians, not as population-weighted or official global rates."),
    ])], className="method-card"),
    html.Section([html.H2("Limitations to keep in view"), html.Ul([
        html.Li("World Bank indicator coverage differs by year and country. The 2025 observations are the latest values in the downloaded files and may not be equally complete across indicators."),
        html.Li("Unemployment is a modeled ILO estimate; country labor markets and price baskets are not perfectly comparable."),
        html.Li("Google mobility measures changes from its pre-pandemic baseline for opted-in users, not absolute visits; 2020 and 2022 source periods are partial."),
        html.Li("OxCGRT indices describe policy stringency/support, not implementation or effectiveness."),
        html.Li("Reported COVID deaths and cases have differences in testing, reporting and attribution across countries."),
        html.Li("Cross-country associations are descriptive and do not establish that policy, mobility or pandemic severity caused an economic outcome."),
        html.Li("The no-COVID benchmark is a simple continuation of historical average growth, not a statistically identified causal effect. It assumes no-COVID growth would have matched the chosen pre-pandemic average and cannot account for other shocks; the result is a growth-rate gap, not GDP-level losses."),
        html.Li("The strain index is an exploratory three-indicator summary. Scores depend on the selected components, equal-weight choice and standardization reference; they do not represent the complete economic impact of COVID-19."),
        html.Li("The exploratory dashboard does not claim to measure the full economic cost of COVID-19."),
    ])], className="method-card"),
    source_note("World Bank downloads in Data_cleaning/data/raw/world_bank/economic_indicators/; existing pipeline and source limitations in Data_cleaning/DATA_CLEANING_DOCUMENTATION.md."),
])
