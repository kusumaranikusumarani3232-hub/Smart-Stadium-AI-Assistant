"""
📊 Analytics Dashboard
Pure Plotly charts across attendance, incidents, volunteers, and crowd trends.
NO Groq API calls — all visualisations are data-driven only.
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from utils.ui_helpers import inject_custom_css, page_header, sidebar_brand, plotly_dark_layout
from utils.data_loader import load_crowd_data, load_incidents, load_volunteers, load_events

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Analytics | Smart Stadium",
    page_icon="📊",
    layout="wide",
)
inject_custom_css()
sidebar_brand()
page_header("Analytics Dashboard", "Stadium-wide performance insights — no AI required", "📊")

# ── Load all datasets (cached, no API) ────────────────────────────────────────
crowd_df = load_crowd_data()
inc_df   = load_incidents()
vol_df   = load_volunteers()
evt_df   = load_events()

crowd_df["timestamp"] = pd.to_datetime(crowd_df["timestamp"])

# ── Sidebar date filter ────────────────────────────────────────────────────────
st.sidebar.markdown("### 📅 Filters")
all_dates = sorted(crowd_df["timestamp"].dt.date.unique())
date_range = st.sidebar.select_slider(
    "Select Date Range",
    options=all_dates,
    value=(all_dates[0], all_dates[-1]),
    key="analytics_dates",
)
filtered_crowd = crowd_df[
    (crowd_df["timestamp"].dt.date >= date_range[0]) &
    (crowd_df["timestamp"].dt.date <= date_range[1])
]

selected_zones = st.sidebar.multiselect(
    "Filter Zones", crowd_df["zone_name"].unique().tolist(),
    default=crowd_df["zone_name"].unique().tolist()[:5],
    key="analytics_zones",
)

st.sidebar.markdown("---")
st.sidebar.caption("All charts use synthetic match-day data seeded for reproducibility.")

# ── Summary KPIs ───────────────────────────────────────────────────────────────
total_events   = len(evt_df)
total_capacity = 30000
peak_density   = round(filtered_crowd["density_pct"].max(), 1)
avg_density    = round(filtered_crowd["density_pct"].mean(), 1)
total_incidents = len(inc_df)
resolved_pct   = round(inc_df["resolved"].sum() / len(inc_df) * 100, 1)

k1, k2, k3, k4, k5, k6 = st.columns(6)
k1.metric("🏟️ Venue Capacity",   f"{total_capacity:,}")
k2.metric("📅 Total Events",     total_events)
k3.metric("📈 Peak Density",     f"{peak_density}%")
k4.metric("📊 Avg Density",      f"{avg_density}%")
k5.metric("🚨 Incidents",        total_incidents)
k6.metric("✅ Resolved",          f"{resolved_pct}%")

st.markdown("<br>", unsafe_allow_html=True)

# ── Tab layout ─────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Crowd Trends", "🚨 Incidents", "🤝 Volunteers", "📅 Events",
])

# ── Tab 1: Crowd Trends ────────────────────────────────────────────────────────
with tab1:
    c1, c2 = st.columns(2)

    with c1:
        # Time-series density by zone
        if selected_zones:
            zf = filtered_crowd[filtered_crowd["zone_name"].isin(selected_zones)]
        else:
            zf = filtered_crowd
        fig_ts = px.line(
            zf, x="timestamp", y="density_pct", color="zone_name",
            labels={"density_pct": "Density (%)", "timestamp": "Time", "zone_name": "Zone"},
        )
        fig_ts.add_hline(y=75, line_dash="dot", line_color="#f59e0b")
        fig_ts.add_hline(y=90, line_dash="dot", line_color="#dc2626")
        plotly_dark_layout(fig_ts, "Crowd Density Over Time", height=360)
        st.plotly_chart(fig_ts, use_container_width=True, config={"displayModeBar": False})

    with c2:
        # Hourly average density (heatmap style)
        filtered_crowd["hour"] = filtered_crowd["timestamp"].dt.hour
        hourly = filtered_crowd.groupby(["hour", "zone_name"])["density_pct"].mean().reset_index()
        pivot  = hourly.pivot(index="zone_name", columns="hour", values="density_pct").fillna(0)
        fig_hm = go.Figure(go.Heatmap(
            z=pivot.values,
            x=[f"{h:02d}:00" for h in pivot.columns],
            y=pivot.index.tolist(),
            colorscale=[[0, "#0a2a1c"], [0.5, "#f59e0b"], [1, "#dc2626"]],
            hoverongaps=False,
            hovertemplate="Zone: %{y}<br>Hour: %{x}<br>Avg Density: %{z:.1f}%<extra></extra>",
        ))
        plotly_dark_layout(fig_hm, "Avg Density by Zone × Hour", height=360)
        st.plotly_chart(fig_hm, use_container_width=True, config={"displayModeBar": False})

    # Alert level distribution over time
    alert_counts = filtered_crowd.groupby(
        [filtered_crowd["timestamp"].dt.date.rename("date"), "alert_level"]
    ).size().reset_index(name="count")
    alert_counts["date"] = alert_counts["date"].astype(str)

    ALERT_COLOR_MAP = {
        "LOW": "#10b981", "MODERATE": "#f59e0b",
        "HIGH": "#ef4444", "CRITICAL": "#dc2626",
    }
    fig_alert = px.bar(
        alert_counts, x="date", y="count", color="alert_level",
        color_discrete_map=ALERT_COLOR_MAP,
        labels={"count": "Zone-Readings", "date": "Date", "alert_level": "Alert Level"},
        barmode="stack",
    )
    plotly_dark_layout(fig_alert, "Alert Level Distribution by Day", height=320)
    st.plotly_chart(fig_alert, use_container_width=True, config={"displayModeBar": False})

# ── Tab 2: Incidents ───────────────────────────────────────────────────────────
with tab2:
    c1, c2 = st.columns(2)

    with c1:
        # Incidents by type
        type_counts = inc_df.groupby("type").size().reset_index(name="count").sort_values("count")
        fig_types = px.bar(
            type_counts, x="count", y="type", orientation="h",
            color="count", color_continuous_scale=["#1a1f35", "#ef4444"],
            text="count", labels={"count": "Incidents", "type": ""},
        )
        fig_types.update_traces(textposition="outside", textfont_color="#e2e8f0")
        plotly_dark_layout(fig_types, "Incidents by Type", height=360)
        st.plotly_chart(fig_types, use_container_width=True, config={"displayModeBar": False})

    with c2:
        # Severity distribution (donut)
        sev_counts = inc_df.groupby("severity").size().reset_index(name="count")
        SEV_COLORS = {"Low": "#10b981", "Medium": "#f59e0b", "High": "#ef4444", "Critical": "#dc2626"}
        fig_sev = px.pie(
            sev_counts, names="severity", values="count",
            color="severity", color_discrete_map=SEV_COLORS, hole=0.55,
        )
        plotly_dark_layout(fig_sev, "Incident Severity Distribution", height=360)
        st.plotly_chart(fig_sev, use_container_width=True, config={"displayModeBar": False})

    # Incidents by zone
    zone_inc = inc_df.groupby("zone_name").size().reset_index(name="count").sort_values("count", ascending=False)
    fig_zone_inc = px.bar(
        zone_inc, x="zone_name", y="count",
        color="count", color_continuous_scale=["#1a1f35", "#ef4444"],
        text="count", labels={"zone_name": "Zone", "count": "Incidents"},
    )
    fig_zone_inc.update_traces(textposition="outside", textfont_color="#e2e8f0")
    plotly_dark_layout(fig_zone_inc, "Incidents by Zone", height=300)
    st.plotly_chart(fig_zone_inc, use_container_width=True, config={"displayModeBar": False})

# ── Tab 3: Volunteers ──────────────────────────────────────────────────────────
with tab3:
    c1, c2 = st.columns(2)

    with c1:
        role_counts = vol_df.groupby("role").size().reset_index(name="count")
        fig_roles = px.bar(
            role_counts, x="count", y="role", orientation="h",
            color="count", color_continuous_scale=["#1a1f35", "#00d4ff"],
            text="count", labels={"count": "Count", "role": ""},
        )
        fig_roles.update_traces(textposition="outside", textfont_color="#e2e8f0")
        plotly_dark_layout(fig_roles, "Volunteers by Role", height=340)
        st.plotly_chart(fig_roles, use_container_width=True, config={"displayModeBar": False})

    with c2:
        zone_counts = vol_df.groupby("zone").size().reset_index(name="count")
        fig_zones_v = px.pie(
            zone_counts, names="zone", values="count",
            hole=0.5,
            color_discrete_sequence=px.colors.sequential.Plasma_r,
        )
        plotly_dark_layout(fig_zones_v, "Volunteer Zone Distribution", height=340)
        st.plotly_chart(fig_zones_v, use_container_width=True, config={"displayModeBar": False})

    # Status timeline-style
    status_zone = vol_df.groupby(["zone", "status"]).size().reset_index(name="count")
    STATUS_COLORS_MAP = {
        "On Duty": "#10b981", "On Break": "#f59e0b",
        "Off Shift": "#475569", "Standby": "#8b5cf6",
    }
    fig_sv = px.bar(
        status_zone, x="zone", y="count", color="status",
        color_discrete_map=STATUS_COLORS_MAP,
        labels={"zone": "Zone", "count": "Count", "status": "Status"},
        barmode="stack",
    )
    plotly_dark_layout(fig_sv, "Volunteer Status by Zone", height=320)
    st.plotly_chart(fig_sv, use_container_width=True, config={"displayModeBar": False})

# ── Tab 4: Events ──────────────────────────────────────────────────────────────
with tab4:
    c1, c2 = st.columns(2)

    with c1:
        fig_att = px.bar(
            evt_df.sort_values("expected_attendance", ascending=False),
            x="match_name", y="expected_attendance",
            color="status",
            color_discrete_map={"Live": "#ef4444", "Upcoming": "#00d4ff", "Completed": "#10b981"},
            text="expected_attendance",
            labels={"match_name": "Event", "expected_attendance": "Expected Attendance"},
        )
        fig_att.update_traces(textposition="outside", textfont_color="#e2e8f0")
        fig_att.update_xaxes(tickangle=-35)
        plotly_dark_layout(fig_att, "Expected Attendance by Event", height=380)
        st.plotly_chart(fig_att, use_container_width=True, config={"displayModeBar": False})

    with c2:
        status_event = evt_df.groupby("status").size().reset_index(name="count")
        fig_estatus = px.pie(
            status_event, names="status", values="count",
            color="status",
            color_discrete_map={"Live": "#ef4444", "Upcoming": "#00d4ff", "Completed": "#10b981"},
            hole=0.55,
        )
        plotly_dark_layout(fig_estatus, "Event Status Breakdown", height=380)
        st.plotly_chart(fig_estatus, use_container_width=True, config={"displayModeBar": False})

