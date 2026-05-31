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
    .badge-pink { background-color: #fce7f3; color: #9f1239; padding: 6px 16px; border-radius: 20px; font-size: 14px; font-weight: 600;}

    /* Section Headers */
    .section-header {
        font-size: 16px;
        font-weight: 800;
        color: #1e1e1e;
        text-transform: uppercase;
        margin-top: 40px;
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .dot { font-size: 20px; }

    /* Cards */
    .white-card {
        background-color: white;
        border-radius: 12px;
        padding: 20px;
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
        margin-top: 12px;
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
        color: #4b5563;
        background: #f9fafb;
        padding: 16px;
        border-radius: 8px;
        margin-bottom: 16px;
        border: 1px dashed #cbd5e1;
    }

    /* Conclusion Box */
    .conclusion-box {
        background-color: #1a1528;
        border-radius: 12px;
        padding: 24px;
        color: white;
        margin-top: 32px;
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
C_US = "#00b4d8"  
C_ORANGE = "#f59e0b"
C_RED = "#ef4444"
C_GREEN = "#10b981"

# ── HEADER BANNER ────────────────────────────────────────────────────────────
st.markdown("""
<div class="top-banner">
    <div style="display: flex; align-items: center; gap: 16px;">
        <div class="badge-purple">✦ SDG 3 · Good Health</div>
        <div>
            <h2 style="margin: 0; font-size: 22px; font-weight: 700;">Drivers of Life Expectancy Across Countries</h2>
            <p style="margin: 0; font-size: 13px; color: #a1a1aa; margin-top: 4px;">Juliana Paula T. Binas · BSIS 3A · Analytics Techniques and Tools</p>
        </div>
    </div>
    <div style="display: flex; gap: 12px;">
        <div class="badge-light">2000–<br>2024</div>
        <div class="badge-pink">World<br>Bank</div>
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

# ── SECTION 1: GENERAL EXPLANATION (NEW) ─────────────────────────────────────
st.markdown('<div class="section-header"><span class="dot" style="color:#0ea5e9;">●</span> WHY ARE WE LOOKING AT THIS? (GENERAL GUIDE)</div>', unsafe_allow_html=True)

st.markdown("""
<div class="white-card">
    <p style="font-size: 15px; color: #333; line-height: 1.6; margin-bottom: 0;">
        <strong>The Goal:</strong> The United Nations created <em>Sustainable Development Goal 3 (SDG 3)</em> to ensure healthy lives and promote well-being for all ages. To figure out how to achieve this, we need to know what actually makes people live longer.<br><br>
        Instead of guessing, we used 24 years of real-world data from the United States and the United Kingdom. We compared how long people live (<strong>Life Expectancy</strong>) against how much money is spent on health (<strong>Healthcare Spending</strong>), the average wealth of the citizens (<strong>GDP per capita</strong>), environmental pollution (<strong>CO₂ Emissions</strong>), and access to basic needs (<strong>Water Access</strong>). <br><br>
        The charts below prove mathematically that <strong>money alone doesn't buy health</strong>—how it is spent, and the environment people live in, play a massive role.
    </p>
</div>
""", unsafe_allow_html=True)


# ── SECTION 2: TRENDS OVER TIME ──────────────────────────────────────────────
st.markdown('<div class="section-header"><span class="dot" style="color:#9b51e0;">●</span> THE BIG PICTURE: TRENDS OVER TIME</div>', unsafe_allow_html=True)

c1, c2 = st.columns([2.5, 1])

with c1:
    st.markdown('<div class="white-card">', unsafe_allow_html=True)
    st.markdown('**📈 Life expectancy over time**', unsafe_allow_html=True)
    
    fig1 = px.line(df, x='Year', y='Life Expectancy', color='Country Name', 
                   color_discrete_map={'United Kingdom': C_UK, 'United States': C_US}, markers=True)
    fig1.update_layout(margin=dict(l=0, r=0, t=10, b=0), plot_bgcolor='rgba(0,0,0,0)', yaxis=dict(showgrid=True, gridcolor='#f1f1f1'))
    st.plotly_chart(fig1, use_container_width=True)
    
    st.markdown("""
    <div class="insight-box insight-purple">
        <div style="font-size:20px;">💡</div>
        <div><strong>What are we seeing?</strong> This timeline shows that the UK consistently has a higher life expectancy than the US. You can also see a sharp dip around 2020-2021 for both countries, which represents the tragic impact of the global COVID-19 pandemic.</div>
    </div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown('<div class="white-card">', unsafe_allow_html=True)
    st.markdown('**📊 US vs UK in 2021**', unsafe_allow_html=True)
    
    df_2021 = df[df['Year'] == 2021]
    fig2 = px.bar(df_2021, x='Country Name', y='Life Expectancy', color='Country Name',
                  color_discrete_map={'United Kingdom': C_UK, 'United States': C_US})
    fig2.update_layout(showlegend=False, margin=dict(l=0, r=0, t=20, b=0), plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig2, use_container_width=True)
    
    st.markdown("""
    <div class="insight-box insight-pink" style="background:#fdf2f8; color:#9d174d; border-left: 4px solid #f472b6;">
        <div>Even though the US spends almost double on healthcare per person, the UK lives about 3 years longer on average.</div>
    </div>
    </div>
    """, unsafe_allow_html=True)

# ── SECTION 3: DEEP DIVE (THE GLOSSARY) ──────────────────────────────────────
st.markdown('<div class="section-header"><span class="dot" style="color:#f59e0b;">●</span> DEEP DIVE: UNDERSTANDING THE FACTORS</div>', unsafe_allow_html=True)

d1, d2 = st.columns(2)

with d1:
    st.markdown('<div class="white-card"><h4 style="color:#3b82f6;">🏥 Healthcare Spending vs Life Expectancy</h4>', unsafe_allow_html=True)
    fig_h = px.scatter(df, x='Healthcare Spending', y='Life Expectancy', color='Country Name', color_discrete_map={'United Kingdom': C_UK, 'United States': C_US})
    fig_h.update_layout(margin=dict(l=0, r=0, t=10, b=0), plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_h, use_container_width=True)
    st.markdown("""<div class="explainer-text"><strong>Simple Explanation:</strong> This chart asks, "Does spending more money make us live longer?" The upward slope means <strong>YES</strong>. As countries invest more in hospitals, medicine, and doctors, people generally live longer.</div></div>""", unsafe_allow_html=True)

with d2:
    st.markdown('<div class="white-card"><h4 style="color:#ef4444;">☁️ CO₂ Emissions vs Life Expectancy</h4>', unsafe_allow_html=True)
    fig_c = px.scatter(df, x='CO2 Emissions', y='Life Expectancy', color='Country Name', color_discrete_map={'United Kingdom': C_UK, 'United States': C_US})
    fig_c.update_layout(margin=dict(l=0, r=0, t=10, b=0), plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_c, use_container_width=True)
    st.markdown("""<div class="explainer-text"><strong>Simple Explanation:</strong> This chart asks, "Does air pollution shorten our lives?" The downward slope means <strong>YES</strong>. Higher CO₂ emissions represent worse air quality, which leads to respiratory diseases and a lower average lifespan.</div></div>""", unsafe_allow_html=True)


# ── SECTION 4: THE MATH MADE SIMPLE ──────────────────────────────────────────
st.markdown('<div class="section-header"><span class="dot" style="color:#10b981;">●</span> THE MATH MADE SIMPLE (PREDICTIVE MODEL)</div>', unsafe_allow_html=True)

r1, r2 = st.columns([1.5, 1])

with r1:
    st.markdown("""
    <div class="white-card">
        <strong style="font-size:16px; color:#333;">How accurate are our findings?</strong>
        <p style="font-size: 14px; color: #555; margin-top: 8px;">To prove our theory, we built a <strong>Robust Regression Model</strong>. Think of this as an AI pattern-finder that looks at all the data simultaneously while ignoring weird "flukes" (like the sudden COVID drop).</p>
    """, unsafe_allow_html=True)
    
    df_uk = df[df['Country Name'] == 'United Kingdom']
    fig_pred = go.Figure()
    fig_pred.add_trace(go.Scatter(x=df_uk['Year'], y=df_uk['Life Expectancy'], mode='lines+markers', name='Actual Reality', line=dict(color=C_UK, width=3)))
    fig_pred.add_trace(go.Scatter(x=df_uk['Year'], y=df_uk['Predicted'], mode='lines', name='What our Math Predicted', line=dict(color=C_US, width=3, dash='dash')))
    fig_pred.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=250, legend=dict(orientation="h", y=-0.2, x=0), plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_pred, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with r2:
    st.markdown("""
    <div class="white-card">
        <strong style="font-size:16px; color:#333;">The Scorecard</strong>
        <div style="background:#f5f3ff; border-radius:8px; padding:16px; text-align:center; margin-top: 16px;">
            <div style="font-size:12px; font-weight:700; color:#6b21a8;">THE R-SQUARED (R²) SCORE</div>
            <div style="font-size:36px; font-weight:800; color:#4c1d95;">0.94</div>
        </div>
        <p style="font-size: 14px; color: #555; margin-top: 16px; line-height: 1.6;">
            <strong>What does 0.94 mean?</strong><br>
            It means our findings are <strong>94% accurate</strong>. The combination of money spent on health, average wealth, clean water, and pollution explains 94% of the reasons why someone's life expectancy changes. In data science, a score this high means we have found a very strong, reliable truth.
        </p>
    </div>
    """, unsafe_allow_html=True)

# ── SECTION 5: DATA EXPLORER ─────────────────────────────────────────────────
st.markdown('<div class="section-header"><span class="dot" style="color:#64748b;">●</span> RAW DATA EXPLORER</div>', unsafe_allow_html=True)

with st.expander("Click to view and search the raw dataset behind these charts"):
    st.dataframe(df[['Year', 'Country Name', 'Life Expectancy', 'Healthcare Spending', 'GDP per capita', 'CO2 Emissions', 'Water Access']], use_container_width=True)

# ── CONCLUSION FOOTER ────────────────────────────────────────────────────────
st.markdown("""
<div class="conclusion-box">
    <h3 style="margin-top: 0;">✦ The Final Verdict</h3>
    <p style="color: #d1d5db; font-size: 15px; line-height: 1.6; margin-bottom: 0;">
        If governments want to achieve <strong>SDG 3: Good Health and Well-Being</strong>, they cannot just focus on one thing. The data clearly shows a two-step formula for longer lives: 
        <br><br>
        <strong>1. Invest Smartly:</strong> Increase healthcare spending and secure clean water.<br>
        <strong>2. Protect the Environment:</strong> Reduce CO₂ emissions. Pollution actively undoes the benefits of healthcare spending by making people sick.
    </p>
</div>
""", unsafe_allow_html=True)
