"""Interactive multi-country comparison across economic indicators."""

import pandas as pd
import plotly.express as px
from dash import Input, Output, callback, dcc, html, register_page

from components.layout import chart_card, empty_figure, page_header, source_note, styled_figure
from data_utils import country_options, filtered_data, load_data
from theme import PALETTE


register_page(__name__, path="/country-lab", name="Country lab", order=4)

_available = {option["value"] for option in country_options()}
_default_countries = [code for code in ["USA", "FRA", "CHN", "BRA"] if code in _available][:3]

layout = html.Div([
    page_header("Compare trajectories, not just snapshots.", "COUNTRY COMPARISON LAB", "Select countries to compare economic indicators from their available historical records. Pandemic policy and mobility series are shown only in years where the project dataset contains them."),
    html.Div([
        html.Label([html.Span("Countries", className="filter-label"), dcc.Dropdown(id="country-selection", options=country_options(), value=_default_countries, multi=True, placeholder="Choose two or more countries", className="filter-dropdown")], className="country-select"),
    ], className="country-filter-bar"),
    html.Div([
        chart_card("Real GDP growth", "Annual real GDP growth (%)", "country-growth"),
        chart_card("Unemployment and inflation", "Annual rates (%). Missing values are left as gaps.", "country-labor-prices"),
    ], className="chart-grid two-up"),
    chart_card("Policy and mobility during the pandemic", "OxCGRT annual stringency and workplace mobility relative to baseline; project coverage is 2020–2022.", "country-policy", class_name="wide-card"),
    html.Div(id="country-table", className="table-wrap"),
    source_note("Each country is identified by ISO3. GDP growth, unemployment and inflation are World Bank annual indicators. The nominal GDP level column is not used as a substitute for real output growth."),
])


@callback(Output("country-growth", "figure"), Output("country-labor-prices", "figure"), Output("country-policy", "figure"), Output("country-table", "children"), Input("country-selection", "value"), Input("filter-region", "value"), Input("filter-income", "value"))
def update_country_lab(codes, region, income):
    if not codes:
        empty = empty_figure("Choose at least one country to begin")
        return empty, empty, empty, html.P("Select countries above.", className="empty-state")
    data = filtered_data("all", region, income)
    data = data.loc[data["country_code"].isin(codes)].copy()
    if data.empty:
        empty = empty_figure("Selected countries do not match the current region/income filters")
        return empty, empty, empty, html.P("No rows match the selected countries and global filters.", className="empty-state")
    name_col = "country" if "country" in data else "countryname"
    data["country_display"] = data[name_col].fillna(data["country_code"]) + " (" + data["country_code"] + ")"
    def line(column, ylabel, height=350):
        subset = data.dropna(subset=[column])
        if subset.empty:
            return empty_figure("No observations for selected countries")
        fig = px.line(subset, x="year", y=column, color="country_display", markers=False, color_discrete_sequence=PALETTE, labels={"year": "Year", column: ylabel, "country_display": "Country"})
        return styled_figure(fig, height)
    growth = line("real_gdp_growth_pct", "Real GDP growth (%)")
    labor = data.melt(id_vars=["year", "country_display"], value_vars=["unemployment_rate_pct", "inflation_rate_pct"], var_name="indicator", value_name="rate")
    labor = labor.dropna(subset=["rate"])
    if labor.empty:
        labor_fig = empty_figure("No unemployment or inflation observations for selected countries")
    else:
        labor["indicator"] = labor["indicator"].map({"unemployment_rate_pct": "Unemployment", "inflation_rate_pct": "Inflation"})
        labor_fig = px.line(labor, x="year", y="rate", color="country_display", line_dash="indicator", color_discrete_sequence=PALETTE, labels={"year": "Year", "rate": "Annual rate (%)", "country_display": "Country", "indicator": "Indicator"})
        labor_fig = styled_figure(labor_fig, 350)
    pandemic = data.dropna(subset=["stringency_index_avg", "mobility_workplaces_avg"])
    if pandemic.empty:
        policy_fig = empty_figure("Policy and mobility data are available for 2020–2022 only")
    else:
        policy_long = pandemic.melt(id_vars=["year", "country_display"], value_vars=["stringency_index_avg", "mobility_workplaces_avg"], var_name="measure", value_name="value")
        policy_long["measure"] = policy_long["measure"].map({"stringency_index_avg": "Stringency index (0–100)", "mobility_workplaces_avg": "Workplace mobility change (%)"})
        policy_fig = px.line(policy_long, x="year", y="value", color="country_display", facet_row="measure", markers=True, color_discrete_sequence=PALETTE, labels={"year": "Year", "value": "Value in measure units", "country_display": "Country", "measure": ""})
        policy_fig.update_yaxes(matches=None)
        policy_fig.for_each_annotation(lambda annotation: annotation.update(text=annotation.text.split("=")[-1]))
        policy_fig = styled_figure(policy_fig, 350)
    metrics = data.sort_values(["country_display", "year"]).groupby("country_display", as_index=False).agg(
        years=("year", lambda x: f"{x.min()}–{x.max()}"),
        real_gdp_growth_pct=("real_gdp_growth_pct", "last"),
        unemployment_rate_pct=("unemployment_rate_pct", "last"),
        inflation_rate_pct=("inflation_rate_pct", "last"),
        gdp_growth_deterioration_vs_2019_pp=("gdp_growth_deterioration_vs_2019_pp", "last"),
    )
    table = html.Table([
        html.Thead(html.Tr([html.Th("Country"), html.Th("Available years"), html.Th("Latest real GDP growth"), html.Th("Latest unemployment"), html.Th("Latest inflation"), html.Th("Growth slowdown vs 2019")])) ,
        html.Tbody([html.Tr([html.Td(row.country_display), html.Td(row.years), html.Td(_fmt(row.real_gdp_growth_pct)), html.Td(_fmt(row.unemployment_rate_pct)), html.Td(_fmt(row.inflation_rate_pct)), html.Td(_fmt(row.gdp_growth_deterioration_vs_2019_pp, " pp"))]) for row in metrics.itertuples()]),
    ], className="data-table")
    return growth, labor_fig, policy_fig, table


def _fmt(value, suffix="%"):
    return "—" if pd.isna(value) else f"{value:.2f}{suffix}"
