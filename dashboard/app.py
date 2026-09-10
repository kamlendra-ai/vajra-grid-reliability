import streamlit as st
import pandas as pd


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Vajra | Grid Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>

.main {
    background-color: #f7f9fc;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

.hero {
    padding: 25px 30px;
    border-radius: 18px;
    background: linear-gradient(
        135deg,
        #0f172a 0%,
        #1e293b 100%
    );
    color: white;
    margin-bottom: 25px;
}

.hero h1 {
    font-size: 42px;
    margin-bottom: 5px;
}

.hero p {
    font-size: 17px;
    color: #cbd5e1;
}

.section-title {
    font-size: 25px;
    font-weight: 700;
    margin-top: 25px;
    margin-bottom: 15px;
}

.status-safe {
    background: #dcfce7;
    color: #166534;
    padding: 8px 15px;
    border-radius: 20px;
    font-weight: 700;
    display: inline-block;
}

.status-watch {
    background: #fef9c3;
    color: #854d0e;
    padding: 8px 15px;
    border-radius: 20px;
    font-weight: 700;
    display: inline-block;
}

.status-high {
    background: #ffedd5;
    color: #9a3412;
    padding: 8px 15px;
    border-radius: 20px;
    font-weight: 700;
    display: inline-block;
}

.status-critical {
    background: #fee2e2;
    color: #991b1b;
    padding: 8px 15px;
    border-radius: 20px;
    font-weight: 700;
    display: inline-block;
}

.alert-box {
    padding: 20px;
    border-radius: 14px;
    background: #fff1f2;
    border-left: 6px solid #dc2626;
    margin-bottom: 20px;
}

.info-box {
    padding: 20px;
    border-radius: 14px;
    background: #eff6ff;
    border-left: 6px solid #2563eb;
    margin-bottom: 20px;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# LOAD DATA
# ============================================================

df = pd.read_csv(
    "data/processed/vajra_intelligence.csv"
)

df["timestamp"] = pd.to_datetime(
    df["timestamp"]
)

df = df.sort_values(
    "timestamp"
).reset_index(drop=True)


# ============================================================
# LOAD 24-HOUR FORECAST
# ============================================================

forecast_file = (
    "data/processed/load_forecast_24h.csv"
)

try:
    forecast_df = pd.read_csv(
        forecast_file
    )

    forecast_df["timestamp"] = pd.to_datetime(
        forecast_df["timestamp"]
    )

except FileNotFoundError:
    forecast_df = pd.DataFrame()


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("⚡ Vajra")

st.sidebar.caption(
    "Grid Reliability Intelligence"
)

st.sidebar.divider()

view = st.sidebar.radio(
    "Dashboard View",
    [
        "Overview",
        "Risk Intelligence",
        "Grid Analytics"
    ]
)

st.sidebar.divider()

st.sidebar.info(
    "Prototype system demonstrated using "
    "synthetic grid telemetry."
)


# ============================================================
# CURRENT STATE
# ============================================================

latest = df.iloc[-1]

risk_score = float(
    latest["risk_score"]
)

risk_level = latest["risk_level"]

load = float(
    latest["load_mw"]
)

renewable = float(
    latest["renewable_supply_mw"]
)

gap = float(
    latest["supply_gap_mw"]
)

solar = float(
    latest["solar_mw"]
)

wind = float(
    latest["wind_mw"]
)

voltage = float(
    latest["voltage"]
)

frequency = float(
    latest["frequency"]
)

temperature = float(
    latest["temperature"]
)


# ============================================================
# STATUS
# ============================================================

if risk_score <= 30:

    status_class = "status-safe"
    status_icon = "🟢"

elif risk_score <= 60:

    status_class = "status-watch"
    status_icon = "🟡"

elif risk_score <= 80:

    status_class = "status-high"
    status_icon = "🟠"

else:

    status_class = "status-critical"
    status_icon = "🔴"


# ============================================================
# HERO
# ============================================================

st.markdown("""
<div class="hero">

<h1>⚡ Vajra Grid Intelligence</h1>

<p>
AI-driven predictive grid reliability and energy management
</p>

</div>
""", unsafe_allow_html=True)


# ============================================================
# OVERVIEW
# ============================================================

if view == "Overview":

    st.markdown(
        '<div class="section-title">'
        'Grid Command Center'
        '</div>',
        unsafe_allow_html=True
    )

    # ========================================================
    # KPI ROW
    # ========================================================

    c1, c2, c3, c4 = st.columns(4)

    with c1:

        st.metric(
            "Grid Risk Score",
            f"{risk_score:.1f}/100"
        )

        st.markdown(
            f'<span class="{status_class}">'
            f'{status_icon} {risk_level}'
            f'</span>',
            unsafe_allow_html=True
        )

    with c2:

        st.metric(
            "Current Load",
            f"{load:.1f} MW"
        )

    with c3:

        st.metric(
            "Renewable Supply",
            f"{renewable:.1f} MW"
        )

    with c4:

        st.metric(
            "Supply Gap",
            f"{gap:.1f} MW"
        )

    st.divider()

    # ========================================================
    # CURRENT GRID STATUS
    # ========================================================

    st.markdown(
        '<div class="section-title">'
        '🔍 Current Grid Status'
        '</div>',
        unsafe_allow_html=True
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:

        st.metric(
            "Voltage",
            f"{voltage:.2f} V"
        )

    with c2:

        st.metric(
            "Frequency",
            f"{frequency:.2f} Hz"
        )

    with c3:

        st.metric(
            "Solar",
            f"{solar:.1f} MW"
        )

    with c4:

        st.metric(
            "Wind",
            f"{wind:.1f} MW"
        )

    # ========================================================
    # 24-HOUR AI FORECAST
    # ========================================================

    st.markdown(
        '<div class="section-title">'
        '🔮 Vajra 24-Hour AI Load Forecast'
        '</div>',
        unsafe_allow_html=True
    )

    if not forecast_df.empty:

        peak_index = (
            forecast_df[
                "predicted_load_mw"
            ].idxmax()
        )

        peak_load = float(
            forecast_df.loc[
                peak_index,
                "predicted_load_mw"
            ]
        )

        peak_time = forecast_df.loc[
            peak_index,
            "timestamp"
        ]

        average_forecast = float(
            forecast_df[
                "predicted_load_mw"
            ].mean()
        )

        c1, c2, c3 = st.columns(3)

        with c1:

            st.metric(
                "Predicted Peak Load",
                f"{peak_load:.1f} MW"
            )

        with c2:

            st.metric(
                "Peak Time",
                peak_time.strftime(
                    "%d %b, %H:%M"
                )
            )

        with c3:

            st.metric(
                "Average Forecast Load",
                f"{average_forecast:.1f} MW"
            )

        forecast_chart = (
            forecast_df[
                [
                    "timestamp",
                    "predicted_load_mw"
                ]
            ]
            .set_index("timestamp")
        )

        forecast_chart.columns = [
            "Predicted Load (MW)"
        ]

        st.line_chart(
            forecast_chart,
            height=350
        )

        with st.expander(
            "View hourly forecast"
        ):

            display_forecast = (
                forecast_df.copy()
            )

            display_forecast["timestamp"] = (
                display_forecast[
                    "timestamp"
                ].dt.strftime(
                    "%d %b %H:%M"
                )
            )

            display_forecast[
                "predicted_load_mw"
            ] = (
                display_forecast[
                    "predicted_load_mw"
                ].round(2)
            )

            st.dataframe(
                display_forecast,
                use_container_width=True,
                hide_index=True
            )

    else:

        st.warning(
            "24-hour forecast is not available. "
            "Run forecast_24h.py first."
        )

    # ========================================================
    # LOAD VS RENEWABLE
    # ========================================================

    st.markdown(
        '<div class="section-title">'
        '📈 Load vs Renewable Generation'
        '</div>',
        unsafe_allow_html=True
    )

    days = st.slider(
        "Historical window",
        min_value=7,
        max_value=90,
        value=30,
        step=7
    )

    start_time = (
        df["timestamp"].max()
        - pd.Timedelta(days=days)
    )

    chart_df = (
        df[
            df["timestamp"] >= start_time
        ][
            [
                "timestamp",
                "load_mw",
                "renewable_supply_mw"
            ]
        ]
        .set_index("timestamp")
    )

    chart_df.columns = [
        "Grid Load (MW)",
        "Renewable Supply (MW)"
    ]

    st.line_chart(
        chart_df
    )

    # ========================================================
    # SUPPLY GAP + RISK
    # ========================================================

    c1, c2 = st.columns(2)

    with c1:

        st.markdown(
            '<div class="section-title">'
            '⚡ Supply-Demand Gap'
            '</div>',
            unsafe_allow_html=True
        )

        gap_chart = (
            df[
                df["timestamp"] >= start_time
            ][
                [
                    "timestamp",
                    "supply_gap_mw"
                ]
            ]
            .set_index("timestamp")
        )

        st.area_chart(
            gap_chart
        )

    with c2:

        st.markdown(
            '<div class="section-title">'
            '🚨 Risk Trend'
            '</div>',
            unsafe_allow_html=True
        )

        risk_chart = (
            df[
                df["timestamp"] >= start_time
            ][
                [
                    "timestamp",
                    "risk_score"
                ]
            ]
            .set_index("timestamp")
        )

        st.line_chart(
            risk_chart
        )


# ============================================================
# RISK INTELLIGENCE
# ============================================================

elif view == "Risk Intelligence":

    st.markdown(
        '<div class="section-title">'
        '🚨 Vajra Risk Intelligence'
        '</div>',
        unsafe_allow_html=True
    )

    c1, c2, c3 = st.columns(3)

    with c1:

        st.metric(
            "Current Risk",
            f"{risk_score:.1f}"
        )

    with c2:

        st.metric(
            "Average Risk",
            f"{df['risk_score'].mean():.1f}"
        )

    with c3:

        st.metric(
            "Maximum Risk",
            f"{df['risk_score'].max():.1f}"
        )

    st.divider()

    # ========================================================
    # RISK DISTRIBUTION
    # ========================================================

    st.markdown(
        '<div class="section-title">'
        'Risk Distribution'
        '</div>',
        unsafe_allow_html=True
    )

    risk_distribution = (
        df["risk_level"]
        .value_counts()
        .reindex(
            [
                "SAFE",
                "WATCH",
                "HIGH",
                "CRITICAL"
            ],
            fill_value=0
        )
    )

    st.bar_chart(
        risk_distribution
    )

    # ========================================================
    # CRITICAL EVENTS
    # ========================================================

    st.markdown(
        '<div class="section-title">'
        '🔴 Highest Risk Events'
        '</div>',
        unsafe_allow_html=True
    )

    critical = (
        df[
            [
                "timestamp",
                "load_mw",
                "renewable_supply_mw",
                "supply_gap_mw",
                "risk_score",
                "risk_level",
                "recommendation"
            ]
        ]
        .sort_values(
            "risk_score",
            ascending=False
        )
        .head(10)
    )

    st.dataframe(
        critical,
        use_container_width=True,
        hide_index=True
    )

    # ========================================================
    # WHY RISK?
    # ========================================================

    st.markdown(
        '<div class="section-title">'
        '🧠 Why is Vajra Watching?'
        '</div>',
        unsafe_allow_html=True
    )

    reasons = []

    if load > df["load_mw"].mean() * 1.15:

        reasons.append(
            "High electricity demand detected."
        )

    if solar < 5:

        reasons.append(
            "Solar generation is currently very low."
        )

    if gap > 100:

        reasons.append(
            "Supply-demand gap is elevated."
        )

    if latest["anomaly"] == 1:

        reasons.append(
            "Anomalous grid behavior detected."
        )

    if abs(voltage - 230) > 2:

        reasons.append(
            "Voltage deviation detected."
        )

    if abs(frequency - 50) > 0.15:

        reasons.append(
            "Frequency deviation detected."
        )

    if not reasons:

        reasons.append(
            "Current grid indicators are within "
            "normal operating ranges."
        )

    for reason in reasons:

        st.write(
            "✓",
            reason
        )


# ============================================================
# GRID ANALYTICS
# ============================================================

elif view == "Grid Analytics":

    st.markdown(
        '<div class="section-title">'
        '📊 Grid Analytics'
        '</div>',
        unsafe_allow_html=True
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:

        st.metric(
            "Average Load",
            f"{df['load_mw'].mean():.1f} MW"
        )

    with c2:

        st.metric(
            "Peak Load",
            f"{df['load_mw'].max():.1f} MW"
        )

    with c3:

        st.metric(
            "Average Gap",
            f"{df['supply_gap_mw'].mean():.1f} MW"
        )

    with c4:

        st.metric(
            "Critical Events",
            f"{(df['risk_level'] == 'CRITICAL').sum()}"
        )

    st.divider()

    # ========================================================
    # RENEWABLE ANALYTICS
    # ========================================================

    st.markdown(
        '<div class="section-title">'
        '☀️ Renewable Generation'
        '</div>',
        unsafe_allow_html=True
    )

    renewable_chart = (
        df[
            [
                "timestamp",
                "solar_mw",
                "wind_mw"
            ]
        ]
        .set_index("timestamp")
    )

    renewable_chart.columns = [
        "Solar (MW)",
        "Wind (MW)"
    ]

    st.line_chart(
        renewable_chart
    )

    # ========================================================
    # RECENT ALERTS
    # ========================================================

    st.markdown(
        '<div class="section-title">'
        '🚨 Recent Alerts'
        '</div>',
        unsafe_allow_html=True
    )

    alerts = (
        df[
            [
                "timestamp",
                "alert_level",
                "risk_score",
                "supply_gap_mw",
                "alert"
            ]
        ]
        .tail(20)
        .sort_values(
            "timestamp",
            ascending=False
        )
    )

    st.dataframe(
        alerts,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "⚡ Vajra — Predictive Grid Reliability Intelligence System | "
    "Prototype using synthetic grid telemetry"
)