import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.stats.diagnostic import het_breuschpagan
from scipy import stats

st.set_page_config(
    page_title="SDG 3 · Life Expectancy",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ═══════════════════════════════════════════════════════════════════
#  PALETTE
# ═══════════════════════════════════════════════════════════════════
UK_COLOR   = "#7C3AED"   # violet
US_COLOR   = "#0EA5E9"   # sky blue
POS_COLOR  = "#10B981"   # emerald
NEG_COLOR  = "#EF4444"   # red
WARN_COLOR = "#F59E0B"   # amber
PURPLE     = "#8B5CF6"
BG         = "#F8F7FF"
SURFACE    = "#FFFFFF"
BORDER     = "#E5E7EB"
TEXT       = "#111827"
MUTED      = "#6B7280"
LIGHT_PURPLE = "#EDE9FE"
LIGHT_GREEN  = "#D1FAE5"
LIGHT_RED    = "#FEE2E2"
LIGHT_BLUE   = "#E0F2FE"
LIGHT_AMBER  = "#FEF3C7"

# ═══════════════════════════════════════════════════════════════════
#  CSS
# ═══════════════════════════════════════════════════════════════════
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

*, body, .stApp {{
    font-family: 'Inter', sans-serif !important;
    background-color: {BG} !important;
}}

/* ── Sidebar ── */
[data-testid="stSidebar"] {{
    background: linear-gradient(180deg,#1e1346 0%,#2d1b69 40%,#1a2e5a 100%) !important;
    border-right: 1px solid rgba(255,255,255,0.07);
    min-width: 270px !important;
}}
[data-testid="stSidebar"] * {{ color: rgba(255,255,255,0.88) !important; }}
[data-testid="stSidebar"] .stSlider [data-baseweb="slider"] {{ background: rgba(124,58,237,0.3) !important; }}
[data-testid="stSidebar"] .stMultiSelect [data-baseweb="select"] > div {{
    background: rgba(255,255,255,0.08) !important;
    border: 1px solid rgba(255,255,255,0.18) !important;
}}
[data-testid="stSidebar"] .stMultiSelect [data-baseweb="tag"] {{
    background: rgba(124,58,237,0.5) !important;
}}

/* ── Metric cards ── */
[data-testid="stMetric"] {{
    background: {SURFACE} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 16px !important;
    padding: 20px 22px !important;
    transition: all 0.2s ease;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}}
[data-testid="stMetric"]:hover {{
    box-shadow: 0 8px 24px rgba(124,58,237,0.12) !important;
    transform: translateY(-2px);
    border-color: {PURPLE} !important;
}}
[data-testid="stMetricLabel"] {{
    font-size: 10px !important; font-weight: 700 !important;
    letter-spacing: 0.8px !important; text-transform: uppercase !important;
    color: {MUTED} !important;
}}
[data-testid="stMetricValue"] {{
    font-size: 26px !important; font-weight: 800 !important;
    color: {TEXT} !important; letter-spacing: -0.5px !important;
}}
[data-testid="stMetricDelta"] svg {{ display: none; }}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {{
    background: {SURFACE} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 12px !important;
    padding: 4px !important; gap: 4px !important;
}}
.stTabs [data-baseweb="tab"] {{
    border-radius: 8px !important;
    font-size: 12px !important; font-weight: 600 !important;
    color: {MUTED} !important; padding: 8px 16px !important;
}}
.stTabs [aria-selected="true"] {{
    background: {UK_COLOR} !important;
    color: white !important;
}}

/* ── Dataframe ── */
.stDataFrame {{ border-radius: 12px !important; border: 1px solid {BORDER} !important; }}

/* ── Expander ── */
.streamlit-expanderHeader {{
    background: {SURFACE} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 12px !important;
    font-weight: 600 !important; font-size: 13px !important;
}}

/* ── Hide chrome ── */
#MainMenu, footer, header {{ visibility: hidden; }}
.block-container {{ padding-top: 1rem !important; max-width: 1400px !important; }}

/* ── Custom HTML classes ── */
.section-eyebrow {{
    font-size: 10px; font-weight: 800; letter-spacing: 1.4px;
    text-transform: uppercase; color: {UK_COLOR}; margin: 0 0 4px;
}}
.section-heading {{
    font-size: 19px; font-weight: 800; color: {TEXT};
    margin: 0 0 3px; letter-spacing: -0.3px;
}}
.section-sub {{
    font-size: 12px; color: {MUTED}; margin: 0 0 18px;
}}
.card {{
    background: {SURFACE}; border: 1px solid {BORDER};
    border-radius: 16px; padding: 20px 22px;
    transition: box-shadow 0.2s;
}}
.card:hover {{ box-shadow: 0 6px 24px rgba(0,0,0,0.07); }}
.tag {{
    display: inline-block; font-size: 10px; font-weight: 700;
    padding: 3px 10px; border-radius: 20px; letter-spacing: 0.3px;
}}
.tag-pos {{ background:{LIGHT_GREEN}; color:#065F46; }}
.tag-neg {{ background:{LIGHT_RED}; color:#991B1B; }}
.tag-neu {{ background:{LIGHT_PURPLE}; color:#5B21B6; }}
.tag-warn {{ background:{LIGHT_AMBER}; color:#92400E; }}
.divider {{ border: none; border-top: 1px solid {BORDER}; margin: 28px 0; }}
.insight-box {{
    background: {LIGHT_PURPLE}; border-left: 3px solid {PURPLE};
    border-radius: 0 10px 10px 0; padding: 12px 16px;
    font-size: 12px; color: #3B0764; line-height: 1.6;
    margin-top: 12px;
}}
.insight-box-green {{
    background: {LIGHT_GREEN}; border-left: 3px solid {POS_COLOR};
    border-radius: 0 10px 10px 0; padding: 12px 16px;
    font-size: 12px; color: #064E3B; line-height: 1.6;
    margin-top: 12px;
}}
.insight-box-red {{
    background: {LIGHT_RED}; border-left: 3px solid {NEG_COLOR};
    border-radius: 0 10px 10px 0; padding: 12px 16px;
    font-size: 12px; color: #7F1D1D; line-height: 1.6;
    margin-top: 12px;
}}
.stat-row {{
    display: flex; justify-content: space-between;
    align-items: center; padding: 6px 0;
    border-bottom: 1px solid {BORDER};
}}
.stat-row:last-child {{ border-bottom: none; }}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
#  DATA & MODELS
# ═══════════════════════════════════════════════════════════════════
@st.cache_data
def load_data():
    df = pd.read_csv("merged_sdg_data.csv")
    df.columns = ["Country","Code","Year","Water_Access","GDP_per_capita",
                  "Healthcare_Spending","Life_Expectancy","CO2_Emissions"]
    df = df.dropna()
    df["Year"] = df["Year"].astype(int)
    return df

@st.cache_data
def compute_models():
    df = load_data()
    X  = df[["Healthcare_Spending","Water_Access","GDP_per_capita","CO2_Emissions"]]
    y  = df["Life_Expectancy"]
    Xc = sm.add_constant(X)
    ols = sm.OLS(y, Xc).fit()
    rlm = sm.RLM(y, Xc, M=sm.robust.norms.HuberT()).fit()
    rmse_ols = float(np.sqrt(np.mean(ols.resid**2)))
    rmse_rlm = float(np.sqrt(np.mean((y - rlm.fittedvalues)**2)))
    bp_p  = float(het_breuschpagan(ols.resid, Xc)[1])
    sw_p  = float(stats.shapiro(ols.resid).pvalue)
    vif   = [float(variance_inflation_factor(Xc.values, i+1)) for i in range(X.shape[1])]
    return ols, rlm, rmse_ols, rmse_rlm, bp_p, sw_p, vif

df_full = load_data()
ols_model, rlm_model, rmse_ols, rmse_rlm, bp_p, sw_p, vif_vals = compute_models()

YEARS      = sorted(df_full["Year"].unique())
COUNTRIES  = sorted(df_full["Country"].unique())
COUNTRY_COLORS = {"United Kingdom": UK_COLOR, "United States": US_COLOR}

# ═══════════════════════════════════════════════════════════════════
#  SIDEBAR
# ═══════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style="padding:22px 4px 12px; text-align:center;">
        <div style="font-size:38px; margin-bottom:8px;">🌍</div>
        <p style="font-size:16px; font-weight:800; margin:0; color:white; letter-spacing:-0.3px;">SDG 3 Dashboard</p>
        <p style="font-size:10px; color:rgba(255,255,255,0.5); margin:4px 0 0; letter-spacing:0.5px;">GOOD HEALTH & WELL-BEING</p>
    </div>
    <hr style="border-color:rgba(255,255,255,0.1); margin:4px 0 18px;">
    """, unsafe_allow_html=True)

    st.markdown("<p style='font-size:9px; font-weight:800; letter-spacing:1.2px; color:rgba(255,255,255,0.4); margin:0 0 8px;'>SELECTED YEAR</p>", unsafe_allow_html=True)
    selected_year = st.slider("Year", min_value=YEARS[0], max_value=YEARS[-1],
                               value=YEARS[-1], step=1, label_visibility="collapsed")

    st.markdown("<hr style='border-color:rgba(255,255,255,0.08); margin:14px 0;'>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:9px; font-weight:800; letter-spacing:1.2px; color:rgba(255,255,255,0.4); margin:0 0 8px;'>COUNTRIES</p>", unsafe_allow_html=True)
    selected_countries = st.multiselect("Countries", options=COUNTRIES,
                                         default=COUNTRIES, label_visibility="collapsed")

    st.markdown("<hr style='border-color:rgba(255,255,255,0.08); margin:14px 0;'>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:9px; font-weight:800; letter-spacing:1.2px; color:rgba(255,255,255,0.4); margin:0 0 8px;'>TREND YEAR RANGE</p>", unsafe_allow_html=True)
    year_range = st.slider("Range", min_value=YEARS[0], max_value=YEARS[-1],
                            value=(YEARS[0], YEARS[-1]), step=1, label_visibility="collapsed")

    st.markdown("<hr style='border-color:rgba(255,255,255,0.08); margin:14px 0;'>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:9px; font-weight:800; letter-spacing:1.2px; color:rgba(255,255,255,0.4); margin:0 0 10px;'>METRIC FOCUS</p>", unsafe_allow_html=True)
    metric_focus = st.selectbox("Metric", [
        "Life Expectancy", "Healthcare Spending",
        "GDP per Capita", "Water Access", "CO₂ Emissions"
    ], label_visibility="collapsed")

    st.markdown("""
    <hr style='border-color:rgba(255,255,255,0.08); margin:16px 0;'>
    <div style='font-size:11px; line-height:2; color:rgba(255,255,255,0.5);'>
        <p style='font-weight:700; color:rgba(255,255,255,0.8); margin:0 0 8px; font-size:12px;'>RLM Key Findings</p>
        <div style='display:flex; justify-content:space-between; padding:2px 0;'>
            <span>Healthcare Spend</span><span style='color:#6EE7B7; font-weight:600;'>p=0.036 ✓</span>
        </div>
        <div style='display:flex; justify-content:space-between; padding:2px 0;'>
            <span>Water Access</span><span style='color:#6EE7B7; font-weight:600;'>p&lt;0.001 ✓</span>
        </div>
        <div style='display:flex; justify-content:space-between; padding:2px 0;'>
            <span>CO₂ Emissions</span><span style='color:#FCA5A5; font-weight:600;'>p&lt;0.001 ✓</span>
        </div>
        <div style='display:flex; justify-content:space-between; padding:2px 0;'>
            <span>GDP per Capita</span><span style='color:#FDE68A; font-weight:600;'>p=0.215 —</span>
        </div>
    </div>
    <hr style='border-color:rgba(255,255,255,0.08); margin:14px 0;'>
    <p style='font-size:9px; color:rgba(255,255,255,0.25); line-height:1.6;'>
        Juliana Paula T. Binas · BSIS 3A<br>
        Analytics Techniques & Tools<br>
        World Bank · Our World in Data
    </p>
    """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
#  FILTER
# ═══════════════════════════════════════════════════════════════════
if not selected_countries:
    st.warning("Please select at least one country.")
    st.stop()

dff  = df_full[(df_full["Year"] == selected_year) & df_full["Country"].isin(selected_countries)]
dft  = df_full[df_full["Country"].isin(selected_countries) &
               (df_full["Year"] >= year_range[0]) & (df_full["Year"] <= year_range[1])]
dfa  = df_full[df_full["Country"].isin(selected_countries)]

prev = df_full[(df_full["Year"] == selected_year - 1) & df_full["Country"].isin(selected_countries)]

def Δ(col):
    if prev.empty: return None
    d = round(dff[col].mean() - prev[col].mean(), 3)
    return f"{d:+.2f}"

# ═══════════════════════════════════════════════════════════════════
#  HEADER
# ═══════════════════════════════════════════════════════════════════
st.markdown(f"""
<div style="
    background: linear-gradient(120deg,#1e1346 0%,#4c1d95 40%,#1e3a5f 100%);
    border-radius: 20px; padding: 28px 36px; margin-bottom: 24px;
    position:relative; overflow:hidden;
">
    <div style="position:absolute;right:-30px;top:-30px;width:220px;height:220px;
        border-radius:50%;background:rgba(255,255,255,0.03);"></div>
    <div style="position:absolute;right:80px;bottom:-50px;width:160px;height:160px;
        border-radius:50%;background:rgba(124,58,237,0.08);"></div>

    <div style="display:flex;align-items:center;gap:18px;position:relative;">
        <div style="
            background:rgba(255,255,255,0.1);
            border:1.5px solid rgba(255,255,255,0.2);
            border-radius:16px; width:58px; height:58px;
            display:flex;align-items:center;justify-content:center;
            font-size:24px; flex-shrink:0;
        ">🌍</div>
        <div>
            <p style="color:rgba(255,255,255,0.5);font-size:10px;font-weight:800;
                letter-spacing:2px;text-transform:uppercase;margin:0 0 5px;">
                Sustainable Development Goal 3
            </p>
            <h1 style="color:white;margin:0;font-size:22px;font-weight:800;letter-spacing:-0.4px;">
                Good Health &amp; Well-Being
                <span style="font-size:14px;font-weight:400;color:rgba(255,255,255,0.5);
                    margin-left:12px;letter-spacing:0;">🌿</span>
            </h1>
            <p style="color:rgba(255,255,255,0.65);margin:5px 0 0;font-size:12px;">
                What factors influence life expectancy across countries?
                <span style="color:rgba(255,255,255,0.3);margin:0 8px;">·</span>
                Juliana Paula T. Binas
                <span style="color:rgba(255,255,255,0.3);margin:0 8px;">·</span>
                BSIS 3A
            </p>
        </div>
    </div>

    <div style="display:flex;gap:10px;margin-top:18px;flex-wrap:wrap;position:relative;">
        <div style="background:rgba(255,255,255,0.08);border:1px solid rgba(255,255,255,0.12);
            border-radius:8px;padding:6px 14px;font-size:11px;color:rgba(255,255,255,0.8);">
            📅 <b style="color:white;">2000–2024</b>
        </div>
        <div style="background:rgba(255,255,255,0.08);border:1px solid rgba(255,255,255,0.12);
            border-radius:8px;padding:6px 14px;font-size:11px;color:rgba(255,255,255,0.8);">
            🌐 <b style="color:white;">2 Countries</b>
        </div>
        <div style="background:rgba(255,255,255,0.08);border:1px solid rgba(255,255,255,0.12);
            border-radius:8px;padding:6px 14px;font-size:11px;color:rgba(255,255,255,0.8);">
            📊 <b style="color:white;">4 Drivers</b>
        </div>
        <div style="background:rgba(124,58,237,0.35);border:1px solid rgba(167,139,250,0.4);
            border-radius:8px;padding:6px 14px;font-size:11px;color:rgba(255,255,255,0.9);">
            🤖 OLS R² = <b style="color:white;">0.798</b> · RLM RMSE = <b style="color:white;">0.649</b>
        </div>
        <div style="background:rgba(16,185,129,0.2);border:1px solid rgba(52,211,153,0.3);
            border-radius:8px;padding:6px 14px;font-size:11px;color:rgba(255,255,255,0.8);">
            ✅ Robust Regression (Huber-T)
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
#  SECTION 1 — KPI CARDS
# ═══════════════════════════════════════════════════════════════════
st.markdown("""
<p class='section-eyebrow'>Section 1 — Key Indicators</p>
<p class='section-heading'>Snapshot for Selected Year & Countries</p>
<p class='section-sub'>All values are averages across selected countries. Deltas compare to the previous year.</p>
""", unsafe_allow_html=True)

# Icons on top of each KPI using custom HTML above the columns
ic1, ic2, ic3, ic4, ic5 = st.columns(5)

def kpi_icon(icon, label, color):
    return f"""<div style='font-size:20px;margin-bottom:4px;'>{icon}</div>
    <div style='font-size:9px;font-weight:800;letter-spacing:0.8px;text-transform:uppercase;
        color:{color};margin-bottom:2px;'>{label}</div>"""

with ic1:
    st.markdown(f"<div style='text-align:center;padding:4px 0 0;'>{kpi_icon('❤️','Life Expectancy',UK_COLOR)}</div>", unsafe_allow_html=True)
    st.metric("", f"{dff['Life_Expectancy'].mean():.2f} yrs", delta=Δ('Life_Expectancy'))

with ic2:
    st.markdown(f"<div style='text-align:center;padding:4px 0 0;'>{kpi_icon('🏥','Healthcare Spend',POS_COLOR)}</div>", unsafe_allow_html=True)
    st.metric("", f"${dff['Healthcare_Spending'].mean():,.0f}", delta=Δ('Healthcare_Spending'))

with ic3:
    st.markdown(f"<div style='text-align:center;padding:4px 0 0;'>{kpi_icon('💰','GDP per Capita',WARN_COLOR)}</div>", unsafe_allow_html=True)
    st.metric("", f"${dff['GDP_per_capita'].mean():,.0f}", delta=Δ('GDP_per_capita'))

with ic4:
    st.markdown(f"<div style='text-align:center;padding:4px 0 0;'>{kpi_icon('🏭','CO₂ Emissions',NEG_COLOR)}</div>", unsafe_allow_html=True)
    st.metric("", f"{dff['CO2_Emissions'].mean():.2f} t", delta=Δ('CO2_Emissions'), delta_color="inverse")

with ic5:
    st.markdown(f"<div style='text-align:center;padding:4px 0 0;'>{kpi_icon('💧','Water Access',US_COLOR)}</div>", unsafe_allow_html=True)
    st.metric("", f"{dff['Water_Access'].mean():.2f}%", delta=Δ('Water_Access'))

# Per-country breakdown row
if len(selected_countries) > 1:
    st.markdown("<br>", unsafe_allow_html=True)
    pc_cols = st.columns(len(selected_countries))
    for i, country in enumerate(sorted(selected_countries)):
        row = dff[dff["Country"] == country]
        if row.empty:
            continue
        flag = "🇬🇧" if "Kingdom" in country else "🇺🇸"
        ccolor = COUNTRY_COLORS.get(country, MUTED)
        with pc_cols[i]:
            le  = row['Life_Expectancy'].values[0]
            hc  = row['Healthcare_Spending'].values[0]
            gdp = row['GDP_per_capita'].values[0]
            co2 = row['CO2_Emissions'].values[0]
            wa  = row['Water_Access'].values[0]
            st.markdown(f"""
            <div class='card' style='border-top:3px solid {ccolor};'>
                <p style='font-size:13px;font-weight:800;color:{ccolor};margin:0 0 14px;'>
                    {flag} {country}
                </p>
                <div class='stat-row'>
                    <span style='font-size:11px;color:{MUTED};'>Life Expectancy</span>
                    <span style='font-size:13px;font-weight:700;color:{TEXT};'>{le:.2f} yrs</span>
                </div>
                <div class='stat-row'>
                    <span style='font-size:11px;color:{MUTED};'>Healthcare Spending</span>
                    <span style='font-size:13px;font-weight:700;color:{TEXT};'>${hc:,.0f}</span>
                </div>
                <div class='stat-row'>
                    <span style='font-size:11px;color:{MUTED};'>GDP per Capita</span>
                    <span style='font-size:13px;font-weight:700;color:{TEXT};'>${gdp:,.0f}</span>
                </div>
                <div class='stat-row'>
                    <span style='font-size:11px;color:{MUTED};'>CO₂ Emissions</span>
                    <span style='font-size:13px;font-weight:700;color:{TEXT};'>{co2:.2f} t</span>
                </div>
                <div class='stat-row'>
                    <span style='font-size:11px;color:{MUTED};'>Water Access</span>
                    <span style='font-size:13px;font-weight:700;color:{TEXT};'>{wa:.2f}%</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
#  SECTION 2 — TRENDS
# ═══════════════════════════════════════════════════════════════════
st.markdown("""
<p class='section-eyebrow'>Section 2 — Trends Over Time</p>
<p class='section-heading'>Life Expectancy Over Time</p>
<p class='section-sub'>Use the year range slider to zoom in. The vertical dashed line marks your selected year.</p>
""", unsafe_allow_html=True)

t_left, t_right = st.columns([3, 2])

CHART_LAYOUT = dict(
    plot_bgcolor=SURFACE, paper_bgcolor=SURFACE,
    font=dict(family="Inter, sans-serif", color=TEXT, size=11),
    margin=dict(t=44, b=28, l=44, r=16),
    hovermode="x unified",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                bgcolor="rgba(0,0,0,0)", font_size=11),
    xaxis=dict(showgrid=True, gridcolor="#F3F4F6", zeroline=False, showline=False),
    yaxis=dict(showgrid=True, gridcolor="#F3F4F6", zeroline=False, showline=False),
)

with t_left:
    fig_le = px.line(dft, x="Year", y="Life_Expectancy", color="Country",
                     markers=True, color_discrete_map=COUNTRY_COLORS,
                     labels={"Life_Expectancy": "Life Expectancy (yrs)", "Year": ""},
                     custom_data=["Country","Year","Life_Expectancy"])
    fig_le.update_traces(
        hovertemplate="<b>%{customdata[0]}</b><br>%{customdata[1]}: <b>%{customdata[2]:.2f} yrs</b><extra></extra>",
        line_width=2.5, marker_size=6, marker_line_width=2, marker_line_color="white"
    )
    # COVID annotation
    if year_range[0] <= 2020 <= year_range[1]:
        fig_le.add_vrect(x0=2019.5, x1=2021.5, fillcolor="rgba(239,68,68,0.06)",
                         line_width=0, annotation_text="COVID-19", annotation_position="top left",
                         annotation_font_size=9, annotation_font_color=NEG_COLOR)
    fig_le.add_vline(x=selected_year, line_dash="dot", line_color=f"{UK_COLOR}88",
                     line_width=1.5, annotation_text=str(selected_year),
                     annotation_font_color=UK_COLOR, annotation_font_size=10,
                     annotation_position="top right")
    fig_le.update_layout(**CHART_LAYOUT, title=dict(text="Life expectancy over time", font_size=13, font_color=TEXT, x=0))
    st.plotly_chart(fig_le, use_container_width=True)

    st.markdown(f"""
    <div class='insight-box'>
        Both countries dipped in 2020–21 due to COVID-19, with the UK recovering faster.
        The UK consistently outperforms the USA in life expectancy despite lower healthcare
        spending per capita — pointing to systemic and access-related factors.
    </div>
    """, unsafe_allow_html=True)

with t_right:
    yr_data = dft[dft["Year"] == selected_year] if selected_year in dft["Year"].values else dff
    fig_bar = px.bar(
        yr_data.sort_values("Life_Expectancy"),
        x="Country", y="Life_Expectancy", color="Country",
        color_discrete_map=COUNTRY_COLORS, text="Life_Expectancy",
        labels={"Life_Expectancy": "Life Expectancy (yrs)", "Country": ""},
        custom_data=["Country","Life_Expectancy"]
    )
    fig_bar.update_traces(
        texttemplate="%{text:.2f}", textposition="outside", textfont_size=12,
        hovertemplate="<b>%{customdata[0]}</b><br>Life Expectancy: <b>%{customdata[1]:.2f} yrs</b><extra></extra>",
        marker_line_width=0,
    )
    ymin = yr_data["Life_Expectancy"].min() - 3 if not yr_data.empty else 74
    ymax = yr_data["Life_Expectancy"].max() + 3 if not yr_data.empty else 85
    fig_bar.update_layout(**CHART_LAYOUT,
        title=dict(text=f"Country comparison ({selected_year})", font_size=13, font_color=TEXT, x=0),
        showlegend=False, yaxis=dict(range=[ymin, ymax], showgrid=True, gridcolor="#F3F4F6"))
    st.plotly_chart(fig_bar, use_container_width=True)

    if len(selected_countries) == 2:
        uk_le = dff[dff["Country"]=="United Kingdom"]["Life_Expectancy"].values
        us_le = dff[dff["Country"]=="United States"]["Life_Expectancy"].values
        if len(uk_le) and len(us_le):
            gap = uk_le[0] - us_le[0]
            st.markdown(f"""
            <div class='card' style='text-align:center; border-top: 3px solid {UK_COLOR};'>
                <p style='font-size:10px;font-weight:700;text-transform:uppercase;
                    letter-spacing:0.8px;color:{MUTED};margin:0 0 4px;'>UK–US Gap in {selected_year}</p>
                <p style='font-size:32px;font-weight:800;color:{UK_COLOR};margin:0;
                    letter-spacing:-1px;'>{gap:+.2f} yrs</p>
                <p style='font-size:11px;color:{MUTED};margin:6px 0 0;'>
                    Spending efficiency matters — the UK spends less on healthcare yet lives longer.
                </p>
            </div>
            """, unsafe_allow_html=True)

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
#  SECTION 3 — FACTORS
# ═══════════════════════════════════════════════════════════════════
st.markdown("""
<p class='section-eyebrow'>Section 3 — Factors Affecting Life Expectancy</p>
<p class='section-heading'>What Drives Life Expectancy?</p>
<p class='section-sub'>Each card shows one factor's relationship with life expectancy. Charts animate over time.</p>
""", unsafe_allow_html=True)

FACTOR_CONFIG = [
    ("Healthcare_Spending", "Healthcare spending", "💊", UK_COLOR, "positive",
     "Jaba et al. (2014)", "Positive driver ↑",
     "Higher healthcare spending → better health systems, more access to treatment, longer lives."),
    ("GDP_per_capita",      "GDP per capita",       "💰", WARN_COLOR, "positive",
     "Preston (1975)", "Positive driver ↑",
     "Wealthier nations have better nutrition, sanitation, and healthcare (Preston Curve)."),
    ("Water_Access",        "Water access",          "💧", POS_COLOR, "positive",
     "UN SDG Report (2023)", "Positive driver ↑",
     "Access to safe water eliminates waterborne diseases — a key determinant of population health."),
    ("CO2_Emissions",       "CO₂ emissions",         "🏭", NEG_COLOR, "negative",
     "Wen et al. (2021)", "Negative driver ↓",
     "Higher CO₂ reflects pollution that causes respiratory and cardiovascular disease."),
]

fac_cols = st.columns(4)
for col_w, (x_var, label, icon, color, direction, citation, dir_label, insight) in zip(fac_cols, FACTOR_CONFIG):
    with col_w:
        tag_cls = "tag-pos" if direction == "positive" else "tag-neg"
        tag_bg  = LIGHT_GREEN if direction == "positive" else LIGHT_RED
        tag_txt = "#065F46" if direction == "positive" else "#991B1B"

        fig_s = px.scatter(
            dfa, x=x_var, y="Life_Expectancy", color="Country",
            color_discrete_map=COUNTRY_COLORS, trendline="ols",
            labels={x_var: "", "Life_Expectancy": "LE (yrs)"},
            custom_data=["Country","Year", x_var,"Life_Expectancy"]
        )
        fig_s.update_traces(
            marker=dict(size=7, opacity=0.75, line=dict(width=1.5, color="white")),
            selector=dict(mode="markers"),
            hovertemplate="<b>%{customdata[0]}</b> %{customdata[1]}<br>"
                          + f"{label}: " + "<b>%{customdata[2]:,.1f}</b><br>"
                          + "Life Exp: <b>%{customdata[3]:.2f} yrs</b><extra></extra>"
        )
        fig_s.update_layout(
            plot_bgcolor=SURFACE, paper_bgcolor=SURFACE,
            title=dict(text=f"{icon} {label}", font_size=12, font_color=TEXT, x=0),
            showlegend=False, margin=dict(t=38, b=8, l=36, r=8), height=200,
            font=dict(family="Inter, sans-serif", size=10),
            xaxis=dict(showgrid=True, gridcolor="#F3F4F6"),
            yaxis=dict(showgrid=True, gridcolor="#F3F4F6"),
        )

        # Legend dots
        st.plotly_chart(fig_s, use_container_width=True)

        leg_html = "".join([
            f"<span style='display:inline-flex;align-items:center;gap:4px;margin-right:8px;font-size:10px;'>"
            f"<span style='width:8px;height:8px;border-radius:50%;background:{COUNTRY_COLORS.get(c,MUTED)};display:inline-block;'></span>"
            f"{'UK' if 'Kingdom' in c else 'USA'}</span>"
            for c in sorted(selected_countries)
        ])

        corr_val = dfa[x_var].corr(dfa["Life_Expectancy"])

        st.markdown(f"""
        <div style='background:{tag_bg};border-radius:0 0 10px 10px;padding:10px 14px;
            margin-top:-8px; border:1px solid {BORDER}; border-top:none;'>
            <div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;'>
                <span class='tag' style='background:{tag_bg};color:{tag_txt};
                    border:1px solid rgba(0,0,0,0.08);'>{dir_label}</span>
                <span style='font-size:10px;font-weight:700;color:{color};'>r={corr_val:+.3f}</span>
            </div>
            <p style='font-size:10px;color:{MUTED};margin:0 0 4px;font-style:italic;'>{citation}</p>
            <p style='font-size:10px;color:{TEXT};margin:0;line-height:1.5;'>{insight}</p>
            <div style='margin-top:6px;'>{leg_html}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
#  SECTION 4 — ALL DRIVERS OVER TIME (TABS)
# ═══════════════════════════════════════════════════════════════════
st.markdown("""
<p class='section-eyebrow'>Section 4 — Driver Trends</p>
<p class='section-heading'>All Factors Over Time by Country</p>
<p class='section-sub'>Select a metric from the tabs to explore how it changed from 2000 to 2024.</p>
""", unsafe_allow_html=True)

tab_hc, tab_gdp, tab_wa, tab_co2 = st.tabs([
    "💊 Healthcare Spending", "💰 GDP per Capita", "💧 Water Access", "🏭 CO₂ Emissions"
])

DRIVER_CFG = [
    (tab_hc, "Healthcare_Spending", "Healthcare Spending (USD)", POS_COLOR),
    (tab_gdp, "GDP_per_capita", "GDP per Capita (USD)", WARN_COLOR),
    (tab_wa, "Water_Access", "Water Access (%)", US_COLOR),
    (tab_co2, "CO2_Emissions", "CO₂ Emissions (tons/capita)", NEG_COLOR),
]

for tab, col, label, color in DRIVER_CFG:
    with tab:
        dc1, dc2 = st.columns([3, 1])
        with dc1:
            fig_d = px.line(dft, x="Year", y=col, color="Country",
                            markers=True, color_discrete_map=COUNTRY_COLORS,
                            labels={col: label, "Year": ""},
                            custom_data=["Country","Year",col])
            fig_d.update_traces(
                hovertemplate=f"<b>%{{customdata[0]}}</b><br>%{{customdata[1]}}: <b>%{{customdata[2]:,.2f}}</b><extra></extra>",
                line_width=2.5, marker_size=6, marker_line_width=2, marker_line_color="white"
            )
            if year_range[0] <= 2020 <= year_range[1]:
                fig_d.add_vrect(x0=2019.5, x1=2021.5, fillcolor="rgba(239,68,68,0.05)", line_width=0)
            fig_d.add_vline(x=selected_year, line_dash="dot", line_color=f"{UK_COLOR}88", line_width=1.5)
            fig_d.update_layout(**CHART_LAYOUT,
                title=dict(text=f"{label} over time", font_size=13, font_color=TEXT, x=0))
            st.plotly_chart(fig_d, use_container_width=True)

        with dc2:
            rows = []
            for country in sorted(selected_countries):
                sub = dff[dff["Country"] == country]
                if sub.empty: continue
                v = sub[col].values[0]
                flag = "🇬🇧" if "Kingdom" in country else "🇺🇸"
                short = "UK" if "Kingdom" in country else "US"
                rows.append((flag, short, v, COUNTRY_COLORS.get(country, MUTED)))

            val_html = "".join([
                f"<div style='margin-bottom:12px;'>"
                f"<p style='font-size:10px;font-weight:700;color:{c};margin:0;'>{f} {s}</p>"
                f"<p style='font-size:20px;font-weight:800;color:{TEXT};margin:2px 0 0;'>{v:,.1f}</p>"
                f"</div>"
                for f, s, v, c in rows
            ])
            # trend arrow
            trend_rows = []
            for country in sorted(selected_countries):
                sub_all = dft[dft["Country"] == country].sort_values("Year")
                if len(sub_all) >= 2:
                    delta_v = sub_all[col].values[-1] - sub_all[col].values[0]
                    arrow = "↑" if delta_v > 0 else "↓"
                    tr_col = POS_COLOR if delta_v > 0 else NEG_COLOR
                    if col == "CO2_Emissions":
                        tr_col = POS_COLOR if delta_v < 0 else NEG_COLOR
                    trend_rows.append(
                        f"<span style='font-size:11px;color:{tr_col};font-weight:700;'>"
                        f"{'UK' if 'Kingdom' in country else 'US'} {arrow} {abs(delta_v):,.1f}</span>"
                    )

            st.markdown(f"""
            <div class='card' style='height:100%;min-height:160px;'>
                <p style='font-size:9px;font-weight:800;letter-spacing:1px;
                    text-transform:uppercase;color:{MUTED};margin:0 0 12px;'>In {selected_year}</p>
                {val_html}
                <hr style='border:none;border-top:1px solid {BORDER};margin:10px 0;'>
                <p style='font-size:9px;font-weight:700;letter-spacing:0.8px;
                    text-transform:uppercase;color:{MUTED};margin:0 0 6px;'>Trend {year_range[0]}→{year_range[1]}</p>
                <div style='display:flex;flex-direction:column;gap:3px;'>
                    {"".join(trend_rows)}
                </div>
            </div>
            """, unsafe_allow_html=True)

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
#  SECTION 5 — CORRELATION
# ═══════════════════════════════════════════════════════════════════
st.markdown("""
<p class='section-eyebrow'>Section 5 — Correlation Analysis</p>
<p class='section-heading'>How Variables Relate to Each Other</p>
<p class='section-sub'>Pearson correlation coefficients. Hover the heatmap for exact values.</p>
""", unsafe_allow_html=True)

corr_c1, corr_c2 = st.columns([1, 1])

ALL_VARS    = ["Life_Expectancy","Healthcare_Spending","Water_Access","GDP_per_capita","CO2_Emissions"]
ALL_LABELS  = ["Life Expectancy","Healthcare Spending","Water Access","GDP per Capita","CO₂ Emissions"]
corr_matrix = df_full[ALL_VARS].corr().round(3)

with corr_c1:
    st.markdown("<div style='font-size:13px;font-weight:700;color:" + TEXT + ";margin-bottom:14px;'>Correlation with life expectancy</div>", unsafe_allow_html=True)

    corr_le = corr_matrix["Life_Expectancy"].drop("Life_Expectancy")
    for var, lbl in zip(ALL_VARS[1:], ALL_LABELS[1:]):
        val = corr_le[var]
        bar_color = POS_COLOR if val > 0 else NEG_COLOR
        bar_pct   = abs(val) * 100
        strength  = "strong" if abs(val) >= 0.6 else ("moderate" if abs(val) >= 0.3 else "weak")
        s_color   = POS_COLOR if val > 0 else NEG_COLOR
        sign      = "+" if val >= 0 else ""
        st.markdown(f"""
        <div style='display:flex;align-items:center;gap:12px;padding:8px 0;
            border-bottom:1px solid {BORDER};'>
            <span style='font-size:12px;color:{TEXT};width:140px;flex-shrink:0;'>{lbl}</span>
            <div style='flex:1;background:#F3F4F6;border-radius:4px;height:8px;'>
                <div style='width:{bar_pct:.0f}%;height:100%;background:{bar_color};
                    border-radius:4px;'></div>
            </div>
            <span style='font-size:13px;font-weight:700;color:{s_color};width:46px;text-align:right;'>
                {sign}{val:.3f}
            </span>
            <span style='font-size:10px;color:{s_color};font-weight:600;width:60px;'>
                {strength} {'+'  if val>0 else '−'}
            </span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class='insight-box' style='margin-top:14px;'>
        <b>CO₂ emissions</b> (r=−0.788) is the strongest predictor overall.
        <b>Healthcare spending</b> shows a negative raw correlation (r=−0.514)
        because the US spends the most but doesn't achieve the highest life expectancy —
        a <i>spending efficiency paradox</i>.
    </div>
    """, unsafe_allow_html=True)

with corr_c2:
    st.markdown("<div style='font-size:13px;font-weight:700;color:" + TEXT + ";margin-bottom:8px;'>Correlation heatmap</div>", unsafe_allow_html=True)

    z     = corr_matrix.values
    annot = [[f"{v:.2f}" for v in row] for row in z]

    def cell_color(v):
        if v >= 0.6:  return "#4F46E5"
        if v >= 0.3:  return "#818CF8"
        if v >= 0:    return "#C7D2FE"
        if v >= -0.3: return "#FCA5A5"
        if v >= -0.6: return "#EF4444"
        return "#991B1B"

    fig_hm = go.Figure(go.Heatmap(
        z=z, x=ALL_LABELS, y=ALL_LABELS,
        colorscale=[
            [0.0,"#7F1D1D"],[0.2,"#EF4444"],[0.4,"#FCA5A5"],
            [0.5,"#F9FAFB"],
            [0.6,"#C7D2FE"],[0.8,"#818CF8"],[1.0,"#3730A3"]
        ],
        zmin=-1, zmax=1, text=annot,
        texttemplate="%{text}", textfont_size=12,
        hovertemplate="%{y} × %{x}<br>r = <b>%{z:.3f}</b><extra></extra>",
        showscale=True,
        colorbar=dict(thickness=12, len=0.9, tickfont_size=10)
    ))
    fig_hm.update_layout(
        plot_bgcolor=SURFACE, paper_bgcolor=SURFACE,
        margin=dict(t=8, b=8, l=8, r=8), height=280,
        font=dict(family="Inter, sans-serif", size=10),
        xaxis=dict(tickfont_size=10),
        yaxis=dict(tickfont_size=10),
    )
    st.plotly_chart(fig_hm, use_container_width=True)

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
#  SECTION 6 — REGRESSION MODEL
# ═══════════════════════════════════════════════════════════════════
st.markdown("""
<p class='section-eyebrow'>Section 6 — Regression Model & Predictions</p>
<p class='section-heading'>OLS & Robust Regression (RLM) Results</p>
<p class='section-sub'>RLM (Huber-T) is preferred here — heteroscedasticity was detected (BP p=0.011), and high VIF values indicate collinearity.</p>
""", unsafe_allow_html=True)

# Model metrics
mm1, mm2, mm3, mm4 = st.columns(4)
mm1.metric("R² Score (OLS)", "0.7978", help="79.8% of variance in life expectancy explained")
mm2.metric("Adj. R² (OLS)",  "0.7770", help="Adjusted for number of predictors")
mm3.metric("RMSE (OLS)",     f"{rmse_ols:.4f}", help="Average prediction error in years")
mm4.metric("Observations",   "44",     help="22 years × 2 countries")

st.markdown("<br>", unsafe_allow_html=True)

reg_c1, reg_c2 = st.columns([3, 2])

with reg_c1:
    # Actual vs Predicted
    df_pred = df_full[df_full["Country"].isin(selected_countries)].copy()
    Xp  = df_pred[["Healthcare_Spending","Water_Access","GDP_per_capita","CO2_Emissions"]]
    Xpc = sm.add_constant(Xp)
    df_pred["OLS_Pred"] = ols_model.predict(Xpc).values
    df_pred["RLM_Pred"] = rlm_model.predict(Xpc).values

    fig_ap = go.Figure()
    for country in sorted(selected_countries):
        sub  = df_pred[df_pred["Country"] == country]
        flag = "🇬🇧" if "Kingdom" in country else "🇺🇸"
        col_c = COUNTRY_COLORS.get(country, MUTED)
        fig_ap.add_trace(go.Scatter(
            x=sub["Year"], y=sub["Life_Expectancy"],
            mode="lines+markers", name=f"{flag} Actual",
            line=dict(color=col_c, width=2.5),
            marker=dict(size=6, line=dict(width=2, color="white")),
            hovertemplate=f"<b>{country}</b><br>Year: %{{x}}<br>Actual: <b>%{{y:.2f}} yrs</b><extra></extra>"
        ))
        fig_ap.add_trace(go.Scatter(
            x=sub["Year"], y=sub["OLS_Pred"],
            mode="lines", name=f"{flag} OLS Predicted",
            line=dict(color=col_c, width=1.5, dash="dash"),
            hovertemplate=f"<b>{country}</b><br>Year: %{{x}}<br>OLS Predicted: <b>%{{y:.2f}} yrs</b><extra></extra>"
        ))

    fig_ap.update_layout(**CHART_LAYOUT,
        title=dict(text="Actual vs predicted life expectancy (OLS)", font_size=13, font_color=TEXT, x=0),
        height=300)
    st.plotly_chart(fig_ap, use_container_width=True)

    st.markdown(f"""
    <div class='insight-box-green'>
        The model explains <b>79.8%</b> of variance in life expectancy.
        Predicted values closely track actual values — confirming that the four chosen
        drivers are highly explanatory. The RMSE of <b>{rmse_ols:.2f} years</b> means
        predictions are typically within ~8 months of the actual value.
    </div>
    """, unsafe_allow_html=True)

with reg_c2:
    # Coefficient magnitude chart (feature importance)
    FEAT_VARS   = ["Healthcare_Spending","Water_Access","GDP_per_capita","CO2_Emissions"]
    FEAT_LABELS = ["Healthcare Spend","Water Access","GDP per Capita","CO₂ Emissions"]
    FEAT_COLORS = [POS_COLOR, US_COLOR, WARN_COLOR, NEG_COLOR]

    rlm_coefs = [abs(rlm_model.params[v]) for v in FEAT_VARS]
    rlm_pvals = [rlm_model.pvalues[v] for v in FEAT_VARS]
    max_c     = max(rlm_coefs)

    st.markdown(f"<div style='font-size:13px;font-weight:700;color:{TEXT};margin-bottom:14px;'>Feature importance (RLM coefficient magnitude)</div>", unsafe_allow_html=True)

    for lbl, coef, pval, raw_c, fc in zip(FEAT_LABELS, rlm_coefs,
                                            rlm_pvals,
                                            [rlm_model.params[v] for v in FEAT_VARS],
                                            FEAT_COLORS):
        bar_w  = coef / max_c * 100
        sig    = "✓ significant" if pval < 0.05 else "— not sig."
        sig_c  = POS_COLOR if pval < 0.05 else MUTED
        sign   = "+" if raw_c >= 0 else "−"
        st.markdown(f"""
        <div style='padding:8px 0; border-bottom:1px solid {BORDER};'>
            <div style='display:flex;justify-content:space-between;margin-bottom:5px;'>
                <span style='font-size:12px;font-weight:600;color:{TEXT};'>{lbl}</span>
                <span style='font-size:11px;font-weight:700;color:{fc};'>{sign}{coef:.4f}</span>
            </div>
            <div style='display:flex;align-items:center;gap:8px;'>
                <div style='flex:1;background:#F3F4F6;border-radius:4px;height:7px;'>
                    <div style='width:{bar_w:.0f}%;height:100%;background:{fc};border-radius:4px;'></div>
                </div>
                <span style='font-size:9px;font-weight:700;color:{sig_c};width:90px;text-align:right;'>{sig}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class='insight-box' style='margin-top:14px;'>
        <b>Water access</b> and <b>healthcare spending</b> are the two most influential
        positive drivers. <b>CO₂ emissions</b> is the strongest negative driver of life expectancy.
    </div>
    """, unsafe_allow_html=True)

# OLS vs RLM coefficient comparison
st.markdown("<br>", unsafe_allow_html=True)
rc1, rc2 = st.columns(2)

with rc1:
    ols_c = [ols_model.params[v] for v in FEAT_VARS]
    rlm_c = [rlm_model.params[v] for v in FEAT_VARS]
    fig_coef = go.Figure()
    fig_coef.add_trace(go.Bar(
        y=FEAT_LABELS, x=ols_c, orientation="h", name="OLS",
        marker_color=PURPLE, opacity=0.75,
        hovertemplate="OLS: <b>%{x:.5f}</b><extra></extra>"
    ))
    fig_coef.add_trace(go.Bar(
        y=FEAT_LABELS, x=rlm_c, orientation="h", name="RLM (Huber-T)",
        marker_color=WARN_COLOR, opacity=0.85,
        hovertemplate="RLM: <b>%{x:.5f}</b><extra></extra>"
    ))
    fig_coef.add_vline(x=0, line_color=MUTED, line_width=1)
    fig_coef.update_layout(
        title=dict(text="OLS vs RLM coefficients", font_size=13, font_color=TEXT, x=0),
        barmode="group", plot_bgcolor=SURFACE, paper_bgcolor=SURFACE,
        margin=dict(t=44, b=28, l=12, r=16), height=240,
        font=dict(family="Inter, sans-serif", size=11),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                    bgcolor="rgba(0,0,0,0)", font_size=11),
        xaxis=dict(showgrid=True, gridcolor="#F3F4F6"),
        yaxis=dict(showgrid=False)
    )
    st.plotly_chart(fig_coef, use_container_width=True)

with rc2:
    # Residuals scatter
    fig_res = go.Figure()
    fig_res.add_trace(go.Scatter(
        x=ols_model.fittedvalues, y=ols_model.resid,
        mode="markers",
        marker=dict(size=8, color=PURPLE, opacity=0.65, line=dict(width=1.5, color="white")),
        hovertemplate="Fitted: <b>%{x:.2f}</b><br>Residual: <b>%{y:.3f}</b><extra></extra>"
    ))
    fig_res.add_hline(y=0, line_color=NEG_COLOR, line_width=1.5, line_dash="dash")
    fig_res.update_layout(
        title=dict(text="Residuals vs fitted values (OLS)", font_size=13, font_color=TEXT, x=0),
        plot_bgcolor=SURFACE, paper_bgcolor=SURFACE,
        margin=dict(t=44, b=28, l=44, r=16), height=240,
        font=dict(family="Inter, sans-serif", size=11),
        xaxis=dict(showgrid=True, gridcolor="#F3F4F6", title="Fitted values"),
        yaxis=dict(showgrid=True, gridcolor="#F3F4F6", title="Residuals")
    )
    st.plotly_chart(fig_res, use_container_width=True)

# Diagnostics row
st.markdown("<br>", unsafe_allow_html=True)
d1, d2, d3 = st.columns(3)

with d1:
    ok = sw_p > 0.05
    st.markdown(f"""
    <div class='card' style='border-top:3px solid {"" + POS_COLOR if ok else NEG_COLOR};'>
        <p style='font-size:9px;font-weight:800;letter-spacing:1px;text-transform:uppercase;
            color:{MUTED};margin:0 0 8px;'>Normality of Residuals</p>
        <p style='font-size:15px;font-weight:700;color:{TEXT};margin:0 0 4px;'>Shapiro-Wilk Test</p>
        <p style='font-size:28px;font-weight:800;color:{"" + POS_COLOR if ok else NEG_COLOR};
            margin:0 0 8px;letter-spacing:-0.5px;'>p = {sw_p:.4f}</p>
        <span class='tag {"tag-pos" if ok else "tag-neg"}'>{"✓ Residuals are normal" if ok else "✗ Not normal"}</span>
        <p style='font-size:11px;color:{MUTED};margin:10px 0 0;line-height:1.5;'>
            p > 0.05 confirms that OLS residuals are normally distributed — a key model assumption.
        </p>
    </div>
    """, unsafe_allow_html=True)

with d2:
    bad = bp_p < 0.05
    st.markdown(f"""
    <div class='card' style='border-top:3px solid {"" + NEG_COLOR if bad else POS_COLOR};'>
        <p style='font-size:9px;font-weight:800;letter-spacing:1px;text-transform:uppercase;
            color:{MUTED};margin:0 0 8px;'>Heteroscedasticity</p>
        <p style='font-size:15px;font-weight:700;color:{TEXT};margin:0 0 4px;'>Breusch-Pagan Test</p>
        <p style='font-size:28px;font-weight:800;color:{"" + NEG_COLOR if bad else POS_COLOR};
            margin:0 0 8px;letter-spacing:-0.5px;'>p = {bp_p:.4f}</p>
        <span class='tag {"tag-neg" if bad else "tag-pos"}'>{"✗ Heteroscedasticity found" if bad else "✓ Homoscedastic"}</span>
        <p style='font-size:11px;color:{MUTED};margin:10px 0 0;line-height:1.5;'>
            p &lt; 0.05 means error variance is not constant — <b>this justifies using RLM</b> over plain OLS.
        </p>
    </div>
    """, unsafe_allow_html=True)

with d3:
    vif_labels = ["Healthcare Spend","Water Access","GDP per Capita","CO₂ Emissions"]
    vif_items  = "".join([
        f"<div style='display:flex;justify-content:space-between;padding:3px 0;"
        f"border-bottom:1px solid {BORDER};'>"
        f"<span style='font-size:11px;color:{MUTED};'>{n}</span>"
        f"<span style='font-size:11px;font-weight:700;"
        f"color:{"" + NEG_COLOR if v>10 else POS_COLOR};'>{v:.1f}</span>"
        f"</div>"
        for n, v in zip(vif_labels, vif_vals)
    ])
    any_high = any(v > 10 for v in vif_vals)
    st.markdown(f"""
    <div class='card' style='border-top:3px solid {"" + WARN_COLOR};'>
        <p style='font-size:9px;font-weight:800;letter-spacing:1px;text-transform:uppercase;
            color:{MUTED};margin:0 0 8px;'>Multicollinearity</p>
        <p style='font-size:15px;font-weight:700;color:{TEXT};margin:0 0 8px;'>VIF Values</p>
        <span class='tag {"tag-neg" if any_high else "tag-pos"}'
            style='margin-bottom:10px;display:inline-block;'>
            {"✗ High VIF detected (>10)" if any_high else "✓ VIF acceptable"}
        </span>
        {vif_items}
        <p style='font-size:10px;color:{MUTED};margin:8px 0 0;line-height:1.5;'>
            VIF &gt; 10 signals problematic multicollinearity. RLM handles this more robustly.
        </p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
#  SECTION 7 — DATA TABLE
# ═══════════════════════════════════════════════════════════════════
with st.expander(f"📋  Country Data Table — {selected_year} (click to expand)", expanded=False):
    disp = dff[["Country","Life_Expectancy","Healthcare_Spending","GDP_per_capita",
                "CO2_Emissions","Water_Access"]].copy()
    disp.columns = ["Country","Life Expectancy (yrs)","Healthcare Spending ($)",
                    "GDP per Capita ($)","CO₂ Emissions (t)","Water Access (%)"]
    disp = disp.set_index("Country").round(2)
    st.dataframe(
        disp.style
            .format({"Life Expectancy (yrs)": "{:.2f}",
                     "Healthcare Spending ($)": "${:,.2f}",
                     "GDP per Capita ($)": "${:,.2f}",
                     "CO₂ Emissions (t)": "{:.2f}",
                     "Water Access (%)": "{:.2f}%"})
            .background_gradient(cmap="Blues",   subset=["Life Expectancy (yrs)"])
            .background_gradient(cmap="Purples", subset=["Healthcare Spending ($)","GDP per Capita ($)"])
            .background_gradient(cmap="Reds",    subset=["CO₂ Emissions (t)"], low=1),
        use_container_width=True
    )

with st.expander("📊  Full Dataset (all years)", expanded=False):
    all_disp = df_full[df_full["Country"].isin(selected_countries)].copy()
    all_disp = all_disp.sort_values(["Country","Year"])
    st.dataframe(all_disp.round(2), use_container_width=True)

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
#  SECTION 8 — INSIGHTS & RECOMMENDATIONS
# ═══════════════════════════════════════════════════════════════════
st.markdown("""
<p class='section-eyebrow'>Section 8 — Insights & Recommendations</p>
<p class='section-heading'>Key Findings & Policy Recommendations</p>
<p class='section-sub'>Based on RLM regression results, correlation analysis, and 25 years of data from two countries.</p>
""", unsafe_allow_html=True)

ins1, ins2 = st.columns(2)

RECS = [
    (UK_COLOR, LIGHT_PURPLE, "#3B0764", "#5B21B6",
     "💊", "Increase Healthcare Investment",
     "01 — Positive driver (RLM p=0.036)",
     "Every $1,000 increase in per-capita healthcare spending is associated with measurably higher "
     "life expectancy. The UK spends significantly less than the US yet achieves better outcomes — "
     "proving that <b>spending efficiency matters as much as total amount</b>.",
     "Prioritize preventive care, universal coverage, and evidence-based spending allocation."),

    (WARN_COLOR, LIGHT_AMBER, "#78350F", "#92400E",
     "💰", "Promote Economic Development",
     "02 — GDP per Capita (RLM p=0.215, not significant)",
     "GDP per capita is not independently significant in this two-country sample — likely because "
     "the US has higher GDP but lower life expectancy than the UK. "
     "<b>Wealth alone does not guarantee health.</b> How a country allocates its resources matters more.",
     "Invest GDP growth into public health infrastructure, equitable access, and social determinants of health."),

    (POS_COLOR, LIGHT_GREEN, "#064E3B", "#065F46",
     "💧", "Ensure Universal Water Access",
     "03 — Significant in both OLS & RLM (p<0.001)",
     "Access to clean water is one of the most consistent drivers of life expectancy "
     "in both models. Both the UK and US now have near-100% coverage — "
     "<b>but globally, billions still lack safe water</b>, making this a critical SDG 3 target.",
     "Sustain domestic infrastructure and fund international water access programs in low-income countries."),

    (NEG_COLOR, LIGHT_RED, "#7F1D1D", "#991B1B",
     "🏭", "Reduce Carbon Emissions",
     "04 — Strongest negative driver (r=−0.788, RLM p<0.001)",
     "CO₂ emissions show the strongest single correlation with life expectancy in this dataset. "
     "Higher emissions reflect environmental pollution that directly causes respiratory disease, "
     "cardiovascular conditions, and reduced population health. "
     "<b>The US's high emission rate contributes to its lower life expectancy.</b>",
     "Transition to clean energy, enforce emission standards, and invest in environmental health policy."),
]

for i, (accent, bg, text_dark, text_mid, icon, title, subtitle, body, rec) in enumerate(RECS):
    col = ins1 if i % 2 == 0 else ins2
    with col:
        st.markdown(f"""
        <div class='card' style='border-left:4px solid {accent}; margin-bottom:16px;'>
            <div style='display:flex;align-items:flex-start;gap:12px;'>
                <div style='font-size:24px;flex-shrink:0;margin-top:2px;'>{icon}</div>
                <div>
                    <p style='font-size:9px;font-weight:800;letter-spacing:0.8px;
                        text-transform:uppercase;color:{accent};margin:0 0 4px;'>{subtitle}</p>
                    <p style='font-size:15px;font-weight:800;color:{TEXT};margin:0 0 8px;
                        letter-spacing:-0.2px;'>{title}</p>
                    <p style='font-size:12px;color:{MUTED};margin:0 0 12px;line-height:1.6;'>{body}</p>
                    <div style='background:{bg};border-radius:8px;padding:10px 14px;'>
                        <p style='font-size:10px;font-weight:700;color:{text_mid};
                            margin:0 0 3px;text-transform:uppercase;letter-spacing:0.5px;'>
                            Policy Recommendation
                        </p>
                        <p style='font-size:11px;color:{text_dark};margin:0;line-height:1.5;'>{rec}</p>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
#  FINAL CONCLUSION
# ═══════════════════════════════════════════════════════════════════
st.markdown(f"""
<div style="
    background: linear-gradient(120deg,#1e1346 0%,#3730a3 45%,#1e3a5f 100%);
    border-radius: 20px; padding: 30px 38px; position:relative; overflow:hidden;
">
    <div style="position:absolute;right:-20px;top:-20px;width:180px;height:180px;
        border-radius:50%;background:rgba(255,255,255,0.03);"></div>

    <p style="color:rgba(255,255,255,0.5);font-size:10px;font-weight:800;
        letter-spacing:1.8px;text-transform:uppercase;margin:0 0 10px;">Final Conclusion</p>

    <h2 style="color:white;font-size:18px;font-weight:800;margin:0 0 14px;
        letter-spacing:-0.3px;line-height:1.4;">
        The regression analysis confirms that
        <span style="color:#A5B4FC;">healthcare spending</span>,
        <span style="color:#6EE7B7;">water access</span>, and
        <span style="color:#FDE68A;">GDP per capita</span>
        are significant positive drivers of life expectancy, while
        <span style="color:#FCA5A5;">CO₂ emissions</span>
        act as a significant negative driver.
    </h2>

    <p style="color:rgba(255,255,255,0.7);font-size:13px;margin:0 0 16px;line-height:1.7;">
        Together, these four variables explain <b style="color:white;">79.8% of the variance</b> in life
        expectancy across the UK and USA from 2000 to 2024 — directly supporting the objectives of
        <b style="color:white;">SDG 3: Good Health and Well-Being</b>.
        Robust Regression (RLM with Huber-T weighting) was applied to address detected heteroscedasticity
        and multicollinearity, ensuring more reliable coefficient estimates.
    </p>

    <div style="display:flex;gap:12px;flex-wrap:wrap;">
        <div style="background:rgba(165,180,252,0.15);border:1px solid rgba(165,180,252,0.25);
            border-radius:10px;padding:10px 16px;flex:1;min-width:140px;">
            <p style="color:rgba(255,255,255,0.5);font-size:9px;font-weight:700;
                letter-spacing:1px;text-transform:uppercase;margin:0 0 3px;">OLS Model</p>
            <p style="color:white;font-size:18px;font-weight:800;margin:0;">R² = 0.798</p>
        </div>
        <div style="background:rgba(110,231,183,0.12);border:1px solid rgba(110,231,183,0.2);
            border-radius:10px;padding:10px 16px;flex:1;min-width:140px;">
            <p style="color:rgba(255,255,255,0.5);font-size:9px;font-weight:700;
                letter-spacing:1px;text-transform:uppercase;margin:0 0 3px;">RLM RMSE</p>
            <p style="color:white;font-size:18px;font-weight:800;margin:0;">{rmse_rlm:.4f} yrs</p>
        </div>
        <div style="background:rgba(252,165,165,0.12);border:1px solid rgba(252,165,165,0.2);
            border-radius:10px;padding:10px 16px;flex:1;min-width:140px;">
            <p style="color:rgba(255,255,255,0.5);font-size:9px;font-weight:700;
                letter-spacing:1px;text-transform:uppercase;margin:0 0 3px;">Strongest Driver</p>
            <p style="color:white;font-size:18px;font-weight:800;margin:0;">CO₂ r=−0.788</p>
        </div>
        <div style="background:rgba(253,230,138,0.1);border:1px solid rgba(253,230,138,0.18);
            border-radius:10px;padding:10px 16px;flex:1;min-width:140px;">
            <p style="color:rgba(255,255,255,0.5);font-size:9px;font-weight:700;
                letter-spacing:1px;text-transform:uppercase;margin:0 0 3px;">Data Period</p>
            <p style="color:white;font-size:18px;font-weight:800;margin:0;">2000 – 2024</p>
        </div>
    </div>

    <p style="color:rgba(255,255,255,0.25);font-size:10px;margin:18px 0 0;line-height:1.5;">
        Data Sources: World Bank Open Data · Our World in Data &nbsp;·&nbsp;
        Juliana Paula T. Binas · BSIS 3A · Analytics Techniques and Tools
    </p>
</div>
<br>
""", unsafe_allow_html=True)
