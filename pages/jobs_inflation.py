"""Labor-market and price trends alongside real growth."""

import pandas as pd
import plotly.express as px
from dash import Input, Output, callback, html, register_page

from components.layout import chart_card, empty_figure, insight, page_header, source_note, styled_figure
from components.data_utils import filtered_data
from assets.theme import PALETTE


register_page(__name__, path="/jobs-prices", name="Jobs & prices", order=2)

layout = html.Div([
    page_header("Jobs and prices moved on different timelines.", "JOBS & INFLATION", "Follow unemployment and consumer-price inflation across the observed years, then inspect how labor-market pressure aligns with real GDP growth in a selected snapshot."),
    html.Div(id="jobs-insight"),
    html.Div([
        chart_card("Country medians over time", "Annual median unemployment and inflation rates across countries in the selected region and income group.", "jobs-trends"),
        chart_card("Unemployment and real growth", "One point per country. A high unemployment rate with weak growth is a descriptive combination, not by itself a diagnosis of stagflation.", "jobs-scatter"),
    ], className="chart-grid two-up"),
    html.Div(id="jobs-diagnostics", className="insight-box subtle"),
    source_note("Sources: World Bank real GDP growth, modeled ILO unemployment estimate, and consumer-price inflation series. Rate changes are percentage-point differences."),
])


@callback(Output("jobs-trends", "figure"), Output("jobs-scatter", "figure"), Output("jobs-insight", "children"), Output("jobs-diagnostics", "children"), Input("filter-year", "value"), Input("filter-region", "value"), Input("filter-income", "value"))
def update_jobs(year, region, income):
    history = filtered_data("all", region, income)
    trend = history.groupby("year", as_index=False).agg(unemployment=("unemployment_rate_pct", "median"), inflation=("inflation_rate_pct", "median")).melt("year", var_name="measure", value_name="country_median")
    trend = trend.dropna(subset=["country_median"])
    if trend.empty:
        trend_fig = empty_figure("No labor-market or inflation observations for these filters")
    else:
        trend["measure"] = trend["measure"].map({"unemployment": "Unemployment", "inflation": "Inflation"})
        trend_fig = px.line(trend, x="year", y="country_median", color="measure", markers=False, color_discrete_sequence=PALETTE, labels={"year": "Year", "country_median": "Median rate (%)", "measure": ""})
        trend_fig = styled_figure(trend_fig, 380)
    snapshot_year = 2020 if year == "all" else year
    data = filtered_data(snapshot_year, region, income).dropna(subset=["unemployment_rate_pct", "real_gdp_growth_pct"])
    if data.empty:
        scatter = empty_figure("No countries have both measures in this selection")
        note = "No countries have complete unemployment and real-growth observations for the selected snapshot."
    else:
        name_col = "country" if "country" in data else "countryname"
        scatter = px.scatter(data, x="real_gdp_growth_pct", y="unemployment_rate_pct", color="region" if data["region"].notna().any() else None, hover_name=name_col, hover_data={"country_code": True, "inflation_rate_pct": ":.2f", "unemployment_change_vs_2019_pp": ":.2f"}, labels={"real_gdp_growth_pct": "Real GDP growth (%)", "unemployment_rate_pct": "Unemployment (% of labor force)", "region": "Region"}, color_discrete_sequence=PALETTE)
        scatter = styled_figure(scatter, 380)
        weak = data.loc[data["real_gdp_growth_pct"].lt(0) & data["inflation_rate_pct"].gt(data["inflation_rate_pct"].median())]
        note = f"{len(data)} countries have both unemployment and real-growth data in {snapshot_year}. {len(weak)} combine negative real growth with inflation above the sample median; this is a descriptive screen, not a causal or official stagflation classification."
    change_rows = data.dropna(subset=["unemployment_change_vs_2019_pp"])
    if len(change_rows):
        most = change_rows.loc[change_rows["unemployment_change_vs_2019_pp"].idxmax()]
        readout = f"In {snapshot_year}, unemployment was up a median {change_rows['unemployment_change_vs_2019_pp'].median():.1f} percentage points from 2019 across {len(change_rows)} countries with a baseline. The largest rise in this selection was {most.get('country', most['country_code'])} ({most['unemployment_change_vs_2019_pp']:.1f} pp)."
    else:
        readout = f"No {snapshot_year} unemployment observations have a matching country-level 2019 baseline in this selection."
    return trend_fig, scatter, insight(readout), html.P(note)
