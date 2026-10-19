"""Descriptive associations between policy, mobility, health, and growth."""

import pandas as pd
import plotly.express as px
from dash import Input, Output, callback, html, register_page

from components.layout import chart_card, empty_figure, insight, page_header, source_note, styled_figure
from components.data_utils import filtered_data
from assets.theme import AMBER, BLUE, RED, TEAL


register_page(__name__, path="/pandemic-policy", name="Pandemic & policy", order=3)

layout = html.Div([
    page_header("Policy, mobility and outcomes moved together in complex ways.", "COVID-19 · POLICY · MOBILITY", "Explore country-year associations among government response, workplace mobility, deaths and economic performance. These views are descriptive: they cannot isolate policy effects from timing, severity, economic structure or other factors."),
    html.Div(id="policy-insight"),
    html.Div([
        chart_card("Stricter policy and workplace mobility", "Annual mean stringency index versus workplace visits relative to the pre-pandemic baseline.", "policy-mobility"),
        chart_card("Pandemic mortality and growth slowdown", "Annual new deaths per 1,000 people versus real GDP growth deterioration from 2019.", "policy-mortality"),
    ], className="chart-grid two-up"),
    chart_card("Economic support and growth slowdown", "Annual mean support index versus growth-rate deterioration relative to 2019.", "policy-support", class_name="wide-card"),
    html.Div(className="caution-line", children="Interpretation: points are country-level annual observations; correlations are not causal effects. Death reporting, policy indices and mobility coverage differ across countries."),
    source_note("Sources: OxCGRT policy indices, Google mobility, project COVID annual totals, and World Bank GDP growth. COVID/policy/mobility coverage is limited to the project’s pandemic-era years."),
])


def _scatter(data, x, y, title, x_label, y_label, color=BLUE, custom=None):
    complete = data.dropna(subset=[x, y])
    if complete.empty:
        return empty_figure("No paired observations for this selection"), complete
    name_col = "country" if "country" in complete else "countryname"
    fig = px.scatter(complete, x=x, y=y, color="region" if complete["region"].notna().any() else None, hover_name=name_col, hover_data={"country_code": True}, labels={x: x_label, y: y_label, "region": "Region"}, color_discrete_sequence=[color, TEAL, AMBER, RED, "#687da9"])
    fig = styled_figure(fig, 350)
    return fig, complete


@callback(Output("policy-mobility", "figure"), Output("policy-mortality", "figure"), Output("policy-support", "figure"), Output("policy-insight", "children"), Input("filter-year", "value"), Input("filter-region", "value"), Input("filter-income", "value"))
def update_policy(year, region, income):
    snapshot_year = 2020 if year == "all" else year
    data = filtered_data(snapshot_year, region, income).copy()
    mobility_fig, mobility = _scatter(data, "stringency_index_avg", "mobility_workplaces_avg", "", "Stringency index (0–100)", "Workplace mobility change (%)")
    if "newdeaths" in data and "population" in data:
        data["new_deaths_per_1000"] = data["newdeaths"] / data["population"] * 1000
    mortality_fig, mortality = _scatter(data, "new_deaths_per_1000", "gdp_growth_deterioration_vs_2019_pp", "", "New deaths per 1,000 people", "Growth slowdown vs 2019 (pp)", RED)
    support_fig, support = _scatter(data, "economic_support_index_avg", "gdp_growth_deterioration_vs_2019_pp", "", "Economic support index (0–100)", "Growth slowdown vs 2019 (pp)", AMBER)
    pairs = []
    for frame, x, y, label in [
        (mobility, "stringency_index_avg", "mobility_workplaces_avg", "stringency and workplace mobility"),
        (mortality, "new_deaths_per_1000", "gdp_growth_deterioration_vs_2019_pp", "mortality and growth slowdown"),
        (support, "economic_support_index_avg", "gdp_growth_deterioration_vs_2019_pp", "support and growth slowdown"),
    ]:
        if len(frame) >= 3:
            corr = frame[[x, y]].corr(method="spearman").iloc[0, 1]
            pairs.append(f"{label}: Spearman ρ={corr:.2f} (n={len(frame)})")
        else:
            pairs.append(f"{label}: insufficient paired data (n={len(frame)})")
    text = f"Selected year: {snapshot_year}. " + " · ".join(pairs) + ". Descriptive associations only; no causal interpretation is warranted from these comparisons."
    return mobility_fig, mortality_fig, support_fig, insight(text)
