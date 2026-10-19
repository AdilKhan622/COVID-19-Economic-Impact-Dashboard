"""Shared visual and Plotly theme tokens for the dashboard."""

INK = "#17242d"
MUTED = "#667782"
PAPER = "#f6f7f5"
PANEL = "#ffffff"
LINE = "#dfe5e5"
BLUE = "#176b87"
TEAL = "#4b9e91"
RED = "#b7473e"
AMBER = "#c27b28"
PALETTE = [BLUE, TEAL, "#6c7fb4", AMBER, RED, "#546a5b"]

FIGURE_STYLE = {
    "template": "plotly_white",
    "font": {"family": "Inter, Arial, sans-serif", "color": INK, "size": 12},
    "paper_bgcolor": PANEL,
    "plot_bgcolor": PANEL,
    "margin": {"l": 48, "r": 24, "t": 48, "b": 44},
    "legend": {"orientation": "h", "y": 1.12, "x": 0, "title": {"text": ""}},
    "hoverlabel": {"bgcolor": "#ffffff", "bordercolor": LINE, "font": {"color": INK}},
}
