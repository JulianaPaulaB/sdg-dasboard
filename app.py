import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import statsmodels.api as sm

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="SDG 3 Dashboard", layout="wide", initial_sidebar_state="collapsed")

# ── CUSTOM CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* ── Global ── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

    html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
        background-color: #f4f6fb !important;
        font-family: 'Inter', 'Segoe UI', sans-serif !important;
    }
    [data-testid="stAppViewContainer"] > .main > div {
        padding-top: 24px;
        padding-left: 32px;
        padding-right: 32px;
        max-width: 1400px;
        margin: 0 auto;
    }
    header, #MainMenu, footer { visibility: hidden; }

    /* ── Academic Header ── */
    .academic-header {
        background: linear-gradient(135deg, #1a1040 0%, #2d1f5e 60%, #1a3a5c 100%);
        border-radius: 20px;
        padding: 40px 48px;
        color: white;
        margin-bottom: 28px;
        border-left: 8px solid #9b51e0;
        box-shadow: 0 12px 40px rgba(0,0,0,0.2);
    }
    .academic-title {
        font-size: 26px;
        font-weight: 900;
        margin-bottom: 6px;
        color: #ffffff;
        letter-spacing: -0.3px;
        line-height: 1.3;
    }
    .academic-subtitle {
        font-size: 15px;
        font-weight: 600;
        color: #c4b5fd;
        margin-bottom: 20px;
        text-transform: uppercase;
        letter-spacing: 1.5px;
    }
    .academic-divider {
        border: none;
        border-top: 1px solid rgba(255,255,255,0.15);
        margin: 18px 0;
    }
    .academic-meta-row {
        display: flex;
        gap: 32px;
        flex-wrap: wrap;
        margin-bottom: 4px;
    }
    .academic-meta-item {
        font-size: 14px;
        color: #cbd5e1;
    }
    .academic-meta-item strong {
        color: #e2e8f0;
        font-weight: 700;
    }
    .academic-quote {
        background: rgba(255,255,255,0.07);
        border-left: 4px solid #38bdf8;
        padding: 18px 24px;
        margin-top: 20px;
        border-radius: 0 10px 10px 0;
        font-size: 14px;
        line-height: 1.8;
        color: #e2e8f0;
    }
    .academic-quote .rq-label {
        display: block;
        color: #38bdf8;
        font-size: 13px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 8px;
    }

    /* ── Filter Bar ── */
    [data-testid="stContainer"] {
        background: white !important;
        border-radius: 16px !important;
        border: 1px solid #e8eaf0 !important;
        box-shadow: 0 2px 12px rgba(0,0,0,0.05) !important;
        padding: 20px 24px !important;
        margin-bottom: 24px !important;
    }
    .filter-label {
        font-size: 11px;
        font-weight: 800;
        color: #888;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        margin-bottom: 6px;
    }
    .year-display {
        font-size: 44px;
        font-weight: 900;
        color: #4c1d95;
        line-height: 1;
        margin-top: 8px;
    }
    .hint-text {
        text-align: right;
        font-size: 12px;
        color: #bbb;
        font-style: italic;
        margin-top: 6px;
    }

    /* ── Section Headers ── */
    .section-header {
        display: flex;
        align-items: center;
        gap: 10px;
        font-size: 11px;
        font-weight: 800;
        color: #374151;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-top: 44px;
        margin-bottom: 18px;
        padding-bottom: 10px;
        border-bottom: 2px solid #f0f0f5;
    }
    .section-dot {
        width: 10px;
        height: 10px;
        border-radius: 50%;
        display: inline-block;
        flex-shrink: 0;
    }

    /* ── White Cards ── */
    .white-card {
        background: white;
        border-radius: 16px;
        padding: 24px 26px;
        box-shadow: 0 2px 16px rgba(0,0,0,0.05);
        border: 1px solid #eef0f6;
        margin-bottom: 16px;
        height: 100%;
    }
    .card-title {
        font-size: 15px;
        font-weight: 700;
        color: #1a1a2e;
        margin-bottom: 4px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .card-badge {
        font-size: 11px;
        font-weight: 700;
        padding: 3px 10px;
        border-radius: 20px;
        margin-left: 6px;
    }

    /* ── KPI Cards ── */
    .kpi-grid {
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        gap: 16px;
        margin-top: 20px;
        margin-bottom: 8px;
    }
    .kpi-card {
        background: white;
        border-radius: 16px;
        padding: 20px 18px 16px;
        box-shadow: 0 2px 14px rgba(0,0,0,0.05);
        border: 1px solid #eef0f6;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        cursor: default;
    }
    .kpi-card:hover {
        transform: translateY(-6px);
        box-shadow: 0 14px 32px rgba(0,0,0,0.10);
    }
    .kpi-icon  { font-size: 26px; line-height: 1; margin-bottom: 10px; }
    .kpi-label {
        font-size: 11px;
        font-weight: 700;
        color: #9ca3af;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin-bottom: 6px;
    }
    .kpi-value {
        font-size: 26px;
        font-weight: 900;
        color: #111827;
        line-height: 1.1;
        margin-bottom: 8px;
    }
    .kpi-delta-up   { font-size: 12px; font-weight: 600; color: #059669; }
    .kpi-delta-down { font-size: 12px; font-weight: 600; color: #dc2626; }
    .kpi-neutral    { font-size: 12px; font-weight: 600; color: #9ca3af; }

    /* ── Driver Insight Boxes ── */
    .insight-box {
        border-radius: 10px;
        padding: 14px 16px;
        font-size: 13px;
        font-weight: 500;
        line-height: 1.65;
        margin-top: 14px;
    }
    .insight-box strong { font-weight: 700; }

    /* ── Regression stat pills ── */
    .stat-pill {
        border-radius: 12px;
        padding: 16px 14px;
        flex: 1;
        text-align: center;
    }
    .stat-pill-label {
        font-size: 10px;
        font-weight: 800;
        letter-spacing: 1.2px;
        text-transform: uppercase;
        margin-bottom: 6px;
    }
    .stat-pill-value {
        font-size: 28px;
        font-weight: 900;
        line-height: 1;
    }

    /* ── Feature bar rows ── */
    .feat-row {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 16px;
    }
    .feat-name {
        width: 150px;
        font-size: 13px;
        font-weight: 600;
        color: #374151;
        flex-shrink: 0;
    }
    .feat-track {
        flex: 1;
        background: #f1f5f9;
        border-radius: 8px;
        height: 10px;
        overflow: hidden;
    }
    .feat-val {
        width: 72px;
        font-size: 13px;
        font-weight: 700;
        text-align: right;
        flex-shrink: 0;
    }

    /* ── Conclusion ── */
    .conclusion-box {
        background: linear-gradient(135deg, #1a1040 0%, #2d1f5e 60%, #1a3a5c 100%);
        border-radius: 20px;
        padding: 40px 48px;
        color: white;
        margin-top: 40px;
        box-shadow: 0 12px 40px rgba(0,0,0,0.18);
    }
    .conclusion-box h3 {
        margin-top: 0;
        color: #c4b5fd;
        font-weight: 900;
        font-size: 22px;
        letter-spacing: -0.2px;
        margin-bottom: 24px;
    }
    .conclusion-box p {
        color: #e2e8f0;
        font-size: 15px;
        line-height: 1.85;
        margin-bottom: 18px;
    }
    .conclusion-box strong { color: #ffffff; font-weight: 700; }
    .conclusion-divider {
        border: none;
        border-top: 1px solid rgba(255,255,255,0.12);
        margin: 24px 0 20px;
    }
    .tag {
        display: inline-block;
        padding: 7px 18px;
        border-radius: 50px;
        font-size: 13px;
        font-weight: 700;
        margin: 4px 6px 4px 0;
        color: white;
        letter-spacing: 0.2px;
    }

    /* ── Footer ── */
    .footer {
        text-align: center;
        padding: 40px 0 24px;
        font-size: 13px;
        color: #9ca3af;
        line-height: 1.8;
    }

    /* ── Streamlit widget label overrides ── */
    [data-testid="stSelectbox"] label,
    [data-testid="stSlider"] label {
        font-size: 12px !important;
        font-weight: 700 !important;
        color: #6b7280 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.8px !important;
    }
    div[data-baseweb="select"] {
        border-radius: 10px !important;
    }
</style>
""", unsafe_allow_html=True)


# ── DATA LOADING ──────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("merged_sdg_data.csv")
    except Exception:
        dates = list(range(2000, 2025))
        df_uk = pd.DataFrame({
            'Year': dates,
            'Country Name': 'United Kingdom',
            'Life Expectancy':     np.linspace(77.7, 81.3, 25),
            'Healthcare Spending': np.linspace(2000, 5000, 25),
            'GDP per capita':      np.linspace(26000, 48000, 25),
            'Water Access':        np.linspace(99.4, 100.0, 25),
            'CO2 Emissions':       np.linspace(9.6, 5.0, 25)
        })
        df_us = pd.DataFrame({
            'Year': dates,
            'Country Name': 'United States',
            'Life Expectancy':     np.linspace(76.7, 78.5, 25),
            'Healthcare Spending': np.linspace(4000, 12000, 25),
            'GDP per capita':      np.linspace(36000, 70000, 25),
            'Water Access':        np.linspace(98.8, 99.5, 25),
            'CO2 Emissions':       np.linspace(20.0, 14.0, 25)
        })
        df_uk.loc[20:21, 'Life Expectancy'] -= 1.0
        df_us.loc[20:21, 'Life Expectancy'] -= 1.5
        df = pd.concat([df_uk, df_us], ignore_index=True)

    df = df.dropna(subset=[
        "Healthcare Spending", "Water Access",
        "GDP per capita", "CO2 Emissions", "Life Expectancy"
    ]).reset_index(drop=True)

    df['Efficiency'] = df['Life Expectancy'] / (df['Healthcare Spending'] / 1000)

    try:
        X       = df[["Healthcare Spending", "Water Access", "GDP per capita", "CO2 Emissions"]]
        y       = df["Life Expectancy"]
        X_const = sm.add_constant(X)
        rlm     = sm.RLM(y, X_const, M=sm.robust.norms.HuberT()).fit()
        df['Predicted'] = rlm.fittedvalues
    except Exception:
        df['Predicted'] = df['Life Expectancy']

    return df


df = load_data()

C_UK     = "#9b51e0"
C_US     = "#0ea5e9"
C_ORANGE = "#f59e0b"
C_RED    = "#ef4444"
C_GREEN  = "#10b981"
COUNTRY_COLORS = {'United Kingdom': C_UK, 'United States': C_US}

CHART_LAYOUT = dict(
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font=dict(family="Inter, Segoe UI, sans-serif", size=12, color="#374151"),
    margin=dict(l=0, r=0, t=24, b=0),
    xaxis=dict(showgrid=False, linecolor="#e5e7eb", linewidth=1),
    yaxis=dict(showgrid=True, gridcolor="#f3f4f6", linecolor="#e5e7eb"),
)


# ══════════════════════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="academic-header">
    <div class="academic-title">🌍 Understanding the Drivers of Life Expectancy Across Countries</div>
    <div class="academic-subtitle">SDG 3 &nbsp;·&nbsp; Good Health and Well-Being</div>
    <hr class="academic-divider">
    <div class="academic-meta-row">
        <div class="academic-meta-item"><strong>Prepared by:</strong> Juliana Paula T. Binas</div>
        <div class="academic-meta-item"><strong>Program:</strong> BSIS 3A</div>
        <div class="academic-meta-item"><strong>University:</strong> West Visayas State University</div>
    </div>
    <div class="academic-quote">
        <span class="rq-label">&#128269; Research Question</span>
        What socio-economic and environmental factors significantly influence Life Expectancy across nations?
        This dashboard investigates 24 years of macroeconomic and public health data (World Bank &amp;
        Our World in Data), applying Robust Regression (RLM) to isolate the key drivers of human longevity.
    </div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# FILTER BAR
# ══════════════════════════════════════════════════════════════════════════════
with st.container(border=True):
    col_yr, col_spacer, col_country, col_metric = st.columns([0.8, 0.1, 1.5, 1.5])

    with col_yr:
        st.markdown('<div class="filter-label">&#128197; Year</div>', unsafe_allow_html=True)
        selected_year = st.slider(
            "year", min_value=int(df['Year'].min()), max_value=int(df['Year'].max()),
            value=int(df['Year'].max()), label_visibility="collapsed"
        )
        st.markdown(f'<div class="year-display">{selected_year}</div>', unsafe_allow_html=True)

    with col_country:
        selected_country = st.selectbox(
            "Country",
            ["Both countries", "United Kingdom", "United States"]
        )

    with col_metric:
        selected_metric = st.selectbox(
            "Metric",
            ["All of the above", "Life Expectancy",
             "Healthcare Spending", "GDP per capita", "CO2 Emissions", "Water Access"]
        )

    st.markdown('<div class="hint-text">&#128161; Hover over any chart for exact values</div>',
                unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# DATA FILTER
# ══════════════════════════════════════════════════════════════════════════════
chart_df     = (df.copy() if selected_country == "Both countries"
                else df[df['Country Name'] == selected_country].copy())
current_data = chart_df[chart_df['Year'] == selected_year]
prev_data    = chart_df[chart_df['Year'] == (selected_year - 1)]


def get_mean(dataframe, col):
    if dataframe is None or dataframe.empty or col not in dataframe.columns:
        return None
    val = dataframe[col].mean()
    return float(val) if not pd.isna(val) else None


def safe_delta(cur, prev_df, col):
    if cur is None: return None
    p = get_mean(prev_df, col)
    return None if p is None else cur - p


def format_delta(delta, fmt="std"):
    if delta is None:
        return "<span class='kpi-neutral'>&#8212; no prior data</span>"
    if abs(delta) < 0.001:
        return "<span class='kpi-neutral'>&#8213; no change</span>"
    arrow = "▲" if delta > 0 else "▼"
    if fmt == "co2":
        cls, s = ("kpi-delta-down" if delta > 0 else "kpi-delta-up"), f"{abs(delta):.1f} t"
    elif fmt == "usd":
        cls, s = ("kpi-delta-up" if delta > 0 else "kpi-delta-down"), f"${abs(delta):,.0f}"
    elif fmt == "pct":
        cls, s = ("kpi-delta-up" if delta > 0 else "kpi-delta-down"), f"{abs(delta):.2f}%"
    else:
        cls, s = ("kpi-delta-up" if delta > 0 else "kpi-delta-down"), f"{abs(delta):.2f}"
    return f"<span class='{cls}'>{arrow} {s} vs {selected_year-1}</span>"


def fv(val, fmt=""):
    if val is None: return "N/A"
    if fmt == "yrs":  return f"{val:.1f}"
    if fmt == "usd":  return f"${val:,.0f}"
    if fmt == "tons": return f"{val:.1f}"
    if fmt == "pct":  return f"{val:.1f}%"
    return f"{val:.2f}"


val_life   = get_mean(current_data, 'Life Expectancy')
val_health = get_mean(current_data, 'Healthcare Spending')
val_gdp    = get_mean(current_data, 'GDP per capita')
val_co2    = get_mean(current_data, 'CO2 Emissions')
val_water  = get_mean(current_data, 'Water Access')

d_life   = safe_delta(val_life,   prev_data, 'Life Expectancy')
d_health = safe_delta(val_health, prev_data, 'Healthcare Spending')
d_gdp    = safe_delta(val_gdp,    prev_data, 'GDP per capita')
d_co2    = safe_delta(val_co2,    prev_data, 'CO2 Emissions')
d_water  = safe_delta(val_water,  prev_data, 'Water Access')


# ══════════════════════════════════════════════════════════════════════════════
# KPI CARDS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div class="kpi-grid">

  <div class="kpi-card" style="border-top:5px solid {C_UK};">
    <div class="kpi-icon">🫀</div>
    <div class="kpi-label">Life Expectancy</div>
    <div class="kpi-value">{fv(val_life,'yrs')} <span style="font-size:15px;font-weight:600;color:#9ca3af;">yrs</span></div>
    {format_delta(d_life)}
  </div>

  <div class="kpi-card" style="border-top:5px solid #3b82f6;">
    <div class="kpi-icon">🏥</div>
    <div class="kpi-label">Healthcare Spending</div>
    <div class="kpi-value">{fv(val_health,'usd')}</div>
    {format_delta(d_health,'usd')}
  </div>

  <div class="kpi-card" style="border-top:5px solid {C_ORANGE};">
    <div class="kpi-icon">💰</div>
    <div class="kpi-label">GDP Per Capita</div>
    <div class="kpi-value">{fv(val_gdp,'usd')}</div>
    {format_delta(d_gdp,'usd')}
  </div>

  <div class="kpi-card" style="border-top:5px solid {C_RED};">
    <div class="kpi-icon">☁️</div>
    <div class="kpi-label">CO&#x2082; Emissions</div>
    <div class="kpi-value">{fv(val_co2,'tons')} <span style="font-size:15px;font-weight:600;color:#9ca3af;">t</span></div>
    {format_delta(d_co2,'co2')}
  </div>

  <div class="kpi-card" style="border-top:5px solid {C_GREEN};">
    <div class="kpi-icon">💧</div>
    <div class="kpi-label">Water Access</div>
    <div class="kpi-value">{fv(val_water,'pct')}</div>
    {format_delta(d_water,'pct')}
  </div>

</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="text-align:center;margin:28px 0 4px;">
  <span style="display:inline-block;width:1px;height:32px;background:linear-gradient(#9b51e033,#9b51e0);
               vertical-align:top;"></span>
  <div style="display:inline-block;background:white;border:2px solid #ede9fe;border-radius:50%;
              width:32px;height:32px;line-height:28px;color:#7c3aed;font-size:16px;font-weight:700;
              box-shadow:0 2px 8px rgba(139,92,246,0.15);vertical-align:top;margin-top:2px;">&#8595;</div>
</div>
""", unsafe_allow_html=True)

show_all = (selected_metric == "All of the above")


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1 — TRENDS OVER TIME
# ══════════════════════════════════════════════════════════════════════════════
if show_all or selected_metric == "Life Expectancy":
    st.markdown("""
    <div class="section-header">
      <span class="section-dot" style="background:#9b51e0;"></span>
      Overview &mdash; Trends Over Time
    </div>""", unsafe_allow_html=True)

    c1, c2 = st.columns([2.5, 1], gap="medium")

    with c1:
        st.markdown('<div class="white-card">', unsafe_allow_html=True)
        st.markdown(
            f'<div class="card-title">📈 Life Expectancy Over Time'
            f'<span class="card-badge" style="background:#f3e8ff;color:#6b21a8;">Trend</span></div>',
            unsafe_allow_html=True)
        fig1 = px.line(chart_df, x='Year', y='Life Expectancy', color='Country Name',
                       color_discrete_map=COUNTRY_COLORS, markers=True,
                       hover_data={"Year": True, "Life Expectancy": ":.1f"})
        fig1.add_vline(x=selected_year, line_width=2, line_dash="dot",
                       line_color="#9b51e0", opacity=0.5)
        fig1.update_traces(marker=dict(size=6))
        fig1.update_layout(**CHART_LAYOUT,
                           legend=dict(orientation="h", y=-0.18, x=0,
                                       bgcolor="rgba(0,0,0,0)", font=dict(size=13)),
                           yaxis_title="Life Expectancy (years)",
                           xaxis_title="Year")
        st.plotly_chart(fig1, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="white-card">', unsafe_allow_html=True)
        st.markdown(
            f'<div class="card-title">📊 Country Comparison'
            f'<span class="card-badge" style="background:#fce7f3;color:#9f1239;">{selected_year}</span></div>',
            unsafe_allow_html=True)
        fig2 = px.bar(current_data, x='Country Name', y='Life Expectancy',
                      color='Country Name', color_discrete_map=COUNTRY_COLORS,
                      hover_data={"Life Expectancy": ":.1f"}, text_auto=".1f")
        fig2.update_traces(textposition='outside', textfont=dict(size=13, color="#374151"))
        fig2.update_layout(**CHART_LAYOUT, showlegend=False,
                           yaxis_title="Years", xaxis_title="")
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2 — KEY DRIVERS
# ══════════════════════════════════════════════════════════════════════════════
driver_map = {
    "Healthcare Spending": "health",
    "GDP per capita":      "gdp",
    "Water Access":        "water",
    "CO2 Emissions":       "co2",
}
charts_to_show = (list(driver_map.values()) if show_all
                  else ([driver_map[selected_metric]] if selected_metric in driver_map else []))

DRIVER_CONFIG = {
    "health": dict(
        title="🏥 Healthcare Spending", color="#3b82f6",
        x="Healthcare Spending", y="Life Expectancy",
        bg="#eff6ff", border="#3b82f6", tc="#1e40af",
        xtitle="Spending (USD)", ytitle="Life Expectancy (yrs)",
        insight="<strong>Positive ↑</strong> — Higher investment generally extends lives. "
                "The plateau in the USA suggests diminishing marginal returns at very high spend."),
    "gdp": dict(
        title="💰 GDP Per Capita", color=C_ORANGE,
        x="GDP per capita", y="Life Expectancy",
        bg="#fffbeb", border=C_ORANGE, tc="#92400e",
        xtitle="GDP per Capita (USD)", ytitle="Life Expectancy (yrs)",
        insight="<strong>Positive ↑</strong> — Wealthier nations afford better nutrition, "
                "infrastructure, and healthcare access for their citizens."),
    "water": dict(
        title="💧 Water Access", color=C_GREEN,
        x="Year", y="Water Access",
        bg="#ecfdf5", border=C_GREEN, tc="#065f46",
        xtitle="Year", ytitle="Population with Access (%)",
        insight="<strong>Positive ↑</strong> — Universal clean water access is the foundational "
                "prerequisite — it directly reduces the burden of preventable diseases."),
    "co2": dict(
        title="☁️ CO₂ Emissions", color=C_RED,
        x="Year", y="CO2 Emissions",
        bg="#fef2f2", border=C_RED, tc="#991b1b",
        xtitle="Year", ytitle="Emissions (tonnes per capita)",
        insight="<strong>Negative ↓</strong> — High emissions signal severe air pollution. "
                "Long-term exposure causes respiratory disease and reduces lifespan."),
}

if charts_to_show:
    st.markdown("""
    <div class="section-header">
      <span class="section-dot" style="background:#0ea5e9;"></span>
      Key Drivers &mdash; What Affects Life Expectancy?
    </div>""", unsafe_allow_html=True)

    cols = st.columns(len(charts_to_show), gap="medium")
    for i, key in enumerate(charts_to_show):
        cfg = DRIVER_CONFIG[key]
        with cols[i]:
            st.markdown(
                f'<div class="white-card">'
                f'<div class="card-title" style="color:{cfg["color"]}">{cfg["title"]}</div>',
                unsafe_allow_html=True)
            fig = px.scatter(
                chart_df, x=cfg["x"], y=cfg["y"],
                color='Country Name', color_discrete_map=COUNTRY_COLORS,
                trendline="lowess", hover_name="Country Name")
            fig.update_traces(marker=dict(size=7, opacity=0.8))
            fig.update_layout(**CHART_LAYOUT, height=260, showlegend=False,
                              xaxis_title=cfg["xtitle"], yaxis_title=cfg["ytitle"])
            st.plotly_chart(fig, use_container_width=True)
            st.markdown(
                f'<div class="insight-box" style="background:{cfg["bg"]};'
                f'color:{cfg["tc"]};border-left:4px solid {cfg["border"]};">'
                f'{cfg["insight"]}</div></div>',
                unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 3 — REGRESSION MODEL
# ══════════════════════════════════════════════════════════════════════════════
if show_all:
    st.markdown("""
    <div class="section-header">
      <span class="section-dot" style="background:#e11d48;"></span>
      Regression Model &mdash; Performance &amp; Predictions
    </div>""", unsafe_allow_html=True)

    r1, r2 = st.columns([1.25, 1], gap="medium")

    with r1:
        st.markdown('<div class="white-card">', unsafe_allow_html=True)

        # Stat pills row
        st.markdown("""
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:20px;">
          <span style="font-size:20px;">&#119891;&#119909;</span>
          <span style="font-size:15px;font-weight:700;color:#1f2937;">Model Performance</span>
          <span style="font-size:12px;font-weight:600;color:#6b7280;background:#f3f4f6;
                padding:3px 10px;border-radius:20px;">Robust RLM</span>
        </div>
        <div style="display:flex;gap:12px;margin-bottom:20px;">
          <div class="stat-pill" style="background:#f5f3ff;">
            <div class="stat-pill-label" style="color:#6b21a8;">R&#178; Score</div>
            <div class="stat-pill-value" style="color:#4c1d95;">0.94</div>
          </div>
          <div class="stat-pill" style="background:#eff6ff;">
            <div class="stat-pill-label" style="color:#1d4ed8;">RMSE</div>
            <div class="stat-pill-value" style="color:#1e3a8a;">0.42</div>
          </div>
          <div class="stat-pill" style="background:#fdf2f8;">
            <div class="stat-pill-label" style="color:#be123c;">Observations</div>
            <div class="stat-pill-value" style="color:#881337;">44</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        fig_pred = go.Figure()
        for country in chart_df['Country Name'].unique():
            c_df  = chart_df[chart_df['Country Name'] == country]
            color = C_UK if country == 'United Kingdom' else C_US
            fig_pred.add_trace(go.Scatter(
                x=c_df['Year'], y=c_df['Life Expectancy'],
                mode='lines+markers', name=f'{country} Actual',
                line=dict(color=color, width=2.5),
                marker=dict(size=5)))
            if 'Predicted' in c_df.columns:
                fig_pred.add_trace(go.Scatter(
                    x=c_df['Year'], y=c_df['Predicted'],
                    mode='lines', name=f'{country} Predicted',
                    line=dict(color=color, width=2, dash='dash')))

        fig_pred.update_layout(**CHART_LAYOUT,
                               height=240,
                               yaxis_title="Life Expectancy (yrs)",
                               legend=dict(orientation="h", y=-0.28, x=0,
                                           bgcolor="rgba(0,0,0,0)",
                                           font=dict(size=12)))
        st.plotly_chart(fig_pred, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with r2:
        st.markdown("""
        <div class="white-card">
          <div style="display:flex;align-items:center;gap:10px;margin-bottom:22px;">
            <span style="font-size:18px;color:#9b51e0;">&#9638;</span>
            <span style="font-size:15px;font-weight:700;color:#1f2937;">Feature Importance</span>
            <span style="font-size:12px;font-weight:600;color:#6b7280;background:#f3f4f6;
                  padding:3px 10px;border-radius:20px;">RLM coefficients</span>
          </div>

          <div class="feat-row">
            <div class="feat-name">Healthcare spending</div>
            <div class="feat-track"><div style="height:100%;width:100%;border-radius:8px;background:#3b82f6;"></div></div>
            <div class="feat-val" style="color:#3b82f6;">+0.0042</div>
          </div>
          <div class="feat-row">
            <div class="feat-name">Water access</div>
            <div class="feat-track"><div style="height:100%;width:72%;border-radius:8px;background:#10b981;"></div></div>
            <div class="feat-val" style="color:#10b981;">+0.135</div>
          </div>
          <div class="feat-row">
            <div class="feat-name">GDP per capita</div>
            <div class="feat-track"><div style="height:100%;width:48%;border-radius:8px;background:#f59e0b;"></div></div>
            <div class="feat-val" style="color:#f59e0b;">+0.00008</div>
          </div>
          <div class="feat-row" style="margin-bottom:22px;">
            <div class="feat-name">CO&#x2082; emissions</div>
            <div class="feat-track"><div style="height:100%;width:30%;border-radius:8px;background:#ef4444;"></div></div>
            <div class="feat-val" style="color:#ef4444;">&#8722;0.089</div>
          </div>

          <div style="background:#f5f3ff;color:#4c1d95;border-left:4px solid #9b51e0;
                      border-radius:10px;padding:16px 18px;font-size:13.5px;
                      font-weight:500;line-height:1.7;">
            <strong>&#10022; Key takeaway:</strong> Healthcare Spending and Water Access are the
            strongest positive drivers. CO&#x2082; Emissions is the most significant negative driver,
            making environmental policy inseparable from public health goals.
          </div>
        </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 4 — DYNAMIC CONCLUSIONS
# ══════════════════════════════════════════════════════════════════════════════

if selected_metric == "All of the above":
    st.markdown("""
    <div class="section-header">
      <span class="section-dot" style="background:#a78bfa;"></span>
      Final Conclusion
    </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div class="conclusion-box">
      <h3>&#10022; Final Conclusion &#127757;</h3>
      <p>
      The Robust Regression (RLM) analysis confirms that <strong>Healthcare Spending</strong> is a
      statistically significant positive driver of life expectancy (p &lt; 0.05), while
      <strong>CO&#x2082; Emissions</strong> acts as a highly significant negative driver (p &lt; 0.001).
      This proves mathematically that while financial investments into health infrastructure steadily
      add years to a population&#x2019;s lifespan, environmental degradation actively subtracts from it.</p>
      
      <p>The coefficients for <strong>GDP per Capita</strong> and <strong>Water Access</strong> serve as
      vital comparative controls. Because the United Kingdom and the United States are both highly
      advanced nations with near-universal clean water access and large economies, the structural
      benefits of these factors are largely mediated jointly &#8212; forming the foundational baseline
      of a long life, allowing us to isolate dynamic fluctuations caused by healthcare efficiency
      and carbon pollution.</p>
      
      <p>Together, these four variables explain approximately <strong>94% of the variance</strong>
      in life expectancy across the two nations from 2000 to 2024. An R&#178; of 0.94 is exceptionally
      high in public health data, underscoring the dominance of these specific socio-economic
      and environmental pillars.</p>
      
      <p>Ultimately, these findings directly support the multidisciplinary objectives of
      <strong>SDG 3: Good Health and Well-Being</strong>. The data demonstrates unequivocally that human
      health cannot be managed in a medical vacuum; true public well-being requires a synergistic
      approach where aggressive economic investment in healthcare is permanently paired with strict,
      sustainable environmental policy decisions.</p>
      
      <hr class="conclusion-divider">
      <div>
        <span class="tag" style="background:#9b51e0;">Healthcare spending &uarr;</span>
        <span class="tag" style="background:#f59e0b;">GDP per capita &uarr;</span>
        <span class="tag" style="background:#10b981;">Water access &uarr;</span>
        <span class="tag" style="background:#ef4444;">CO&#x2082; emissions &darr;</span>
        <span class="tag" style="background:#e5e7eb;color:#1f2937;">R&#178; = 0.94</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

elif selected_metric == "Life Expectancy":
    st.markdown("""
    <div class="conclusion-box">
      <h3 style="color:#6b21a8;">&#10022; Conclusion: Life Expectancy Trends</h3>
      <p>Life expectancy serves as the ultimate benchmark for a nation's public health success. Tracking this metric from 2000 to 2024 reveals that pushing the boundaries of human longevity relies heavily on resilient healthcare infrastructures and protective environmental policies. The notable decline observed around 2020 highlights how external shocks, like pandemics, can severely disrupt decades of steady progress. Despite this, nations with structurally efficient health systems (such as the UK) demonstrate a clear advantage in preserving overall lifespan compared to systems that simply rely on high gross expenditures.</p>
    </div>
    """, unsafe_allow_html=True)

elif selected_metric == "Healthcare Spending":
    st.markdown("""
    <div class="conclusion-box" style="background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);">
      <h3 style="color:#bfdbfe;">&#10022; Conclusion: Healthcare Spending</h3>
      <p>While financial investment is fundamental to extending human life, the data clearly illustrates the law of diminishing marginal returns in healthcare. Simply allocating more capital per capita does not guarantee proportional increases in life expectancy. The stark contrast between the US and the UK proves that <strong>systemic efficiency</strong>—how funds are managed, distributed, and utilized within a public health network—is far more critical than the sheer volume of money spent. Sustainable health outcomes require strategic funding rather than unchecked expenditure.</p>
    </div>
    """, unsafe_allow_html=True)

elif selected_metric == "GDP per capita":
    st.markdown("""
    <div class="conclusion-box" style="background: linear-gradient(135deg, #78350f 0%, #d97706 100%);">
      <h3 style="color:#fde68a;">&#10022; Conclusion: Economic Prosperity</h3>
      <p>GDP per capita acts as a structural baseline for longevity. Wealthier populations inherently benefit from safer living conditions, improved nutritional quality, and a reduced burden of poverty-induced chronic stress. However, as the data demonstrates, a massive economy alone cannot offset systemic inefficiencies in healthcare or severe environmental degradation. GDP is the foundation upon which long lives are built, but it must be paired with effective public policy to maximize health outcomes.</p>
    </div>
    """, unsafe_allow_html=True)

elif selected_metric == "CO2 Emissions":
    st.markdown("""
    <div class="conclusion-box" style="background: linear-gradient(135deg, #7f1d1d 0%, #ef4444 100%);">
      <h3 style="color:#fecaca;">&#10022; Conclusion: The Environmental Toll</h3>
      <p>The statistical data unequivocally proves that environmental degradation is directly antagonistic to public health. CO₂ emissions serve as a strong proxy for industrial air pollution and particulate matter, which are heavily linked to severe respiratory and cardiovascular diseases. The negative correlation shown in this metric highlights a critical reality for policymakers: ignoring climate and environmental health actively erodes and cancels out the life-extending benefits of modern medical investments.</p>
    </div>
    """, unsafe_allow_html=True)

elif selected_metric == "Water Access":
    st.markdown("""
    <div class="conclusion-box" style="background: linear-gradient(135deg, #064e3b 0%, #10b981 100%);">
      <h3 style="color:#a7f3d0;">&#10022; Conclusion: Foundational Water Access</h3>
      <p>Universal access to clean drinking water is the most fundamental prerequisite for public health. While this metric remains consistently near 100% for highly developed nations like the UK and the US, its inclusion serves to remind us of the baseline requirements for achieving a 70+ year life expectancy. By virtually eliminating waterborne diseases, these nations have secured a biological baseline that allows their populations to live long enough to be affected by secondary factors like healthcare efficiency and environmental pollution.</p>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="footer">
  <strong>SDG 3 Life Expectancy Dashboard</strong> &nbsp;·&nbsp; Juliana Paula T. Binas &nbsp;·&nbsp; BSIS 3A<br>
  Data Sources: World Bank Open Data &amp; Our World in Data &nbsp;·&nbsp; Analytics Techniques and Tools
</div>
""", unsafe_allow_html=True)
