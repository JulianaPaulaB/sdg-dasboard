import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SDG 3: Life Expectancy Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── SDG 3 Theme Colors ─────────────────────────────────────────────────────────
# SDG 3 official color is green (#4C9F38)
SDG_GREEN      = "#4C9F38"
SDG_DARK_GREEN = "#2d6a22"
SDG_LIGHT_GREEN= "#e8f5e2"
WHITE          = "#ffffff"
LIGHT_BG       = "#f4faf2"
TEXT_DARK      = "#1a2e18"
TEXT_GRAY      = "#5f6368"
ACCENT_BLUE    = "#1a73e8"
ACCENT_RED     = "#ea4335"
ACCENT_YELLOW  = "#f9ab00"
ACCENT_TEAL    = "#00897b"

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
    /* Main background */
    .stApp {{
        background-color: {LIGHT_BG};
        font-family: 'Segoe UI', Arial, sans-serif;
    }}

    /* Sidebar */
    [data-testid="stSidebar"] {{
        background-color: {SDG_DARK_GREEN} !important;
    }}
    [data-testid="stSidebar"] * {{
        color: white !important;
    }}
    [data-testid="stSidebar"] .stSlider label {{
        color: white !important;
        font-weight: 600;
    }}

    /* Metric cards */
    [data-testid="stMetric"] {{
        background-color: {WHITE};
        border-radius: 12px;
        padding: 16px 20px;
        border-left: 5px solid {SDG_GREEN};
        box-shadow: 0 2px 8px rgba(0,0,0,0.07);
    }}
    [data-testid="stMetricLabel"] {{
        color: {TEXT_GRAY} !important;
        font-size: 12px !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    [data-testid="stMetricValue"] {{
        color: {SDG_DARK_GREEN} !important;
        font-size: 22px !important;
        font-weight: 700 !important;
    }}

    /* Section headers */
    .section-title {{
        font-size: 17px;
        font-weight: 700;
        color: {SDG_DARK_GREEN};
        border-left: 5px solid {SDG_GREEN};
        padding-left: 12px;
        margin: 24px 0 14px 0;
    }}

    /* Divider */
    hr {{
        border: none;
        border-top: 2px solid {SDG_LIGHT_GREEN};
        margin: 20px 0;
    }}

    /* Chart containers */
    .chart-card {{
        background: {WHITE};
        border-radius: 14px;
        padding: 16px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }}

    /* Hide Streamlit default elements */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
</style>
""", unsafe_allow_html=True)

# ── Load Data ──────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv('merged_sdg_data.csv')
    df.columns = ['Country', 'Code', 'Year', 'Water_Access', 'GDP_per_capita',
                  'Healthcare_Spending', 'Life_Expectancy', 'CO2_Emissions']
    df = df.dropna()
    df['Year'] = df['Year'].astype(int)
    return df

df = load_data()
years = sorted(df['Year'].unique())
countries = sorted(df['Country'].unique())
color_map = {
    'United Kingdom': SDG_GREEN,
    'United States':  ACCENT_BLUE
}

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="
    background: linear-gradient(135deg, {SDG_DARK_GREEN} 0%, {SDG_GREEN} 100%);
    padding: 28px 36px;
    border-radius: 16px;
    margin-bottom: 24px;
    box-shadow: 0 4px 16px rgba(44,106,34,0.25);
">
    <div style="display:flex; align-items:center; gap:16px;">
        <div style="
            background:white;
            border-radius:50%;
            width:58px; height:58px;
            display:flex; align-items:center; justify-content:center;
            font-size:28px; flex-shrink:0;
        ">3</div>
        <div>
            <h1 style="color:white; margin:0; font-size:24px; font-weight:800; letter-spacing:0.3px;">
                SDG 3: Good Health and Well-Being
            </h1>
            <p style="color:rgba(255,255,255,0.88); margin:5px 0 0 0; font-size:13px;">
                Drivers of Life Expectancy Across Countries &nbsp;|&nbsp;
                Juliana Paula T. Binas &nbsp;|&nbsp; BSIS 3A &nbsp;|&nbsp; Analytics Techniques and Tools
            </p>
        </div>
    </div>
    <div style="
        background:rgba(255,255,255,0.15);
        border-radius:10px;
        padding:10px 16px;
        margin-top:16px;
        font-size:13px;
        color:white;
    ">
        <b>Research Question:</b> What factors influence Life Expectancy across countries?
        &nbsp;&nbsp;|&nbsp;&nbsp;
        <b>Data Source:</b> World Bank Open Data &amp; Our World in Data
        &nbsp;&nbsp;|&nbsp;&nbsp;
        <b>Period:</b> 2000 – 2024
    </div>
</div>
""", unsafe_allow_html=True)

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style="text-align:center; padding:16px 0 8px 0;">
        <div style="
            background:rgba(255,255,255,0.15);
            border-radius:50%;
            width:64px; height:64px;
            margin:0 auto 10px auto;
            display:flex; align-items:center; justify-content:center;
            font-size:32px;
        ">3</div>
        <h3 style="color:white; margin:0; font-size:16px;">SDG 3 Dashboard</h3>
        <p style="color:rgba(255,255,255,0.7); font-size:11px; margin:4px 0 0 0;">Good Health and Well-Being</p>
    </div>
    <hr style="border-color:rgba(255,255,255,0.2); margin:12px 0;">
    """, unsafe_allow_html=True)

    st.markdown("<p style='color:white; font-weight:700; font-size:13px; margin-bottom:6px;'>SELECT YEAR</p>", unsafe_allow_html=True)
    selected_year = st.slider(
        "Year",
        min_value=years[0],
        max_value=years[-1],
        value=years[-1],
        step=1,
        label_visibility="collapsed"
    )

    st.markdown("<hr style='border-color:rgba(255,255,255,0.2); margin:16px 0;'>", unsafe_allow_html=True)
    st.markdown("<p style='color:white; font-weight:700; font-size:13px; margin-bottom:6px;'>SELECT COUNTRIES</p>", unsafe_allow_html=True)
    selected_countries = st.multiselect(
        "Countries",
        options=countries,
        default=countries,
        label_visibility="collapsed"
    )

    st.markdown(f"""
    <hr style="border-color:rgba(255,255,255,0.2); margin:16px 0;">
    <div style="font-size:11px; color:rgba(255,255,255,0.7); line-height:1.6;">
        <b style="color:white;">Key Drivers (from Regression)</b><br><br>
        Healthcare Spending — <span style="color:#a8e6a3;">Positive</span><br>
        Water Access — <span style="color:#a8e6a3;">Positive</span><br>
        GDP per Capita — <span style="color:#a8e6a3;">Positive</span><br>
        CO2 Emissions — <span style="color:#ff9999;">Negative</span>
    </div>
    """, unsafe_allow_html=True)

# ── Filter Data ────────────────────────────────────────────────────────────────
dff_year    = df[(df['Year'] == selected_year) & (df['Country'].isin(selected_countries))]
dff_all     = df[df['Country'].isin(selected_countries)]

if dff_year.empty:
    st.warning("No data available for the selected filters. Please adjust your selection.")
    st.stop()

# ── KPI Cards ──────────────────────────────────────────────────────────────────
st.markdown(f"<div class='section-title'>Key Indicators for {selected_year}</div>", unsafe_allow_html=True)

k1, k2, k3, k4, k5 = st.columns(5)

# Compute deltas vs previous year
prev_year_df = df[(df['Year'] == selected_year - 1) & (df['Country'].isin(selected_countries))]

def get_delta(col):
    if prev_year_df.empty:
        return None
    return round(dff_year[col].mean() - prev_year_df[col].mean(), 2)

k1.metric("Avg Life Expectancy",
          f"{dff_year['Life_Expectancy'].mean():.2f} yrs",
          delta=f"{get_delta('Life_Expectancy'):+.2f} yrs" if get_delta('Life_Expectancy') is not None else None)

k2.metric("Healthcare Spending",
          f"${dff_year['Healthcare_Spending'].mean():,.0f}",
          delta=f"${get_delta('Healthcare_Spending'):+,.0f}" if get_delta('Healthcare_Spending') is not None else None)

k3.metric("GDP per Capita",
          f"${dff_year['GDP_per_capita'].mean():,.0f}",
          delta=f"${get_delta('GDP_per_capita'):+,.0f}" if get_delta('GDP_per_capita') is not None else None)

k4.metric("CO2 Emissions",
          f"{dff_year['CO2_Emissions'].mean():.2f} tons",
          delta=f"{get_delta('CO2_Emissions'):+.2f} tons" if get_delta('CO2_Emissions') is not None else None,
          delta_color="inverse")

k5.metric("Water Access",
          f"{dff_year['Water_Access'].mean():.2f}%",
          delta=f"{get_delta('Water_Access'):+.2f}%" if get_delta('Water_Access') is not None else None)

st.markdown("<hr>", unsafe_allow_html=True)

# ── Row 1: Trend Line + Country Bar ───────────────────────────────────────────
st.markdown("<div class='section-title'>Trends Over Time & Country Comparison</div>", unsafe_allow_html=True)

col_left, col_right = st.columns([2, 1])

with col_left:
    fig_trend = px.line(
        dff_all, x='Year', y='Life_Expectancy', color='Country',
        title='Life Expectancy Over Time by Country',
        markers=True,
        color_discrete_map=color_map,
        labels={'Life_Expectancy': 'Life Expectancy (years)', 'Year': 'Year'}
    )
    fig_trend.add_vline(
        x=selected_year,
        line_dash='dash',
        line_color='rgba(76,159,56,0.6)',
        line_width=2,
        annotation_text=f'Selected: {selected_year}',
        annotation_font_color=SDG_DARK_GREEN,
        annotation_position='top right'
    )
    fig_trend.update_layout(
        plot_bgcolor=WHITE, paper_bgcolor=WHITE,
        title_font_size=14, title_font_color=TEXT_DARK,
        legend_title_text='Country',
        margin=dict(t=45, b=30, l=40, r=20),
        hovermode='x unified',
        font=dict(family='Segoe UI, Arial')
    )
    fig_trend.update_xaxes(showgrid=True, gridcolor='#f0f0f0')
    fig_trend.update_yaxes(showgrid=True, gridcolor='#f0f0f0')
    st.plotly_chart(fig_trend, use_container_width=True)

with col_right:
    fig_bar = px.bar(
        dff_year, x='Country', y='Life_Expectancy',
        title=f'Life Expectancy by Country ({selected_year})',
        color='Country',
        color_discrete_map=color_map,
        text_auto='.2f',
        labels={'Life_Expectancy': 'Life Expectancy (years)'}
    )
    fig_bar.update_traces(textposition='outside', textfont_size=12)
    fig_bar.update_layout(
        plot_bgcolor=WHITE, paper_bgcolor=WHITE,
        title_font_size=14, showlegend=False,
        margin=dict(t=45, b=30, l=40, r=20),
        font=dict(family='Segoe UI, Arial'),
        yaxis_range=[70, dff_year['Life_Expectancy'].max() + 3]
    )
    fig_bar.update_xaxes(showgrid=False)
    fig_bar.update_yaxes(showgrid=True, gridcolor='#f0f0f0')
    st.plotly_chart(fig_bar, use_container_width=True)

st.markdown("<hr>", unsafe_allow_html=True)

# ── Row 2: Key Driver Scatter Plots ───────────────────────────────────────────
st.markdown("<div class='section-title'>Key Drivers vs Life Expectancy (Regression Insights)</div>", unsafe_allow_html=True)
st.caption("Scatter plots show the relationship between each significant driver and Life Expectancy. Trendlines are based on OLS regression.")

col_a, col_b, col_c = st.columns(3)

scatter_config = [
    ('GDP_per_capita',       'GDP per Capita (USD)',       f'GDP per Capita vs Life Expectancy', ACCENT_BLUE,   'Positive driver — wealthier nations live longer (Preston, 1975)'),
    ('CO2_Emissions',        'CO2 Emissions (tons/capita)','CO2 Emissions vs Life Expectancy',   ACCENT_RED,    'Negative driver — pollution reduces life quality (Wen et al., 2021)'),
    ('Healthcare_Spending',  'Healthcare Spending (USD)',  'Healthcare Spending vs Life Expectancy', SDG_GREEN, 'Positive driver — more investment, better outcomes (Jaba et al., 2014)'),
]

for col_widget, (x_var, x_label, title, color, insight) in zip([col_a, col_b, col_c], scatter_config):
    with col_widget:
        fig_s = px.scatter(
            dff_all, x=x_var, y='Life_Expectancy',
            color='Country',
            animation_frame='Year',
            title=title,
            trendline='ols',
            color_discrete_map=color_map,
            labels={x_var: x_label, 'Life_Expectancy': 'Life Expectancy (years)'}
        )
        fig_s.update_layout(
            plot_bgcolor=WHITE, paper_bgcolor=WHITE,
            title_font_size=13, showlegend=False,
            margin=dict(t=45, b=30, l=40, r=20),
            font=dict(family='Segoe UI, Arial')
        )
        fig_s.update_xaxes(showgrid=True, gridcolor='#f0f0f0')
        fig_s.update_yaxes(showgrid=True, gridcolor='#f0f0f0')
        st.plotly_chart(fig_s, use_container_width=True)
        st.markdown(f"<p style='font-size:11px; color:{TEXT_GRAY}; margin-top:-10px; text-align:center;'>{insight}</p>", unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# ── Row 3: Multi-line Drivers Over Time ───────────────────────────────────────
st.markdown("<div class='section-title'>All Drivers Over Time</div>", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs([
    "Healthcare Spending",
    "GDP per Capita",
    "Water Access",
    "CO2 Emissions"
])

driver_tabs = [
    (tab1, 'Healthcare_Spending', 'Healthcare Spending (USD)',      SDG_GREEN),
    (tab2, 'GDP_per_capita',      'GDP per Capita (USD)',           ACCENT_BLUE),
    (tab3, 'Water_Access',        'Access to Clean Water (%)',      ACCENT_TEAL),
    (tab4, 'CO2_Emissions',       'CO2 Emissions (tons per capita)',ACCENT_RED),
]

for tab, col, label, color in driver_tabs:
    with tab:
        fig_d = px.line(
            dff_all, x='Year', y=col, color='Country',
            markers=True,
            color_discrete_map=color_map,
            labels={col: label, 'Year': 'Year'},
            title=f'{label} Over Time'
        )
        fig_d.add_vline(
            x=selected_year,
            line_dash='dash',
            line_color='rgba(76,159,56,0.5)',
            annotation_text=f'{selected_year}',
            annotation_position='top right',
            annotation_font_color=SDG_DARK_GREEN
        )
        fig_d.update_layout(
            plot_bgcolor=WHITE, paper_bgcolor=WHITE,
            margin=dict(t=45, b=30, l=40, r=20),
            font=dict(family='Segoe UI, Arial'),
            hovermode='x unified'
        )
        fig_d.update_xaxes(showgrid=True, gridcolor='#f0f0f0')
        fig_d.update_yaxes(showgrid=True, gridcolor='#f0f0f0')
        st.plotly_chart(fig_d, use_container_width=True)

st.markdown("<hr>", unsafe_allow_html=True)

# ── Row 4: Side-by-side Country Detail Table ──────────────────────────────────
st.markdown(f"<div class='section-title'>Country Data Summary for {selected_year}</div>", unsafe_allow_html=True)

display_df = dff_year[['Country', 'Life_Expectancy', 'Healthcare_Spending',
                         'GDP_per_capita', 'CO2_Emissions', 'Water_Access']].copy()
display_df.columns = ['Country', 'Life Expectancy (yrs)', 'Healthcare Spending (USD)',
                       'GDP per Capita (USD)', 'CO2 Emissions (tons)', 'Water Access (%)']
display_df = display_df.set_index('Country')
display_df = display_df.round(2)

st.dataframe(
    display_df.style
        .format({
            'Life Expectancy (yrs)': '{:.2f}',
            'Healthcare Spending (USD)': '${:,.2f}',
            'GDP per Capita (USD)': '${:,.2f}',
            'CO2 Emissions (tons)': '{:.2f}',
            'Water Access (%)': '{:.2f}%'
        })
        .background_gradient(cmap='Greens', subset=['Life Expectancy (yrs)'])
        .background_gradient(cmap='Blues',  subset=['Healthcare Spending (USD)', 'GDP per Capita (USD)'])
        .background_gradient(cmap='Reds',   subset=['CO2 Emissions (tons)'], low=1),
    use_container_width=True
)

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="
    background: linear-gradient(135deg, {SDG_DARK_GREEN} 0%, {SDG_GREEN} 100%);
    border-radius: 12px;
    padding: 18px 28px;
    margin-top: 28px;
    text-align: center;
">
    <p style="color:white; margin:0; font-size:13px; font-weight:600;">
        SDG 3: Good Health and Well-Being Dashboard
    </p>
    <p style="color:rgba(255,255,255,0.8); margin:4px 0 0 0; font-size:11px;">
        Juliana Paula T. Binas &nbsp;|&nbsp; BSIS 3A &nbsp;|&nbsp; Analytics Techniques and Tools &nbsp;|&nbsp;
        Data Sources: World Bank Open Data, Our World in Data
    </p>
</div>
""", unsafe_allow_html=True)
