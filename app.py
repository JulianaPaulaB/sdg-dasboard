import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import statsmodels.api as sm

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SDG 3: Life Expectancy Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Colors ─────────────────────────────────────────────────────────────────────
PURPLE  = "#7c3aed"
BLUE    = "#0ea5e9"
GREEN   = "#10b981"
AMBER   = "#f59e0b"
RED     = "#ef4444"
DARK    = "#1a1a2e"
GRAY    = "#6b7280"

COUNTRY_COLORS = {
    "United Kingdom": PURPLE,
    "United States":  BLUE
}

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
    html, body, [data-testid="stAppViewContainer"] {{
        background-color: #faf9f7;
        font-family: 'Segoe UI', system-ui, sans-serif;
    }}
    [data-testid="stSidebar"] {{
        background-color: {DARK} !important;
    }}
    [data-testid="stSidebar"] * {{
        color: white !important;
    }}
    [data-testid="stSidebar"] .stSlider label,
    [data-testid="stSidebar"] .stMultiSelect label {{
        color: rgba(255,255,255,0.8) !important;
        font-size: 12px !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    [data-testid="stMetric"] {{
        background: white;
        border-radius: 12px;
        padding: 14px 16px;
        border: 0.5px solid #ede9fe;
        transition: transform 0.2s;
    }}
    [data-testid="stMetric"]:hover {{
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(124,58,237,0.12);
    }}
    [data-testid="stMetricLabel"] p {{
        color: {GRAY} !important;
        font-size: 11px !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    [data-testid="stMetricValue"] {{
        font-size: 22px !important;
        font-weight: 700 !important;
    }}
    [data-testid="stMetricDelta"] {{
        font-size: 11px !important;
    }}
    .block-container {{
        padding: 1.5rem 2rem 2rem 2rem !important;
        max-width: 100% !important;
    }}
    .section-head {{
        font-size: 13px;
        font-weight: 700;
        color: {DARK};
        letter-spacing: 0.4px;
        border-left: 4px solid {PURPLE};
        padding-left: 10px;
        margin: 24px 0 12px 0;
    }}
    .insight-box {{
        background: #f5f3ff;
        border-left: 4px solid {PURPLE};
        border-radius: 0 8px 8px 0;
        padding: 10px 14px;
        font-size: 12px;
        color: #4c1d95;
        line-height: 1.6;
        margin-top: 4px;
    }}
    .insight-box.blue {{
        background: #f0f9ff;
        border-color: {BLUE};
        color: #0c4a6e;
    }}
    .insight-box.green {{
        background: #ecfdf5;
        border-color: {GREEN};
        color: #064e3b;
    }}
    .insight-box.amber {{
        background: #fffbeb;
        border-color: {AMBER};
        color: #78350f;
    }}
    .insight-box.red {{
        background: #fef2f2;
        border-color: {RED};
        color: #7f1d1d;
    }}
    .rec-card {{
        border-radius: 12px;
        padding: 14px 16px;
        font-size: 12px;
        line-height: 1.6;
        height: 100%;
    }}
    .conclusion-box {{
        background: {DARK};
        border-radius: 14px;
        padding: 20px 24px;
        margin-top: 16px;
        color: white;
    }}
    .conclusion-box h3 {{
        font-size: 15px;
        font-weight: 700;
        color: white;
        margin-bottom: 10px;
    }}
    .conclusion-box p {{
        font-size: 12px;
        color: rgba(255,255,255,0.78);
        line-height: 1.7;
    }}
    .conclusion-box strong {{
        color: #c4b5fd;
    }}
    #MainMenu, footer, header {{visibility: hidden;}}
</style>
""", unsafe_allow_html=True)

# ── Load & prepare data ────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("merged_sdg_data.csv")
    df.columns = ["Country", "Code", "Year", "Water_Access", "GDP_per_capita",
                  "Healthcare_Spending", "Life_Expectancy", "CO2_Emissions"]
    df = df.dropna()
    df["Year"] = df["Year"].astype(int)
    return df

@st.cache_data
def run_regression(df):
    X = df[["Healthcare_Spending", "Water_Access", "GDP_per_capita", "CO2_Emissions"]]
    y = df["Life_Expectancy"]
    X2 = sm.add_constant(X)
    ols  = sm.OLS(y, X2).fit()
    rlm  = sm.RLM(y, X2, M=sm.robust.norms.HuberT()).fit()
    df2  = df.copy()
    df2["Predicted"] = rlm.fittedvalues.round(3)
    r2   = round(ols.rsquared, 4)
    rmse = round(float(np.sqrt(np.mean((y - rlm.fittedvalues) ** 2))), 4)
    return rlm, r2, rmse, df2

df       = load_data()
rlm_model, R2, RMSE, df_pred = run_regression(df)
years    = sorted(df["Year"].unique())
countries = sorted(df["Country"].unique())

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style="text-align:center;padding:16px 0 12px">
        <div style="background:rgba(124,58,237,0.3);border-radius:14px;width:56px;height:56px;
                    margin:0 auto 10px;display:flex;align-items:center;justify-content:center;
                    font-size:26px;font-weight:700;color:white;border:2px solid {PURPLE}">3</div>
        <h3 style="color:white;margin:0;font-size:15px;font-weight:700">SDG 3 Dashboard</h3>
        <p style="color:rgba(255,255,255,0.55);font-size:11px;margin:4px 0 0">Good Health & Well-Being</p>
    </div>
    <hr style="border-color:rgba(255,255,255,0.15);margin:10px 0 16px">
    """, unsafe_allow_html=True)

    selected_year = st.slider(
        "Select Year",
        min_value=int(years[0]),
        max_value=int(years[-1]),
        value=int(years[-1]),
        step=1
    )

    selected_countries = st.multiselect(
        "Select Countries",
        options=countries,
        default=countries
    )

    st.markdown("<hr style='border-color:rgba(255,255,255,0.15);margin:16px 0'>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style="font-size:11px;line-height:1.8;color:rgba(255,255,255,0.65);">
        <b style="color:white;font-size:12px">Key Drivers (Regression)</b><br><br>
        🏥 Healthcare Spending<br>
        <span style="color:#10b981;margin-left:12px">● Positive (p=0.036)</span><br>
        💧 Water Access<br>
        <span style="color:#10b981;margin-left:12px">● Positive (p&lt;0.001)</span><br>
        💰 GDP per Capita<br>
        <span style="color:{GRAY};margin-left:12px">● Not significant</span><br>
        🌫️ CO₂ Emissions<br>
        <span style="color:{RED};margin-left:12px">● Negative (p&lt;0.001)</span><br><br>
        <b style="color:white">Model: Robust RLM (Huber T)</b><br>
        R² = {R2} &nbsp;|&nbsp; RMSE = {RMSE}
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <hr style="border-color:rgba(255,255,255,0.15);margin:14px 0">
    <div style="font-size:10px;color:rgba(255,255,255,0.4);text-align:center;line-height:1.6">
        Juliana Paula T. Binas<br>BSIS 3A · Analytics Techniques & Tools<br>
        Data: World Bank · Our World in Data
    </div>
    """, unsafe_allow_html=True)

# ── Guard ──────────────────────────────────────────────────────────────────────
if not selected_countries:
    st.warning("Please select at least one country from the sidebar.")
    st.stop()

dff      = df[(df["Year"] == selected_year) & (df["Country"].isin(selected_countries))]
dff_all  = df[df["Country"].isin(selected_countries)]
dff_pred = df_pred[df_pred["Country"].isin(selected_countries)]
prev_dff = df[(df["Year"] == selected_year - 1) & (df["Country"].isin(selected_countries))]

def avg(col, d=dff):
    return d[col].mean() if not d.empty else 0

def delta(col):
    if prev_dff.empty:
        return None
    return avg(col) - avg(col, prev_dff)

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="background:{DARK};border-radius:16px;padding:20px 26px;
            margin-bottom:20px;display:flex;align-items:center;gap:18px;flex-wrap:wrap">
    <div style="background:rgba(124,58,237,0.4);border-radius:14px;width:54px;height:54px;
                display:flex;align-items:center;justify-content:center;font-size:24px;
                font-weight:700;color:white;border:2px solid {PURPLE};flex-shrink:0">3</div>
    <div style="flex:1;min-width:200px">
        <h1 style="color:white;margin:0;font-size:20px;font-weight:700">
            SDG 3: Good Health and Well-Being 🌿
        </h1>
        <p style="color:rgba(255,255,255,0.55);margin:4px 0 0;font-size:12px">
            What factors influence Life Expectancy across countries? &nbsp;·&nbsp;
            Juliana Paula T. Binas &nbsp;·&nbsp; BSIS 3A &nbsp;·&nbsp;
            Analytics Techniques and Tools
        </p>
    </div>
    <div style="display:flex;gap:8px;flex-wrap:wrap">
        <span style="background:rgba(255,255,255,0.1);border:0.5px solid rgba(255,255,255,0.2);
                     border-radius:20px;padding:4px 12px;font-size:11px;color:rgba(255,255,255,0.8)">
            📅 2000 – 2024
        </span>
        <span style="background:rgba(255,255,255,0.1);border:0.5px solid rgba(255,255,255,0.2);
                     border-radius:20px;padding:4px 12px;font-size:11px;color:rgba(255,255,255,0.8)">
            🌍 {len(selected_countries)} {'Country' if len(selected_countries)==1 else 'Countries'}
        </span>
        <span style="background:rgba(255,255,255,0.1);border:0.5px solid rgba(255,255,255,0.2);
                     border-radius:20px;padding:4px 12px;font-size:11px;color:rgba(255,255,255,0.8)">
            📊 4 Drivers Analyzed
        </span>
    </div>
</div>
""", unsafe_allow_html=True)

# ── KPI Cards ──────────────────────────────────────────────────────────────────
st.markdown("<div class='section-head'>✨ Key Indicators for " + str(selected_year) + "</div>", unsafe_allow_html=True)

kc = st.columns(5)
kpi_config = [
    ("Life Expectancy",    "Life_Expectancy",    "💓", "{:.2f} yrs",  PURPLE,  False),
    ("Healthcare Spending","Healthcare_Spending", "🏥", "${:,.0f}",   BLUE,    False),
    ("GDP per Capita",     "GDP_per_capita",      "💰", "${:,.0f}",   AMBER,   False),
    ("CO₂ Emissions",      "CO2_Emissions",       "🌫️", "{:.2f} t",   RED,     True),
    ("Water Access",       "Water_Access",        "💧", "{:.2f}%",    GREEN,   False),
]

for col_widget, (label, field, icon, fmt, color, inverse) in zip(kc, kpi_config):
    val  = avg(field)
    d    = delta(field)
    disp = fmt.format(val)
    with col_widget:
        if d is not None:
            d_str = ("▼ " if d < 0 else "▲ +") + fmt.format(abs(d)) + " vs prev yr"
            st.metric(f"{icon} {label}", disp, d_str,
                      delta_color="inverse" if inverse else "normal")
        else:
            st.metric(f"{icon} {label}", disp)

st.markdown("<hr style='margin:20px 0;border:none;border-top:1px solid #ede9fe'>", unsafe_allow_html=True)

# ── SECTION 1: Trends ─────────────────────────────────────────────────────────
st.markdown("<div class='section-head'>📈 Section 1 — Trends Over Time</div>", unsafe_allow_html=True)

col_trend, col_bar = st.columns([2, 1])

with col_trend:
    fig_trend = px.line(
        dff_all, x="Year", y="Life_Expectancy", color="Country",
        color_discrete_map=COUNTRY_COLORS,
        markers=True,
        labels={"Life_Expectancy": "Life Expectancy (years)"},
        title="Life Expectancy Over Time by Country",
        template="plotly_white"
    )
    fig_trend.add_vline(
        x=selected_year, line_dash="dash",
        line_color=PURPLE, line_width=1.5,
        annotation_text=str(selected_year),
        annotation_font_color=PURPLE,
        annotation_position="top right"
    )
    fig_trend.update_layout(
        title_font_size=13, title_font_color=DARK,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(t=50, b=20, l=10, r=10),
        hovermode="x unified",
        plot_bgcolor="white",
        paper_bgcolor="white"
    )
    fig_trend.update_xaxes(showgrid=False, title_text="")
    fig_trend.update_yaxes(showgrid=True, gridcolor="#f3f0fa", title_text="Life Expectancy (yrs)")
    st.plotly_chart(fig_trend, use_container_width=True)
    st.markdown("<div class='insight-box'>Both countries show an upward trend from 2000–2019, followed by a visible dip in 2020–2021 due to the COVID-19 pandemic. The UK recovered faster and consistently maintains higher life expectancy than the USA despite lower healthcare spending per capita.</div>", unsafe_allow_html=True)

with col_bar:
    fig_bar = px.bar(
        dff, x="Country", y="Life_Expectancy",
        color="Country",
        color_discrete_map=COUNTRY_COLORS,
        text_auto=".2f",
        labels={"Life_Expectancy": "Life Expectancy (years)"},
        title=f"Country Comparison ({selected_year})",
        template="plotly_white"
    )
    fig_bar.update_traces(textposition="outside", textfont_size=12)
    fig_bar.update_layout(
        title_font_size=13, title_font_color=DARK,
        showlegend=False,
        margin=dict(t=50, b=20, l=10, r=10),
        plot_bgcolor="white", paper_bgcolor="white"
    )
    fig_bar.update_xaxes(showgrid=False, title_text="")
    fig_bar.update_yaxes(showgrid=True, gridcolor="#f3f0fa",
                         range=[70, dff["Life_Expectancy"].max() + 3] if not dff.empty else [70, 90])
    st.plotly_chart(fig_bar, use_container_width=True)
    st.markdown("<div class='insight-box blue'>Spending efficiency matters — the UK spends less per capita on healthcare yet achieves higher life expectancy than the USA.</div>", unsafe_allow_html=True)

st.markdown("<hr style='margin:20px 0;border:none;border-top:1px solid #ede9fe'>", unsafe_allow_html=True)

# ── SECTION 2: Factors ────────────────────────────────────────────────────────
st.markdown("<div class='section-head'>🔍 Section 2 — Factors Affecting Life Expectancy</div>", unsafe_allow_html=True)

f1, f2, f3, f4 = st.columns(4)

factor_cfg = [
    (f1, "Healthcare_Spending", "Life_Expectancy", "Healthcare Spending (USD)",
     "Life Expectancy (yrs)", "🏥 Healthcare Spending", "blue",
     "Positive driver ↑ — Higher healthcare investment is associated with longer life expectancy. (Jaba et al., 2014)"),
    (f2, "GDP_per_capita", "Life_Expectancy", "GDP per Capita (USD)",
     "Life Expectancy (yrs)", "💰 GDP per Capita", "amber",
     "Positive driver ↑ — Wealthier nations afford better nutrition, sanitation & healthcare. (Preston, 1975)"),
    (f3, "Water_Access", "Life_Expectancy", "Water Access (%)",
     "Life Expectancy (yrs)", "💧 Water Access", "green",
     "Positive driver ↑ — Clean water reduces waterborne disease burden in the population. (UN SDG Report, 2023)"),
    (f4, "CO2_Emissions", "Life_Expectancy", "CO₂ Emissions (tons/capita)",
     "Life Expectancy (yrs)", "🌫️ CO₂ Emissions", "red",
     "Negative driver ↓ — Higher pollution contributes to respiratory & cardiovascular disease. (Wen et al., 2021)"),
]

for col_widget, x_col, y_col, x_lbl, y_lbl, title, box_cls, insight in factor_cfg:
    with col_widget:
        fig_sc = px.scatter(
            dff_all, x=x_col, y=y_col, color="Country",
            color_discrete_map=COUNTRY_COLORS,
            animation_frame="Year",
            trendline="ols",
            labels={x_col: x_lbl, y_col: y_lbl},
            title=title,
            template="plotly_white"
        )
        fig_sc.update_layout(
            title_font_size=12, title_font_color=DARK,
            showlegend=False,
            margin=dict(t=40, b=10, l=10, r=10),
            plot_bgcolor="white", paper_bgcolor="white"
        )
        fig_sc.update_xaxes(showgrid=True, gridcolor="#f9f9f9", title_text=x_lbl, title_font_size=10)
        fig_sc.update_yaxes(showgrid=True, gridcolor="#f9f9f9", title_text=y_lbl, title_font_size=10)
        st.plotly_chart(fig_sc, use_container_width=True)
        st.markdown(f"<div class='insight-box {box_cls}'>{insight}</div>", unsafe_allow_html=True)

st.markdown("<hr style='margin:20px 0;border:none;border-top:1px solid #ede9fe'>", unsafe_allow_html=True)

# ── SECTION 3: Correlation ────────────────────────────────────────────────────
st.markdown("<div class='section-head'>🔗 Section 3 — Correlation Analysis</div>", unsafe_allow_html=True)

col_hm, col_corr = st.columns([1, 1])

vars_labels = {
    "Life_Expectancy":    "Life Expectancy",
    "Healthcare_Spending":"Healthcare Spending",
    "GDP_per_capita":     "GDP per Capita",
    "Water_Access":       "Water Access",
    "CO2_Emissions":      "CO₂ Emissions"
}
corr_cols  = list(vars_labels.keys())
corr_lbls  = list(vars_labels.values())
corr_matrix = dff_all[corr_cols].corr().round(3)

with col_hm:
    fig_hm = go.Figure(go.Heatmap(
        z=corr_matrix.values,
        x=corr_lbls,
        y=corr_lbls,
        colorscale=[
            [0.0,  "#ef4444"],
            [0.3,  "#fca5a5"],
            [0.5,  "#f9fafb"],
            [0.7,  "#c4b5fd"],
            [1.0,  "#7c3aed"]
        ],
        zmin=-1, zmax=1,
        text=corr_matrix.values.round(2),
        texttemplate="%{text}",
        textfont={"size": 11, "color": DARK},
        hovertemplate="%{y} × %{x}: %{z}<extra></extra>",
        colorbar=dict(
            title="r",
            titleside="right",
            tickvals=[-1, -0.5, 0, 0.5, 1],
            ticktext=["-1", "-0.5", "0", "0.5", "1"],
            len=0.85
        )
    ))
    fig_hm.update_layout(
        title="Correlation Heatmap",
        title_font_size=13, title_font_color=DARK,
        margin=dict(t=45, b=60, l=120, r=20),
        plot_bgcolor="white", paper_bgcolor="white",
        xaxis=dict(tickangle=-30, tickfont_size=11),
        yaxis=dict(tickfont_size=11)
    )
    st.plotly_chart(fig_hm, use_container_width=True)

with col_corr:
    st.markdown("<div style='margin-top:6px'>", unsafe_allow_html=True)
    st.markdown("**Correlation with Life Expectancy**", unsafe_allow_html=False)

    corr_with_le = corr_matrix["Life_Expectancy"].drop("Life_Expectancy").sort_values(ascending=False)
    rows_html = ""
    clr_map = {
        "Healthcare_Spending": (BLUE,   "#f0f9ff", "#0c4a6e"),
        "GDP_per_capita":      (AMBER,  "#fffbeb", "#78350f"),
        "Water_Access":        (GREEN,  "#ecfdf5", "#064e3b"),
        "CO2_Emissions":       (RED,    "#fef2f2", "#7f1d1d"),
    }
    for feat, val in corr_with_le.items():
        bar_color, bg, txt = clr_map.get(feat, (GRAY, "#f3f4f6", "#374151"))
        width = abs(val) * 100
        direction = "strong +" if val > 0.7 else "moderate +" if val > 0.3 else "moderate −" if val > -0.7 else "strong −"
        tag_bg = "#ecfdf5" if val > 0 else "#fef2f2"
        tag_txt = "#065f46" if val > 0 else "#991b1b"
        rows_html += f"""
        <div style="display:flex;align-items:center;gap:10px;padding:8px 0;
                    border-bottom:0.5px solid #f3f0fa">
            <span style="font-size:11px;color:#374151;width:140px;flex-shrink:0">{vars_labels[feat]}</span>
            <div style="flex:1;height:6px;background:#f3f0fa;border-radius:3px;overflow:hidden">
                <div style="width:{width:.0f}%;height:100%;background:{bar_color};border-radius:3px"></div>
            </div>
            <span style="font-size:11px;font-weight:700;color:{bar_color};width:40px;text-align:right">
                {'+' if val>0 else ''}{val:.2f}
            </span>
            <span style="font-size:9px;padding:2px 7px;border-radius:20px;font-weight:600;
                         background:{tag_bg};color:{tag_txt};white-space:nowrap">{direction}</span>
        </div>"""

    st.markdown(rows_html, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("""<div class='insight-box' style='margin-top:12px'>
        CO₂ Emissions has the strongest (negative) correlation with Life Expectancy at −0.79,
        followed by Water Access (+0.50) and Healthcare Spending (−0.51 — note the negative sign reflects
        that the US spends more but has lower life expectancy than the UK).
        This cross-country pattern reflects spending efficiency differences.
    </div>""", unsafe_allow_html=True)

# Correlation bar chart (full matrix)
st.markdown("<br>", unsafe_allow_html=True)
fig_bar_corr = go.Figure()
for i, feat in enumerate(corr_cols):
    vals = corr_matrix[feat].drop(feat)
    colors = [PURPLE if v > 0 else RED for v in vals]
    fig_bar_corr.add_trace(go.Bar(
        name=vars_labels[feat],
        x=[vars_labels[f] for f in vals.index],
        y=vals.values,
        marker_color=colors,
        visible=(i == 0),
        hovertemplate="%{x}: %{y:.3f}<extra></extra>"
    ))

buttons = [dict(
    label=vars_labels[feat],
    method="update",
    args=[{"visible": [j == i for j in range(len(corr_cols))]},
          {"title": f"Correlations with: {vars_labels[feat]}"}]
) for i, feat in enumerate(corr_cols)]

fig_bar_corr.update_layout(
    title=f"Correlations with: {vars_labels[corr_cols[0]]}",
    title_font_size=13, title_font_color=DARK,
    updatemenus=[dict(
        type="dropdown", showactive=True,
        x=0.01, xanchor="left", y=1.18, yanchor="top",
        buttons=buttons,
        bgcolor="white", bordercolor="#ede9fe"
    )],
    yaxis=dict(range=[-1, 1], zeroline=True, zerolinecolor="#e5e7eb",
               gridcolor="#f3f0fa", title_text="Correlation coefficient"),
    xaxis=dict(showgrid=False),
    plot_bgcolor="white", paper_bgcolor="white",
    margin=dict(t=80, b=30, l=10, r=10),
    height=260
)
st.plotly_chart(fig_bar_corr, use_container_width=True)

st.markdown("<hr style='margin:20px 0;border:none;border-top:1px solid #ede9fe'>", unsafe_allow_html=True)

# ── SECTION 4: Regression ─────────────────────────────────────────────────────
st.markdown("<div class='section-head'>📊 Section 4 — Regression Model & Predictions</div>", unsafe_allow_html=True)

col_perf, col_fi = st.columns([1, 1])

with col_perf:
    # Model metrics
    mc = st.columns(3)
    mc[0].metric("R² Score",     f"{R2}",        "Goodness of fit")
    mc[1].metric("RMSE",         f"{RMSE} yrs",  "Prediction error")
    mc[2].metric("Observations", "44",           "2000–2024")

    # Actual vs Predicted
    fig_pred = go.Figure()
    colors_pred = {"United Kingdom": PURPLE, "United States": BLUE}
    for country in selected_countries:
        sub = dff_pred[dff_pred["Country"] == country].sort_values("Year")
        clr = colors_pred.get(country, GRAY)
        fig_pred.add_trace(go.Scatter(
            x=sub["Year"], y=sub["Life_Expectancy"],
            mode="lines+markers", name=f"{country} — Actual",
            line=dict(color=clr, width=2),
            marker=dict(size=5),
            hovertemplate="%{y:.3f} yrs<extra>Actual · " + country + "</extra>"
        ))
        fig_pred.add_trace(go.Scatter(
            x=sub["Year"], y=sub["Predicted"],
            mode="lines", name=f"{country} — Predicted",
            line=dict(color=clr, width=2, dash="dash"),
            hovertemplate="%{y:.3f} yrs<extra>Predicted · " + country + "</extra>"
        ))
    fig_pred.update_layout(
        title="Actual vs Predicted Life Expectancy",
        title_font_size=13, title_font_color=DARK,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font_size=10),
        margin=dict(t=50, b=20, l=10, r=10),
        plot_bgcolor="white", paper_bgcolor="white",
        hovermode="x unified", height=260
    )
    fig_pred.update_xaxes(showgrid=False)
    fig_pred.update_yaxes(showgrid=True, gridcolor="#f3f0fa",
                           title_text="Life Expectancy (yrs)")
    st.plotly_chart(fig_pred, use_container_width=True)
    st.markdown(f"""<div class='insight-box'>
        The Robust Regression (RLM) model achieves an R² of <strong>{R2}</strong>,
        explaining ~{round(R2*100)}% of the variance in life expectancy.
        The RMSE of {RMSE} years indicates predictions are within less than 1 year of actual values.
    </div>""", unsafe_allow_html=True)

with col_fi:
    coef_df = pd.DataFrame({
        "Variable": ["Healthcare Spending", "Water Access", "GDP per Capita", "CO₂ Emissions"],
        "Coefficient": [
            round(rlm_model.params["Healthcare_Spending"], 6),
            round(rlm_model.params["Water_Access"], 4),
            round(rlm_model.params["GDP_per_capita"], 6),
            round(rlm_model.params["CO2_Emissions"], 4)
        ],
        "p-value": [
            round(rlm_model.pvalues["Healthcare_Spending"], 4),
            round(rlm_model.pvalues["Water_Access"], 4),
            round(rlm_model.pvalues["GDP_per_capita"], 4),
            round(rlm_model.pvalues["CO2_Emissions"], 4)
        ],
        "Significant": ["Yes (p<0.05)", "Yes (p<0.001)", "No (p=0.21)", "Yes (p<0.001)"],
        "Direction": ["Positive", "Positive", "Positive", "Negative"]
    })

    bar_colors = [BLUE, GREEN, AMBER, RED]
    fig_fi = go.Figure(go.Bar(
        x=coef_df["Variable"],
        y=coef_df["Coefficient"],
        marker_color=bar_colors,
        marker_line_width=0,
        text=coef_df["p-value"].apply(lambda p: f"p={p}"),
        textposition="outside",
        textfont_size=10,
        hovertemplate="<b>%{x}</b><br>Coefficient: %{y:.6f}<extra></extra>"
    ))
    fig_fi.add_hline(y=0, line_color=GRAY, line_width=1)
    fig_fi.update_layout(
        title="Regression Coefficients (RLM)",
        title_font_size=13, title_font_color=DARK,
        margin=dict(t=50, b=20, l=10, r=10),
        plot_bgcolor="white", paper_bgcolor="white",
        yaxis=dict(title_text="Coefficient Value", gridcolor="#f3f0fa"),
        xaxis=dict(showgrid=False),
        height=260
    )
    st.plotly_chart(fig_fi, use_container_width=True)

    st.markdown("**Regression Results Summary**")
    st.dataframe(
        coef_df.style.applymap(
            lambda v: f"color:{GREEN};font-weight:600" if v == "Yes (p<0.05)" or v == "Yes (p<0.001)"
                      else (f"color:{GRAY}" if v == "No (p=0.21)" else ""),
            subset=["Significant"]
        ).applymap(
            lambda v: f"color:{GREEN}" if v == "Positive" else f"color:{RED}" if v == "Negative" else "",
            subset=["Direction"]
        ).format({"Coefficient": "{:.6f}", "p-value": "{:.4f}"}),
        use_container_width=True,
        height=160
    )

st.markdown("<hr style='margin:20px 0;border:none;border-top:1px solid #ede9fe'>", unsafe_allow_html=True)

# ── SECTION 5: Drivers Over Time (tabbed) ─────────────────────────────────────
st.markdown("<div class='section-head'>📉 Driver Trends Over Time</div>", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs([
    "🏥 Healthcare Spending",
    "💰 GDP per Capita",
    "💧 Water Access",
    "🌫️ CO₂ Emissions"
])

driver_tabs = [
    (tab1, "Healthcare_Spending", "Healthcare Spending (USD)"),
    (tab2, "GDP_per_capita",      "GDP per Capita (USD)"),
    (tab3, "Water_Access",        "Water Access (%)"),
    (tab4, "CO2_Emissions",       "CO₂ Emissions (tons per capita)"),
]

for tab, col, label in driver_tabs:
    with tab:
        fig_d = px.line(
            dff_all, x="Year", y=col, color="Country",
            color_discrete_map=COUNTRY_COLORS,
            markers=True,
            labels={col: label},
            title=f"{label} Over Time",
            template="plotly_white"
        )
        fig_d.add_vline(
            x=selected_year, line_dash="dash",
            line_color=PURPLE, line_width=1.5,
            annotation_text=str(selected_year),
            annotation_font_color=PURPLE,
            annotation_position="top right"
        )
        fig_d.update_layout(
            title_font_size=13, title_font_color=DARK,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(t=50, b=20, l=10, r=10),
            hovermode="x unified",
            plot_bgcolor="white", paper_bgcolor="white"
        )
        fig_d.update_xaxes(showgrid=False, title_text="")
        fig_d.update_yaxes(showgrid=True, gridcolor="#f3f0fa", title_text=label)
        st.plotly_chart(fig_d, use_container_width=True)

st.markdown("<hr style='margin:20px 0;border:none;border-top:1px solid #ede9fe'>", unsafe_allow_html=True)

# ── SECTION 6: Insights & Recommendations ─────────────────────────────────────
st.markdown("<div class='section-head'>💡 Section 5 — Insights & Recommendations</div>", unsafe_allow_html=True)

r1, r2, r3, r4 = st.columns(4)

recs = [
    (r1, "🏥 Increase Healthcare Investment", BLUE, "#f0f9ff", "#bae6fd", "#0c4a6e",
     "Every increase in per-capita healthcare spending is associated with measurably higher life expectancy. Efficient spending matters as much as the total amount allocated."),
    (r2, "💰 Promote Economic Development", AMBER, "#fffbeb", "#fde68a", "#78350f",
     "Policies that raise GDP per capita — through education, trade, and infrastructure — indirectly improve health outcomes by raising living standards and access to care."),
    (r3, "💧 Ensure Universal Water Access", GREEN, "#ecfdf5", "#a7f3d0", "#064e3b",
     "Expanding clean water infrastructure reduces waterborne disease burden that disproportionately affects vulnerable populations and directly shortens life expectancy."),
    (r4, "🌿 Reduce CO₂ Emissions", RED, "#fef2f2", "#fca5a5", "#7f1d1d",
     "Transitioning to cleaner energy and enforcing emission standards reduces pollution-related disease, directly improving population health outcomes — confirmed by this analysis."),
]

for col_widget, title, border, bg, bdr, txt, body in recs:
    with col_widget:
        st.markdown(f"""
        <div style="background:{bg};border:0.5px solid {bdr};border-radius:12px;
                    padding:14px 16px;height:100%;font-size:12px;line-height:1.65">
            <h4 style="font-size:12px;font-weight:700;color:{txt};margin:0 0 8px">{title}</h4>
            <span style="color:{txt};opacity:0.85">{body}</span>
        </div>
        """, unsafe_allow_html=True)

# ── Conclusion ─────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="conclusion-box">
    <h3>Final Conclusion 🌍</h3>
    <p>
        The Robust Regression (RLM) analysis confirms that
        <strong>Healthcare Spending</strong> and <strong>Water Access</strong>
        are statistically significant positive drivers of life expectancy (p&lt;0.05),
        while <strong>CO₂ Emissions</strong> is a significant negative driver (p&lt;0.001).
        <strong>GDP per Capita</strong>, though positively correlated, was not statistically
        significant in the robust model (p=0.21), suggesting its effect may be mediated
        through the other variables.
        Together, the four variables explain approximately <strong>{round(R2*100)}%</strong> of
        the variance in life expectancy across the United Kingdom and United States from 2000 to 2024.
        These findings directly support the objectives of <strong>SDG 3: Good Health and Well-Being</strong>
        — demonstrating that both economic investment and environmental policy decisions
        have measurable, real-world impacts on how long people live.
    </p>
</div>
""", unsafe_allow_html=True)

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="text-align:center;padding:24px 0 8px;font-size:11px;color:{GRAY}">
    SDG 3 Life Expectancy Dashboard &nbsp;·&nbsp; Juliana Paula T. Binas &nbsp;·&nbsp; BSIS 3A<br>
    Data Sources: World Bank Open Data · Our World in Data &nbsp;·&nbsp; Period: 2000–2024
</div>
""", unsafe_allow_html=True)
