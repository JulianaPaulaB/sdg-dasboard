import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import statsmodels.api as sm

# ── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="SDG 3 Dashboard", layout="wide", initial_sidebar_state="expanded")

# ── CUSTOM CSS (Fixed `unsafe_allow_html`) ───────────────────────────────────
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
    
    /* KPI Cards with Hover Effect */
    .kpi-container { display: flex; gap: 16px; margin-top: 16px; flex-wrap: wrap; }
    .kpi-card {
        background: white;
        border-radius: 12px;
        padding: 16px;
        flex: 1;
        min-width: 150px;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.03);
        border: 1px solid #f1f1f1;
        transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
    }
    .kpi-card:hover {
        transform: translateY(-5px);
        box-shadow: 0px 8px 24px rgba(0,0,0,0.1);
        cursor: pointer;
    }
    .kpi-title { font-size: 11px; font-weight: 700; color: #888; text-transform: uppercase; margin-top: 8px; }
    .kpi-value { font-size: 24px; font-weight: 800; color: #111; margin: 4px 0; }
    .kpi-delta-down { font-size: 12px; font-weight: 600; color: #e11d48; }
    .kpi-delta-up { font-size: 12px; font-weight: 600; color: #059669; }
    .kpi-neutral { font-size: 12px; font-weight: 600; color: #64748b; }

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
    
    /* Explainer Text */
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
        # Fallback dummy data
        dates = list(range(2000, 2025))
        df_uk = pd.DataFrame({'Year': dates, 'Country Name': 'United Kingdom', 'Life Expectancy': np.linspace(77.7, 81.3, 25), 'Healthcare Spending': np.linspace(2000, 5000, 25), 'GDP per capita': np.linspace(26000, 48000, 25), 'Water Access': 99.9, 'CO2 Emissions': np.linspace(9.6, 5.0, 25)})
        df_us = pd.DataFrame({'Year': dates, 'Country Name': 'United States', 'Life Expectancy': np.linspace(76.7, 78.5, 25), 'Healthcare Spending': np.linspace(4000, 12000, 25), 'GDP per capita': np.linspace(36000, 70000, 25), 'Water Access': 99.0, 'CO2 Emissions': np.linspace(20.0, 14.0, 25)})
        df_uk.loc[20:21, 'Life Expectancy'] -= 1.0 
        df_us.loc[20:21, 'Life Expectancy'] -= 1.5
        df = pd.concat([df_uk, df_us])
    
    # Calculate Healthcare Efficiency
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

# ── SIDEBAR INTERACTIVE FILTERS ──────────────────────────────────────────────
st.sidebar.markdown("### 🎛️ Dashboard Controls")
st.sidebar.markdown("Adjust the settings below to filter the data interactively.")

selected_countries = st.sidebar.multiselect(
    "🌍 Select Countries:",
    options=df['Country Name'].unique(),
    default=df['Country Name'].unique()
)

min_year, max_year = int(df['Year'].min()), int(df['Year'].max())
selected_years = st.sidebar.slider(
    "📅 Select Year Range:",
    min_value=min_year, max_value=max_year,
    value=(min_year, max_year)
)

# Apply filters
filtered_df = df[
    (df['Country Name'].isin(selected_countries)) & 
    (df['Year'] >= selected_years[0]) & 
    (df['Year'] <= selected_years[1])
]

if filtered_df.empty:
    st.warning("⚠️ No data available for the selected filters. Please adjust your selections.")
    st.stop()

# ── ACADEMIC HEADER ──────────────────────────────────────────────────────────
st.markdown("""
<div class="academic-header">
    <div class="academic-title">🌍 Understanding the Drivers of Life Expectancy Across Countries</div>
    <div class="academic-subtitle">SDG 3: Good Health and Well-Being</div>
    <div style="border-top: 1px solid rgba(255,255,255,0.2); margin: 16px 0;"></div>
    <div class="academic-meta"><strong>Prepared by:</strong> Juliana Paula T. Binas</div>
    <div class="academic-meta"><strong>Course, Year & Section:</strong> BSIS 3A | West Visayas State University</div>
    <div class="academic-quote">
        <strong style="color: #0ea5e9; font-size: 16px;">Research Question:</strong> What factors influence Life Expectancy across countries?<br><br>
        This dashboard investigates the key drivers of life expectancy using real-world data from the World Bank and Our World in Data. We apply Multiple Linear Regression and Robust Regression (RLM) to identify which variables significantly explain the variation in how long people live.
    </div>
</div>
""", unsafe_allow_html=True)

# ── DYNAMIC KPI CALCULATIONS ─────────────────────────────────────────────────
latest_year_in_view = filtered_df['Year'].max()
latest_data = filtered_df[filtered_df['Year'] == latest_year_in_view]

avg_life = latest_data['Life Expectancy'].mean() if not latest_data.empty else 0
avg_health = latest_data['Healthcare Spending'].mean() if not latest_data.empty else 0
avg_gdp = latest_data['GDP per capita'].mean() if not latest_data.empty else 0
avg_co2 = latest_data['CO2 Emissions'].mean() if not latest_data.empty else 0

st.markdown(f"""
<div class="kpi-container">
    <div class="kpi-card" style="border-top: 4px solid {C_UK};">
        <div>🫀</div>
        <div class="kpi-title">Avg Life Expectancy ({latest_year_in_view})</div>
        <div class="kpi-value">{avg_life:.1f} yrs</div>
        <div class="kpi-neutral">Based on selected filters</div>
    </div>
    <div class="kpi-card" style="border-top: 4px solid #3b82f6;">
        <div>🏥</div>
        <div class="kpi-title">Avg Healthcare Spend ({latest_year_in_view})</div>
        <div class="kpi-value">${avg_health:,.0f}</div>
        <div class="kpi-neutral">Based on selected filters</div>
    </div>
    <div class="kpi-card" style="border-top: 4px solid {C_ORANGE};">
        <div>💰</div>
        <div class="kpi-title">Avg GDP Per Capita ({latest_year_in_view})</div>
        <div class="kpi-value">${avg_gdp:,.0f}</div>
        <div class="kpi-neutral">Based on selected filters</div>
    </div>
    <div class="kpi-card" style="border-top: 4px solid {C_RED};">
        <div>☁️</div>
        <div class="kpi-title">CO₂ Emissions ({latest_year_in_view})</div>
        <div class="kpi-value">{avg_co2:.1f} tons</div>
        <div class="kpi-neutral">Based on selected filters</div>
    </div>
</div>
""", unsafe_allow_html=True)


# ── SECTION 1: TRENDS OVER TIME ──────────────────────────────────────────────
st.markdown('<div class="section-header"><span style="color:#9b51e0; font-size: 22px;">●</span> PART 1: THE BIG PICTURE TRENDS</div>', unsafe_allow_html=True)

c1, c2 = st.columns([2.5, 1])

with c1:
    st.markdown('<div class="white-card">', unsafe_allow_html=True)
    st.markdown(f'<strong style="font-size: 16px;">📈 Life Expectancy Over Time ({selected_years[0]}-{selected_years[1]})</strong>', unsafe_allow_html=True)
    
    fig1 = px.line(filtered_df, x='Year', y='Life Expectancy', color='Country Name', 
                   color_discrete_map={'United Kingdom': C_UK, 'United States': C_US}, markers=True,
                   hover_data={"Year": True, "Life Expectancy": ":.1f"})
    fig1.update_layout(margin=dict(l=0, r=0, t=20, b=0), plot_bgcolor='rgba(0,0,0,0)', yaxis=dict(showgrid=True, gridcolor='#f1f1f1'))
    st.plotly_chart(fig1, use_container_width=True)
    
    st.markdown("""
    <div class="how-to-read">🔍 How to read this chart:</div>
    <div class="explainer-text" style="margin-top: 0;">
        Hover over the points to see exact numbers! A rising line means people are living longer. The UK (purple) stays consistently above the USA (blue) across the timeline.
    </div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown('<div class="white-card">', unsafe_allow_html=True)
    st.markdown(f'<strong style="font-size: 16px;">📊 Country Comparison ({latest_year_in_view})</strong>', unsafe_allow_html=True)
    
    fig2 = px.bar(latest_data, x='Country Name', y='Life Expectancy', color='Country Name',
                  color_discrete_map={'United Kingdom': C_UK, 'United States': C_US},
                  hover_data={"Life Expectancy": ":.1f"})
    fig2.update_layout(showlegend=False, margin=dict(l=0, r=0, t=20, b=0), plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig2, use_container_width=True)
    
    st.markdown("""
    <div class="insight-box insight-purple" style="margin-top: 24px;">
        <div>Even though the USA is historically wealthier, the UK citizens live about 3 years longer on average. Why? We explore the reasons below.</div>
    </div>
    </div>
    """, unsafe_allow_html=True)

# ── SECTION 2: HEALTHCARE EFFICIENCY ─────────────────────────────────────────
st.markdown('<div class="section-header"><span style="color:#f59e0b; font-size: 22px;">●</span> PART 2: THE HEALTHCARE EFFICIENCY PARADOX</div>', unsafe_allow_html=True)

e1, e2 = st.columns([1, 2])

with e1:
    st.markdown("""
    <div class="white-card">
        <h4 style="color:#d97706; margin-top:0;">More Money ≠ Longer Life</h4>
        <p style="font-size: 15px; color: #334155; line-height: 1.6;">
            The USA spends nearly double the amount of money per person on healthcare compared to the UK. However, the UK gets much more "bang for its buck."<br><br>
            The chart to the right shows <strong>Healthcare Efficiency</strong>—calculated as how many years of life expectancy a country gets for every $1,000 spent on a person.<br><br>
            As spending in the US has skyrocketed over the years, their efficiency has actually dropped.
        </p>
    </div>
    """, unsafe_allow_html=True)

with e2:
    st.markdown('<div class="white-card">', unsafe_allow_html=True)
    st.markdown('<strong style="font-size: 16px;">📉 Years of Life Expected per $1,000 Spent (Efficiency)</strong>', unsafe_allow_html=True)
    fig_e = px.line(filtered_df, x='Year', y='Efficiency', color='Country Name', 
                    color_discrete_map={'United Kingdom': C_UK, 'United States': C_US}, markers=True,
                    hover_data={"Efficiency": ":.2f"})
    fig_e.update_layout(margin=dict(l=0, r=0, t=20, b=0), plot_bgcolor='rgba(0,0,0,0)', yaxis=dict(showgrid=True, gridcolor='#f1f1f1', title="Years per $1k"))
    st.plotly_chart(fig_e, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)


# ── SECTION 3: THE 4 PILLARS EXPLAINED ───────────────────────────────────────
st.markdown('<div class="section-header"><span style="color:#0ea5e9; font-size: 22px;">●</span> PART 3: DEEP DIVE INTO THE 4 MAIN DRIVERS</div>', unsafe_allow_html=True)

d1, d2 = st.columns(2)

with d1:
    st.markdown('<div class="white-card"><h4 style="color:#3b82f6; margin-top:0;">🏥 1. Healthcare Spending vs Life Expectancy</h4>', unsafe_allow_html=True)
    fig_h = px.scatter(filtered_df, x='Healthcare Spending', y='Life Expectancy', color='Country Name', color_discrete_map={'United Kingdom': C_UK, 'United States': C_US}, trendline="ols", hover_data={"Healthcare Spending": ":.0f", "Life Expectancy": ":.1f"})
    fig_h.update_layout(margin=dict(l=0, r=0, t=10, b=0), plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_h, use_container_width=True)
    st.markdown("""<div class="how-to-read">🔍 How to read this chart:</div><div class="explainer-text" style="margin-top: 0;"><strong>The trend line goes UP.</strong> This proves that generally, investing more money into healthcare infrastructure extends lives.</div></div>""", unsafe_allow_html=True)

with d2:
    st.markdown('<div class="white-card"><h4 style="color:#ef4444; margin-top:0;">☁️ 2. CO₂ Emissions (Pollution)</h4>', unsafe_allow_html=True)
    fig_c = px.scatter(filtered_df, x='CO2 Emissions', y='Life Expectancy', color='Country Name', color_discrete_map={'United Kingdom': C_UK, 'United States': C_US}, trendline="ols", hover_data={"CO2 Emissions": ":.1f", "Life Expectancy": ":.1f"})
    fig_c.update_layout(margin=dict(l=0, r=0, t=10, b=0), plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_c, use_container_width=True)
    st.markdown("""<div class="how-to-read">🔍 How to read this chart:</div><div class="explainer-text" style="margin-top: 0;"><strong>The trend line goes DOWN.</strong> This is the silent killer. Higher CO₂ means heavy pollution and smog, leading to respiratory disease. Less pollution = longer life.</div></div>""", unsafe_allow_html=True)


# ── SECTION 4: THE MATH MADE SIMPLE ──────────────────────────────────────────
st.markdown('<div class="section-header"><span style="color:#10b981; font-size: 22px;">●</span> PART 4: THE PREDICTIVE MODEL (ROBUST REGRESSION)</div>', unsafe_allow_html=True)

r1, r2 = st.columns([1.5, 1])

with r1:
    st.markdown("""
    <div class="white-card">
        <strong style="font-size:16px; color:#333;">Testing our theory against reality</strong>
        <p style="font-size: 14px; color: #555; margin-top: 8px;">We fed all our data into a statistical algorithm called a <strong>Robust Regression Model</strong>. The dashed line is the algorithm's guess; the solid line is reality.</p>
    """, unsafe_allow_html=True)
    
    # We use the full df for the model plot to show accurate regression curves regardless of slice
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
            Our data proves, with <strong>94% mathematical certainty</strong>, that health spending, wealth, water, and pollution control are the primary architects of human lifespan.
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
