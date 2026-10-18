"""Entry point for the Global Economic Impact of COVID-19 dashboard."""

from dash import Dash, Input, Output, State, dcc, html, page_container, page_registry

from data_utils import load_data


app = Dash(__name__, use_pages=True, suppress_callback_exceptions=True, title="COVID-19 & the Global Economy")
server = app.server


def _options(column: str):
    data = load_data()
    values = sorted(data[column].dropna().unique().tolist())
    return [{"label": str(value), "value": value} for value in values]


page_links = [
    dcc.Link(page["name"], href=page["relative_path"], className="nav-link")
    for page in sorted(page_registry.values(), key=lambda record: record.get("order", 99))
]

app.layout = html.Div([
    dcc.Location(id="url"),
    html.Header([
        dcc.Link([html.Span("C", className="brand-mark"), html.Span([html.Strong("COVID-19"), html.Small("& THE GLOBAL ECONOMY")])], href="/", className="brand"),
        html.Nav(page_links, className="main-nav"),
    ], className="site-header"),
    html.Main([
        html.Div([
            html.Div([html.Span("GLOBAL FILTERS", className="eyebrow"), html.Span("Choose a snapshot; trend charts retain their available years.", className="filter-hint")], className="filter-intro"),
            html.Label([html.Span("Year", className="filter-label"), dcc.Dropdown(id="filter-year", options=[{"label": "All available years", "value": "all"}, *_options("year")], value=2020, clearable=False, className="filter-dropdown")], className="filter-control"),
            html.Label([html.Span("World Bank region", className="filter-label"), dcc.Dropdown(id="filter-region", options=[{"label": "All regions", "value": "all"}, *_options("region")], value="all", clearable=False, className="filter-dropdown")], className="filter-control"),
            html.Label([html.Span("Income group", className="filter-label"), dcc.Dropdown(id="filter-income", options=[{"label": "All income groups", "value": "all"}, *_options("income_group")], value="all", clearable=False, className="filter-dropdown")], className="filter-control"),
            html.Button("Download filtered CSV", id="download-button", className="download-button"),
            dcc.Download(id="download-data"),
        ], className="filter-bar"),
        page_container,
    ], className="main-content"),
], className="app-shell")


@app.callback(
    Output("download-data", "data"),
    Input("download-button", "n_clicks"),
    State("filter-year", "value"),
    State("filter-region", "value"),
    State("filter-income", "value"),
    prevent_initial_call=True,
)
def download_filtered(_clicks, year, region, income):
    import pandas as pd
    from data_utils import filtered_data

    data = filtered_data(year, region, income)
    if data.empty:
        data = pd.DataFrame(columns=load_data().columns)
    return dcc.send_data_frame(data.to_csv, "covid_economic_impact_filtered.csv", index=False)


if __name__ == "__main__":
    import os
    app.run(debug=False, host="127.0.0.1", port=int(os.environ.get("PORT", "8050")))
