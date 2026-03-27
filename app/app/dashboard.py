import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# ─── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Cost of Living vs Salary Tracker",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Syne:wght@400;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Space Grotesk', sans-serif;
    }
    .main { background-color: #0a0e1a; }
    .stApp { background: linear-gradient(135deg, #0a0e1a 0%, #0d1526 50%, #0a1628 100%); }

    .hero-title {
        font-family: 'Syne', sans-serif;
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, #00d4ff, #7b2fff, #00d4ff);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: shine 3s linear infinite;
        line-height: 1.1;
        margin-bottom: 0.3rem;
    }
    @keyframes shine {
        to { background-position: 200% center; }
    }
    .hero-sub {
        color: #8892a4;
        font-size: 1.05rem;
        font-weight: 400;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, rgba(255,255,255,0.05), rgba(255,255,255,0.02));
        border: 1px solid rgba(0, 212, 255, 0.15);
        border-radius: 16px;
        padding: 1.2rem 1.5rem;
        text-align: center;
        backdrop-filter: blur(10px);
        transition: border-color 0.3s;
    }
    .metric-card:hover { border-color: rgba(0, 212, 255, 0.4); }
    .metric-value {
        font-family: 'Syne', sans-serif;
        font-size: 2rem;
        font-weight: 700;
        color: #00d4ff;
    }
    .metric-label {
        font-size: 0.78rem;
        color: #8892a4;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-top: 0.2rem;
    }
    .section-title {
        font-family: 'Syne', sans-serif;
        font-size: 1.4rem;
        font-weight: 700;
        color: #e8eaf6;
        margin: 1.5rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid rgba(0, 212, 255, 0.2);
    }
    .rank-card {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 12px;
        padding: 0.8rem 1rem;
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        gap: 0.8rem;
    }
    .insight-box {
        background: linear-gradient(135deg, rgba(0,212,255,0.08), rgba(123,47,255,0.08));
        border: 1px solid rgba(0,212,255,0.2);
        border-radius: 12px;
        padding: 1rem 1.2rem;
        color: #c8d0e0;
        font-size: 0.9rem;
        line-height: 1.6;
        margin-bottom: 1rem;
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d1526, #0a1020);
        border-right: 1px solid rgba(0,212,255,0.1);
    }
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stMultiSelect label,
    [data-testid="stSidebar"] .stSlider label {
        color: #8892a4 !important;
        font-size: 0.82rem;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }
    div[data-testid="metric-container"] {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(0,212,255,0.15);
        border-radius: 12px;
        padding: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# ─── Load Data ─────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("data/cost_of_living.csv")
    df["savings_potential"] = df["avg_monthly_salary"] - df["total_living_cost"]
    df["savings_rate"] = (df["savings_potential"] / df["avg_monthly_salary"] * 100).round(1)
    df["salary_usd_k"] = (df["avg_monthly_salary"] / 1000).round(1)
    return df

df = load_data()

# ─── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🌍 Filters")
    st.markdown("---")

    regions = ["All Regions"] + sorted(df["region"].unique().tolist())
    selected_region = st.selectbox("Region", regions)

    filtered = df if selected_region == "All Regions" else df[df["region"] == selected_region]

    salary_min, salary_max = int(df["avg_monthly_salary"].min()), int(df["avg_monthly_salary"].max())
    salary_range = st.slider("Monthly Salary Range (USD)", salary_min, salary_max, (salary_min, salary_max), step=100)
    filtered = filtered[
        (filtered["avg_monthly_salary"] >= salary_range[0]) &
        (filtered["avg_monthly_salary"] <= salary_range[1])
    ]

    top_n = st.slider("Cities to Display", 5, 47, 20)
    color_by = st.selectbox("Color Charts By", ["region", "affordability_index", "savings_rate"])

    st.markdown("---")
    st.markdown("**📊 Dataset Stats**")
    st.markdown(f"<span style='color:#8892a4;font-size:0.85rem;'>{len(filtered)} cities · {filtered['region'].nunique()} regions</span>", unsafe_allow_html=True)

# ─── Header ────────────────────────────────────────────────────────────────────
st.markdown('<div class="hero-title">💰 Cost of Living vs Salary</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">Global affordability intelligence across 47 cities · Data Analyst Portfolio Project</div>', unsafe_allow_html=True)

# ─── KPI Row ───────────────────────────────────────────────────────────────────
c1, c2, c3, c4, c5 = st.columns(5)
kpis = [
    ("🏙️", f"{len(filtered)}", "Cities Tracked"),
    ("💵", f"${filtered['avg_monthly_salary'].mean():,.0f}", "Avg Monthly Salary"),
    ("🏠", f"${filtered['total_living_cost'].mean():,.0f}", "Avg Living Cost"),
    ("📈", f"{filtered['affordability_index'].mean():.2f}x", "Avg Affordability"),
    ("💾", f"{filtered['savings_rate'].mean():.0f}%", "Avg Savings Rate"),
]
for col, (icon, val, label) in zip([c1,c2,c3,c4,c5], kpis):
    with col:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size:1.6rem">{icon}</div>
            <div class="metric-value">{val}</div>
            <div class="metric-label">{label}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─── Tab Layout ────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["🗺️ World Map", "📊 Comparisons", "🏆 Rankings", "🔍 City Deep Dive"])

COLORS = {
    "bg": "#0a0e1a", "card": "rgba(255,255,255,0.03)",
    "cyan": "#00d4ff", "purple": "#7b2fff", "text": "#e8eaf6", "muted": "#8892a4"
}
PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color=COLORS["text"], family="Space Grotesk"),
    margin=dict(l=10, r=10, t=40, b=10),
    legend=dict(bgcolor="rgba(0,0,0,0.3)", bordercolor="rgba(255,255,255,0.1)", borderwidth=1)
)

# ─── Tab 1: World Map ──────────────────────────────────────────────────────────
with tab1:
    st.markdown('<div class="section-title">Global Affordability Map</div>', unsafe_allow_html=True)

    map_metric = st.radio("Map Metric", ["affordability_index", "avg_monthly_salary", "savings_rate", "total_living_cost"], horizontal=True,
                          format_func=lambda x: {"affordability_index":"Affordability","avg_monthly_salary":"Avg Salary","savings_rate":"Savings Rate","total_living_cost":"Living Cost"}[x])

    fig_map = px.scatter_geo(
        filtered.head(top_n),
        lat=filtered.head(top_n).apply(lambda _: None, axis=1),  # placeholder
        locations="country",
        locationmode="country names",
        size=map_metric,
        color=map_metric,
        hover_name="city",
        hover_data={"avg_monthly_salary": ":$,.0f", "total_living_cost": ":$,.0f", "affordability_index": ":.2f", "savings_rate": ":.1f"},
        color_continuous_scale=[[0,"#7b2fff"],[0.5,"#00d4ff"],[1,"#00ff88"]],
        title="",
        size_max=35,
    )
    fig_map.update_layout(**PLOTLY_LAYOUT, height=460,
        geo=dict(bgcolor="rgba(0,0,0,0)", showland=True, landcolor="#1a2035",
                 showocean=True, oceancolor="#0a0e1a", showframe=False,
                 coastlinecolor="rgba(255,255,255,0.1)", showcoastlines=True,
                 projection_type="natural earth"))
    st.plotly_chart(fig_map, use_container_width=True)

    st.markdown('<div class="insight-box">💡 <strong>Insight:</strong> Southeast Asian and Eastern European cities consistently show high affordability indexes despite lower nominal salaries. Cities like Bangalore, Seoul, and Warsaw offer strong value for money compared to Western counterparts.</div>', unsafe_allow_html=True)

# ─── Tab 2: Comparisons ────────────────────────────────────────────────────────
with tab2:
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown('<div class="section-title">Salary vs Living Cost</div>', unsafe_allow_html=True)
        top_df = filtered.nlargest(top_n, "avg_monthly_salary")
        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(name="Avg Monthly Salary", x=top_df["city"], y=top_df["avg_monthly_salary"],
            marker_color=COLORS["cyan"], opacity=0.9))
        fig_bar.add_trace(go.Bar(name="Total Living Cost", x=top_df["city"], y=top_df["total_living_cost"],
            marker_color=COLORS["purple"], opacity=0.9))
        fig_bar.update_layout(**PLOTLY_LAYOUT, barmode="group", height=380,
            xaxis=dict(tickangle=-40, gridcolor="rgba(255,255,255,0.05)"),
            yaxis=dict(gridcolor="rgba(255,255,255,0.05)", tickprefix="$"))
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_b:
        st.markdown('<div class="section-title">Salary vs Affordability Index</div>', unsafe_allow_html=True)
        fig_scatter = px.scatter(
            filtered, x="avg_monthly_salary", y="affordability_index",
            size="savings_rate", color=color_by, hover_name="city",
            hover_data={"avg_monthly_salary":":.0f","affordability_index":":.2f","savings_rate":":.1f"},
            color_continuous_scale=[[0,"#7b2fff"],[1,"#00d4ff"]] if color_by != "region" else None,
            size_max=30,
        )
        fig_scatter.add_hline(y=1.5, line_dash="dot", line_color="rgba(255,200,0,0.4)",
            annotation_text="Sweet Spot Threshold", annotation_font_color="#ffc800")
        fig_scatter.update_layout(**PLOTLY_LAYOUT, height=380,
            xaxis=dict(gridcolor="rgba(255,255,255,0.05)", tickprefix="$"),
            yaxis=dict(gridcolor="rgba(255,255,255,0.05)"))
        st.plotly_chart(fig_scatter, use_container_width=True)

    st.markdown('<div class="section-title">Cost Breakdown by Region</div>', unsafe_allow_html=True)
    cost_cols = ["rent_1br_center","groceries_monthly","transport_monthly","utilities_monthly","eating_out_avg"]
    cost_labels = ["Rent","Groceries","Transport","Utilities","Eating Out"]
    region_costs = filtered.groupby("region")[cost_cols].mean().reset_index()
    fig_region = go.Figure()
    colors_stack = ["#00d4ff","#7b2fff","#00ff88","#ff6b6b","#ffd93d"]
    for col, label, clr in zip(cost_cols, cost_labels, colors_stack):
        fig_region.add_trace(go.Bar(name=label, x=region_costs["region"], y=region_costs[col],
            marker_color=clr, opacity=0.85))
    fig_region.update_layout(**PLOTLY_LAYOUT, barmode="stack", height=340,
        xaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.05)", tickprefix="$"))
    st.plotly_chart(fig_region, use_container_width=True)

# ─── Tab 3: Rankings ───────────────────────────────────────────────────────────
with tab3:
    r1, r2 = st.columns(2)

    with r1:
        st.markdown('<div class="section-title">🥇 Most Affordable Cities</div>', unsafe_allow_html=True)
        top_afford = filtered.nlargest(10, "affordability_index")[["city","country","affordability_index","avg_monthly_salary","savings_rate"]]
        colors_rank = ["#ffd700","#c0c0c0","#cd7f32"] + ["#00d4ff"]*7
        for i, row in enumerate(top_afford.itertuples()):
            medal = ["🥇","🥈","🥉"][i] if i < 3 else f"#{i+1}"
            st.markdown(f"""
            <div class="rank-card">
                <span style="font-size:1.3rem;min-width:2rem">{medal}</span>
                <div style="flex:1">
                    <div style="color:#e8eaf6;font-weight:600">{row.city}, {row.country}</div>
                    <div style="color:#8892a4;font-size:0.8rem">Salary: ${row.avg_monthly_salary:,} · Savings: {row.savings_rate:.0f}%</div>
                </div>
                <div style="color:{colors_rank[i]};font-weight:700;font-size:1.1rem">{row.affordability_index:.2f}x</div>
            </div>""", unsafe_allow_html=True)

    with r2:
        st.markdown('<div class="section-title">💰 Highest Salary Cities</div>', unsafe_allow_html=True)
        top_sal = filtered.nlargest(10, "avg_monthly_salary")[["city","country","avg_monthly_salary","total_living_cost","savings_rate"]]
        for i, row in enumerate(top_sal.itertuples()):
            medal = ["🥇","🥈","🥉"][i] if i < 3 else f"#{i+1}"
            savings_color = "#00ff88" if row.savings_rate > 20 else "#ffd93d" if row.savings_rate > 0 else "#ff6b6b"
            st.markdown(f"""
            <div class="rank-card">
                <span style="font-size:1.3rem;min-width:2rem">{medal}</span>
                <div style="flex:1">
                    <div style="color:#e8eaf6;font-weight:600">{row.city}, {row.country}</div>
                    <div style="color:#8892a4;font-size:0.8rem">Cost: ${row.total_living_cost:,} · Savings: <span style="color:{savings_color}">{row.savings_rate:.0f}%</span></div>
                </div>
                <div style="color:#00d4ff;font-weight:700;font-size:1.1rem">${row.avg_monthly_salary:,}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-title">📉 Savings Rate by City (Top 20)</div>', unsafe_allow_html=True)
    sav_df = filtered.nlargest(20, "savings_rate").sort_values("savings_rate", ascending=True)
    bar_colors = ["#00ff88" if x > 30 else "#00d4ff" if x > 15 else "#ffd93d" if x > 0 else "#ff6b6b" for x in sav_df["savings_rate"]]
    fig_sav = go.Figure(go.Bar(
        x=sav_df["savings_rate"], y=sav_df["city"] + ", " + sav_df["country"],
        orientation="h", marker_color=bar_colors,
        text=[f"{v:.0f}%" for v in sav_df["savings_rate"]], textposition="outside",
        textfont=dict(color="#e8eaf6")
    ))
    fig_sav.update_layout(**PLOTLY_LAYOUT, height=420,
        xaxis=dict(gridcolor="rgba(255,255,255,0.05)", ticksuffix="%"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.05)"))
    st.plotly_chart(fig_sav, use_container_width=True)

# ─── Tab 4: City Deep Dive ─────────────────────────────────────────────────────
with tab4:
    st.markdown('<div class="section-title">🔍 City Deep Dive</div>', unsafe_allow_html=True)
    city_list = sorted(filtered["city"].tolist())
    sel_cities = st.multiselect("Compare Cities", city_list, default=city_list[:3] if len(city_list) >= 3 else city_list)

    if sel_cities:
        cmp = filtered[filtered["city"].isin(sel_cities)]

        # Radar Chart
        cats = ["Salary (norm)","Affordability","Savings Rate","Low Rent","Low Groceries"]
        fig_radar = go.Figure()
        radar_colors = ["#00d4ff","#7b2fff","#00ff88","#ff6b6b","#ffd93d"]
        for i, (_, row) in enumerate(cmp.iterrows()):
            vals = [
                row["avg_monthly_salary"] / df["avg_monthly_salary"].max() * 10,
                row["affordability_index"] / df["affordability_index"].max() * 10,
                max(0, row["savings_rate"]) / 100 * 10,
                (1 - row["rent_1br_center"] / df["rent_1br_center"].max()) * 10,
                (1 - row["groceries_monthly"] / df["groceries_monthly"].max()) * 10,
            ]
            fig_radar.add_trace(go.Scatterpolar(r=vals+[vals[0]], theta=cats+[cats[0]],
                fill="toself", name=row["city"],
                line_color=radar_colors[i % len(radar_colors)],
                fillcolor=radar_colors[i % len(radar_colors)].replace("ff","33") if "#" in radar_colors[i % len(radar_colors)] else radar_colors[i % len(radar_colors)],
                opacity=0.7))
        fig_radar.update_layout(**PLOTLY_LAYOUT, height=400,
            polar=dict(bgcolor="rgba(0,0,0,0)",
                radialaxis=dict(gridcolor="rgba(255,255,255,0.1)", range=[0,10], tickfont=dict(size=9)),
                angularaxis=dict(gridcolor="rgba(255,255,255,0.1)")))
        st.plotly_chart(fig_radar, use_container_width=True)

        # Comparison Table
        display_cols = ["city","country","avg_monthly_salary","total_living_cost","savings_potential","savings_rate","affordability_index"]
        display_labels = {"city":"City","country":"Country","avg_monthly_salary":"Monthly Salary","total_living_cost":"Living Cost","savings_potential":"Monthly Savings","savings_rate":"Savings %","affordability_index":"Affordability"}
        styled = cmp[display_cols].rename(columns=display_labels).style\
            .format({"Monthly Salary":"${:,.0f}","Living Cost":"${:,.0f}","Monthly Savings":"${:,.0f}","Savings %":"{:.1f}%","Affordability":"{:.2f}x"})\
            .background_gradient(subset=["Affordability","Savings %"], cmap="Blues")
        st.dataframe(styled, use_container_width=True, hide_index=True)
    else:
        st.info("Select at least one city to compare.")

# ─── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style="text-align:center; color:#8892a4; font-size:0.8rem; padding:1rem 0">
    Built with 🐍 Python · Streamlit · Plotly &nbsp;|&nbsp; 
    Data sources: Numbeo, World Bank, Kaggle &nbsp;|&nbsp;
    <strong style="color:#00d4ff">Data Analyst Portfolio Project</strong>
</div>
""", unsafe_allow_html=True)
