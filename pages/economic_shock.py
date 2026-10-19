"""Country-level real growth shock comparisons."""

import pandas as pd
import plotly.express as px
from dash import Input, Output, callback, html, register_page

from components.layout import chart_card, empty_figure, insight, page_header, source_note, styled_figure
from components.counterfactual import PANDEMIC_YEARS, build_growth_counterfactual
from components.data_utils import filtered_data, load_impact_index
from assets.theme import BLUE, RED


register_page(__name__, path="/economic-shock", name="Economic shock", order=1)

layout = html.Div([
    page_header("Where did growth slow most?", "ECONOMIC SHOCK", "Compare each country’s annual real GDP growth with its own 2019 growth rate. A positive deterioration means the growth rate was lower; it does not mean output fell by that amount."),
    html.Div(id="shock-insight"),
    html.Div([
        chart_card("Largest growth slowdowns", "Growth deterioration = 2019 real GDP growth minus selected-year growth (percentage points). Countries require both years.", "shock-ranking"),
        chart_card("The slowdown was uneven", "Country-level change relative to 2019. The diverging scale is centered at zero.", "shock-map"),
    ], className="chart-grid two-up"),
    html.Section([
        html.H2("What might growth have looked like without COVID-19?"),
        html.P("A historical benchmark estimates each country’s expected annual real GDP growth using its 2015–2019 average. We compare observed pandemic-year growth with that benchmark; a second 2010–2019 benchmark checks how sensitive the result is to the chosen pre-pandemic window.", className="chart-note"),
        html.Div(id="counterfactual-insight"),
        html.Div([
            chart_card("Observed growth vs historical benchmark", "Country medians for 2020–2022. The benchmark is a scenario based on pre-pandemic growth, not an observed no-COVID outcome.", "counterfactual-trend"),
            chart_card("Largest shortfalls vs benchmark", "Selected pandemic year. Gap = actual growth minus expected growth (percentage points); negative values are below the historical benchmark.", "counterfactual-ranking"),
        ], className="chart-grid two-up"),
        html.P("Interpretation limit: this assumes each country would have continued growing at its 2015–2019 average without the pandemic. It does not account for other shocks or establish that COVID-19 caused the gap. It estimates growth-rate differences, not GDP-level losses.", className="caution-line"),
    ], className="method-card counterfactual-panel"),
    html.Section([
        html.H2("Economic strain across output, jobs and prices"),
        html.Div([
            html.P("This exploratory score combines three ways economies can come under pressure during the pandemic: slower real-GDP growth, rising unemployment, and rising inflation. Each measure is put on a common scale, then all three receive equal weight.", className="chart-note"),
            html.P([html.Strong("Formula: "), html.Code("Strain score = (GDP slowdown z-score + unemployment-increase z-score + inflation-pressure z-score) ÷ 3")], className="index-formula"),
            html.P("A z-score shows how far a value is above or below the reference-sample average, measured in standard deviations. Higher scores mean more strain relative to the pooled 2020–2022 comparison sample; a negative score does not mean there was no economic impact.", className="chart-note"),
            html.P("GDP slowdown is 2019 growth minus selected-year growth. Unemployment increase is the selected-year rate minus 2019. Inflation pressure is the positive inflation increase versus 2019; an inflation decrease is assigned zero pressure, not treated as a benefit. Only country-years with all three measures are scored. The same complete-country sample sets the scale for every region and income filter.", className="chart-note"),
        ], className="index-explanation"),
        html.Div(id="strain-insight"),
        html.Div([
            chart_card("Country median strain over time", "Index scores are relative to the pooled 2020–2022 sample; the country/income filters change which observations are displayed, not the standardization reference.", "strain-timeline"),
            chart_card("Highest strain scores", "Selected pandemic year. Hover to inspect all three component changes and the index score.", "strain-ranking"),
        ], className="chart-grid two-up"),
        html.P("This is a project-defined summary of three measured dimensions, not an official economic measure or the full cost of COVID-19. Scores require all three components and are not causal estimates.", className="caution-line"),
    ], className="method-card strain-panel"),
    source_note("Source: World Bank indicator NY.GDP.MKTP.KD.ZG. Rankings exclude regional and income-group aggregates; coverage varies by year."),
])


@callback(
    Output("shock-ranking", "figure"), Output("shock-map", "figure"), Output("shock-insight", "children"),
    Output("counterfactual-trend", "figure"), Output("counterfactual-ranking", "figure"), Output("counterfactual-insight", "children"),
    Input("filter-year", "value"), Input("filter-region", "value"), Input("filter-income", "value"),
)
def update_shock(year, region, income):
    selected_year = 2020 if year == "all" else int(year)
    data = filtered_data(selected_year, region, income).dropna(subset=["gdp_growth_deterioration_vs_2019_pp"]).copy()
    if data.empty:
        shock_outputs = (empty_figure("No 2019 baseline and selected-year growth values for this selection"), empty_figure(), insight("This selection has no comparable 2019 baseline."))
    else:
        name_col = "country" if "country" in data else "countryname"
        ranked = data.sort_values("gdp_growth_deterioration_vs_2019_pp", ascending=False).head(12)
        fig = px.bar(ranked.sort_values("gdp_growth_deterioration_vs_2019_pp"), x="gdp_growth_deterioration_vs_2019_pp", y=name_col, orientation="h", color="gdp_growth_deterioration_vs_2019_pp", color_continuous_scale=[[0, BLUE], [0.5, "#f4f3ef"], [1, RED]], color_continuous_midpoint=0, hover_data={"country_code": True, "real_gdp_growth_pct": ":.2f", "gdp_growth_deterioration_vs_2019_pp": ":.2f"}, labels={"gdp_growth_deterioration_vs_2019_pp": "Growth slowdown (pp)", name_col: "Country"})
        fig = styled_figure(fig, 440)
        fig.update_layout(coloraxis_showscale=False)
        map_fig = px.choropleth(data, locations="country_code", color="gdp_growth_deterioration_vs_2019_pp", hover_name=name_col, hover_data={"real_gdp_growth_pct": ":.2f", "gdp_growth_deterioration_vs_2019_pp": ":.2f"}, color_continuous_scale=[[0, BLUE], [0.5, "#f4f3ef"], [1, RED]], color_continuous_midpoint=0, labels={"gdp_growth_deterioration_vs_2019_pp": "Growth slowdown (pp)"})
        map_fig.update_geos(showframe=False, showcoastlines=False, projection_type="natural earth")
        map_fig = styled_figure(map_fig, 440)
        leader = data.loc[data["gdp_growth_deterioration_vs_2019_pp"].idxmax()]
        text = f"Among {len(data)} countries with a 2019 baseline and {selected_year} observation, {leader.get(name_col, leader['country_code'])} had the largest growth-rate slowdown: {leader['gdp_growth_deterioration_vs_2019_pp']:.1f} percentage points."
        shock_outputs = (fig, map_fig, insight(text))

    panel = filtered_data("all", region, income)
    counterfactual = build_growth_counterfactual(panel)
    country_names = panel[[column for column in ["country_code", "country", "countryname"] if column in panel]].drop_duplicates("country_code")
    counterfactual = counterfactual.merge(country_names, on="country_code", how="left", validate="many_to_one")
    pandemic = counterfactual.loc[counterfactual["year"].isin(PANDEMIC_YEARS)].copy()
    if pandemic.empty:
        return (*shock_outputs, empty_figure("No eligible country observations for the counterfactual"), empty_figure(), insight("No countries in this selection have enough 2015–2019 growth data and observed pandemic-year growth."))

    annual = pandemic.groupby("year", as_index=False).agg(
        actual_growth_pct=("actual_growth_pct", "median"),
        baseline_2015_19_pct=("baseline_2015_19_pct", "median"),
        baseline_2010_19_pct=("baseline_2010_19_pct", "median"),
        countries=("country_code", "nunique"),
    )
    trend = annual.melt(id_vars=["year", "countries"], value_vars=["actual_growth_pct", "baseline_2015_19_pct", "baseline_2010_19_pct"], var_name="series", value_name="median_growth_pct")
    series_names = {
        "actual_growth_pct": "Observed growth",
        "baseline_2015_19_pct": "No-COVID benchmark · 2015–19 mean",
        "baseline_2010_19_pct": "Sensitivity benchmark · 2010–19 mean",
    }
    trend["series"] = trend["series"].map(series_names)
    trend_fig = px.line(trend, x="year", y="median_growth_pct", color="series", markers=True, hover_data={"countries": True}, labels={"year": "Year", "median_growth_pct": "Median real GDP growth (%)", "series": "Series", "countries": "Countries"}, color_discrete_sequence=["#176b87", "#b7473e", "#c27b28"])
    trend_fig = styled_figure(trend_fig, 390)
    trend_fig.update_xaxes(dtick=1)

    selected = pandemic.loc[pandemic["year"].eq(selected_year)].dropna(subset=["growth_gap_vs_2015_19_baseline_pp"]).copy()
    if selected.empty:
        ranking_fig = empty_figure("Choose 2020, 2021 or 2022 to compare with the historical benchmark")
        cf_note = insight(f"The historical counterfactual covers 2020–2022. The selected year ({selected_year}) is outside that window. The trend chart still shows the full pandemic period.")
    else:
        selected_year_data = selected.copy()
        ranking_data = selected_year_data.sort_values("growth_gap_vs_2015_19_baseline_pp").head(12)
        name_col = "country" if "country" in selected else "countryname"
        ranking_fig = px.bar(ranking_data.sort_values("growth_gap_vs_2015_19_baseline_pp", ascending=False), x="growth_gap_vs_2015_19_baseline_pp", y=name_col, orientation="h", color="growth_gap_vs_2015_19_baseline_pp", color_continuous_scale=[[0, RED], [0.5, "#f4f3ef"], [1, BLUE]], color_continuous_midpoint=0, hover_data={"country_code": True, "actual_growth_pct": ":.2f", "baseline_2015_19_pct": ":.2f", "baseline_2015_19_years": True, "growth_gap_vs_2015_19_baseline_pp": ":.2f"}, labels={"growth_gap_vs_2015_19_baseline_pp": "Actual minus benchmark (pp)", name_col: "Country"})
        ranking_fig = styled_figure(ranking_fig, 390)
        ranking_fig.update_layout(coloraxis_showscale=False)
        median_actual = selected_year_data["actual_growth_pct"].median()
        median_baseline = selected_year_data["baseline_2015_19_pct"].median()
        median_gap = selected_year_data["growth_gap_vs_2015_19_baseline_pp"].median()
        alt = selected_year_data["growth_gap_vs_2010_19_baseline_pp"].dropna()
        alt_text = f" Against the 2010–2019 sensitivity benchmark, the median gap is {alt.median():+.1f} points across {len(alt)} countries." if len(alt) else " The longer-baseline sensitivity estimate is unavailable for some or all selected countries."
        cf_note = insight(f"For {selected_year}, {len(selected)} countries meet the minimum 2015–2019 coverage rule. Median actual growth was {median_actual:.1f}%; the 2015–2019 historical benchmark was {median_baseline:.1f}%; the median gap was {median_gap:+.1f} percentage points.{alt_text}")
    return (*shock_outputs, trend_fig, ranking_fig, cf_note)


@callback(
    Output("strain-timeline", "figure"), Output("strain-ranking", "figure"), Output("strain-insight", "children"),
    Input("filter-year", "value"), Input("filter-region", "value"), Input("filter-income", "value"),
)
def update_strain_index(year, region, income):
    scores = load_impact_index()
    if region not in (None, "all", ""):
        scores = scores.loc[scores["region"].eq(region)]
    if income not in (None, "all", ""):
        scores = scores.loc[scores["income_group"].eq(income)]

    if scores.empty:
        return empty_figure("No complete country observations for this group selection"), empty_figure(), insight("No selected countries have all three index components in the 2020–2022 comparison period.")

    annual = scores.groupby("year", as_index=False).agg(
        median_strain=("economic_strain_index", "median"),
        countries=("country_code", "nunique"),
    )
    trend_fig = px.line(annual, x="year", y="median_strain", markers=True, hover_data={"countries": True}, labels={"year": "Year", "median_strain": "Median Economic Strain Index (z-score)", "countries": "Countries"}, color_discrete_sequence=["#176b87"])
    trend_fig = styled_figure(trend_fig, 390)
    trend_fig.update_xaxes(dtick=1)

    selected_year = 2020 if year == "all" else int(year)
    selected = scores.loc[scores["year"].eq(selected_year)].copy()
    if selected.empty:
        return trend_fig, empty_figure("The Economic Strain Index is available for 2020–2022 only"), insight(f"The filtered sample contains {scores['country_code'].nunique()} countries across the pandemic window. Select 2020, 2021 or 2022 to see the country ranking.")

    name_column = "country" if "country" in selected else "countryname"
    highest = selected.nlargest(12, "economic_strain_index").sort_values("economic_strain_index")
    ranking_fig = px.bar(
        highest, x="economic_strain_index", y=name_column, orientation="h",
        color="economic_strain_index", color_continuous_scale=[[0, "#4b9e91"], [0.5, "#f4f3ef"], [1, "#b7473e"]], color_continuous_midpoint=0,
        hover_data={"country_code": True, "economic_strain_index": ":.2f", "gdp_deterioration_pp": ":.2f", "unemployment_increase_pp": ":.2f", "inflation_pressure_pp": ":.2f"},
        labels={"economic_strain_index": "Economic Strain Index (z-score)", name_column: "Country", "gdp_deterioration_pp": "GDP growth deterioration (pp)", "unemployment_increase_pp": "Unemployment increase (pp)", "inflation_pressure_pp": "Inflation pressure (pp)"},
    )
    ranking_fig = styled_figure(ranking_fig, 390)
    ranking_fig.update_layout(coloraxis_showscale=False)
    median_score = selected["economic_strain_index"].median()
    above_average = (selected["economic_strain_index"] > 0).mean() * 100
    return trend_fig, ranking_fig, insight(f"In {selected_year}, {len(selected)} countries have complete GDP, unemployment and inflation components. Their median index score is {median_score:+.2f}; {above_average:.0f}% score above zero, the pooled reference-sample average.")
