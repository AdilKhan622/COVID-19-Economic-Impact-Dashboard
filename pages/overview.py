"""Global snapshot and the long-run economic context."""

import pandas as pd
import plotly.express as px
from dash import Input, Output, callback, html, register_page

from components.layout import chart_card, empty_figure, insight, kpi_card, page_header, select, source_note, styled_figure
from data_utils import filtered_data, load_data
from theme import BLUE, PALETTE, RED, TEAL


register_page(__name__, path="/", name="Overview", order=0)

layout = html.Div([
    page_header("The shock was global. The outcomes were not.", "GLOBAL ECONOMIC OVERVIEW", "Explore real GDP growth, labor-market pressure, prices and pandemic-era policy across countries. The World Bank series extends beyond the pandemic window, while policy, mobility and COVID measures are available mainly for 2020–2022."),
    html.Div(id="overview-insight"),
    html.Div(id="overview-kpis", className="kpi-grid"),
    html.Div([select("Map indicator", "overview-indicator", [
            {"label": "Real GDP growth (%)", "value": "real_gdp_growth_pct"},
            {"label": "Growth slowdown vs 2019 (pp)", "value": "gdp_growth_deterioration_vs_2019_pp"},
            {"label": "Unemployment (%)", "value": "unemployment_rate_pct"},
            {"label": "Inflation (%)", "value": "inflation_rate_pct"},
        ], "real_gdp_growth_pct")], className="map-filter"),
    html.Div([
        chart_card("Country map · selected indicator", "One value per country. When all years are selected, the map shows each country’s median across its available years; World Bank aggregates are excluded.", "overview-map"),
        chart_card("The economic record extends beyond the pandemic", "Median country observation by year. Each line is a country median, not a population-weighted global rate.", "overview-trend"),
    ], className="chart-grid two-up"),
    source_note("Sources: World Bank World Development Indicators; project COVID, policy, mobility and country metadata tables. Missing values are not imputed."),
])


@callback(
    Output("overview-kpis", "children"), Output("overview-insight", "children"), Output("overview-map", "figure"), Output("overview-trend", "figure"),
    Input("filter-year", "value"), Input("filter-region", "value"), Input("filter-income", "value"), Input("overview-indicator", "value"),
)
def update_overview(year, region, income, indicator):
    selected = filtered_data(year, region, income)
    def median_text(column, suffix="%"):
        values = selected[column].dropna() if column in selected else pd.Series(dtype=float)
        return f"{values.median():.1f}{suffix}" if len(values) else "—"
    year_note = "all years · country-year median" if year == "all" else f"{year} · country median"
    countries_covered = (
        selected.loc[selected["real_gdp_growth_pct"].notna(), "country_code"].nunique()
        if "real_gdp_growth_pct" in selected
        else 0
    )
    cards = [
        kpi_card("Real GDP growth", median_text("real_gdp_growth_pct"), year_note),
        kpi_card("Unemployment", median_text("unemployment_rate_pct"), year_note),
        kpi_card("Inflation", median_text("inflation_rate_pct"), year_note),
        kpi_card("COVID cases / deaths per 100k", "—", f"annual new cases / deaths · {year_note}"),
        kpi_card("Countries covered", f"{countries_covered:,}", "with real GDP growth in selection"),
    ]
    if "newdeaths" in selected and "newcases" in selected and "population" in selected:
        selected = selected.copy()
        selected["_cases_per_100k"] = selected["newcases"] / selected["population"] * 100_000
        selected["_deaths_per_100k"] = selected["newdeaths"] / selected["population"] * 100_000
        case_values, death_values = selected["_cases_per_100k"].dropna(), selected["_deaths_per_100k"].dropna()
        cases = f"{case_values.median():.0f}" if len(case_values) else "—"
        deaths = f"{death_values.median():.1f}" if len(death_values) else "—"
        cards[3] = kpi_card("COVID cases / deaths per 100k", f"{cases} / {deaths}", f"annual new cases / deaths · {year_note}")
    map_data = selected.dropna(subset=[indicator]).copy() if indicator in selected else pd.DataFrame()
    name_col = "country" if "country" in map_data else "countryname"
    if year == "all" and not map_data.empty:
        map_data = map_data.groupby("country_code", as_index=False).agg(
            **{indicator: (indicator, "median"), name_col: (name_col, "first")}
        )
    labels = {
        "real_gdp_growth_pct": "Real GDP growth (%)",
        "gdp_growth_deterioration_vs_2019_pp": "Growth slowdown vs 2019 (pp)",
        "unemployment_rate_pct": "Unemployment (% of labor force)",
        "inflation_rate_pct": "Consumer-price inflation (%)",
    }
    label = labels.get(indicator, "Selected indicator")
    if not map_data.empty:
        map_value = map_data[indicator].median()
        map_period = "the median of country medians across available years" if year == "all" else f"the country median in {year}"
        insight_text = f"Across {map_data['country_code'].nunique()} countries with observations, {map_period} for {label.lower()} was {map_value:.1f}. This is an unweighted country summary, not a global aggregate."
        map_color_scale = [[0, RED], [0.5, "#f5f5f1"], [1, BLUE]] if indicator in {"real_gdp_growth_pct", "gdp_growth_deterioration_vs_2019_pp"} else [[0, "#eef3f2"], [1, BLUE]]
        map_kwargs = {"color_continuous_midpoint": 0} if indicator in {"real_gdp_growth_pct", "gdp_growth_deterioration_vs_2019_pp"} else {}
        map_fig = px.choropleth(map_data, locations="country_code", color=indicator, hover_name=name_col, hover_data={"country_code": True, indicator: ":.2f"}, color_continuous_scale=map_color_scale, labels={indicator: label}, **map_kwargs)
        map_fig.update_geos(showframe=False, showcoastlines=False, projection_type="natural earth")
        map_fig = styled_figure(map_fig, 420)
    else:
        insight_text, map_fig = f"No {label.lower()} observations match these filters.", empty_figure()
    trend_data = filtered_data("all", region, income)
    if trend_data["real_gdp_growth_pct"].notna().any():
        yearly = trend_data.groupby("year", as_index=False).agg(
            real_gdp_growth_pct=("real_gdp_growth_pct", "median"),
            unemployment_rate_pct=("unemployment_rate_pct", "median"),
            inflation_rate_pct=("inflation_rate_pct", "median"),
        ).melt("year", var_name="indicator", value_name="country_median")
        labels = {"real_gdp_growth_pct": "Real GDP growth", "unemployment_rate_pct": "Unemployment", "inflation_rate_pct": "Inflation"}
        yearly["indicator"] = yearly["indicator"].map(labels)
        trend_fig = px.line(yearly, x="year", y="country_median", color="indicator", facet_row="indicator", markers=False, color_discrete_sequence=PALETTE, labels={"year": "Year", "country_median": "Median country rate (%)", "indicator": ""}, category_orders={"indicator": ["Real GDP growth", "Unemployment", "Inflation"]})
        trend_fig.update_yaxes(matches=None)
        trend_fig.for_each_annotation(lambda annotation: annotation.update(text=annotation.text.split("=")[-1]))
        trend_fig = styled_figure(trend_fig, 520)
    else:
        trend_fig = empty_figure("No economic observations for these region and income filters")
    return cards, insight(insight_text), map_fig, trend_fig
