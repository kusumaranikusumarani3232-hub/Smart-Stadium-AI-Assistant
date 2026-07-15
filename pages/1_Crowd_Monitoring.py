"""
🎯 Crowd Monitoring Dashboard
Displays real-time zone density with charts and alert management.
Groq AI is called ONLY for the Decision Support recommendation button.
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

from utils.ui_helpers import (
    inject_custom_css, page_header, zone_density_bar,
    alert_badge, ai_badge, sidebar_brand, plotly_dark_layout,
)
from utils.data_loader import load_crowd_data, load_zones
from utils.groq_client import chat_completion, is_api_available

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Crowd Monitoring | Smart Stadium",
    page_icon="🎯",
    layout="wide",
)
inject_custom_css()
sidebar_brand()
page_header("Crowd Monitoring", "Real-time zone density, alerts & AI decision support", "🎯")

# ── Load data ──────────────────────────────────────────────────────────────────
crowd_df = load_crowd_data()
zones_df = load_zones()

latest_time = crowd_df["timestamp"].max()
latest = crowd_df[crowd_df["timestamp"] == latest_time].copy()

# ── Live Alert Banner ──────────────────────────────────────────────────────────
critical = latest[latest["alert_level"] == "CRITICAL"]
high     = latest[latest["alert_level"] == "HIGH"]

if not critical.empty:
    st.error(
        f"🚨 **CRITICAL ALERT** — Overcrowding in: "
        f"{', '.join(critical['zone_name'].tolist())}",
        icon="🚨",
    )
elif not high.empty:
    st.warning(
        f"⚠️ **HIGH ALERT** — Elevated density in: "
        f"{', '.join(high['zone_name'].tolist())}",
        icon="⚠️",
    )
else:
    st.success("✅ All zones within safe density limits.", icon="✅")

st.caption(f"Snapshot: {latest_time}  ·  Refresh the page to simulate a new reading")
st.markdown("<br>", unsafe_allow_html=True)

# ── KPI Row ────────────────────────────────────────────────────────────────────
total_cap  = int(latest["capacity"].sum())
total_occ  = int(latest["current_occupancy"].sum())
overall    = round(total_occ / total_cap * 100, 1)
n_critical = len(critical)
n_high     = len(high)
n_safe     = len(latest[latest["alert_level"] == "LOW"])

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("🏟️ Total Capacity",    f"{total_cap:,}")
k2.metric("👥 Current Occupancy", f"{total_occ:,}", f"{overall}% full")
k3.metric("🟢 Safe Zones",        n_safe)
k4.metric("🟡 Moderate / High",   len(latest[latest["alert_level"].isin(["MODERATE", "HIGH"])]))
k5.metric("🔴 Critical Zones",    n_critical, delta=f"{n_critical} zone(s)" if n_critical else None)

st.markdown("<br>", unsafe_allow_html=True)

# ── Zone Cards ─────────────────────────────────────────────────────────────────
st.subheader("Zone Status")
cols = st.columns(4)
for idx, (_, row) in enumerate(latest.iterrows()):
    with cols[idx % 4]:
        zone_density_bar(
            row["zone_name"], row["density_pct"],
            int(row["current_occupancy"]), int(row["capacity"]),
            row["alert_level"],
        )

st.markdown("---")

# ── Charts (no API calls) ──────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["📊 Zone Density", "📈 Time Series", "🗺️ Spatial Map"])

ALERT_PALETTE = {
    "LOW": "#10b981", "MODERATE": "#f59e0b",
    "HIGH": "#ef4444", "CRITICAL": "#dc2626",
}

with tab1:
    ordered = latest.sort_values("density_pct", ascending=True)
    fig = go.Figure(go.Bar(
        x=ordered["density_pct"],
        y=ordered["zone_name"],
        orientation="h",
        marker_color=[ALERT_PALETTE.get(a, "#94a3b8") for a in ordered["alert_level"]],
        text=[f"{d}%" for d in ordered["density_pct"]],
        textposition="outside",
        textfont=dict(color="#e2e8f0", size=11),
        hovertemplate="<b>%{y}</b><br>Density: %{x:.1f}%<extra></extra>",
    ))
    fig.add_vline(x=75,  line_dash="dot", line_color="#f59e0b",
                  annotation_text="High (75%)",  annotation_font_color="#f59e0b")
    fig.add_vline(x=90,  line_dash="dot", line_color="#dc2626",
                  annotation_text="Critical (90%)", annotation_font_color="#dc2626")
    fig.update_xaxes(range=[0, 115])
    plotly_dark_layout(fig, "Current Zone Occupancy (%)", height=380)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

with tab2:
    zone_opts = crowd_df["zone_name"].unique().tolist()
    sel = st.multiselect(
        "Select zones to compare",
        zone_opts, default=zone_opts[:4], key="crowd_ts",
    )
    if sel:
        filt = crowd_df[crowd_df["zone_name"].isin(sel)]
        fig2 = px.line(
            filt, x="timestamp", y="density_pct", color="zone_name",
            labels={"density_pct": "Density (%)", "timestamp": "Time", "zone_name": "Zone"},
        )
        fig2.add_hline(y=75, line_dash="dot", line_color="#f59e0b",
                       annotation_text="High Threshold")
        fig2.add_hline(y=90, line_dash="dot", line_color="#dc2626",
                       annotation_text="Critical Threshold")
        plotly_dark_layout(fig2, "Zone Density Over Time (%)", height=400)
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})
    else:
        st.info("Select at least one zone above.")

with tab3:
    merged = zones_df.merge(
        latest[["zone_id", "density_pct", "alert_level", "current_occupancy"]],
        on="zone_id", how="left",
    )
    # Fill NaN for zones not in the latest snapshot (avoids Plotly size NaN error)
    merged["density_pct"]       = merged["density_pct"].fillna(0).clip(lower=1)
    merged["current_occupancy"] = merged["current_occupancy"].fillna(0).astype(int)
    merged["alert_level"]       = merged["alert_level"].fillna("LOW")
    fig3 = px.scatter(
        merged, x="x_coord", y="y_coord",
        size="density_pct", color="density_pct",
        hover_name="name",
        hover_data={"current_occupancy": True, "x_coord": False, "y_coord": False},
        color_continuous_scale=[
            (0.00, "#10b981"), (0.50, "#f59e0b"),
            (0.75, "#ef4444"), (1.00, "#dc2626"),
        ],
        size_max=55,
        labels={"density_pct": "Density %"},
    )
    fig3.update_traces(
        marker=dict(line=dict(width=1.5, color="#0a0e1a")),
    )
    # Add zone labels
    for _, row in merged.iterrows():
        fig3.add_annotation(
            x=row["x_coord"], y=row["y_coord"] - 6,
            text=row["name"], showarrow=False,
            font=dict(size=8, color="#94a3b8"),
        )
    plotly_dark_layout(fig3, "Stadium Zone Density Map", height=460)
    fig3.update_xaxes(showgrid=False, showticklabels=False, title="")
    fig3.update_yaxes(showgrid=False, showticklabels=False, title="")
    st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})

st.markdown("---")

# ── AI Decision Support (Groq called HERE only) ────────────────────────────────
st.subheader("🤖 AI Decision Support")
ai_badge()

if not is_api_available():
    st.info(
        "💡 Add `GROQ_API_KEY` to Streamlit Secrets to enable AI Decision Support. "
        "All charts and dashboards above work without an API key."
    )

with st.expander("Generate AI Operational Recommendations", expanded=False):
    if st.button("⚡ Analyse Crowd Conditions & Get Recommendations", key="btn_ai_crowd"):
        crowd_ctx = latest[
            ["zone_name", "density_pct", "alert_level", "current_occupancy", "capacity"]
        ].to_string(index=False)

        prompt = f"""You are a smart stadium operations AI. Analyse the real-time crowd density
data below and provide specific, actionable operational recommendations.

Current Crowd Data:
{crowd_ctx}

Provide a structured response with these sections:
1. 🚨 Immediate Actions (if any zones are CRITICAL or HIGH)
2. 🔀 Crowd Flow Optimisation
3. 👥 Staff Deployment Suggestions
4. 🛡️ Safety Precautions
5. 🔮 Predictive Outlook (next 60 minutes)

Be specific, practical, and concise. Use bullet points."""

        with st.spinner("Analysing with Groq Llama 3…"):
            response = chat_completion(
                [{"role": "user", "content": prompt}],
                model="llama-3.3-70b-versatile",
                max_tokens=900,
            )
        st.markdown(response)

