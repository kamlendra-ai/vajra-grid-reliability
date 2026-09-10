import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go


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
# LOAD 24-HOUR FUTURE RISK FORECAST
# ============================================================

future_risk_file = (
    "data/processed/future_risk_24h.csv"
)

try:
    future_risk_df = pd.read_csv(
        future_risk_file
    )

    future_risk_df["timestamp"] = pd.to_datetime(
        future_risk_df["timestamp"]
    )

except FileNotFoundError:
    future_risk_df = pd.DataFrame()


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
# LIVE WHAT-IF GRID STRESS SIMULATOR
# ============================================================

st.sidebar.divider()
st.sidebar.subheader("🎛️ Grid Stress Simulator")
st.sidebar.caption(
    "Run a controlled what-if scenario on the latest historical grid state."
)

# One-click demo presets for hackathon presentations.
scenario_presets = {
    "Custom": (0, 0, 1.00),
    "☁️ Cloudy Evening": (60, 10, 0.85),
    "📈 Peak Demand": (20, 30, 0.90),
    "🌪️ Renewable Stress": (75, 15, 0.65),
    "🚨 Extreme Grid Stress": (90, 45, 0.55),
}

selected_preset = st.sidebar.selectbox(
    "Scenario preset",
    list(scenario_presets.keys())
)

preset_solar, preset_load, preset_wind = scenario_presets[selected_preset]

if "scenario_preset" not in st.session_state:
    st.session_state.scenario_preset = selected_preset

if st.session_state.scenario_preset != selected_preset:
    st.session_state.scenario_preset = selected_preset
    st.session_state.solar_drop = preset_solar
    st.session_state.load_surge = preset_load
    st.session_state.wind_factor = preset_wind

if "solar_drop" not in st.session_state:
    st.session_state.solar_drop = preset_solar
if "load_surge" not in st.session_state:
    st.session_state.load_surge = preset_load
if "wind_factor" not in st.session_state:
    st.session_state.wind_factor = preset_wind

solar_drop = st.sidebar.slider(
    "☀️ Solar generation drop (%)", 0, 100, 0, 5, key="solar_drop"
)

load_surge = st.sidebar.slider(
    "📈 Load demand surge (%)", 0, 50, 0, 5, key="load_surge"
)

wind_factor = st.sidebar.slider(
    "🌬️ Wind generation factor", 0.50, 1.50, 1.00, 0.05, key="wind_factor"
)

scenario_active = (
    solar_drop > 0 or load_surge > 0 or wind_factor != 1.0
)

if scenario_active:
    st.sidebar.success("Scenario simulation ACTIVE")
else:
    st.sidebar.info("Baseline scenario")


# ============================================================
# CURRENT STATE
# ============================================================

latest = df.iloc[-1]

# Baseline values from the latest historical observation.
base_risk_score = float(latest["risk_score"])
base_risk_level = latest["risk_level"]

base_load = float(latest["load_mw"])
base_renewable = float(latest["renewable_supply_mw"])
base_gap = float(latest["supply_gap_mw"])
base_solar = float(latest["solar_mw"])
base_wind = float(latest["wind_mw"])
voltage = float(latest["voltage"])
frequency = float(latest["frequency"])
temperature = float(latest["temperature"])

# Apply controlled what-if changes.
simulated_load = base_load * (1 + load_surge / 100.0)
simulated_solar = base_solar * (1 - solar_drop / 100.0)
simulated_wind = base_wind * wind_factor
simulated_renewable = simulated_solar + simulated_wind
simulated_gap = max(0.0, simulated_load - simulated_renewable)

# Preserve Vajra's original multi-signal risk concept while adding
# transparent scenario pressure.
load_stress = min(100.0, (simulated_load / 200.0) * 100.0)
renewable_shortfall = min(
    100.0,
    (simulated_gap / max(simulated_load, 1.0)) * 100.0
)
voltage_score = min(100.0, abs(voltage - 230.0) / 10.0 * 100.0)
frequency_score = min(100.0, abs(frequency - 50.0) / 0.50 * 100.0)

if int(latest.get("anomaly", 0)) == 1:
    anomaly_score = 70.0
elif base_risk_level == "WATCH":
    anomaly_score = 30.0
else:
    anomaly_score = 0.0

core_risk = (
    0.30 * load_stress
    + 0.25 * renewable_shortfall
    + 0.15 * voltage_score
    + 0.15 * frequency_score
    + 0.15 * anomaly_score
)

scenario_pressure = (
    0.35 * (load_surge / 50.0) * 100.0
    + 0.25 * (solar_drop / 100.0) * 100.0
    + 0.15 * max(0.0, (1.0 - wind_factor) / 0.50) * 100.0
)

risk_score = float(np.clip(core_risk + scenario_pressure, 0, 100))

if risk_score <= 30:
    risk_level = "SAFE"
elif risk_score <= 60:
    risk_level = "WATCH"
elif risk_score <= 80:
    risk_level = "HIGH"
else:
    risk_level = "CRITICAL"

load = simulated_load
renewable = simulated_renewable
gap = simulated_gap
solar = simulated_solar
wind = simulated_wind


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

    if scenario_active:
        st.info(
            f"🧪 Scenario active — Solar {solar_drop}% drop | "
            f"Load +{load_surge}% | Wind factor {wind_factor:.2f}x"
        )

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
            "Latest Historical Load",
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
    # PRESCRIPTIVE DECISION ENGINE
    # ========================================================

    st.markdown(
        '<div class="section-title">🤖 Vajra Prescriptive Decision Engine</div>',
        unsafe_allow_html=True
    )

    if risk_level == "CRITICAL":
        alert_bg = "#fee2e2"
        alert_border = "#dc2626"
        recommendation = (
            "Activate available reserve capacity, prioritize critical feeders, "
            "and reduce non-essential flexible demand."
        )
        impact = "High grid-stress risk if the deficit persists."
    elif risk_level == "HIGH":
        alert_bg = "#ffedd5"
        alert_border = "#ea580c"
        recommendation = (
            "Prepare reserve capacity, optimize renewable dispatch, and "
            "consider demand-response actions for flexible loads."
        )
        impact = "Elevated grid stress; proactive intervention is recommended."
    elif risk_level == "WATCH":
        alert_bg = "#fef9c3"
        alert_border = "#ca8a04"
        recommendation = (
            "Increase monitoring, review reserve availability, and watch "
            "the next forecast window for worsening conditions."
        )
        impact = "Conditions are manageable but should be monitored."
    else:
        alert_bg = "#dcfce7"
        alert_border = "#16a34a"
        recommendation = "Maintain normal dispatch and continue routine monitoring."
        impact = "No major simulated grid stress detected."

    st.markdown(
        f"""
        <div style="
            padding:18px;
            border-radius:14px;
            background:{alert_bg};
            border-left:6px solid {alert_border};
            margin-bottom:18px;
        ">
            <b>ALERT LEVEL: {risk_level}</b><br><br>
            <b>Why:</b> Simulated load is {simulated_load:.1f} MW while
            renewable supply is {simulated_renewable:.1f} MW, producing a
            {simulated_gap:.1f} MW supply gap.<br>
            <b>Impact:</b> {impact}<br>
            <b>Recommended Action:</b> {recommendation}
        </div>
        """,
        unsafe_allow_html=True
    )

    # ========================================================
    # OPERATOR ACTION CHECKLIST
    # ========================================================

    st.markdown(
        '<div class="section-title">🎯 Operator Action Checklist</div>',
        unsafe_allow_html=True
    )

    actions = []
    if simulated_gap >= 150:
        actions.append("Escalate the supply deficit and prepare reserve capacity.")
    elif simulated_gap >= 100:
        actions.append("Review reserve availability and prepare demand-response actions.")
    else:
        actions.append("Continue monitoring the supply-demand balance.")

    if solar_drop >= 50:
        actions.append("Check renewable forecast and prepare for reduced solar contribution.")
    if load_surge >= 20:
        actions.append("Prioritize flexible-load management during the demand surge.")
    if wind_factor < 0.80:
        actions.append("Review wind-generation uncertainty and available balancing resources.")

    for i, action in enumerate(actions[:4], 1):
        st.write(f"**{i}.** {action}")

    # ========================================================
    # RISK EXPLAINABILITY
    # ========================================================

    st.markdown(
        '<div class="section-title">🧠 Risk Explainability</div>',
        unsafe_allow_html=True
    )

    risk_components = pd.DataFrame({
        "Factor": [
            "Load Stress",
            "Renewable Shortfall",
            "Voltage Deviation",
            "Frequency Deviation",
            "Anomaly Signal",
            "Scenario Pressure"
        ],
        "Contribution": [
            0.30 * load_stress,
            0.25 * renewable_shortfall,
            0.15 * voltage_score,
            0.15 * frequency_score,
            0.15 * anomaly_score,
            scenario_pressure
        ]
    }).sort_values("Contribution", ascending=True)

    fig_risk = go.Figure(go.Bar(
        x=risk_components["Contribution"],
        y=risk_components["Factor"],
        orientation="h",
        text=risk_components["Contribution"].round(1),
        textposition="auto"
    ))
    fig_risk.update_layout(
        xaxis_title="Risk contribution",
        yaxis_title="",
        height=330,
        margin=dict(l=20, r=20, t=20, b=20)
    )
    st.plotly_chart(fig_risk, use_container_width=True)

    # ========================================================
    # RESILIENCE INDICATORS
    # ========================================================

    st.markdown(
        '<div class="section-title">🛡️ Grid Resilience Indicators</div>',
        unsafe_allow_html=True
    )

    renewable_coverage = (
        simulated_renewable / simulated_load * 100
        if simulated_load > 0 else 0
    )
    reserve_need = max(simulated_gap * 0.20, 0)
    gap_ratio = (
        simulated_gap / simulated_load * 100
        if simulated_load > 0 else 0
    )

    r1, r2, r3 = st.columns(3)
    with r1:
        st.metric("Renewable Coverage", f"{renewable_coverage:.1f}%")
    with r2:
        st.metric("Estimated Reserve Need", f"{reserve_need:.1f} MW")
    with r3:
        st.metric("Gap / Load Ratio", f"{gap_ratio:.1f}%")

    # ========================================================
    # SCENARIO IMPACT
    # ========================================================

    st.markdown(
        '<div class="section-title">🧪 Scenario Impact Analysis</div>',
        unsafe_allow_html=True
    )

    scenario_data = pd.DataFrame({
        "Metric": ["Load", "Solar", "Wind", "Renewable Supply", "Supply Gap"],
        "Baseline": [
            base_load, base_solar, base_wind,
            base_renewable, base_gap
        ],
        "Simulated": [
            simulated_load, simulated_solar, simulated_wind,
            simulated_renewable, simulated_gap
        ]
    })

    fig_scenario = go.Figure()
    fig_scenario.add_trace(go.Bar(
        x=scenario_data["Metric"],
        y=scenario_data["Baseline"],
        name="Baseline"
    ))
    fig_scenario.add_trace(go.Bar(
        x=scenario_data["Metric"],
        y=scenario_data["Simulated"],
        name="Simulated"
    ))
    fig_scenario.update_layout(
        barmode="group",
        height=360,
        margin=dict(l=20, r=20, t=30, b=20)
    )
    st.plotly_chart(fig_scenario, use_container_width=True)

    # ========================================================
    # CURRENT GRID STATUS
    # ========================================================

    st.markdown(
        '<div class="section-title">'
        '🔍 Latest Historical Grid State'
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
    # 24-HOUR FUTURE RISK FORECAST
    # ========================================================

    st.markdown(
        '<div class="section-title">'
        '🚨 Vajra 24-Hour Future Risk Forecast'
        '</div>',
        unsafe_allow_html=True
    )

    if not future_risk_df.empty:

        risk_counts = (
            future_risk_df["risk_level"]
            .value_counts()
            .reindex(
                ["SAFE", "WATCH", "HIGH", "CRITICAL"],
                fill_value=0
            )
        )

        critical_rows = future_risk_df[
            future_risk_df["risk_level"] == "CRITICAL"
        ]

        high_rows = future_risk_df[
            future_risk_df["risk_level"] == "HIGH"
        ]

        if not critical_rows.empty:
            first_critical = critical_rows.iloc[0]
            st.error(
                f"🚨 Critical risk expected around "
                f"{first_critical['timestamp'].strftime('%d %b, %H:%M')} "
                f"with forecast risk {first_critical['risk_score']:.1f}/100."
            )
        elif not high_rows.empty:
            first_high = high_rows.iloc[0]
            st.warning(
                f"⚠️ Elevated risk expected around "
                f"{first_high['timestamp'].strftime('%d %b, %H:%M')} "
                f"with forecast risk {first_high['risk_score']:.1f}/100."
            )
        else:
            st.success(
                "🟢 No HIGH or CRITICAL risk is currently forecast "
                "in the next 24 hours."
            )

        rc1, rc2, rc3, rc4 = st.columns(4)

        with rc1:
            st.metric("SAFE Hours", int(risk_counts["SAFE"]))

        with rc2:
            st.metric("WATCH Hours", int(risk_counts["WATCH"]))

        with rc3:
            st.metric("HIGH Hours", int(risk_counts["HIGH"]))

        with rc4:
            st.metric("CRITICAL Hours", int(risk_counts["CRITICAL"]))

        risk_forecast_fig = go.Figure()

        risk_forecast_fig.add_trace(
            go.Scatter(
                x=future_risk_df["timestamp"],
                y=future_risk_df["risk_score"],
                mode="lines+markers",
                name="Forecast Risk"
            )
        )

        risk_forecast_fig.add_hline(
            y=60,
            line_dash="dash",
            annotation_text="HIGH threshold"
        )

        risk_forecast_fig.add_hline(
            y=80,
            line_dash="dash",
            annotation_text="CRITICAL threshold"
        )

        risk_forecast_fig.update_layout(
            xaxis_title="Time",
            yaxis_title="Risk Score",
            yaxis=dict(range=[0, 100]),
            height=380,
            margin=dict(l=20, r=20, t=30, b=20)
        )

        st.plotly_chart(
            risk_forecast_fig,
            use_container_width=True
        )

        with st.expander(
            "View 24-hour risk forecast details"
        ):

            display_future = future_risk_df.copy()

            display_future["timestamp"] = (
                display_future["timestamp"]
                .dt.strftime("%d %b %H:%M")
            )

            display_future["predicted_load_mw"] = (
                display_future["predicted_load_mw"]
                .round(2)
            )

            display_future["renewable_forecast_mw"] = (
                display_future["renewable_forecast_mw"]
                .round(2)
            )

            display_future["supply_gap_mw"] = (
                display_future["supply_gap_mw"]
                .round(2)
            )

            display_future["risk_score"] = (
                display_future["risk_score"]
                .round(1)
            )

            display_future = display_future[
                [
                    "timestamp",
                    "predicted_load_mw",
                    "renewable_forecast_mw",
                    "supply_gap_mw",
                    "risk_score",
                    "risk_level",
                    "recommended_action"
                ]
            ]

            display_future.columns = [
                "Time",
                "Forecast Load (MW)",
                "Forecast Renewable (MW)",
                "Supply Gap (MW)",
                "Risk",
                "Level",
                "Recommended Action"
            ]

            st.dataframe(
                display_future,
                use_container_width=True,
                hide_index=True
            )

    else:
        st.info(
            "Future risk forecast is not available yet. "
            "Run `python src\\risk\\future_risk.py` first."
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

    chart_df = df[
        df["timestamp"] >= start_time
    ][
        ["timestamp", "load_mw", "renewable_supply_mw"]
    ].copy()

    # Apply the same scenario to the historical window so the simulator
    # visibly changes the charts as well as the KPI cards.
    chart_df["Simulated Load (MW)"] = (
        chart_df["load_mw"] * (1 + load_surge / 100.0)
    )
    # Approximate renewable response using the latest solar/wind mix.
    renewable_ratio_solar = (
        base_solar / base_renewable if base_renewable > 0 else 0.5
    )
    solar_component = chart_df["renewable_supply_mw"] * renewable_ratio_solar
    wind_component = chart_df["renewable_supply_mw"] * (1 - renewable_ratio_solar)
    chart_df["Simulated Renewable (MW)"] = (
        solar_component * (1 - solar_drop / 100.0)
        + wind_component * wind_factor
    )

    chart_df = chart_df.set_index("timestamp")[
        ["Simulated Load (MW)", "Simulated Renewable (MW)"]
    ]

    st.line_chart(chart_df)

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

        gap_chart = df[
            df["timestamp"] >= start_time
        ][["timestamp", "load_mw", "renewable_supply_mw"]].copy()

        gap_chart["sim_load"] = gap_chart["load_mw"] * (1 + load_surge / 100.0)

        solar_component = gap_chart["renewable_supply_mw"] * renewable_ratio_solar
        wind_component = gap_chart["renewable_supply_mw"] * (1 - renewable_ratio_solar)

        gap_chart["sim_renewable"] = (
            solar_component * (1 - solar_drop / 100.0)
            + wind_component * wind_factor
        )

        gap_chart["Simulated Supply Gap (MW)"] = np.maximum(
            0,
            gap_chart["sim_load"] - gap_chart["sim_renewable"]
        )

        gap_chart = gap_chart.set_index("timestamp")[
            ["Simulated Supply Gap (MW)"]
        ]

        st.area_chart(gap_chart)

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