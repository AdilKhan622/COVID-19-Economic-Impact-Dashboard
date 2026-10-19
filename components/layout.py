"""Reusable page, chart, and KPI building blocks."""

from dash import dcc, html

from assets.theme import FIGURE_STYLE, INK, LINE, MUTED, PANEL


def page_header(title: str, question: str, description: str):
    return html.Div([
        html.Div(question, className="eyebrow"),
        html.H1(title, className="page-title"),
        html.P(description, className="page-intro"),
    ], className="page-header")


def chart_card(title: str, note: str, graph_id: str, figure=None, *, class_name=""):
    return html.Section([
        html.Div([html.H2(title), html.P(note, className="chart-note")], className="chart-heading"),
        dcc.Graph(id=graph_id, figure=figure, config={"displaylogo": False, "toImageButtonOptions": {"format": "png", "filename": "covid-economic-impact"}}),
    ], className=f"chart-card {class_name}".strip())


def kpi_card(label: str, value: str, note: str):
    return html.Div([html.Div(label, className="kpi-label"), html.Div(value, className="kpi-value"), html.Div(note, className="kpi-note")], className="kpi-card")


def insight(text: str):
    return html.Div([html.Span("READOUT", className="eyebrow"), html.P(text)], className="insight-box")


def empty_figure(message: str = "No observations for this selection"):
    import plotly.graph_objects as go
    fig = go.Figure()
    fig.add_annotation(text=message, x=0.5, y=0.5, xref="paper", yref="paper", showarrow=False, font={"color": MUTED, "size": 14})
    fig.update_layout(**FIGURE_STYLE, xaxis={"visible": False}, yaxis={"visible": False}, height=340)
    return fig


def styled_figure(fig, height=380):
    fig.update_layout(**FIGURE_STYLE, height=height)
    return fig


def source_note(text: str):
    return html.P(text, className="source-note")


def select(label: str, component_id: str, options, value=None, *, multi=False, clearable=False):
    return html.Label([
        html.Span(label, className="filter-label"),
        dcc.Dropdown(id=component_id, options=options, value=value, multi=multi, clearable=clearable, className="filter-dropdown"),
    ], className="filter-control")
