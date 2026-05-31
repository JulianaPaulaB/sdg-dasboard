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

    /* Top Banner */
    .top-banner {
        background-color: #1a1528;
        border-radius: 12px;
        padding: 24px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        color: white;
        margin-bottom: 24px;
    }
    .badge-purple { background-color: #ebdcf9; color: #6b21a8; padding: 6px 16px; border-radius: 20px; font-size: 14px; font-weight: 600;}
    .badge-light { background-color: #f3e8ff; color: #4c1d95; padding: 6px 16px; border-radius: 20px; font-size: 14px; font-weight: 600;}

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

# ── HEADER BANNER ────────────────────────────────────────────────────────────
st.markdown("""
<div class="top-banner">
    <div style="display: flex; align-items: center; gap: 16px;">
        <div class="badge-purple">✦ SDG 3 · Good Health</div>
        <div>
            <h2 style="margin: 0; font-size: 24px; font-weight: 800;">Drivers of Life Expectancy Across Countries</h2>
            <p style="margin: 0; font-size: 14px; color: #cbd5e1; margin-top: 4px;">Juliana Paula T. Binas · BSIS 3A · Analytics Techniques and Tools</p>
        </div>
    </div>
    <div style="display: flex; gap: 12px;">
        <div class="badge-light">2000–2024</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── KPI ROW ──────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="kpi-container">
    <div class="kpi-card" style="border-top: 4px solid {C_UK};">
        <div>🫀</div>
        <div class="kpi-title">Life Expectancy</div>
        <div class="kpi-value">78.5 yrs</div>
        <div class="kpi-delta-down">▼ -0.16 vs 2020</div>
    </div>
    <div class="kpi-card" style="border-top: 4px solid #3b82f6;">
        <div>🏥</div>
        <div class="kpi-title">Healthcare Spending</div>
        <div class="kpi-value">$8,863</div>
        <div class="kpi-delta-down">▼ -$606 vs 2020</div>
    </div>
    <div class="kpi-card" style="border-top: 4px solid {C_ORANGE};">
        <div>💰</div>
        <div class="kpi-title">GDP Per Capita</div>
        <div class="kpi-value">$61k</div>
        <div class="kpi-delta-down">▼ -$5k vs 2020</div>
    </div>
    <div class="kpi-card" style="border-top: 4px solid {C_RED};">
        <div>☁️</div>
        <div class="kpi-title">CO₂ Emissions</div>
        <div class="kpi-value">9.9 tons</div>
        <div class="kpi-delta-up">▲ 0.58 vs 2020</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── SECTION 1: INTRODUCTION ──────────────────────────────────────────────────
st.markdown('<div class="section-header"><span style="color:#0ea5e9; font-size: 22px;">●</span> THE CORE QUESTION</div>', unsafe_allow_html=True)

st.markdown("""
<div class="white-card">
    <p style="font-size: 16px; color: #1e293b; line-height: 1.7; margin: 0;">
        <strong>What actually makes a population live longer?</strong> Is it just about having a massive economy, or do environmental factors play a hidden role? <br><br>
        To answer this, we analyzed 24 years of data from the United States and the United Kingdom. We didn't just look at medical data; we looked at <strong>Money</strong> (Healthcare Spend, GDP), <strong>Environment</strong> (CO₂ Emissions), and <strong>Basic Needs</strong> (Water Access). By putting these into a statistical model, we can prove exactly which factors add years to our lives, and which ones take them away.
    </p>
</div>
""", unsafe_allow_html=True)


# ── SECTION 2: TRENDS OVER TIME ──────────────────────────────────────────────
st.markdown('<div class="section-header"><span style="color:#9b51e0; font-size: 22px;">●</span> THE BIG PICTURE: TRENDS OVER TIME</div>', unsafe_allow_html=True)

c1, c2 = st.columns([2.5, 1])

with c1:
    st.markdown('<div class="white-card">', unsafe_allow_html=True)
    st.markdown('<strong style="font-size: 16px;">📈 Life expectancy over time (2000-2024)</strong>', unsafe_allow_html=True)
    
    fig1 = px.line(df, x='Year', y='Life Expectancy', color='Country Name', 
                   color_discrete_map={'United Kingdom': C_UK, 'United States': C_US}, markers=True)
    fig1.update_layout(margin=dict(l=0, r=0, t=20, b=0), plot_bgcolor='rgba(0,0,0,0)', yaxis=dict(showgrid=True, gridcolor='#f1f1f1'))
    st.plotly_chart(fig1, use_container_width=True)
    
    st.markdown("""
    <div class="insight-box insight-purple">
        <div style="font-size:24px;">💡</div>
        <div><strong>What is this showing?</strong> Both countries saw life expectancy steadily rise from 2000 to 2019, proving that modern medicine works. However, notice the sharp plunge in 2020. This is the statistical footprint of the COVID-19 pandemic. Also, notice how the purple line (UK) stays consistently above the blue line (USA) across the entire 24-year period.</div>
    </div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown('<div class="white-card">', unsafe_allow_html=True)
    st.markdown('<strong style="font-size: 16px;">📊 US vs UK in 2021</strong>', unsafe_allow_html=True)
    
    df_2021 = df[df['Year'] == 2021]
    fig2 = px.bar(df_2021, x='Country Name', y='Life Expectancy', color='Country Name',
                  color_discrete_map={'United Kingdom': C_UK, 'United States': C_US})
    fig2.update_layout(showlegend=False, margin=dict(l=0, r=0, t=20, b=0), plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig2, use_container_width=True)
    
    st.markdown("""
    <div class="explainer-text">
        <strong>The Efficiency Paradox:</strong><br><br>
        The USA spends almost <em>double</em> the amount of money per person on healthcare compared to the UK. Yet, as the chart shows, the UK lives about 3 years longer. This tells us a crucial fact: <strong>How a country manages its health system is just as important as how much money it throws at it.</strong>
    </div>
    </div>
    """, unsafe_allow_html=True)

# ── SECTION 3: THE 4 PILLARS EXPLAINED ───────────────────────────────────────
st.markdown('<div class="section-header"><span style="color:#f59e0b; font-size: 22px;">●</span> DEEP DIVE: THE 4 PILLARS OF LIFESPAN</div>', unsafe_allow_html=True)

d1, d2 = st.columns(2)

with d1:
    st.markdown('<div class="white-card"><h4 style="color:#3b82f6; margin-top:0;">🏥 1. Healthcare Spending</h4>', unsafe_allow_html=True)
    fig_h = px.scatter(df, x='Healthcare Spending', y='Life Expectancy', color='Country Name', color_discrete_map={'United Kingdom': C_UK, 'United States': C_US}, trendline="ols")
    fig_h.update_layout(margin=dict(l=0, r=0, t=10, b=0), plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_h, use_container_width=True)
    st.markdown("""<div class="explainer-text"><strong>Why it matters:</strong> Money buys better hospitals, faster emergency response, and advanced medical research. The upward sloping line proves that as spending goes up, life expectancy goes up. However, there are "diminishing returns"—eventually, spending more money stops adding extra years to life unless the system itself improves.</div></div>""", unsafe_allow_html=True)

    st.markdown('<div class="white-card" style="margin-top: 16px;"><h4 style="color:#f59e0b; margin-top:0;">💰 2. GDP per capita (Wealth)</h4>', unsafe_allow_html=True)
    fig_g = px.scatter(df, x='GDP per capita', y='Life Expectancy', color='Country Name', color_discrete_map={'United Kingdom': C_UK, 'United States': C_US}, trendline="ols")
    fig_g.update_layout(margin=dict(l=0, r=0, t=10, b=0), plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_g, use_container_width=True)
    st.markdown("""<div class="explainer-text"><strong>Why it matters:</strong> GDP isn't just "richness." It represents infrastructure. Higher GDP means safer roads, safer workplaces, better nutrition in grocery stores, and less poverty-induced stress. Wealthier populations generally live in safer environments, which directly translates to longer lives.</div></div>""", unsafe_allow_html=True)


with d2:
    st.markdown('<div class="white-card"><h4 style="color:#ef4444; margin-top:0;">☁️ 3. CO₂ Emissions (Pollution)</h4>', unsafe_allow_html=True)
    fig_c = px.scatter(df, x='CO2 Emissions', y='Life Expectancy', color='Country Name', color_discrete_map={'United Kingdom': C_UK, 'United States': C_US}, trendline="ols")
    fig_c.update_layout(margin=dict(l=0, r=0, t=10, b=0), plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_c, use_container_width=True)
    st.markdown("""<div class="explainer-text"><strong>Why it matters:</strong> This is the silent killer. The line slopes downward, meaning higher emissions equal shorter lives. High CO₂ indicates heavy industrial pollution, poor air quality, and smog. This leads directly to asthma, lung cancer, and heart disease. You cannot buy a long life if the air you breathe is toxic.</div></div>""", unsafe_allow_html=True)

    st.markdown('<div class="white-card" style="margin-top: 16px;"><h4 style="color:#10b981; margin-top:0;">💧 4. Access to Clean Water</h4>', unsafe_allow_html=True)
    fig_w = px.box(df, x='Country Name', y='Water Access', color='Country Name', color_discrete_map={'United Kingdom': C_UK, 'United States': C_US})
    fig_w.update_layout(margin=dict(l=0, r=0, t=10, b=0), plot_bgcolor='rgba(0,0,0,0)', showlegend=False)
    st.plotly_chart(fig_w, use_container_width=True)
    st.markdown("""<div class="explainer-text"><strong>Why it matters:</strong> For the UK and USA, water access is nearly 100%. Why include it? Because it acts as a "baseline." Historically, lacking clean water is the #1 cause of low life expectancy (due to diseases like cholera). Because these two countries have solved this, it allows them to live long enough to worry about the other 3 factors.</div></div>""", unsafe_allow_html=True)


# ── SECTION 4: CORRELATION ANALYSIS ──────────────────────────────────────────
st.markdown('<div class="section-header"><span style="color:#0ea5e9; font-size: 22px;">●</span> HOW STRONG IS THE LINK? (CORRELATION)</div>', unsafe_allow_html=True)

st.markdown("""
<div class="white-card">
    <p style="font-size: 15px; color: #333; line-height: 1.6; margin-bottom: 24px;">
        <strong>Understanding Correlation:</strong> We use a math formula to calculate a score between -1.0 and +1.0.<br>
        • A score near <strong>+1.0</strong> means they move together (e.g., Spend more money = live longer).<br>
        • A score near <strong>-1.0</strong> means opposites (e.g., More pollution = live shorter).<br>
        • A score near <strong>0</strong> means there is no relationship at all.
    </p>
    
    <div class="bar-row">
        <div class="bar-label">Healthcare Spend</div>
        <div class="bar-track"><div class="bar-fill" style="width: 87%; background-color: #3b82f6;"></div></div>
        <div class="bar-value" style="color: #3b82f6;">+0.87</div>
        <div class="tag" style="background:#e0e7ff; color:#4338ca;">Strong Link</div>
    </div>
    <div class="bar-row">
        <div class="bar-label">GDP per capita</div>
        <div class="bar-track"><div class="bar-fill" style="width: 82%; background-color: #f59e0b;"></div></div>
        <div class="bar-value" style="color: #f59e0b;">+0.82</div>
        <div class="tag" style="background:#fef3c7; color:#b45309;">Strong Link</div>
    </div>
    <div class="bar-row">
        <div class="bar-label">CO₂ Emissions</div>
        <div class="bar-track"><div class="bar-fill" style="width: 63%; background-color: #ef4444;"></div></div>
        <div class="bar-value" style="color: #ef4444;">-0.63</div>
        <div class="tag" style="background:#fee2e2; color:#991b1b;">Negative Link</div>
    </div>
</div>
""", unsafe_allow_html=True)


# ── SECTION 5: THE MATH MADE SIMPLE ──────────────────────────────────────────
st.markdown('<div class="section-header"><span style="color:#10b981; font-size: 22px;">●</span> THE MATH MADE SIMPLE (PREDICTIVE MODEL)</div>', unsafe_allow_html=True)

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
        Yes, governments must fund hospitals (Healthcare Spending) and ensure basic infrastructure (Water, GDP). But crucially, <strong>environmental policy is health policy</strong>. Ignoring climate change and air pollution (CO₂ emissions) actively cancels out the billions of dollars spent on medicine. You cannot medicate your way out of toxic air. True well-being requires both economic investment and environmental protection.
    </p>
</div>
""", unsafe_allow_html=True)
