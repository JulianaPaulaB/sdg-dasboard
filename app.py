"""
SDG 3 Life Expectancy Dashboard
Converted from HTML/JS to Python Dash

Author: Juliana Paula T. Binas — BSIS 3A — Analytics Techniques and Tools

Requirements:
    pip install dash plotly pandas

Run:
    python sdg3_dashboard.py
    Then open http://127.0.0.1:8050 in your browser.
"""

import dash
from dash import dcc, html, Input, Output, callback
import plotly.graph_objects as go
import pandas as pd

# ── Data ──────────────────────────────────────────────────────────────────────
YEARS = list(range(2000, 2025))

UK = {
    "le":    [77.74,77.99,78.14,78.45,78.75,79.05,79.25,79.45,79.60,80.05,
              80.40,80.95,80.90,81.00,81.30,80.96,81.16,81.26,81.26,81.37,
              80.33,80.65,81.01,81.24,81.39],
    "hc":    [2021,2075,2364,2774,3362,3528,3803,4416,4280,3813,
              3876,4124,4204,4340,4733,4470,4043,3939,4234,4260,
              4866,5645,5112,5407,5860],
    "gdp":   [26536,27913,29089,30314,32051,32726,34727,35522,36745,35042,
              36484,37224,38337,39948,41267,42515,44085,46113,47212,50065,
              48230,51004,59022,59911,62009],
    "co2":   [9.64,9.75,9.41,9.56,9.53,9.41,9.30,9.09,8.79,7.90,
              8.12,7.40,7.62,7.42,6.76,6.46,6.06,5.84,5.69,5.44,
              4.84,5.06,4.56,4.48,4.53],
    "water": [100]*25,
}

USA = {
    "le":    [None,None,None,None,None,77.49,77.69,77.99,78.04,78.39,
              78.54,78.64,78.74,78.74,78.84,78.69,78.54,78.54,78.64,78.79,
              76.98,76.33,77.43,78.39,78.39],
    "hc":    [None,None,None,None,None,6429,6802,7154,7365,7615,
              7836,8016,8262,8412,8796,9201,9536,9823,10180,10550,
              11648,12080,12586,13473,13473],
    "gdp":   [None,None,None,None,None,44123,46302,48050,48570,47195,
              48643,50025,51708,53297,55153,56849,57977,60048,62876,65228,
              64402,71307,77861,82305,82305],
    "co2":   [None,None,None,None,None,20.72,20.24,20.28,19.41,17.81,
              18.23,17.63,16.81,17.10,17.12,16.46,15.93,15.64,16.00,15.50,
              13.82,14.76,14.80,14.32,14.32],
    "water": [None,None,None,None,None,98.90,98.90,98.91,98.92,98.92,
              99.01,99.10,99.18,99.26,99.35,99.43,99.51,99.59,99.67,99.74,
              99.82,99.89,99.96,100,100],
}

# Colours
PURPLE  = "#9c27b0"
PINK    = "#e91e63"
CYAN    = "#00bcd4"
ORANGE  = "#ff9800"
INDIGO  = "#3949ab"
TEAL    = "#00897b"
RED     = "#c62828"
DARK    = "#1a1a2e"

# ── Helpers ───────────────────────────────────────────────────────────────────
def avg_val(key, yr_idx, country):
    vals = []
    if country != "USA":
        vals.append(UK[key][yr_idx])
    if country != "UK" and USA[key][yr_idx] is not None:
        vals.append(USA[key][yr_idx])
    return sum(vals) / len(vals) if vals else None


def delta_str(key, yr_idx, country):
    cur = avg_val(key, yr_idx, country)
    prev = avg_val(key, max(yr_idx - 1, 0), country)
    if cur is None or prev is None:
        return 0
    return cur - prev


# ── Layout helpers ────────────────────────────────────────────────────────────
def kpi_card(icon, label, value, delta, color, is_good_up=True):
    dv = delta
    good = (dv > 0) == is_good_up
    cls  = "#4caf50" if dv == 0 else ("#4caf50" if good else "#e91e63")
    arrow = "—" if dv == 0 else ("▲" if dv > 0 else "▼")
    delta_txt = f"{arrow} {abs(dv):.2f}"

    return html.Div([
        html.Div(icon, style={"fontSize": "22px", "marginBottom": "6px"}),
        html.Div(label, style={"fontSize": "10px", "fontWeight": "700",
                               "color": "#aaa", "textTransform": "uppercase",
                               "letterSpacing": ".5px", "marginBottom": "4px"}),
        html.Div(value, style={"fontSize": "19px", "fontWeight": "800",
                               "color": DARK, "lineHeight": "1"}),
        html.Div(delta_txt, style={"fontSize": "10px", "marginTop": "5px",
                                   "color": cls, "fontWeight": "600"}),
    ], style={
        "background": "#fff",
        "borderRadius": "14px",
        "border": f"1px solid #ececec",
        "borderTop": f"3px solid {color}",
        "padding": "14px 16px",
        "flex": "1",
        "minWidth": "120px",
    })


def section_head(dot_color, title):
    return html.Div([
        html.Div(style={"width": "8px", "height": "8px", "borderRadius": "50%",
                        "background": dot_color}),
        html.H2(title, style={"fontSize": "13px", "fontWeight": "800",
                              "color": DARK, "textTransform": "uppercase",
                              "letterSpacing": ".8px"}),
    ], style={"display": "flex", "alignItems": "center", "gap": "10px",
              "margin": "20px 0 12px"})


def card(*children, extra_style=None):
    style = {"background": "#fff", "borderRadius": "14px",
             "border": "1px solid #ececec", "padding": "16px"}
    if extra_style:
        style.update(extra_style)
    return html.Div(list(children), style=style)


# ── App ───────────────────────────────────────────────────────────────────────
app = dash.Dash(__name__, title="SDG 3 Dashboard")

app.layout = html.Div([

    # ── Header ────────────────────────────────────────────────────────────────
    html.Div([
        html.Div([
            html.Span("✦ SDG 3 · Good Health", style={
                "background": "#e8d5f5", "borderRadius": "12px",
                "padding": "8px 14px", "fontSize": "11px", "fontWeight": "700",
                "color": "#6a0dad", "letterSpacing": ".5px"}),
        ]),
        html.Div([
            html.Div("Drivers of Life Expectancy Across Countries",
                     style={"color": "#fff", "fontSize": "17px",
                            "fontWeight": "700", "marginBottom": "3px"}),
            html.Div("Juliana Paula T. Binas · BSIS 3A · Analytics Techniques and Tools",
                     style={"color": "rgba(255,255,255,.6)", "fontSize": "11px"}),
        ], style={"marginLeft": "8px"}),
        html.Div([
            html.Span("2000–2024", style={
                "borderRadius": "20px", "padding": "5px 12px",
                "fontSize": "11px", "fontWeight": "700",
                "background": "#e8d5f5", "color": "#6a0dad"}),
            html.Span("World Bank", style={
                "borderRadius": "20px", "padding": "5px 12px",
                "fontSize": "11px", "fontWeight": "700",
                "background": "#fce4ec", "color": "#c2185b"}),
        ], style={"marginLeft": "auto", "display": "flex", "gap": "8px",
                  "alignItems": "center"}),
    ], style={"background": DARK, "padding": "22px 28px", "display": "flex",
              "alignItems": "center", "gap": "16px"}),

    # ── Body ──────────────────────────────────────────────────────────────────
    html.Div([

        # Filter bar
        html.Div([
            html.Label("Year", style={"fontSize": "11px", "fontWeight": "700",
                                      "color": "#888", "textTransform": "uppercase",
                                      "letterSpacing": ".5px"}),
            dcc.Slider(id="yr-slider", min=2000, max=2024, step=1, value=2024,
                       marks={y: str(y) for y in range(2000, 2025, 4)},
                       tooltip={"placement": "bottom", "always_visible": True}),
            html.Div(style={"width": "1px", "height": "20px", "background": "#eee"}),
            html.Label("Country", style={"fontSize": "11px", "fontWeight": "700",
                                         "color": "#888", "textTransform": "uppercase",
                                         "letterSpacing": ".5px"}),
            dcc.Dropdown(id="country-filter",
                         options=[
                             {"label": "🌍 Both countries", "value": "both"},
                             {"label": "🇬🇧 United Kingdom", "value": "UK"},
                             {"label": "🇺🇸 United States",  "value": "USA"},
                         ],
                         value="both", clearable=False,
                         style={"minWidth": "180px", "fontSize": "12px"}),
        ], style={"background": "#fff", "borderRadius": "14px",
                  "border": "1px solid #ececec", "padding": "14px 18px",
                  "marginBottom": "18px", "display": "flex",
                  "alignItems": "center", "gap": "16px", "flexWrap": "wrap"}),

        # KPI row
        html.Div(id="kpi-row",
                 style={"display": "flex", "gap": "10px",
                        "marginBottom": "16px", "flexWrap": "wrap"}),

        # ── Overview ──────────────────────────────────────────────────────────
        section_head(PURPLE, "Overview — trends over time"),
        html.Div([
            card(
                html.Div("Life expectancy over time",
                         style={"fontSize": "12px", "fontWeight": "700",
                                "color": DARK, "marginBottom": "12px"}),
                dcc.Graph(id="trend-chart", config={"displayModeBar": False},
                          style={"height": "200px"}),
                html.Div("✦ Both countries dipped in 2020–2021 due to COVID-19. "
                         "The UK recovered faster and consistently leads the USA "
                         "despite the USA spending nearly 2× more on healthcare.",
                         style={"background": "#f9f0ff", "borderLeft": f"3px solid #ce93d8",
                                "borderRadius": "0 10px 10px 0", "padding": "9px 12px",
                                "marginTop": "10px", "fontSize": "10.5px",
                                "lineHeight": "1.55", "color": "#4a148c"}),
            ),
            card(
                html.Div(id="bar-title",
                         style={"fontSize": "12px", "fontWeight": "700",
                                "color": DARK, "marginBottom": "12px"}),
                dcc.Graph(id="bar-chart", config={"displayModeBar": False},
                          style={"height": "180px"}),
                html.Div("✦ The UK outperforms the USA by ~3 years — spending "
                         "efficiency, not just total spending, drives outcomes.",
                         style={"background": "#fce4ec", "borderLeft": "3px solid #f48fb1",
                                "borderRadius": "0 10px 10px 0", "padding": "9px 12px",
                                "marginTop": "10px", "fontSize": "10.5px",
                                "lineHeight": "1.55", "color": "#880e4f"}),
            ),
        ], style={"display": "grid",
                  "gridTemplateColumns": "minmax(0,2fr) minmax(0,1fr)",
                  "gap": "12px", "marginBottom": "14px"}),

        # ── Key Drivers ───────────────────────────────────────────────────────
        section_head(CYAN, "Key drivers — what affects life expectancy?"),
        html.Div([
            card(
                html.Div("Healthcare spending",
                         style={"fontSize": "12px", "fontWeight": "700", "color": INDIGO}),
                dcc.Graph(id="hc-chart", config={"displayModeBar": False},
                          style={"height": "130px"}),
                html.Div([html.B("Positive ↑"), " — More investment, longer lives. (Jaba et al., 2014)"],
                         style={"background": "#e8eaf6", "borderLeft": f"3px solid #9fa8da",
                                "borderRadius": "0 8px 8px 0", "padding": "9px 12px",
                                "marginTop": "8px", "fontSize": "10.5px",
                                "lineHeight": "1.55", "color": "#1a237e"}),
            ),
            card(
                html.Div("GDP per capita",
                         style={"fontSize": "12px", "fontWeight": "700", "color": ORANGE}),
                dcc.Graph(id="gdp-chart", config={"displayModeBar": False},
                          style={"height": "130px"}),
                html.Div([html.B("Positive ↑"), " — Wealth lifts living standards. (Preston, 1975)"],
                         style={"background": "#fff3e0", "borderLeft": "3px solid #ffcc80",
                                "borderRadius": "0 8px 8px 0", "padding": "9px 12px",
                                "marginTop": "8px", "fontSize": "10.5px",
                                "lineHeight": "1.55", "color": "#e65100"}),
            ),
            card(
                html.Div("Water access",
                         style={"fontSize": "12px", "fontWeight": "700", "color": TEAL}),
                dcc.Graph(id="water-chart", config={"displayModeBar": False},
                          style={"height": "130px"}),
                html.Div([html.B("Positive ↑"), " — Clean water cuts disease burden. (UN, 2023)"],
                         style={"background": "#e0f2f1", "borderLeft": "3px solid #80cbc4",
                                "borderRadius": "0 8px 8px 0", "padding": "9px 12px",
                                "marginTop": "8px", "fontSize": "10.5px",
                                "lineHeight": "1.55", "color": "#004d40"}),
            ),
            card(
                html.Div("CO₂ emissions",
                         style={"fontSize": "12px", "fontWeight": "700", "color": RED}),
                dcc.Graph(id="co2-chart", config={"displayModeBar": False},
                          style={"height": "130px"}),
                html.Div([html.B("Negative ↓"), " — Pollution shortens lives. (Wen et al., 2021)"],
                         style={"background": "#ffebee", "borderLeft": "3px solid #ef9a9a",
                                "borderRadius": "0 8px 8px 0", "padding": "9px 12px",
                                "marginTop": "8px", "fontSize": "10.5px",
                                "lineHeight": "1.55", "color": "#b71c1c"}),
            ),
        ], style={"display": "grid",
                  "gridTemplateColumns": "repeat(4,minmax(0,1fr))",
                  "gap": "10px", "marginBottom": "14px"}),

        # ── Correlation ───────────────────────────────────────────────────────
        section_head(ORANGE, "Correlation analysis"),
        card(
            html.Div("Strength of relationship with life expectancy",
                     style={"fontSize": "12px", "fontWeight": "700",
                            "color": DARK, "marginBottom": "12px"}),
            dcc.Graph(id="corr-chart", config={"displayModeBar": False},
                      style={"height": "180px"}),
            extra_style={"marginBottom": "14px"},
        ),

        # ── Regression ────────────────────────────────────────────────────────
        section_head(PINK, "Regression model — performance & predictions"),
        html.Div([
            card(
                html.Div("Model performance (Robust RLM)",
                         style={"fontSize": "12px", "fontWeight": "700",
                                "color": DARK, "marginBottom": "10px"}),
                html.Div([
                    html.Div([
                        html.Div("R² Score", style={"fontSize": "9px",
                                                    "textTransform": "uppercase",
                                                    "color": "#7b1fa2",
                                                    "fontWeight": "700"}),
                        html.Div("0.94", style={"fontSize": "22px",
                                               "fontWeight": "800",
                                               "color": "#4a148c"}),
                    ], style={"background": "#f3e5f5", "borderRadius": "10px",
                              "padding": "10px 14px", "flex": "1",
                              "textAlign": "center"}),
                    html.Div([
                        html.Div("RMSE", style={"fontSize": "9px",
                                               "textTransform": "uppercase",
                                               "color": "#3949ab",
                                               "fontWeight": "700"}),
                        html.Div("0.42", style={"fontSize": "22px",
                                               "fontWeight": "800",
                                               "color": "#1a237e"}),
                    ], style={"background": "#e8eaf6", "borderRadius": "10px",
                              "padding": "10px 14px", "flex": "1",
                              "textAlign": "center"}),
                    html.Div([
                        html.Div("Obs.", style={"fontSize": "9px",
                                              "textTransform": "uppercase",
                                              "color": "#c2185b",
                                              "fontWeight": "700"}),
                        html.Div("44", style={"fontSize": "22px",
                                             "fontWeight": "800",
                                             "color": "#880e4f"}),
                    ], style={"background": "#fce4ec", "borderRadius": "10px",
                              "padding": "10px 14px", "flex": "1",
                              "textAlign": "center"}),
                ], style={"display": "flex", "gap": "8px", "marginBottom": "12px"}),
                dcc.Graph(id="pred-chart", config={"displayModeBar": False},
                          style={"height": "160px"}),
            ),
            card(
                html.Div("Feature importance (from RLM coefficients)",
                         style={"fontSize": "12px", "fontWeight": "700",
                                "color": DARK, "marginBottom": "12px"}),
                dcc.Graph(id="fi-chart", config={"displayModeBar": False},
                          style={"height": "160px"}),
                html.Div("✦ Healthcare spending and water access are the top positive "
                         "drivers. CO₂ is the strongest negative driver.",
                         style={"background": "#f3e5f5", "borderLeft": "3px solid #ce93d8",
                                "borderRadius": "0 10px 10px 0", "padding": "9px 12px",
                                "marginTop": "10px", "fontSize": "10.5px",
                                "lineHeight": "1.55", "color": "#4a148c"}),
            ),
        ], style={"display": "grid",
                  "gridTemplateColumns": "repeat(2,minmax(0,1fr))",
                  "gap": "12px", "marginBottom": "14px"}),

        # ── Recommendations ───────────────────────────────────────────────────
        section_head("#4caf50", "Insights & recommendations"),
        html.Div([
            html.Div([
                html.H4("🫀 Increase healthcare investment",
                        style={"fontSize": "12px", "fontWeight": "700",
                               "color": "#1a237e", "marginBottom": "5px"}),
                html.Span("Every $1,000 increase in per-capita healthcare spending is "
                          "linked to measurably longer life expectancy. Efficient "
                          "spending matters more than raw totals — the UK proves this.",
                          style={"color": "#283593", "fontSize": "11px",
                                 "lineHeight": "1.55"}),
            ], style={"background": "#e8eaf6", "borderRadius": "12px",
                      "padding": "13px 15px"}),
            html.Div([
                html.H4("🏦 Promote economic growth",
                        style={"fontSize": "12px", "fontWeight": "700",
                               "color": "#e65100", "marginBottom": "5px"}),
                html.Span("Policies that grow GDP per capita — through education, trade, "
                          "and infrastructure — lift living standards and indirectly "
                          "extend lives via better nutrition and healthcare access.",
                          style={"color": "#bf360c", "fontSize": "11px",
                                 "lineHeight": "1.55"}),
            ], style={"background": "#fff3e0", "borderRadius": "12px",
                      "padding": "13px 15px"}),
            html.Div([
                html.H4("💧 Ensure universal water access",
                        style={"fontSize": "12px", "fontWeight": "700",
                               "color": "#004d40", "marginBottom": "5px"}),
                html.Span("Expanding clean water infrastructure reduces preventable "
                          "waterborne diseases that disproportionately shorten life "
                          "expectancy in vulnerable and lower-income populations.",
                          style={"color": "#00695c", "fontSize": "11px",
                                 "lineHeight": "1.55"}),
            ], style={"background": "#e0f2f1", "borderRadius": "12px",
                      "padding": "13px 15px"}),
            html.Div([
                html.H4("🌿 Reduce carbon emissions",
                        style={"fontSize": "12px", "fontWeight": "700",
                               "color": "#b71c1c", "marginBottom": "5px"}),
                html.Span("Transitioning to cleaner energy and enforcing stricter "
                          "emission standards directly reduces pollution-linked disease "
                          "burden — confirmed significant by the regression analysis.",
                          style={"color": "#c62828", "fontSize": "11px",
                                 "lineHeight": "1.55"}),
            ], style={"background": "#ffebee", "borderRadius": "12px",
                      "padding": "13px 15px"}),
        ], style={"display": "grid",
                  "gridTemplateColumns": "repeat(2,minmax(0,1fr))",
                  "gap": "10px", "marginBottom": "14px"}),

        # ── Conclusion ────────────────────────────────────────────────────────
        html.Div([
            html.H3("✦ Final conclusion",
                    style={"fontSize": "14px", "fontWeight": "800",
                           "marginBottom": "8px", "color": "#e8d5f5"}),
            html.P([
                "The robust regression analysis confirms that ",
                html.B("healthcare spending"), ", ",
                html.B("GDP per capita"), ", and ",
                html.B("water access"),
                " are significant positive drivers of life expectancy, while ",
                html.B("CO₂ emissions"),
                " act as a significant negative driver. Together they explain ",
                html.B("94% of the variance"),
                " in life expectancy across the UK and USA from 2000 to 2024 — "
                "directly supporting the goals of SDG 3: Good Health and Well-Being.",
            ], style={"fontSize": "11.5px", "lineHeight": "1.7",
                      "color": "rgba(255,255,255,.8)"}),
            html.Div([
                html.Span("Healthcare spending ↑",
                          style={"background": PURPLE, "color": "#fff",
                                 "borderRadius": "20px", "padding": "5px 13px",
                                 "fontSize": "10px", "fontWeight": "700"}),
                html.Span("GDP per capita ↑",
                          style={"background": "#f57c00", "color": "#fff",
                                 "borderRadius": "20px", "padding": "5px 13px",
                                 "fontSize": "10px", "fontWeight": "700"}),
                html.Span("Water access ↑",
                          style={"background": TEAL, "color": "#fff",
                                 "borderRadius": "20px", "padding": "5px 13px",
                                 "fontSize": "10px", "fontWeight": "700"}),
                html.Span("CO₂ emissions ↓",
                          style={"background": RED, "color": "#fff",
                                 "borderRadius": "20px", "padding": "5px 13px",
                                 "fontSize": "10px", "fontWeight": "700"}),
                html.Span("R² = 0.94",
                          style={"background": "#e8d5f5", "color": "#4a148c",
                                 "borderRadius": "20px", "padding": "5px 13px",
                                 "fontSize": "10px", "fontWeight": "700"}),
            ], style={"display": "flex", "gap": "8px", "marginTop": "12px",
                      "flexWrap": "wrap"}),
        ], style={"background": DARK, "borderRadius": "14px",
                  "padding": "18px 22px", "marginTop": "14px", "color": "#fff"}),

    ], style={"padding": "20px 24px"}),

], style={"background": "#faf9f7", "paddingBottom": "40px",
          "fontFamily": "'Segoe UI', system-ui, sans-serif"})


# ── Callbacks ─────────────────────────────────────────────────────────────────
def mk_layout(show=True):
    return dict(
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        font=dict(size=9, family="Segoe UI, system-ui, sans-serif"),
        xaxis=dict(showgrid=False, tickfont=dict(size=9)),
        yaxis=dict(gridcolor="#f5f5f5", tickfont=dict(size=9)),
        hovermode="x unified",
    )


@callback(
    Output("kpi-row",     "children"),
    Output("bar-title",   "children"),
    Output("trend-chart", "figure"),
    Output("bar-chart",   "figure"),
    Output("hc-chart",    "figure"),
    Output("gdp-chart",   "figure"),
    Output("water-chart", "figure"),
    Output("co2-chart",   "figure"),
    Output("pred-chart",  "figure"),
    Output("corr-chart",  "figure"),
    Output("fi-chart",    "figure"),
    Input("yr-slider",      "value"),
    Input("country-filter", "value"),
)
def update_all(year, country):
    yi = YEARS.index(year)

    # ── KPI cards ─────────────────────────────────────────────────────────────
    def fmt_kpi(key, fmt, icon, label, color, is_good_up=True):
        val  = avg_val(key, yi, country)
        dv   = delta_str(key, yi, country)
        if val is None:
            return html.Div()
        return kpi_card(icon, label, fmt(val), dv, color, is_good_up)

    kpis = [
        fmt_kpi("le",    lambda v: f"{v:.1f} yrs", "🫀", "Life expectancy",     PURPLE,  True),
        fmt_kpi("hc",    lambda v: f"${v:,.0f}",   "🏥", "Healthcare spending", INDIGO,  True),
        fmt_kpi("gdp",   lambda v: f"${v/1000:.0f}k", "💰", "GDP per capita",  ORANGE,  True),
        fmt_kpi("co2",   lambda v: f"{v:.1f} tons","🌫️","CO₂ emissions",       RED,     False),
        fmt_kpi("water", lambda v: f"{v:.1f}%",    "💧", "Water access",        TEAL,    True),
    ]

    # ── Trend chart ───────────────────────────────────────────────────────────
    trend_traces = []
    if country != "USA":
        trend_traces.append(go.Scatter(
            x=YEARS, y=UK["le"], name="United Kingdom",
            line=dict(color=PURPLE, width=2.5),
            fill="tozeroy", fillcolor=PURPLE + "22",
            mode="lines+markers", marker=dict(size=3),
        ))
    if country != "UK":
        trend_traces.append(go.Scatter(
            x=YEARS, y=USA["le"], name="United States",
            line=dict(color=CYAN, width=2.5, dash="dash"),
            fill="tozeroy", fillcolor=CYAN + "15",
            mode="lines+markers", marker=dict(size=3),
        ))
    trend_fig = go.Figure(trend_traces)
    trend_fig.update_layout(**mk_layout(),
                            yaxis=dict(range=[74, 85], gridcolor="#f5f5f5",
                                       ticksuffix="y", tickfont=dict(size=9)))

    # ── Bar chart ─────────────────────────────────────────────────────────────
    bar_lbls, bar_vals, bar_cols = [], [], []
    if country != "USA":
        bar_lbls.append("UK"); bar_vals.append(UK["le"][yi]); bar_cols.append(PURPLE)
    if country != "UK" and USA["le"][yi] is not None:
        bar_lbls.append("USA"); bar_vals.append(USA["le"][yi]); bar_cols.append(CYAN)
    bar_fig = go.Figure(go.Bar(x=bar_lbls, y=bar_vals,
                               marker=dict(color=bar_cols,
                                           line=dict(width=0)),
                               text=[f"{v:.2f} yrs" for v in bar_vals],
                               textposition="outside"))
    bar_fig.update_layout(**mk_layout(),
                          yaxis=dict(range=[70, 85], gridcolor="#f5f5f5",
                                     ticksuffix="y", tickfont=dict(size=9)))

    # ── Scatter helper ────────────────────────────────────────────────────────
    def scatter_fig(x_key, y_key="le", *, xfmt=None):
        traces = []
        if country != "USA":
            traces.append(go.Scatter(
                x=UK[x_key], y=UK[y_key], name="UK",
                mode="markers", marker=dict(color=PURPLE + "cc", size=5),
            ))
        if country != "UK":
            pairs = [(x, y) for x, y in zip(USA[x_key], USA[y_key])
                     if x is not None and y is not None]
            if pairs:
                xs, ys = zip(*pairs)
                traces.append(go.Scatter(
                    x=xs, y=ys, name="USA",
                    mode="markers", marker=dict(color=CYAN + "cc", size=5),
                ))
        fig = go.Figure(traces)
        xtick = dict(tickfont=dict(size=8))
        if xfmt:
            xtick["tickformat"] = xfmt
        fig.update_layout(**mk_layout(),
                          xaxis=dict(**xtick, showgrid=False),
                          yaxis=dict(range=[74, 84], gridcolor="#f8f8f8",
                                     tickfont=dict(size=8)))
        return fig

    hc_fig  = scatter_fig("hc",  xfmt="$,")
    gdp_fig = scatter_fig("gdp", xfmt="$,")

    # ── Water line ────────────────────────────────────────────────────────────
    water_traces = []
    if country != "USA":
        water_traces.append(go.Scatter(x=YEARS, y=UK["water"], name="UK",
                                       line=dict(color=TEAL, width=2),
                                       mode="lines+markers", marker=dict(size=3)))
    if country != "UK":
        water_traces.append(go.Scatter(x=YEARS, y=USA["water"], name="USA",
                                       line=dict(color=ORANGE, width=2, dash="dot"),
                                       mode="lines+markers", marker=dict(size=3)))
    water_fig = go.Figure(water_traces)
    water_fig.update_layout(**mk_layout(),
                            yaxis=dict(range=[97, 101], ticksuffix="%",
                                       gridcolor="#f8f8f8", tickfont=dict(size=8)))

    # ── CO2 line ──────────────────────────────────────────────────────────────
    co2_traces = []
    if country != "USA":
        co2_traces.append(go.Scatter(x=YEARS, y=UK["co2"], name="UK",
                                     line=dict(color=RED, width=2),
                                     mode="lines+markers", marker=dict(size=3)))
    if country != "UK":
        co2_traces.append(go.Scatter(x=YEARS, y=USA["co2"], name="USA",
                                     line=dict(color=ORANGE, width=2, dash="dot"),
                                     mode="lines+markers", marker=dict(size=3)))
    co2_fig = go.Figure(co2_traces)
    co2_fig.update_layout(**mk_layout(),
                          yaxis=dict(ticksuffix=" t", gridcolor="#f8f8f8",
                                     tickfont=dict(size=8)))

    # ── Prediction chart ──────────────────────────────────────────────────────
    actual = [77.7,78.1,78.7,79.2,79.6,80.4,80.9,81.0,81.3,80.96,
              81.16,81.26,81.26,81.37,80.33,80.65,81.01]
    pred   = [77.5,78.3,78.9,79.4,79.8,80.2,81.1,80.8,81.5,80.7,
              81.3, 81.4, 81.1, 81.5, 80.1, 80.9, 81.2]
    pred_yrs = [2000,2002,2004,2006,2008,2010,2012,2014,2016,2018,
                2019,2020,2021,2022,2023,2024]
    pred_fig = go.Figure([
        go.Scatter(x=pred_yrs, y=actual, name="Actual",
                   line=dict(color=PURPLE, width=2.5),
                   mode="lines+markers", marker=dict(size=4)),
        go.Scatter(x=pred_yrs, y=pred, name="Predicted",
                   line=dict(color=CYAN, width=2, dash="dash"),
                   mode="lines+markers", marker=dict(size=3)),
    ])
    pred_fig.update_layout(**mk_layout(),
                           yaxis=dict(range=[75, 84], gridcolor="#f5f5f5",
                                      tickfont=dict(size=8)),
                           showlegend=True,
                           legend=dict(font=dict(size=9), orientation="h",
                                       yanchor="bottom", y=1, x=0))

    # ── Correlation bar ───────────────────────────────────────────────────────
    corr_data = [
        ("Healthcare spending", 0.87, INDIGO),
        ("GDP per capita",      0.82, ORANGE),
        ("Water access",        0.71, TEAL),
        ("CO₂ emissions",      -0.63, RED),
    ]
    corr_fig = go.Figure(go.Bar(
        y=[d[0] for d in corr_data],
        x=[d[1] for d in corr_data],
        orientation="h",
        marker=dict(color=[d[2] for d in corr_data]),
        text=[f"{'+' if d[1]>0 else ''}{d[1]:.2f}" for d in corr_data],
        textposition="outside",
    ))
    corr_fig.update_layout(**mk_layout(),
                           xaxis=dict(range=[-1, 1], showgrid=True,
                                      gridcolor="#f5f5f5", zeroline=True,
                                      zerolinecolor="#ccc",
                                      tickfont=dict(size=9)),
                           yaxis=dict(showgrid=False, tickfont=dict(size=10)))

    # ── Feature importance chart ───────────────────────────────────────────────
    fi_data = [
        ("Healthcare spending", 0.92, INDIGO,  "+0.0042"),
        ("Water access",        0.75, TEAL,    "+0.135"),
        ("GDP per capita",      0.60, ORANGE,  "+0.00008"),
        ("CO₂ emissions",       0.45, RED,     "−0.089"),
    ]
    fi_fig = go.Figure(go.Bar(
        y=[d[0] for d in fi_data],
        x=[d[1] for d in fi_data],
        orientation="h",
        marker=dict(color=[d[2] for d in fi_data]),
        text=[d[3] for d in fi_data],
        textposition="outside",
    ))
    fi_fig.update_layout(**mk_layout(),
                         xaxis=dict(range=[0, 1.1], showgrid=True,
                                    gridcolor="#f5f5f5", tickformat=".0%",
                                    tickfont=dict(size=9)),
                         yaxis=dict(showgrid=False, tickfont=dict(size=10)))

    bar_title = f"Country comparison — {year}"

    return (kpis, bar_title,
            trend_fig, bar_fig,
            hc_fig, gdp_fig,
            water_fig, co2_fig,
            pred_fig, corr_fig, fi_fig)


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True)
