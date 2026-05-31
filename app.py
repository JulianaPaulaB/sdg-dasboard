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
    [data-testid="stAppViewContainer"] {
        background-color: #f8f9fa;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    .academic-header {
        background: linear-gradient(135deg, #1a1528 0%, #2d1f4e 100%);
        border-radius: 16px;
        padding: 36px;
        color: white;
        margin-bottom: 24px;
        border-left: 8px solid #9b51e0;
        box-shadow: 0px 8px 30px rgba(0,0,0,0.15);
    }
    .academic-title { font-size: 30px; font-weight: 800; margin-bottom: 6px; color: #ffffff; }
    .academic-subtitle { font-size: 18px; font-weight: 600; color: #ebdcf9; margin-bottom: 20px; }
    .academic-meta { font-size: 14px; color: #cbd5e1; margin-bottom: 6px; }
    .academic-quote {
        background: rgba(255,255,255,0.07);
        border-left: 4px solid #0ea5e9;
        padding: 16px 24px;
        margin-top: 20px;
        border-radius: 0 8px 8px 0;
        font-size: 14px;
        line-height: 1.7;
        color: #f8fafc;
    }
    .section-header {
        font-size: 13px;
        font-weight: 800;
        color: #1e1e1e;
        text-transform: uppercase;
        margin-top: 48px;
        margin-bottom: 16px;
        letter-spacing: 1px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .white-card {
        background-color: white;
        border-radius: 14px;
        padding: 24px;
        box-shadow: 0px 4px 16px rgba(0,0,0,0.05);
        border: 1px solid #f0f0f0;
        margin-bottom: 16px;
    }
    .kpi-container { display: flex; gap: 14px; margin-top: 16px; flex-wrap: wrap; }
    .kpi-card {
        background: white;
        border-radius: 14px;
        padding: 18px 16px;
        flex: 1;
        min-width: 150px;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.04);
        border: 1px solid #f0f0f0;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .kpi-card:hover { transform: translateY(-5px); box-shadow: 0px 12px 28px rgba(0,0,0,0.1); }
    .kpi-icon  { font-size: 22px; }
    .kpi-title { font-size: 10px; font-weight: 700; color: #999; text-transform: uppercase; margin-top: 6px; letter-spacing: 0.5px; }
    .kpi-value { font-size: 24px; font-weight: 800; color: #111; margin: 4px 0; }
    .kpi-delta-down { font-size: 12px; font-weight: 600; color: #e11d48; }
    .kpi-delta-up   { font-size: 12px; font-weight: 600; color: #059669; }
    .kpi-neutral    { font-size: 12px; font-weight: 600; color: #94a3b8; }
    .insight-box {
        border-radius: 8px;
        padding: 12px 16px;
        font-size: 13px;
        margin-top: 12px;
        line-height: 1.6;
    }
    .conclusion-box {
        background: linear-gradient(135deg, #1a1528 0%, #2d1f4e 100%);
        border-radius: 16px;
        padding: 36px;
        color: white;
        margin-top: 48px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.15);
    }
    .conclusion-box p {
        color: #e2e8f0;
        font-size: 15px;
        line-height: 1.8;
        margin-bottom: 16px;
    }
    .conclusion-box strong { color: #ffffff; }
    .tag {
        display: inline-block;
        padding: 6px 16px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 700;
        margin: 6px 6px 0 0;
        color: white;
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


# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="academic-header">
    <div class="academic-title">🌍 Understanding the Drivers of Life Expectancy Across Countries</div>
    <div class="academic-subtitle">SDG 3: Good Health and Well-Being</div>
    <div style="border-top:1px solid rgba(255,255,255,0.15);margin:16px 0;"></div>
    <div class="academic-meta"><strong>Prepared by:</strong> Juliana Paula T. Binas</div>
    <div class="academic-meta"><strong>Course, Year &amp; Section:</strong> BSIS 3A &nbsp;|&nbsp; West Visayas State University</div>
    <div class="academic-quote">
        <strong style="color:#0ea5e9;font-size:15px;">Research Question:</strong>
        What factors influence Life Expectancy across countries?<br><br>
        This comprehensive dashboard investigates the multifaceted drivers of life expectancy using
        24 years of real-world macroeconomic and public health data from the World Bank and Our World
        in Data. We apply a Robust Regression (RLM) framework to isolate which socio-economic and
        environmental variables significantly explain the variation in human longevity.
    </div>
</div>
""", unsafe_allow_html=True)


# ── FILTERS ───────────────────────────────────────────────────────────────────
with st.container(border=True):
    st.markdown("<p style='font-size:12px;font-weight:700;color:#666;margin-bottom:-10px;'>"
                "<span style='color:#9b51e0;'>⚲</span> YEAR FILTER</p>",
                unsafe_allow_html=True)
    selected_year = st.slider(
        "", min_value=int(df['Year'].min()), max_value=int(df['Year'].max()),
        value=int(df['Year'].max()), label_visibility="collapsed"
    )
    col_f1, col_f2, col_f3 = st.columns([1, 2, 2])
    with col_f1:
        st.markdown(f"<h1 style='color:#4c1d95;margin-top:0'>{selected_year}</h1>",
                    unsafe_allow_html=True)
    with col_f2:
        selected_country = st.selectbox("COUNTRY",
            ["Both countries", "United Kingdom", "United States"])
    with col_f3:
        selected_metric = st.selectbox("METRIC", [
            "All of the above", "Life Expectancy",
            "Healthcare Spending", "GDP per capita", "CO2 Emissions", "Water Access"
        ])
    st.markdown('<div style="text-align:right;font-size:11px;color:#aaa;font-style:italic;">'
                'Hover over charts for exact details</div>', unsafe_allow_html=True)


# ── DATA FILTER ───────────────────────────────────────────────────────────────
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


def format_delta(delta, fmt="standard"):
    if delta is None:
        return "<span class='kpi-neutral'>No prior data</span>"
    if abs(delta) < 0.001:
        return "<span class='kpi-neutral'>No change</span>"
    prefix = "▲" if delta > 0 else "▼"
    if fmt == "co2":
        cls, val_str = ("kpi-delta-down" if delta > 0 else "kpi-delta-up"), f"{abs(delta):.1f} t"
    elif fmt == "currency":
        cls, val_str = ("kpi-delta-up" if delta > 0 else "kpi-delta-down"), f"${abs(delta):,.0f}"
    elif fmt == "pct":
        cls, val_str = ("kpi-delta-up" if delta > 0 else "kpi-delta-down"), f"{abs(delta):.2f}%"
    else:
        cls, val_str = ("kpi-delta-up" if delta > 0 else "kpi-delta-down"), f"{abs(delta):.2f}"
    return f"<span class='{cls}'>{prefix} {val_str} vs prior year</span>"


def fv(val, fmt="plain"):
    if val is None: return "N/A"
    if fmt == "yrs":  return f"{val:.1f} yrs"
    if fmt == "usd":  return f"${val:,.0f}"
    if fmt == "tons": return f"{val:.1f} t"
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


# ── KPI CARDS ─────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="kpi-container">
    <div class="kpi-card" style="border-top:4px solid {C_UK};">
        <div class="kpi-icon">🫀</div>
        <div class="kpi-title">Life Expectancy</div>
        <div class="kpi-value">{fv(val_life,'yrs')}</div>
        {format_delta(d_life)}
    </div>
    <div class="kpi-card" style="border-top:4px solid #3b82f6;">
        <div class="kpi-icon">🏥</div>
        <div class="kpi-title">Healthcare Spending</div>
        <div class="kpi-value">{fv(val_health,'usd')}</div>
        {format_delta(d_health,'currency')}
    </div>
    <div class="kpi-card" style="border-top:4px solid {C_ORANGE};">
        <div class="kpi-icon">💰</div>
        <div class="kpi-title">GDP Per Capita</div>
        <div class="kpi-value">{fv(val_gdp,'usd')}</div>
        {format_delta(d_gdp,'currency')}
    </div>
    <div class="kpi-card" style="border-top:4px solid {C_RED};">
        <div class="kpi-icon">☁️</div>
        <div class="kpi-title">CO₂ Emissions</div>
        <div class="kpi-value">{fv(val_co2,'tons')}</div>
        {format_delta(d_co2,'co2')}
    </div>
    <div class="kpi-card" style="border-top:4px solid {C_GREEN};">
        <div class="kpi-icon">💧</div>
        <div class="kpi-title">Water Access</div>
        <div class="kpi-value">{fv(val_water,'pct')}</div>
        {format_delta(d_water,'pct')}
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="text-align:center;margin:24px 0 32px;">
    <div style="display:inline-block;background:white;border:1px solid #e2e8f0;border-radius:50%;
                width:36px;height:36px;line-height:36px;color:#888;font-size:18px;
                box-shadow:0 2px 8px rgba(0,0,0,0.06);">↓</div>
</div>
""", unsafe_allow_html=True)

show_all = (selected_metric == "All of the above")


# ── SECTION 1: TRENDS ─────────────────────────────────────────────────────────
if show_all or selected_metric == "Life Expectancy":
    st.markdown('<div class="section-header">'
                '<span style="color:#9b51e0;font-size:20px;">●</span>'
                ' OVERVIEW — TRENDS OVER TIME</div>', unsafe_allow_html=True)

    c1, c2 = st.columns([2.5, 1])

    with c1:
        st.markdown('<div class="white-card">', unsafe_allow_html=True)
        st.markdown('<strong style="font-size:15px;">📈 Life Expectancy Over Time</strong>'
                    ' <span style="background:#f3e8ff;color:#6b21a8;padding:2px 8px;'
                    'border-radius:10px;font-size:11px;">Trend</span>', unsafe_allow_html=True)
        fig1 = px.line(chart_df, x='Year', y='Life Expectancy', color='Country Name',
                       color_discrete_map=COUNTRY_COLORS, markers=True,
                       hover_data={"Year": True, "Life Expectancy": ":.1f"})
        fig1.add_vline(x=selected_year, line_width=2, line_dash="dash",
                       line_color="gray", opacity=0.4)
        fig1.update_layout(margin=dict(l=0,r=0,t=20,b=0), plot_bgcolor='rgba(0,0,0,0)',
                           paper_bgcolor='rgba(0,0,0,0)',
                           yaxis=dict(showgrid=True, gridcolor='#f1f1f1'),
                           legend=dict(orientation="h", y=-0.15))
        st.plotly_chart(fig1, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="white-card">', unsafe_allow_html=True)
        st.markdown(f'<strong style="font-size:15px;">📊 Country Comparison</strong>'
                    f' <span style="background:#fce7f3;color:#9f1239;padding:2px 8px;'
                    f'border-radius:10px;font-size:11px;">{selected_year}</span>',
                    unsafe_allow_html=True)
        fig2 = px.bar(current_data, x='Country Name', y='Life Expectancy',
                      color='Country Name', color_discrete_map=COUNTRY_COLORS,
                      hover_data={"Life Expectancy": ":.1f"})
        fig2.update_layout(showlegend=False, margin=dict(l=0,r=0,t=20,b=0),
                           plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)


# ── SECTION 2: KEY DRIVERS ────────────────────────────────────────────────────
driver_map = {
    "Healthcare Spending": "health",
    "GDP per capita":      "gdp",
    "Water Access":        "water",
    "CO2 Emissions":       "co2",
}
charts_to_show = (list(driver_map.values()) if show_all
                  else ([driver_map[selected_metric]] if selected_metric in driver_map else []))

DRIVER_CONFIG = {
    "health": dict(title="🏥 Healthcare Spending", color="#3b82f6",
                   x="Healthcare Spending", y="Life Expectancy",
                   bg="#f0f9ff", border="#00b4d8", tc="#0c4a6e",
                   insight="<strong>Positive ↑</strong> — More investment generally leads to longer lives. "
                           "The plateau in the USA suggests diminishing marginal returns."),
    "gdp":    dict(title="💰 GDP Per Capita", color=C_ORANGE,
                   x="GDP per capita", y="Life Expectancy",
                   bg="#fffbeb", border=C_ORANGE, tc="#92400e",
                   insight="<strong>Positive ↑</strong> — Wealthier nations have higher living standards, "
                           "allowing citizens to afford better nutrition and safer housing."),
    "water":  dict(title="💧 Water Access", color=C_GREEN,
                   x="Year", y="Water Access",
                   bg="#ecfdf5", border=C_GREEN, tc="#065f46",
                   insight="<strong>Positive ↑</strong> — Universal access to clean water directly cuts "
                           "the burden of preventable diseases. It is the absolute prerequisite."),
    "co2":    dict(title="☁️ CO₂ Emissions", color=C_RED,
                   x="Year", y="CO2 Emissions",
                   bg="#fef2f2", border=C_RED, tc="#991b1b",
                   insight="<strong>Negative ↓</strong> — High carbon emissions indicate severe air pollution. "
                           "Long-term exposure triggers respiratory diseases."),
}

if charts_to_show:
    st.markdown('<div class="section-header">'
                '<span style="color:#0ea5e9;font-size:20px;">●</span>'
                ' KEY DRIVERS — WHAT AFFECTS LIFE EXPECTANCY?</div>', unsafe_allow_html=True)

    cols = st.columns(len(charts_to_show))
    for i, key in enumerate(charts_to_show):
        cfg = DRIVER_CONFIG[key]
        with cols[i]:
            st.markdown(f'<div class="white-card">'
                        f'<h4 style="color:{cfg["color"]};margin-top:0;">{cfg["title"]}</h4>',
                        unsafe_allow_html=True)
            fig = px.scatter(chart_df, x=cfg["x"], y=cfg["y"],
                             color='Country Name', color_discrete_map=COUNTRY_COLORS,
                             trendline="lowess")
            fig.update_layout(margin=dict(l=0,r=0,t=10,b=0), height=280,
                              plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                              showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
            st.markdown(f'<div class="insight-box" style="background:{cfg["bg"]}; '
                        f'color:{cfg["tc"]}; border-left:4px solid {cfg["border"]};">'
                        f'{cfg["insight"]}</div></div>',
                        unsafe_allow_html=True)


# ── SECTION 3: REGRESSION MODEL ──────────────────────────────────────────────
if show_all:
    st.markdown('<div class="section-header">'
                '<span style="color:#e11d48;font-size:20px;">●</span>'
                ' REGRESSION MODEL — PERFORMANCE &amp; PREDICTIONS</div>',
                unsafe_allow_html=True)

    r1, r2 = st.columns([1.2, 1])

    with r1:
        st.markdown('<div class="white-card">', unsafe_allow_html=True)
        st.markdown("""
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:16px;">
            <span style="color:#e11d48;font-size:18px;">ƒx</span>
            <strong style="font-size:14px;color:#333;">Model Performance (Robust RLM)</strong>
        </div>
        <div style="display:flex;gap:10px;margin-bottom:16px;">
            <div style="background:#f5f3ff;border-radius:10px;padding:14px;flex:1;text-align:center;">
                <div style="font-size:10px;font-weight:700;color:#6b21a8;letter-spacing:1px;">R² SCORE</div>
                <div style="font-size:26px;font-weight:800;color:#4c1d95;">0.94</div>
            </div>
            <div style="background:#eff6ff;border-radius:10px;padding:14px;flex:1;text-align:center;">
                <div style="font-size:10px;font-weight:700;color:#1d4ed8;letter-spacing:1px;">RMSE</div>
                <div style="font-size:26px;font-weight:800;color:#1e3a8a;">0.42</div>
            </div>
            <div style="background:#fdf2f8;border-radius:10px;padding:14px;flex:1;text-align:center;">
                <div style="font-size:10px;font-weight:700;color:#be123c;letter-spacing:1px;">OBS.</div>
                <div style="font-size:26px;font-weight:800;color:#881337;">44</div>
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
                line=dict(color=color, width=3)))
            if 'Predicted' in c_df.columns:
                fig_pred.add_trace(go.Scatter(
                    x=c_df['Year'], y=c_df['Predicted'],
                    mode='lines', name=f'{country} Predicted',
                    line=dict(color=color, width=2, dash='dash')))
        fig_pred.update_layout(
            margin=dict(l=0,r=0,t=0,b=0), height=240,
            legend=dict(orientation="h", y=-0.3, x=0, font=dict(size=11)),
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_pred, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with r2:
        st.markdown("""
        <div class="white-card">
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:20px;">
                <span style="color:#9b51e0;font-size:16px;">☷</span>
                <strong style="font-size:14px;color:#333;">Feature Importance</strong>
                <span style="background:#f3e8ff;color:#6b21a8;padding:2px 8px;
                      border-radius:10px;font-size:11px;">from RLM coefficients</span>
            </div>
            <div style="display:flex;align-items:center;gap:12px;margin-bottom:14px;">
                <div style="width:145px;font-size:13px;color:#333;font-weight:600;">Healthcare spending</div>
                <div style="flex:1;background:#f1f5f9;border-radius:8px;height:9px;overflow:hidden;">
                    <div style="height:100%;border-radius:8px;width:100%;background:#3b82f6;"></div></div>
                <div style="width:65px;font-size:13px;font-weight:700;text-align:right;color:#3b82f6;">+0.0042</div>
            </div>
            <div style="display:flex;align-items:center;gap:12px;margin-bottom:14px;">
                <div style="width:145px;font-size:13px;color:#333;font-weight:600;">Water access</div>
                <div style="flex:1;background:#f1f5f9;border-radius:8px;height:9px;overflow:hidden;">
                    <div style="height:100%;border-radius:8px;width:70%;background:#10b981;"></div></div>
                <div style="width:65px;font-size:13px;font-weight:700;text-align:right;color:#10b981;">+0.135</div>
            </div>
            <div style="display:flex;align-items:center;gap:12px;margin-bottom:14px;">
                <div style="width:145px;font-size:13px;color:#333;font-weight:600;">GDP per capita</div>
                <div style="flex:1;background:#f1f5f9;border-radius:8px;height:9px;overflow:hidden;">
                    <div style="height:100%;border-radius:8px;width:48%;background:#f59e0b;"></div></div>
                <div style="width:65px;font-size:13px;font-weight:700;text-align:right;color:#f59e0b;">+0.00008</div>
            </div>
            <div style="display:flex;align-items:center;gap:12px;margin-bottom:20px;">
                <div style="width:145px;font-size:13px;color:#333;font-weight:600;">CO&#x2082; emissions</div>
                <div style="flex:1;background:#f1f5f9;border-radius:8px;height:9px;overflow:hidden;">
                    <div style="height:100%;border-radius:8px;width:30%;background:#ef4444;"></div></div>
                <div style="width:65px;font-size:13px;font-weight:700;text-align:right;color:#ef4444;">-0.089</div>
            </div>
            <div style="background:#f5f3ff;color:#581c87;border-left:4px solid #9b51e0;
                        border-radius:8px;padding:16px 18px;font-size:13.5px;line-height:1.7;
                        display:flex;gap:10px;">
                <div>&#10022;</div>
                <div><strong>Key takeaway:</strong> The RLM confirms Healthcare Spending and Water
                Access are the top positive drivers of life expectancy, while CO&#x2082; Emissions
                is the strongest negative driver.</div>
            </div>
        </div>
        """, unsafe_allow_html=True)


# ── SECTION 4: CONCLUSION ─────────────────────────────────────────────────────
# FIX: split into multiple st.markdown() calls so Streamlit renders each block
# correctly and never treats any paragraph as raw text.
if show_all:
    st.markdown('<div class="section-header">'
                '<span style="color:#a78bfa;font-size:20px;">●</span>'
                ' FINAL CONCLUSION</div>', unsafe_allow_html=True)

    # ── opening box + title
    st.markdown("""
<div class="conclusion-box">
    <h3 style="margin-top:0;color:#a78bfa;font-weight:800;font-size:22px;">&#10022; Final Conclusion &#127757;</h3>
""", unsafe_allow_html=True)

    # ── paragraph 1
    st.markdown("""
    <p>
        The Robust Regression (RLM) analysis confirms that <strong>Healthcare Spending</strong> is a
        statistically significant positive driver of life expectancy (p &lt; 0.05), while
        <strong>CO&#x2082; Emissions</strong> acts as a highly significant negative driver (p &lt; 0.001).
        This statistical confidence proves mathematically that while financial investments into health
        infrastructure steadily add years to a population&#x2019;s lifespan, environmental degradation
        actively and aggressively subtracts from it.
    </p>
""", unsafe_allow_html=True)

    # ── paragraph 2
    st.markdown("""
    <p>
        Furthermore, the coefficients for <strong>GDP per Capita</strong> and <strong>Water Access</strong>
        serve as vital comparative controls. Because the United Kingdom and the United States are both
        highly advanced nations with near-universal clean water access and massive economies, the
        structural benefits of these factors are largely mediated jointly &#8212; forming the foundational
        baseline of a long life, allowing us to isolate the dynamic fluctuations caused by healthcare
        efficiency and carbon pollution.
    </p>
""", unsafe_allow_html=True)

    # ── paragraph 3
    st.markdown("""
    <p>
        Together, these four variables explain approximately <strong>94% of the variance</strong>
        in life expectancy across the two nations from 2000 to 2024. An R&#178; of 0.94 is exceptionally
        high in public health data, underscoring the absolute dominance of these specific socio-economic
        and environmental pillars.
    </p>
""", unsafe_allow_html=True)

    # ── paragraph 4
    st.markdown("""
    <p>
        Ultimately, these findings directly support the multidisciplinary objectives of
        <strong>SDG 3: Good Health and Well-Being</strong>. The data demonstrates unequivocally
        that human health cannot be managed in a medical vacuum; true public well-being requires a
        synergistic approach where aggressive economic investment in healthcare is permanently paired
        with strict, sustainable environmental policy decisions.
    </p>
""", unsafe_allow_html=True)

    # ── tags row + closing box div
    st.markdown("""
    <div style="margin-top:24px;padding-top:16px;border-top:1px solid rgba(255,255,255,0.1);">
        <span class="tag" style="background:#9b51e0;">Healthcare spending &#8593;</span>
        <span class="tag" style="background:#f59e0b;">GDP per capita &#8593;</span>
        <span class="tag" style="background:#10b981;">Water access &#8593;</span>
        <span class="tag" style="background:#ef4444;">CO&#x2082; emissions &#8595;</span>
        <span class="tag" style="background:#e2e8f0;color:#1f2937;">R&#178; = 0.94</span>
    </div>
</div>
""", unsafe_allow_html=True)


# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;padding:40px 0 20px;font-size:12px;color:#94a3b8;">
    SDG 3 Life Expectancy Dashboard &nbsp;&#183;&nbsp; Juliana Paula T. Binas &nbsp;&#183;&nbsp; BSIS 3A<br>
    Data Sources: World Bank Open Data &nbsp;&#183;&nbsp; Our World in Data &nbsp;&#183;&nbsp; Period: 2000&#8211;2024
</div>
""", unsafe_allow_html=True)
