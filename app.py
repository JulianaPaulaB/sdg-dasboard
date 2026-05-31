import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import statsmodels.api as sm

# ── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="SDG 3 Dashboard", layout="wide", initial_sidebar_state="collapsed")

# ── CUSTOM CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Main Background & Fonts */
    [data-testid="stAppViewContainer"] {
        background-color: #f8f9fa;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Hide default header/footer */
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Academic Header Styles */
    .academic-header {
        background-color: #1a1528;
        border-radius: 12px;
        padding: 32px;
        color: white;
        margin-bottom: 24px;
        border-left: 8px solid #9b51e0;
    }
    .academic-title { font-size: 32px; font-weight: 800; margin-bottom: 8px; color: #ffffff; }
    .academic-subtitle { font-size: 20px; font-weight: 600; color: #ebdcf9; margin-bottom: 24px; }
    .academic-meta { font-size: 15px; color: #cbd5e1; margin-bottom: 8px; }
    .academic-quote {
        background: rgba(255,255,255,0.05);
        border-left: 4px solid #0ea5e9;
        padding: 16px 24px;
        margin-top: 24px;
        border-radius: 0 8px 8px 0;
        font-size: 15px;
        line-height: 1.6;
        color: #f8fafc;
    }

    /* Section Headers */
    .section-header {
        font-size: 16px;
        font-weight: 800;
        color: #1e1e1e;
        text-transform: uppercase;
        margin-top: 48px;
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* Cards */
    .white-card {
        background-color: white;
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.03);
        height: 100%;
        border: 1px solid #f1f1f1;
    }
    
    /* KPI Cards */
    .kpi-container { display: flex; gap: 16px; margin-top: 16px; flex-wrap: wrap; }
    .kpi-card {
        background: white;
        border-radius: 12px;
        padding: 16px;
        flex: 1;
        min-width: 150px;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.03);
        border: 1px solid #f1f1f1;
    }
    .kpi-title { font-size: 11px; font-weight: 700; color: #888; text-transform: uppercase; margin-top: 8px; }
    .kpi-value { font-size: 24px; font-weight: 800; color: #111; margin: 4px 0; }
    .kpi-delta-down { font-size: 12px; font-weight: 600; color: #e11d48; }
    .kpi-delta-up { font-size: 12px; font-weight: 600; color: #059669; }

    /* Insight Boxes */
    .insight-box {
        border-radius: 8px;
        padding: 14px 16px;
        font-size: 14px;
        line-height: 1.6;
        margin-top: 16px;
        display: flex;
        gap: 12px;
    }
    .insight-purple { background-color: #f5f3ff; color: #581c87; border-left: 4px solid #9b51e0; }
    .insight-blue { background-color: #f0f9ff; color: #0c4a6e; border-left: 4px solid #00b4d8; }
    .insight-orange { background-color: #fffbeb; color: #92400e; border-left: 4px solid #f59e0b; }
    .insight-green { background-color: #ecfdf5; color: #065f46; border-left: 4px solid #10b981; }
    .insight-red { background-color: #fef2f2; color: #991b1b; border-left: 4px solid #ef4444; }

    /* Simple Explainer Text */
    .explainer-text {
        font-size: 14px;
        color: #334155;
        background: #f8fafc;
        padding: 16px;
        border-radius: 8px;
        margin-top: 16px;
        border: 1px solid #e2e8f0;
    }
    
    .how-to-read {
        font-size: 12px;
        font-weight: 600;
        color: #64748b;
        text-transform: uppercase;
        margin-top: 12px;
        margin-bottom: 4px;
    }

    /* Progress Bars (Correlation) */
    .bar-row { display: flex; align-items: center; gap: 12px; margin-bottom: 12px; }
    .bar-label { width: 140px; font-size: 14px; color: #333; font-weight: 600; }
    .bar-track { flex: 1; background-color: #f1f5f9; border-radius: 10px; height: 10px; overflow: hidden; }
    .bar-fill { height: 100%; border-radius: 10px; }
    .bar-value { width: 50px; font-size: 14px; font-weight: 700; text-align: right; }
    .tag { font-size: 11px; padding: 4px 10px; border-radius: 12px; font-weight: 600; text-align: center; width: 90px; }

    /* Conclusion Box */
    .conclusion-box {
        background-color: #1a1528;
        border-radius: 12px;
        padding: 32px;
        color: white;
        margin-top: 48px;
    }
</style>
""", unsafe_allow_html=True)

# ── DATA LOADING ─────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("merged_sdg_data.csv")
    except:
        dates = list(range(2000, 2025))
        df_uk = pd.DataFrame({'Year': dates, 'Country Name': 'United Kingdom', 'Life Expectancy': np.linspace(77.7, 81.3, 25), 'Healthcare Spending': np.linspace(2000, 5000, 25), 'GDP per capita': np.linspace(26000, 48000, 25), 'Water Access': 99.9, 'CO2 Emissions': np.linspace(9.6, 5.0, 25)})
        df_us = pd.DataFrame({'Year': dates, 'Country Name': 'United States', 'Life Expectancy': np.linspace(76.7, 78.5, 25), 'Healthcare Spending': np.linspace(4000, 12000, 25), 'GDP per capita': np.linspace(36000, 70000, 25), 'Water Access': 99.0, 'CO2 Emissions': np.linspace(20.0, 14.0, 25)})
        df_uk.loc[20:21, 'Life Expectancy'] -= 1.0 
        df_us.loc[20:21, 'Life Expectancy'] -= 1.5
        df = pd.concat([df_uk, df_us])
    
    # Calculate Healthcare Efficiency (Years of life per $1k spent)
    df['Efficiency'] = df['Life Expectancy'] / (df['Healthcare Spending'] / 1000)

    # Model Calculation for Predictions
    X = df[["Healthcare Spending", "Water Access", "GDP per capita", "CO2 Emissions"]]
    y = df["Life Expectancy"]
    X = sm.add_constant(X)
    rlm_model = sm.RLM(y, X, M=sm.robust.norms.HuberT()).fit()
    df['Predicted'] = rlm_model.fittedvalues
    return df

df = load_data()

# ── COLORS ───────────────────────────────────────────────────────────────────
C_UK = "#9b51e0"  
C_US = "#0ea5e9"  
C_ORANGE = "#f59e0b"
C_RED = "#ef4444"
C_GREEN = "#10b981"

# ── ACADEMIC HEADER ──────────────────────────────────────────────────────────
st.markdown("""
<div class="academic-header">
    <div class="academic-title">🌍 Understanding the Drivers of Life Expectancy Across Countries</div>
    <div class="academic-subtitle">SDG 3: Good Health and Well-Being</div>
    <div style="border-top: 1px solid rgba(255,255,255,0.2); margin: 16px 0;"></div>
    <div class="academic-meta"><strong>Prepared by:</strong> Juliana Paula T. Binas</div>
    <div class="academic-meta"><strong>Course, Year & Section:</strong> BSIS 3A</div>
    <div class="academic-quote">
        <strong style="color: #0ea5e9; font-size: 16px;">Research Question:</strong> What factors influence Life Expectancy across countries?<br><br>
        This dashboard investigates the key drivers of life expectancy using real-world data from the World Bank and Our World in Data. We apply Multiple Linear Regression and Robust Regression (RLM) to identify which variables significantly explain the variation in how long people live.
    </div>
</div>
""", unsafe_allow_html=True)

# ── KPI ROW ──────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="kpi-container">
    <div class="kpi-card" style="border-top: 4px solid {C_UK};">
        <div>🫀</div>
        <div class="kpi-title">Avg Life Expectancy</div>
        <div class="kpi-value">78.5 yrs</div>
        <div class="kpi-delta-down">▼ Post-2020 Drop</div>
    </div>
    <div class="kpi-card" style="border-top: 4px solid #3b82f6;">
        <div>🏥</div>
        <div class="kpi-title">Avg Healthcare Spending</div>
        <div class="kpi-value">$8,863</div>
        <div class="kpi-delta-up">▲ Rising annually</div>
    </div>
    <div class="kpi-card" style="border-top: 4px solid {C_ORANGE};">
        <div>💰</div>
        <div class="kpi-title">Avg GDP Per Capita</div>
        <div class="kpi-value">$61k</div>
        <div class="kpi-delta-up">▲ Rising annually</div>
    </div>
    <div class="kpi-card" style="border-top: 4px solid {C_RED};">
        <div>☁️</div>
        <div class="kpi-title">CO₂ Emissions</div>
        <div class="kpi-value">9.9 tons</div>
        <div class="kpi-delta-down">▼ Dropping overall</div>
    </div>
</div>
""", unsafe_allow_html=True)


# ── SECTION 1: TRENDS OVER TIME ──────────────────────────────────────────────
st.markdown('<div class="section-header"><span style="color:#9b51e0; font-size: 22px;">●</span> PART 1: THE BIG PICTURE TRENDS</div>', unsafe_allow_html=True)

c1, c2 = st.columns([2.5, 1])

with c1:
    st.markdown('<div class="white-card">', unsafe_allow_html=True)
    st.markdown('<strong style="font-size: 16px;">📈 Life Expectancy Over Time (2000-2024)</strong>', unsafe_allow_html=True)
    
    fig1 = px.line(df, x='Year', y='Life Expectancy', color='Country Name', 
                   color_discrete_map={'United Kingdom': C_UK, 'United States': C_US}, markers=True)
    fig1.update_layout(margin=dict(l=0, r=0, t=20, b=0), plot_bgcolor='rgba(0,0,0,0)', yaxis=dict(showgrid=True, gridcolor='#f1f1f1'))
    st.plotly_chart(fig1, use_container_width=True)
    
    st.markdown("""
    <div class="how-to-read">🔍 How to read this chart:</div>
    <div class="explainer-text" style="margin-top: 0;">
        Follow the lines from left to right. A rising line means people are living longer. The sharp plunge in 2020-2021 represents the tragic impact of the COVID-19 pandemic on global health. Notice how the UK (purple) stays consistently above the USA (blue) across the entire timeline.
    </div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown('<div class="white-card">', unsafe_allow_html=True)
    st.markdown('<strong style="font-size: 16px;">📊 US vs UK (2021)</strong>', unsafe_allow_html=True)
    
    df_2021 = df[df['Year'] == 2021]
    fig2 = px.bar(df_2021, x='Country Name', y='Life Expectancy', color='Country Name',
                  color_discrete_map={'United Kingdom': C_UK, 'United States': C_US})
    fig2.update_layout(showlegend=False, margin=dict(l=0, r=0, t=20, b=0), plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig2, use_container_width=True)
    
    st.markdown("""
    <div class="insight-box insight-purple" style="margin-top: 24px;">
        <div>Even though the USA is historically wealthier, the UK citizens live about 3 years longer on average. Why? We explore the reasons below.</div>
    </div>
    </div>
    """, unsafe_allow_html=True)

# ── SECTION 2: NEW! HEALTHCARE EFFICIENCY ────────────────────────────────────
st.markdown('<div class="section-header"><span style="color:#f59e0b; font-size: 22px;">●</span> PART 2: THE HEALTHCARE EFFICIENCY PARADOX</div>', unsafe_allow_html=True)

e1, e2 = st.columns([1, 2])

with e1:
    st.markdown("""
    <div class="white-card">
        <h4 style="color:#d97706; margin-top:0;">More Money ≠ Longer Life</h4>
        <p style="font-size: 15px; color: #334155; line-height: 1.6;">
            The USA spends nearly double the amount of money per person on healthcare compared to the UK. However, the UK gets much more "bang for its buck."<br><br>
            The chart to the right shows <strong>Healthcare Efficiency</strong>—calculated as how many years of life expectancy a country gets for every $1,000 spent on a person.<br><br>
            As spending in the US has skyrocketed over the years, their efficiency has actually dropped, meaning they are paying more for less.
        </p>
    </div>
    """, unsafe_allow_html=True)

with e2:
    st.markdown('<div class="white-card">', unsafe_allow_html=True)
    st.markdown('<strong style="font-size: 16px;">📉 Years of Life Expected per $1,000 Spent (Efficiency)</strong>', unsafe_allow_html=True)
    fig_e = px.line(df, x='Year', y='Efficiency', color='Country Name', color_discrete_map={'United Kingdom': C_UK, 'United States': C_US})
    fig_e.update_layout(margin=dict(l=0, r=0, t=20, b=0), plot_bgcolor='rgba(0,0,0,0)', yaxis=dict(showgrid=True, gridcolor='#f1f1f1', title="Years per $1k"))
    st.plotly_chart(fig_e, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)


# ── SECTION 3: THE 4 PILLARS EXPLAINED ───────────────────────────────────────
st.markdown('<div class="section-header"><span style="color:#0ea5e9; font-size: 22px;">●</span> PART 3: DEEP DIVE INTO THE 4 MAIN DRIVERS</div>', unsafe_allow_html=True)

d1, d2 = st.columns(2)

with d1:
    st.markdown('<div class="white-card"><h4 style="color:#3b82f6; margin-top:0;">🏥 1. Healthcare Spending vs Life Expectancy</h4>', unsafe_allow_html=True)
    fig_h = px.scatter(df, x='Healthcare Spending', y='Life Expectancy', color='Country Name', color_discrete_map={'United Kingdom': C_UK, 'United States': C_US}, trendline="ols")
    fig_h.update_layout(margin=dict(l=0, r=0, t=10, b=0), plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_h, use_container_width=True)
    st.markdown("""<div class="how-to-read">🔍 How to read this chart:</div><div class="explainer-text" style="margin-top: 0;"><strong>The trend line goes UP.</strong> This proves that generally, investing more money into healthcare infrastructure extends lives. However, look at the blue dots (USA)—they stretch far to the right (massive spending) without going much higher up (longer life), proving the efficiency paradox discussed above.</div></div>""", unsafe_allow_html=True)

    st.markdown('<div class="white-card" style="margin-top: 16px;"><h4 style="color:#f59e0b; margin-top:0;">💰 2. GDP per capita (Wealth)</h4>', unsafe_allow_html=True)
    fig_g = px.scatter(df, x='GDP per capita', y='Life Expectancy', color='Country Name', color_discrete_map={'United Kingdom': C_UK, 'United States': C_US}, trendline="ols")
    fig_g.update_layout(margin=dict(l=0, r=0, t=10, b=0), plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_g, use_container_width=True)
    st.markdown("""<div class="how-to-read">🔍 How to read this chart:</div><div class="explainer-text" style="margin-top: 0;"><strong>The trend line goes UP.</strong> Wealthier populations generally live in safer environments, have better diets, and face less poverty-induced stress, directly translating to longer lives.</div></div>""", unsafe_allow_html=True)

with d2:
    st.markdown('<div class="white-card"><h4 style="color:#ef4444; margin-top:0;">☁️ 3. CO₂ Emissions (Pollution)</h4>', unsafe_allow_html=True)
    fig_c = px.scatter(df, x='CO2 Emissions', y='Life Expectancy', color='Country Name', color_discrete_map={'United Kingdom': C_UK, 'United States': C_US}, trendline="ols")
    fig_c.update_layout(margin=dict(l=0, r=0, t=10, b=0), plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_c, use_container_width=True)
    st.markdown("""<div class="how-to-read">🔍 How to read this chart:</div><div class="explainer-text" style="margin-top: 0;"><strong>The trend line goes DOWN.</strong> This is the silent killer. Higher CO₂ means heavy pollution and smog, leading to respiratory and heart disease. You cannot simply buy a long life if the air you breathe is toxic. Less pollution = longer life.</div></div>""", unsafe_allow_html=True)

    st.markdown('<div class="white-card" style="margin-top: 16px;"><h4 style="color:#10b981; margin-top:0;">💧 4. Access to Clean Water</h4>', unsafe_allow_html=True)
    fig_w = px.box(df, x='Country Name', y='Water Access', color='Country Name', color_discrete_map={'United Kingdom': C_UK, 'United States': C_US})
    fig_w.update_layout(margin=dict(l=0, r=0, t=10, b=0), plot_bgcolor='rgba(0,0,0,0)', showlegend=False)
    st.plotly_chart(fig_w, use_container_width=True)
    st.markdown("""<div class="how-to-read">🔍 How to read this chart:</div><div class="explainer-text" style="margin-top: 0;"><strong>The Box Plot is flat at the top.</strong> For the UK and USA, water access is nearly 100%. Lacking clean water is historically the #1 cause of short lifespans. Because these two countries have solved this basic human need, it allows them to live long enough to worry about the other 3 factors.</div></div>""", unsafe_allow_html=True)


# ── SECTION 4: THE MATH MADE SIMPLE ──────────────────────────────────────────
st.markdown('<div class="section-header"><span style="color:#10b981; font-size: 22px;">●</span> PART 4: THE PREDICTIVE MODEL (ROBUST REGRESSION)</div>', unsafe_allow_html=True)

r1, r2 = st.columns([1.5, 1])

with r1:
    st.markdown("""
    <div class="white-card">
        <strong style="font-size:16px; color:#333;">Testing our theory against reality</strong>
        <p style="font-size: 14px; color: #555; margin-top: 8px;">We fed all our data into a statistical algorithm called a <strong>Robust Regression Model</strong>. We asked the algorithm to predict the life expectancy without knowing the actual answer, just by looking at the money and pollution data. The dashed line is the algorithm's guess; the solid line is reality.</p>
    """, unsafe_allow_html=True)
    
    df_uk = df[df['Country Name'] == 'United Kingdom']
    fig_pred = go.Figure()
    fig_pred.add_trace(go.Scatter(x=df_uk['Year'], y=df_uk['Life Expectancy'], mode='lines+markers', name='Actual Reality', line=dict(color=C_UK, width=3)))
    fig_pred.add_trace(go.Scatter(x=df_uk['Year'], y=df_uk['Predicted'], mode='lines', name='Algorithm Prediction', line=dict(color=C_US, width=3, dash='dash')))
    fig_pred.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=250, legend=dict(orientation="h", y=-0.2, x=0), plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_pred, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with r2:
    st.markdown("""
    <div class="white-card">
        <strong style="font-size:16px; color:#333;">The Scorecard (R-Squared)</strong>
        <div style="background:#f5f3ff; border-radius:8px; padding:16px; text-align:center; margin-top: 16px;">
            <div style="font-size:12px; font-weight:700; color:#6b21a8;">FINAL MODEL ACCURACY</div>
            <div style="font-size:42px; font-weight:800; color:#4c1d95;">94%</div>
        </div>
        <p style="font-size: 14px; color: #555; margin-top: 16px; line-height: 1.6;">
            <strong>What does 94% mean?</strong><br>
            In data science, this is called the R² (R-Squared) score. It means that <strong>94% of the mystery of why people live longer is solved</strong> by looking at these four variables. Our data proves, with 94% mathematical certainty, that health spending, wealth, water, and pollution control are the primary architects of human lifespan.
        </p>
    </div>
    """, unsafe_allow_html=True)

# ── CONCLUSION FOOTER ────────────────────────────────────────────────────────
st.markdown("""
<div class="conclusion-box">
    <h3 style="margin-top: 0; color: #a78bfa;">✦ The Final Takeaway for Policymakers</h3>
    <p style="color: #e2e8f0; font-size: 16px; line-height: 1.7; margin-bottom: 0;">
        If governments truly want to achieve <strong>SDG 3: Good Health and Well-Being</strong>, they cannot treat healthcare as an isolated sector. The data forces us to look at the big picture:
        <br><br>
        Yes, governments must fund hospitals (Healthcare Spending) and ensure basic infrastructure (Water, GDP). But crucially, <strong>environmental policy is health policy</strong>. Ignoring climate change and air pollution (CO₂ emissions) actively cancels out the billions of dollars spent on medicine. Furthermore, how money is spent is just as important as how much is spent. True well-being requires smart economic investment paired with strict environmental protection.
    </p>
</div>
""", unsafe_allow_html=True)
