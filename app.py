import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import statsmodels.api as sm

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SDG 3: Life Expectancy Dashboard",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Colors ─────────────────────────────────────────────────────────────────────
PURPLE  = "#7c3aed"
BLUE    = "#0ea5e9"
GREEN   = "#10b981"
DARK    = "#1a1a2e"
GRAY    = "#6b7280"
LIGHT_BG= "#f8fafc"

COUNTRY_COLORS = {
    "United Kingdom": PURPLE,
    "United States":  BLUE
}

# ── Custom CSS for Responsiveness & Styling ────────────────────────────────────
st.markdown(f"""
<style>
    /* Global background and font */
    html, body, [data-testid="stAppViewContainer"] {{
        background-color: {LIGHT_BG};
        font-family: 'Inter', 'Segoe UI', sans-serif;
    }}
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {{
        background-color: {DARK} !important;
    }}
    [data-testid="stSidebar"] * {{
        color: white !important;
    }}
    
    /* Clean up metric cards */
    [data-testid="stMetricValue"] {{
        font-size: 1.8rem !important;
        font-weight: 700 !important;
    }}
    
    /* Explanation Boxes */
    .explanation-box {{
        background-color: white;
        padding: 16px;
        border-radius: 8px;
        border-left: 4px solid {GREEN};
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        margin-bottom: 24px;
        font-size: 14px;
        color: #334155;
    }}
    
    .conclusion-box {{
        background-color: {DARK};
        color: white;
        padding: 24px;
        border-radius: 12px;
        margin-top: 32px;
    }}
</style>
""", unsafe_allow_html=True)

# ── Data Loading ───────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    # Load the merged dataset
    df = pd.read_csv("merged_sdg_data.csv")
    return df

try:
    df = load_data()
except FileNotFoundError:
    st.error("Dataset 'merged_sdg_data.csv' not found. Please ensure it is in the same directory as this script.")
    st.stop()

# ── Sidebar Filters ────────────────────────────────────────────────────────────
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/a/a8/Sustainable_Development_Goal_3.svg/512px-Sustainable_Development_Goal_3.svg.png", width=150)
st.sidebar.markdown("## Dashboard Filters")

selected_countries = st.sidebar.multiselect(
    "Select Countries:",
    options=df['Country Name'].unique(),
    default=["United Kingdom", "United States"]
)

min_year = int(df['Year'].min())
max_year = int(df['Year'].max())
selected_years = st.sidebar.slider(
    "Select Year Range:",
    min_value=min_year, max_value=max_year,
    value=(min_year, max_year)
)

# Filter dataset based on selection
filtered_df = df[
    (df['Country Name'].isin(selected_countries)) & 
    (df['Year'] >= selected_years[0]) & 
    (df['Year'] <= selected_years[1])
]

# ── Header ─────────────────────────────────────────────────────────────────────
st.title("🌍 SDG 3: Good Health and Well-Being")
st.markdown("### What actually drives Life Expectancy?")
st.markdown("This dashboard explores the relationship between economic investments, environmental factors, and how long people live.")
st.divider()

if filtered_df.empty:
    st.warning("No data available for the selected filters.")
    st.stop()

# ── Top Level Metrics (KPIs) ───────────────────────────────────────────────────
# Calculate averages for the selected period
latest_year = filtered_df['Year'].max()
latest_data = filtered_df[filtered_df['Year'] == latest_year]

col1, col2, col3, col4 = st.columns(4)
with col1:
    avg_life = latest_data['Life Expectancy'].mean()
    st.metric(f"Avg Life Expectancy ({latest_year})", f"{avg_life:.1f} Yrs")
with col2:
    avg_health = latest_data['Healthcare Spending'].mean()
    st.metric(f"Avg Health Spend ({latest_year})", f"${avg_health:,.0f}")
with col3:
    avg_co2 = latest_data['CO2 Emissions'].mean()
    st.metric(f"Avg CO₂ Emissions ({latest_year})", f"{avg_co2:.1f} T")
with col4:
    avg_gdp = latest_data['GDP per capita'].mean()
    st.metric(f"Avg GDP per Capita ({latest_year})", f"${avg_gdp:,.0f}")

st.markdown("<br>", unsafe_allow_html=True)

# ── Main Charts (Row 1) ────────────────────────────────────────────────────────
col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.markdown("#### 📈 Life Expectancy Over Time")
    fig_line = px.line(
        filtered_df, x="Year", y="Life Expectancy", color="Country Name",
        color_discrete_map=COUNTRY_COLORS, markers=True
    )
    fig_line.update_layout(margin=dict(l=0, r=0, t=30, b=0), plot_bgcolor="white")
    # use_container_width=True ensures full responsiveness
    st.plotly_chart(fig_line, use_container_width=True)
    
    st.markdown("""
    <div class="explanation-box">
        <strong>What does this mean?</strong><br>
        Think of this as a simple timeline. It tracks how the average lifespan has gone up or down over the years. A steadily rising line is great news—it means healthcare, safety, and general living conditions are improving in that country.
    </div>
    """, unsafe_allow_html=True)

with col_chart2:
    st.markdown("#### 💰 Does Healthcare Spending Matter?")
    fig_scatter = px.scatter(
        filtered_df, x="Healthcare Spending", y="Life Expectancy", color="Country Name",
        color_discrete_map=COUNTRY_COLORS, trendline="ols"
    )
    fig_scatter.update_layout(margin=dict(l=0, r=0, t=30, b=0), plot_bgcolor="white")
    st.plotly_chart(fig_scatter, use_container_width=True)

    st.markdown("""
    <div class="explanation-box">
        <strong>What does this mean?</strong><br>
        Does throwing money at healthcare actually help people live longer? This chart plots spending against lifespan. Because the lines slope upwards, we can see a clear reward: higher financial investment in health generally results in citizens living longer lives.
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Main Charts (Row 2) ────────────────────────────────────────────────────────
col_chart3, col_chart4 = st.columns(2)

with col_chart3:
    st.markdown("#### 🏭 The Impact of CO₂ Emissions")
    fig_co2 = px.scatter(
        filtered_df, x="CO2 Emissions", y="Life Expectancy", color="Country Name",
        color_discrete_map=COUNTRY_COLORS, trendline="ols"
    )
    fig_co2.update_layout(margin=dict(l=0, r=0, t=30, b=0), plot_bgcolor="white")
    st.plotly_chart(fig_co2, use_container_width=True)
    
    st.markdown("""
    <div class="explanation-box">
        <strong>What does this mean?</strong><br>
        Here we look at the environment's role. We are comparing carbon emissions (pollution) to life expectancy. The downward trend suggests a warning: higher pollution levels in the air are linked to lower average lifespans, likely due to respiratory and environmental health issues.
    </div>
    """, unsafe_allow_html=True)

with col_chart4:
    st.markdown("#### 💧 Water Access & Lifespan")
    fig_water = px.box(
        filtered_df, x="Country Name", y="Water Access", color="Country Name",
        color_discrete_map=COUNTRY_COLORS
    )
    fig_water.update_layout(margin=dict(l=0, r=0, t=30, b=0), plot_bgcolor="white", showlegend=False)
    st.plotly_chart(fig_water, use_container_width=True)
    
    st.markdown("""
    <div class="explanation-box">
        <strong>What does this mean?</strong><br>
        Access to clean drinking water is a fundamental human right. For highly developed nations like the US and UK, this box plot shows that water access remains near 100%. Because it's so consistently high, it acts as a stable foundation rather than a fluctuating driver for these specific countries.
    </div>
    """, unsafe_allow_html=True)

# ── Conclusion Box ─────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="conclusion-box">
    <h3 style="color: white; margin-top: 0;">The Bottom Line 📌</h3>
    <p style="font-size: 16px; line-height: 1.6;">
        Through our analysis, the data tells a very clear story. <strong>Investing in healthcare works.</strong> We see a direct, positive link between the dollars spent on health infrastructure and the years added to a person's life.<br><br>
        However, economic progress has a double edge. <strong>Environmental damage hurts our health.</strong> Rising CO₂ emissions consistently show a negative impact on life expectancy. To truly achieve the goals of <em>SDG 3: Good Health and Well-Being</em>, countries cannot just rely on spending money on hospitals; they must also actively protect the air their citizens breathe.
    </p>
</div>
""", unsafe_allow_html=True)

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="text-align:center;padding:32px 0 16px;font-size:12px;color:{GRAY}">
    <strong>SDG 3 Life Expectancy Dashboard</strong> &nbsp;·&nbsp; Juliana Paula T. Binas &nbsp;·&nbsp; BSIS 3A<br>
    Data Sources: World Bank Open Data · Our World in Data &nbsp;·&nbsp; Analytics Techniques and Tools
</div>
""", unsafe_allow_html=True)
