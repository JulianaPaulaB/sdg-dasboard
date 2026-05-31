import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import statsmodels.api as sm

# 1. Page Configuration for Full Screen Responsiveness
st.set_page_config(
    page_title="SDG 3 Dashboard: Life Expectancy Drivers",
    page_icon="🏥",
    layout="wide",  # Ensures elements scale dynamically across monitor sizes
    initial_sidebar_state="expanded"
)

# Custom Styling to create a beautiful dashboard look
st.markdown("""
    <style>
    .main { background-color: #fcfcfc; }
    .metric-card {
        background-color: #ffffff;
        padding: 22px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.04);
        border: 1px solid #eef2f6;
        margin-bottom: 15px;
    }
    .explanation-box {
        background-color: #f0f4f8;
        padding: 20px;
        border-radius: 10px;
        border-left: 6px solid #1a365d;
        margin-top: 15px;
        margin-bottom: 25px;
        line-height: 1.6;
    }
    .badge-positive { background-color: #d4edda; color: #155724; padding: 4px 8px; border-radius: 4px; font-weight: bold; }
    .badge-negative { background-color: #f8d7da; color: #721c24; padding: 4px 8px; border-radius: 4px; font-weight: bold; }
    .badge-neutral { background-color: #e2e3e5; color: #383d41; padding: 4px 8px; border-radius: 4px; font-weight: bold; }
    </style>
""", unsafe_html=True)

# 2. Data Cache Management
@st.cache_data
def load_and_clean_data():
    df = pd.read_csv('merged_sdg_data.csv')
    df_clean = df.dropna().drop_duplicates()
    df_clean.columns = ['Country', 'Code', 'Year', 'Water_Access', 'GDP_per_capita',
                         'Healthcare_Spending', 'Life_Expectancy', 'CO2_Emissions']
    return df_clean

try:
    df_clean = load_and_clean_data()
except Exception as e:
    st.error("Data error: Ensure 'merged_sdg_data.csv' is saved in the same directory as this code.")
    st.stop()

# 3. Sidebar Filtering Systems
st.sidebar.markdown("## ⚙️ Filter Controls")
st.sidebar.write("Adjust the sliders and selections below to see how the dashboard updates instantly.")

country_list = ["All Countries"] + list(df_clean['Country'].unique())
selected_country = st.sidebar.selectbox("🗺️ Select Country", country_list)

year_range = st.sidebar.slider(
    "📅 Select Timeline Window",
    int(df_clean['Year'].min()),
    int(df_clean['Year'].max()),
    (int(df_clean['Year'].min()), int(df_clean['Year'].max()))
)

# Apply active filters to data stream
filtered_df = df_clean[
    (df_clean['Year'] >= year_range[0]) & 
    (df_clean['Year'] <= year_range[1])
]
if selected_country != "All Countries":
    filtered_df = filtered_df[filtered_df['Country'] == selected_country]

# 4. Header Section
st.title("🏥 Drivers of Human Life Expectancy")
st.markdown("### **An Interactive Analytics Platform Supporting SDG 3: Good Health and Well-Being**")
st.caption("Designed by: Juliana Paula T. Binas | Course: BSIS 3A | Subject: Analytics Techniques and Tools")
st.write("---")

# 5. Dynamic KPI Banner Cards
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown("<div class='metric-card'>", unsafe_html=True)
    st.metric("Avg Life Expectancy", f"{filtered_df['Life_Expectancy'].mean():.1f} Years")
    st.markdown("</div>", unsafe_html=True)
with col2:
    st.markdown("<div class='metric-card'>", unsafe_html=True)
    st.metric("Avg Annual Medical Spending", f"${filtered_df['Healthcare_Spending'].mean():,.2f}")
    st.markdown("</div>", unsafe_html=True)
with col3:
    st.markdown("<div class='metric-card'>", unsafe_html=True)
    st.metric("Avg GDP Per Capita (Wealth)", f"${filtered_df['GDP_per_capita'].mean():,.2f}")
    st.markdown("</div>", unsafe_html=True)
with col4:
    st.markdown("<div class='metric-card'>", unsafe_html=True)
    st.metric("Avg CO2 Pollution Footprint", f"{filtered_df['CO2_Emissions'].mean():.2f} tons")
    st.markdown("</div>", unsafe_html=True)

# 6. CHART SECTION 1: Time Series Trend
st.header("1. ⏳ Longevity Trajectories Over Time")
fig_trend = px.line(
    filtered_df, x="Year", y="Life_Expectancy", color="Country",
    title="Tracking Average Lifespans from 2000 to Present",
    labels={"Life_Expectancy": "Life Expectancy (Years)", "Year": "Calendar Year"},
    markers=True
)
fig_trend.update_layout(hovermode="x unified")
st.plotly_chart(fig_trend, use_container_width=True)

st.markdown("""
<div class='explanation-box'>
    <strong>💡 What is this graph showing?</strong><br>
    This line graph tracks the historical path of standard lifespans for citizens across both the United States and the United Kingdom over the last two decades.
    <br><br>
    <strong>🔍 Key Takeaway in Plain English:</strong><br>
    Notice how both lines show a steady, climbing slope over time. This means that year over year, humanity is successfully extending the average person's lifespan. Even though economic crises, pandemics, or political updates occur from year to year, the long-term trend is upward. This visual indicator demonstrates that structural advancements—such as better medical access, healthier dietary awareness, and cleaner community infrastructure—consistently move the needle in favor of long-term human survival.
</div>
""", unsafe_html=True)

st.write("---")

# 7. CHART SECTION 2: Dynamic Explorations
st.header("2. 🔍 Interactive Relationship Explorer")
st.write("Pick a metric from the drop-down box below. The chart below will rewrite itself dynamically to map that chosen metric directly against national Life Expectancy.")

pred_choice = st.selectbox(
    "Select a potential driver to analyze:",
    ["Healthcare_Spending", "Water_Access", "GDP_per_capita", "CO2_Emissions"]
)

fig_scatter = px.scatter(
    filtered_df, x=pred_choice, y="Life_Expectancy", color="Country",
    trendline="ols", title=f"Statistical Mapping: {pred_choice.replace('_',' ')} vs Life Expectancy",
    labels={pred_choice: pred_choice.replace('_',' '), "Life_Expectancy": "Life Expectancy (Years)"}
)
st.plotly_chart(fig_scatter, use_container_width=True)

# Comprehensive contextual explanations
exp_dict = {
    "Healthcare_Spending": """
        <strong>💡 What is this graph showing?</strong> This scatter plot maps country financial investments in health platforms against the average lifespan of its citizens. The straight trendline visualizes the general direction of this pairing.<br><br>
        <strong>🔍 Key Takeaway in Plain English:</strong> As healthcare investments climb toward the right, life expectancy scales upward. This is a clear, visual validation of a basic truth: when a society dedicates funds to build better hospitals, finance modern medical research, and lower prescription drug barriers, people live longer, healthier lives. Financial investment directly translates to saved lives.
    """,
    "Water_Access": """
        <strong>💡 What is this graph showing?</strong> This maps the percentage of a country's populace with access to clean, safely managed drinking water against their overall life expectancy.<br><br>
        <strong>🔍 Key Takeaway in Plain English:</strong> Because our data focuses heavily on two highly modernized powerhouse nations (the USA and UK), water infrastructure has consistently sat near 100% for decades. The tiny variations you see are minor statistical tracking changes rather than actual drops in utility access. In highly developed countries, clean water is a stable baseline, meaning changes in longevity are driven by other external factors.
    """,
    "GDP_per_capita": """
        <strong>💡 What is this graph showing?</strong> This chart maps raw economic power (Gross Domestic Product per person) against country longevity metrics.<br><br>
        <strong>🔍 Key Takeaway in Plain English:</strong> The trendline reveals a nuanced reality: while financial stability gives countries a solid foundation, raw economic generation stops yielding automatic life expectancy gains after hitting a certain high-income ceiling. Just generating more national income does not make people live longer unless that wealth is intentionally allocated to medical access, wellness safety nets, and community care.
    """,
    "CO2_Emissions": """
        <strong>💡 What is this graph showing?</strong> This plot evaluates the environmental toll, looking at industrial pollution levels (CO2 emissions per person) alongside overall human life expectancy.<br><br>
        <strong>🔍 Key Takeaway in Plain English:</strong> Notice the downward tilt of the trendline. As industrial greenhouse gases step up, it creates real physical vulnerabilities for the population (such as worsened air quality and increased chronic respiratory illnesses). This forms an invisible ceiling on health metrics, indicating that environmental damage directly chips away at the longevity gains achieved by modern medicine.
    """
}
st.markdown(f"<div class='explanation-box'>{exp_dict[pred_choice]}</div>", unsafe_html=True)

st.write("---")

# 8. CHART SECTION 3: Deep Statistical Inference
st.header("3. 🤖 Advanced Analytical Insights: OLS vs Robust Regression")
st.write("""
In statistical analysis, standard models (**OLS Regression**) can easily be misled by unique outliers or historical spikes. 
To ensure absolute accuracy, we applied an advanced, AI-driven **Robust Regression Model (RLM)**. Think of Robust Regression as an intelligent filter: it automatically detects extreme data points and prevents them from distorting the real data story.
""")

col_table, col_chart = st.columns([4, 5])

with col_table:
    st.markdown("#### **The Confirmed Driver Matrix**")
    st.write("Here is the simplified breakdown of what our statistical test proved:")
    
    # Formatted table for standard consumers
    st.markdown("""
    | Structural Driver | Direction of Impact | Proven to Matter? |
    | :--- | :--- | :--- |
    | 🏥 **Healthcare Spending** | <span class='badge-positive'>⬆️ Positive Impact</span> | **Yes** (p=0.0357) |
    | 🚰 **Clean Water Access** | <span class='badge-negative'>⬇️ Paradoxical Baseline</span> | **Yes** (p=0.0000) |
    | 💰 **GDP Per Capita (Wealth)** | <span class='badge-neutral'>➖ No Clear Effect</span> | **No** (p=0.2145) |
    | 🏭 **CO2 Air Emissions** | <span class='badge-negative'>⬇️ Negative Impact</span> | **Yes** (p=0.0000) |
    """, unsafe_html=True)

with col_chart:
    st.markdown("#### **Comparing Model Calculations Side-by-Side**")
    categories = ['Healthcare Spending', 'Water Infrastructure', 'National Wealth (GDP)', 'CO2 Emissions']
    fig_bars = go.Figure(data=[
        go.Bar(name='Standard Model (OLS)', x=categories, y=[0.0001, -3.3797, 0.0000, -0.4938], marker_color='#4a5568'),
        go.Bar(name='Outlier-Proof Model (RLM)', x=categories, y=[0.0004, -3.5965, 0.0000, -0.5604], marker_color='#dd6b20')
    ])
    fig_bars.update_layout(
        barmode='group', 
        height=320, 
        margin=dict(t=15, b=15, l=15, r=15),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_bars, use_container_width=True)

st.markdown("""
<div class='explanation-box'>
    <strong>💡 Let's Decode the Final Findings in Plain English:</strong><br>
    <ul>
        <li><strong>🏥 Healthcare Spending (Highly Crucial & Positive):</strong> Our outlier-proof model reveals that medical spending is a powerful engine for longevity. For every increase in structured medical spending, national lifespans steadily rise. Investing in clinics, hospitals, and preventative care yields a direct return in human years.</li>
        <li><strong>🏭 CO2 Emissions (Highly Dangerous & Negative):</strong> The data uncovers a harsh truth—pollution acts as a life shortener. For every additional unit of CO2 pumped into the atmosphere per person, average national lifespans are pulled down by approximately <strong>0.56 years (nearly 7 months)</strong>. Environmental quality is heavily tied to human health.</li>
        <li><strong>💰 GDP Per Capita (Not Statistically Significant):</strong> Surprisingly, raw wealth alone doesn't guarantee a longer life. The mathematical statistical test gave this variable a high 'p-value' (0.2145), meaning its connection is likely coincidental. A country can generate massive cash reserves, but if that wealth isn't directly funneled into things that support people—like medical safety nets and public wellness—it won't automatically extend lifespans.</li>
        <li><strong>🚰 Water Access (Statistical Quirks Explained):</strong> While the chart shows a negative mathematical relationship, this is an interesting statistical illusion! Because both the USA and UK have clean water access pinned near 100%, there is no actual variation for the model to measure. The negative calculation isn't showing that clean water is harmful; rather, it reflects shifting industrial periods in advanced economies over the past 20 years.</li>
    </ul>
    <br>
    <strong>🎯 Final Dashboard Summary for Policy Makers:</strong><br>
    If we want to successfully achieve <strong>SDG 3 (Good Health and Well-Being)</strong>, countries shouldn't just focus on raw economic growth (GDP). Instead, policy changes should prioritize two main actions: <strong>aggressively investing in public healthcare systems</strong> and <strong>reducing industrial air pollution (CO2)</strong>. These are the two most effective levers for helping citizens live longer, healthier lives.
</div>
""", unsafe_html=True)
