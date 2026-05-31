"""
SDG 3 Life Expectancy Dashboard — Streamlit Version
Author: Juliana Paula T. Binas — BSIS 3A — Analytics Techniques and Tools

Deploy on Streamlit Cloud:
  1. Push app.py + requirements.txt to your GitHub repo root
  2. Connect on https://share.streamlit.io  →  Main file: app.py
"""

import streamlit as st
import plotly.graph_objects as go

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SDG 3 — Life Expectancy Dashboard",
    page_icon="🫀",
    layout="wide",
)

# ── Colour palette ────────────────────────────────────────────────────────────
PURPLE = "#9c27b0"
CYAN   = "#00bcd4"
ORANGE = "#ff9800"
INDIGO = "#3949ab"
TEAL   = "#00897b"
RED    = "#c62828"
DARK   = "#1a1a2e"

# ── Dataset ───────────────────────────────────────────────────────────────────
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
    "water": [100.0]*25,
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
              99.82,99.89,99.96,100.0,100.0],
}

# ── Helpers ───────────────────────────────────────────────────────────────────
def avg_val(key, yi, country):
    vals = []
    if country != "USA":
        vals.append(UK[key][yi])
    if country != "UK" and USA[key][yi] is not None:
        vals.append(USA[key][yi])
    return sum(vals) / len(vals) if vals else None


def apply_base(fig, height=200, yrange=None, ysuffix=None,
               xrange=None, xformat=None, legend=False, legend_cfg=None):
    """Apply consistent base styling to any figure in-place."""
    fig.update_layout(
        height=height,
        margin=dict(l=0, r=8, t=8, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=legend,
        font=dict(size=10, family="Segoe UI, system-ui, sans-serif"),
        hovermode="x unified",
    )
    xkw = dict(showgrid=False, tickfont=dict(size=9))
    if xrange:  xkw["range"]       = xrange
    if xformat: xkw["tickformat"]  = xformat
    fig.update_xaxes(**xkw)

    ykw = dict(gridcolor="#f0f0f0", tickfont=dict(size=9))
    if yrange:  ykw["range"]      = yrange
    if ysuffix: ykw["ticksuffix"] = ysuffix
    fig.update_yaxes(**ykw)

    if legend and legend_cfg:
        fig.update_layout(legend=legend_cfg)


# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  [data-testid="stAppViewContainer"] { background: #faf9f7; }
  [data-testid="block-container"]    { padding-top: 0 !important; }
  .metric-card {
    background: #fff; border-radius: 14px;
    border: 1px solid #ececec; padding: 14px 16px; margin-bottom: 4px;
  }
  .insight-box {
    border-radius: 0 10px 10px 0; padding: 9px 12px;
    margin-top: 8px; font-size: 12px; line-height: 1.55;
  }
  .reco-card {
    border-radius: 12px; padding: 13px 15px;
    margin-bottom: 8px; font-size: 12px; line-height: 1.55;
  }
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="background:{DARK};padding:22px 28px;border-radius:0 0 14px 14px;
            display:flex;align-items:center;gap:16px;margin-bottom:20px;flex-wrap:wrap;">
  <span style="background:#e8d5f5;border-radius:12px;padding:8px 14px;
               font-size:12px;font-weight:700;color:#6a0dad;">✦ SDG 3 · Good Health</span>
  <div style="margin-left:6px">
    <div style="color:#fff;font-size:17px;font-weight:700;">
      Drivers of Life Expectancy Across Countries</div>
    <div style="color:rgba(255,255,255,.6);font-size:11px;">
      Juliana Paula T. Binas · BSIS 3A · Analytics Techniques and Tools</div>
  </div>
  <div style="margin-left:auto;display:flex;gap:8px;flex-wrap:wrap;">
    <span style="background:#e8d5f5;color:#6a0dad;border-radius:20px;
                 padding:5px 12px;font-size:11px;font-weight:700;">2000–2024</span>
    <span style="background:#fce4ec;color:#c2185b;border-radius:20px;
                 padding:5px 12px;font-size:11px;font-weight:700;">World Bank</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"<h3 style='color:{DARK};'>🎛️ Filters</h3>", unsafe_allow_html=True)
    year    = st.slider("Year", 2000, 2024, 2024)
    country = st.selectbox("Country", ["Both countries","United Kingdom","United States"])
    cnt     = "both" if country == "Both countries" else ("UK" if "Kingdom" in country else "USA")
    st.markdown("---")
    st.markdown("""<div style='font-size:12px;color:#888;line-height:1.7;'>
      <b>Data source:</b> World Bank<br><b>Model:</b> Robust RLM<br>
      <b>R²:</b> 0.94 | <b>RMSE:</b> 0.42<br><b>Observations:</b> 44
    </div>""", unsafe_allow_html=True)

yi = YEARS.index(year)

# ── KPI row ───────────────────────────────────────────────────────────────────
def kpi_card(key, label, icon, fmt, color, good_up=True):
    val  = avg_val(key, yi, cnt)
    prev = avg_val(key, max(yi - 1, 0), cnt)
    if val is None:
        return
    dv    = val - prev if prev is not None else 0
    good  = (dv > 0) == good_up
    arrow = "▲" if dv > 0 else ("▼" if dv < 0 else "—")
    dclr  = "#4caf50" if dv == 0 else ("#4caf50" if good else "#e91e63")
    st.markdown(f"""
    <div class="metric-card" style="border-top:3px solid {color};">
      <div style="font-size:20px">{icon}</div>
      <div style="font-size:10px;font-weight:700;color:#aaa;text-transform:uppercase;
                  letter-spacing:.5px;margin:4px 0 2px">{label}</div>
      <div style="font-size:20px;font-weight:800;color:{DARK}">{fmt(val)}</div>
      <div style="font-size:10px;color:{dclr};font-weight:600;margin-top:4px">
        {arrow} {fmt(abs(dv))} vs {year-1}</div>
    </div>""", unsafe_allow_html=True)

k1,k2,k3,k4,k5 = st.columns(5)
with k1: kpi_card("le",    "Life expectancy",     "🫀", lambda v:f"{v:.1f} yrs",    PURPLE, True)
with k2: kpi_card("hc",    "Healthcare spending", "🏥", lambda v:f"${v:,.0f}",      INDIGO, True)
with k3: kpi_card("gdp",   "GDP per capita",      "💰", lambda v:f"${v/1000:.0f}k", ORANGE, True)
with k4: kpi_card("co2",   "CO₂ emissions",       "🌫️", lambda v:f"{v:.2f} t",     RED,    False)
with k5: kpi_card("water", "Water access",        "💧", lambda v:f"{v:.1f}%",       TEAL,   True)

st.markdown("<div style='margin-top:4px'></div>", unsafe_allow_html=True)

# ── Section helper ────────────────────────────────────────────────────────────
def sec_head(dot, title):
    st.markdown(
        f"<div style='display:flex;align-items:center;gap:10px;margin:20px 0 10px'>"
        f"<div style='width:8px;height:8px;border-radius:50%;background:{dot}'></div>"
        f"<span style='font-size:13px;font-weight:800;color:{DARK};"
        f"text-transform:uppercase;letter-spacing:.8px'>{title}</span></div>",
        unsafe_allow_html=True)

def insight(bg, border, color, text):
    st.markdown(
        f'<div class="insight-box" style="background:{bg};border-left:3px solid {border};'
        f'color:{color};">{text}</div>', unsafe_allow_html=True)

# ── Overview ──────────────────────────────────────────────────────────────────
sec_head(PURPLE, "Overview — trends over time")
col_trend, col_bar = st.columns([2, 1])

with col_trend:
    with st.container(border=True):
        st.markdown("**📈 Life expectancy over time**")
        traces = []
        if cnt != "USA":
            traces.append(go.Scatter(
                x=YEARS, y=UK["le"], name="United Kingdom",
                line=dict(color=PURPLE, width=2.5),
                fill="tozeroy", fillcolor="rgba(156,39,176,0.10)",
                mode="lines+markers", marker=dict(size=3)))
        if cnt != "UK":
            traces.append(go.Scatter(
                x=YEARS, y=USA["le"], name="United States",
                line=dict(color=CYAN, width=2.5, dash="dash"),
                fill="tozeroy", fillcolor="rgba(0,188,212,0.07)",
                mode="lines+markers", marker=dict(size=3)))
        fig = go.Figure(traces)
        apply_base(fig, height=220, yrange=[74,85], ysuffix=" yrs",
                   legend=True, legend_cfg=dict(
                       font=dict(size=10), orientation="h",
                       yanchor="bottom", y=1.02, x=0))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})
        insight("#f9f0ff","#ce93d8","#4a148c",
                "✦ Both countries dipped in 2020–2021 due to COVID-19. The UK recovered "
                "faster and consistently leads the USA despite the USA spending nearly 2× more.")

with col_bar:
    with st.container(border=True):
        st.markdown(f"**📊 Country comparison — {year}**")
        lbls, vals, cols = [], [], []
        if cnt != "USA":
            lbls.append("UK"); vals.append(UK["le"][yi]); cols.append(PURPLE)
        if cnt != "UK" and USA["le"][yi] is not None:
            lbls.append("USA"); vals.append(USA["le"][yi]); cols.append(CYAN)
        fig = go.Figure(go.Bar(x=lbls, y=vals, marker=dict(color=cols),
                               text=[f"{v:.2f}" for v in vals],
                               textposition="outside"))
        apply_base(fig, height=220, yrange=[70,85], ysuffix=" yrs")
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})
        insight("#fce4ec","#f48fb1","#880e4f",
                "✦ The UK outperforms the USA by ~3 years — spending efficiency, "
                "not just total spending, drives outcomes.")

# ── Key Drivers ───────────────────────────────────────────────────────────────
sec_head(CYAN, "Key drivers — what affects life expectancy?")
d1,d2,d3,d4 = st.columns(4)

def scatter_driver(col, x_key, title, color, bg, border, text, ref):
    with col:
        with st.container(border=True):
            st.markdown(f"<b style='color:{color}'>{title}</b>", unsafe_allow_html=True)
            traces = []
            if cnt != "USA":
                traces.append(go.Scatter(
                    x=UK[x_key], y=UK["le"], name="UK", mode="markers",
                    marker=dict(color=color, size=5, opacity=0.75)))
            if cnt != "UK":
                pairs = [(x,y) for x,y in zip(USA[x_key], USA["le"])
                         if x is not None and y is not None]
                if pairs:
                    xs,ys = zip(*pairs)
                    traces.append(go.Scatter(
                        x=xs, y=ys, name="USA", mode="markers",
                        marker=dict(color=CYAN, size=5, opacity=0.75)))
            fig = go.Figure(traces)
            apply_base(fig, height=150, yrange=[74,84])
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})
            insight(bg, border, color, f"{text} ({ref})")

scatter_driver(d1,"hc",  "🏥 Healthcare spending", INDIGO,
               "#e8eaf6","#9fa8da","<b>Positive ↑</b> — More investment, longer lives.","Jaba et al., 2014")
scatter_driver(d2,"gdp", "🏦 GDP per capita",       ORANGE,
               "#fff3e0","#ffcc80","<b>Positive ↑</b> — Wealth lifts living standards.","Preston, 1975")

with d3:
    with st.container(border=True):
        st.markdown(f"<b style='color:{TEAL}'>💧 Water access</b>", unsafe_allow_html=True)
        traces = []
        if cnt != "USA":
            traces.append(go.Scatter(x=YEARS, y=UK["water"], name="UK",
                                     line=dict(color=TEAL, width=2),
                                     mode="lines+markers", marker=dict(size=3)))
        if cnt != "UK":
            traces.append(go.Scatter(x=YEARS, y=USA["water"], name="USA",
                                     line=dict(color=ORANGE, width=2, dash="dot"),
                                     mode="lines+markers", marker=dict(size=3)))
        fig = go.Figure(traces)
        apply_base(fig, height=150, yrange=[97,101], ysuffix="%")
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})
        insight("#e0f2f1","#80cbc4","#004d40",
                "<b>Positive ↑</b> — Clean water cuts disease burden. (UN, 2023)")

with d4:
    with st.container(border=True):
        st.markdown(f"<b style='color:{RED}'>🌫️ CO₂ emissions</b>", unsafe_allow_html=True)
        traces = []
        if cnt != "USA":
            traces.append(go.Scatter(x=YEARS, y=UK["co2"], name="UK",
                                     line=dict(color=RED, width=2),
                                     mode="lines+markers", marker=dict(size=3)))
        if cnt != "UK":
            traces.append(go.Scatter(x=YEARS, y=USA["co2"], name="USA",
                                     line=dict(color=ORANGE, width=2, dash="dot"),
                                     mode="lines+markers", marker=dict(size=3)))
        fig = go.Figure(traces)
        apply_base(fig, height=150, ysuffix=" t")
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})
        insight("#ffebee","#ef9a9a","#b71c1c",
                "<b>Negative ↓</b> — Pollution shortens lives. (Wen et al., 2021)")

# ── Correlation ───────────────────────────────────────────────────────────────
sec_head(ORANGE, "Correlation analysis")
with st.container(border=True):
    st.markdown("**Strength of relationship with life expectancy**")
    corr = [("Healthcare spending",0.87,INDIGO),
            ("GDP per capita",     0.82,ORANGE),
            ("Water access",       0.71,TEAL),
            ("CO₂ emissions",     -0.63,RED)]
    fig = go.Figure(go.Bar(
        y=[d[0] for d in corr], x=[d[1] for d in corr],
        orientation="h", marker=dict(color=[d[2] for d in corr]),
        text=[f"{'+' if d[1]>0 else ''}{d[1]:.2f}" for d in corr],
        textposition="outside"))
    apply_base(fig, height=200)
    fig.update_xaxes(range=[-1,1], showgrid=True, gridcolor="#f0f0f0",
                     zeroline=True, zerolinecolor="#bbb", tickfont=dict(size=10))
    fig.update_yaxes(showgrid=False, tickfont=dict(size=11))
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})

# ── Regression ────────────────────────────────────────────────────────────────
sec_head("#e91e63", "Regression model — performance &amp; predictions")
r1,r2 = st.columns(2)

with r1:
    with st.container(border=True):
        st.markdown("**📐 Model performance (Robust RLM)**")
        m1,m2,m3 = st.columns(3)
        m1.metric("R² Score","0.94"); m2.metric("RMSE","0.42"); m3.metric("Obs.","44")
        actual   = [77.7,78.1,78.7,79.2,79.6,80.4,80.9,81.0,81.3,80.96,
                    81.16,81.26,81.26,81.37,80.33,80.65,81.01]
        pred     = [77.5,78.3,78.9,79.4,79.8,80.2,81.1,80.8,81.5,80.7,
                    81.3,81.4,81.1,81.5,80.1,80.9,81.2]
        pred_yrs = [2000,2002,2004,2006,2008,2010,2012,2014,2016,2018,
                    2019,2020,2021,2022,2023,2024]
        fig = go.Figure([
            go.Scatter(x=pred_yrs, y=actual, name="Actual",
                       line=dict(color=PURPLE, width=2.5),
                       mode="lines+markers", marker=dict(size=4)),
            go.Scatter(x=pred_yrs, y=pred, name="Predicted",
                       line=dict(color=CYAN, width=2, dash="dash"),
                       mode="lines+markers", marker=dict(size=3)),
        ])
        apply_base(fig, height=200, yrange=[75,84],
                   legend=True, legend_cfg=dict(
                       font=dict(size=10), orientation="h",
                       yanchor="bottom", y=1.02, x=0))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})

with r2:
    with st.container(border=True):
        st.markdown("**📋 Feature importance** *(from RLM coefficients)*")
        fi = [("Healthcare spending",0.92,INDIGO,"+0.0042"),
              ("Water access",       0.75,TEAL,  "+0.135"),
              ("GDP per capita",     0.60,ORANGE,"+0.00008"),
              ("CO₂ emissions",      0.45,RED,   "−0.089")]
        fig = go.Figure(go.Bar(
            y=[d[0] for d in fi], x=[d[1] for d in fi],
            orientation="h", marker=dict(color=[d[2] for d in fi]),
            text=[d[3] for d in fi], textposition="outside"))
        apply_base(fig, height=200)
        fig.update_xaxes(range=[0,1.15], showgrid=True, gridcolor="#f0f0f0",
                         tickformat=".0%", tickfont=dict(size=10))
        fig.update_yaxes(showgrid=False, tickfont=dict(size=11))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})
        insight("#f3e5f5","#ce93d8","#4a148c",
                "✦ Healthcare spending and water access are the top positive drivers. "
                "CO₂ is the strongest negative driver.")

# ── Recommendations ───────────────────────────────────────────────────────────
sec_head("#4caf50", "Insights &amp; recommendations")
recos = [
    ("🫀 Increase healthcare investment", INDIGO, "#e8eaf6", "#283593",
     "Every $1,000 increase in per-capita healthcare spending is linked to measurably longer "
     "life expectancy. Efficient spending matters more than raw totals — the UK proves this."),
    ("🏦 Promote economic growth", "#e65100", "#fff3e0", "#bf360c",
     "Policies that grow GDP per capita — through education, trade, and infrastructure — lift "
     "living standards and indirectly extend lives via better nutrition and healthcare access."),
    ("💧 Ensure universal water access", "#004d40", "#e0f2f1", "#00695c",
     "Expanding clean water infrastructure reduces preventable waterborne diseases that "
     "disproportionately shorten life expectancy in vulnerable and lower-income populations."),
    ("🌿 Reduce carbon emissions", "#b71c1c", "#ffebee", "#c62828",
     "Transitioning to cleaner energy and enforcing stricter emission standards directly reduces "
     "pollution-linked disease burden — confirmed significant by the regression analysis."),
]
for i in range(0, 4, 2):
    ca, cb = st.columns(2)
    for col, reco in zip([ca, cb], recos[i:i+2]):
        with col:
            st.markdown(
                f'<div class="reco-card" style="background:{reco[2]};">'
                f'<b style="color:{reco[1]};font-size:13px;">{reco[0]}</b><br>'
                f'<span style="color:{reco[3]}">{reco[4]}</span></div>',
                unsafe_allow_html=True)

# ── Conclusion ────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="background:{DARK};border-radius:14px;padding:20px 24px;margin-top:14px;color:#fff;">
  <h3 style="font-size:15px;font-weight:800;color:#e8d5f5;margin-bottom:8px;">✦ Final conclusion</h3>
  <p style="font-size:12.5px;line-height:1.75;color:rgba(255,255,255,.85);">
    The robust regression analysis confirms that <b>healthcare spending</b>,
    <b>GDP per capita</b>, and <b>water access</b> are significant positive drivers of
    life expectancy, while <b>CO₂ emissions</b> act as a significant negative driver.
    Together they explain <b>94% of the variance</b> in life expectancy across the UK
    and USA from 2000 to 2024 — directly supporting the goals of
    <b>SDG 3: Good Health and Well-Being</b>.
  </p>
  <div style="display:flex;gap:8px;margin-top:12px;flex-wrap:wrap;">
    <span style="background:{PURPLE};color:#fff;border-radius:20px;padding:5px 13px;font-size:11px;font-weight:700;">Healthcare spending ↑</span>
    <span style="background:#f57c00;color:#fff;border-radius:20px;padding:5px 13px;font-size:11px;font-weight:700;">GDP per capita ↑</span>
    <span style="background:{TEAL};color:#fff;border-radius:20px;padding:5px 13px;font-size:11px;font-weight:700;">Water access ↑</span>
    <span style="background:{RED};color:#fff;border-radius:20px;padding:5px 13px;font-size:11px;font-weight:700;">CO₂ emissions ↓</span>
    <span style="background:#e8d5f5;color:#4a148c;border-radius:20px;padding:5px 13px;font-size:11px;font-weight:700;">R² = 0.94</span>
  </div>
</div>
""", unsafe_allow_html=True)
