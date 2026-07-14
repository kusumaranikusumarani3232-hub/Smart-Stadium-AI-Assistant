"""
⚙️ Admin Panel
Simulate crowd conditions via sliders (no API).
AI Alert Generation uses Groq ONLY when the dedicated button is clicked.
"""
import streamlit as st
import plotly.graph_objects as go

from utils.ui_helpers import inject_custom_css, page_header, alert_badge, ai_badge, sidebar_brand, plotly_dark_layout
from utils.crowd_simulator import simulate_crowd_snapshot, get_default_densities
from utils.groq_client import chat_completion, is_api_available

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Admin Panel | Smart Stadium",
    page_icon="⚙️",
    layout="wide",
)
inject_custom_css()
sidebar_brand()
page_header("Admin Panel", "Simulate crowd conditions and generate AI operational alerts", "⚙️")

# ── Sidebar controls ───────────────────────────────────────────────────────────
st.sidebar.markdown("### ⚙️ Simulation Settings")
noise = st.sidebar.slider(
    "Background noise level", 0.0, 0.15, 0.05, 0.01, key="admin_noise",
    help="Controls random variation (±) added to each zone's base crowd density",
)

if st.sidebar.button("🔄 Reset to Default Densities", key="admin_reset"):
    for key in list(st.session_state.keys()):
        if key.startswith("slider_"):
            del st.session_state[key]
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown(
    "**How it works**\n\n"
    "Adjust zone density sliders to simulate any crowd scenario. "
    "The simulation runs a pure algorithmic model. "
    "Click **Generate AI Alert** to get Groq AI recommendations."
)

# ── Zone density sliders (no API) ──────────────────────────────────────────────
defaults = get_default_densities()  # {zone_id: default_pct}

ZONE_LABELS = {
    "Z1": "Z1 – North Stand",
    "Z2": "Z2 – South Stand",
    "Z3": "Z3 – East Stand",
    "Z4": "Z4 – West Stand",
    "Z5": "Z5 – VIP Lounge",
    "Z6": "Z6 – Press Box",
    "Z7": "Z7 – Food Court A",
    "Z8": "Z8 – Food Court B",
}

st.subheader("🎛️ Zone Density Simulation")
st.caption("Drag sliders to manually set crowd density per zone, then click 'Simulate'.")

manual_overrides: dict[str, float] = {}
cols = st.columns(4)

for idx, (zone_id, label) in enumerate(ZONE_LABELS.items()):
    with cols[idx % 4]:
        val = st.slider(
            label,
            min_value=0,
            max_value=100,
            value=int(defaults.get(zone_id, 70)),
            step=1,
            key=f"slider_{zone_id}",
        )
        manual_overrides[zone_id] = float(val)

st.markdown("<br>", unsafe_allow_html=True)

# ── Run simulation (pure algorithm, no API) ────────────────────────────────────
if st.button("▶️ Run Simulation", key="btn_simulate", use_container_width=False):
    st.session_state["sim_result"] = simulate_crowd_snapshot(
        manual_overrides=manual_overrides, noise_level=noise
    )

sim_df = st.session_state.get("sim_result", None)

if sim_df is None:
    # Auto-run on first load
    sim_df = simulate_crowd_snapshot(manual_overrides=manual_overrides, noise_level=noise)
    st.session_state["sim_result"] = sim_df

# ── Simulation results ─────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("📊 Simulated Crowd State")

ALERT_COLOR_MAP = {
    "LOW": "#10b981", "MODERATE": "#f59e0b",
    "HIGH": "#ef4444", "CRITICAL": "#dc2626",
}

# KPI row
total_cap = int(sim_df["capacity"].sum())
total_occ = int(sim_df["current_occupancy"].sum())
overall   = round(total_occ / total_cap * 100, 1)
n_crit    = (sim_df["alert_level"] == "CRITICAL").sum()
n_high    = (sim_df["alert_level"] == "HIGH").sum()

k1, k2, k3, k4 = st.columns(4)
k1.metric("👥 Simulated Occupancy", f"{total_occ:,}", f"{overall}% of capacity")
k2.metric("🔴 Critical Zones",      int(n_crit))
k3.metric("🟠 High Zones",          int(n_high))
k4.metric("🟢 Safe Zones",          int((sim_df["alert_level"] == "LOW").sum()))

# Bar chart (no API)
ordered = sim_df.sort_values("density_pct", ascending=True)
fig = go.Figure(go.Bar(
    x=ordered["density_pct"],
    y=ordered["zone_name"],
    orientation="h",
    marker_color=[ALERT_COLOR_MAP.get(a, "#94a3b8") for a in ordered["alert_level"]],
    text=[f"{d:.1f}%" for d in ordered["density_pct"]],
    textposition="outside",
    textfont=dict(color="#e2e8f0"),
    hovertemplate="<b>%{y}</b><br>Density: %{x:.1f}%<extra></extra>",
))
fig.add_vline(x=75, line_dash="dot", line_color="#f59e0b", annotation_text="High")
fig.add_vline(x=90, line_dash="dot", line_color="#dc2626", annotation_text="Critical")
fig.update_xaxes(range=[0, 115])
plotly_dark_layout(fig, "Simulated Zone Density (%)", height=360)
st.plotly_chart(fig, use_container_width=True)

# Zone cards
st.markdown("**Zone Breakdown**")
card_cols = st.columns(4)
for idx, (_, row) in enumerate(sim_df.iterrows()):
    color = ALERT_COLOR_MAP.get(row["alert_level"], "#94a3b8")
    with card_cols[idx % 4]:
        st.markdown(f"""
<div style="background:linear-gradient(135deg,#141929,#1a1f35);
            border:1px solid #2d3748;border-top:2px solid {color};
            border-radius:12px;padding:0.9rem;margin-bottom:0.6rem;">
  <div style="font-size:0.82rem;font-weight:600;color:#e2e8f0;margin-bottom:0.4rem;">
    {row['zone_name']}
  </div>
  <div style="background:#0a0e1a;border-radius:99px;height:4px;margin-bottom:0.4rem;">
    <div style="width:{min(row['density_pct'],100)}%;background:{color};height:4px;border-radius:99px;"></div>
  </div>
  <div style="display:flex;justify-content:space-between;align-items:center;">
    <span style="font-family:'Space Grotesk',sans-serif;font-weight:700;color:{color};font-size:1.1rem;">
      {row['density_pct']:.1f}%
    </span>
    {alert_badge(row['alert_level'])}
  </div>
</div>""", unsafe_allow_html=True)

st.markdown("---")

# ── AI Alert Generation (Groq called HERE only) ────────────────────────────────
st.subheader("🤖 AI Operational Alert")
ai_badge()

if not is_api_available():
    st.info(
        "💡 Add GROQ_API_KEY to Streamlit Secrets to enable AI alerts. "
        "All simulation above runs without an API key."
    )

with st.expander("Generate AI Alert & Recommendations", expanded=False):
    alert_type = st.radio(
        "Alert scenario context",
        ["Match Day Peak", "Pre-Match Arrival", "Post-Match Exodus", "Emergency Drill"],
        horizontal=True,
        key="admin_alert_type",
    )

    if st.button("⚡ Generate AI Operational Alert", key="btn_ai_alert"):
        crowd_ctx = sim_df[
            ["zone_name", "density_pct", "alert_level", "current_occupancy", "capacity"]
        ].to_string(index=False)

        prompt = f"""You are a smart stadium operations AI. Based on the simulated crowd conditions below,
generate a professional operational alert and action plan.

Scenario: {alert_type}
Overall Density: {overall}% ({total_occ:,} / {total_cap:,} capacity)

Simulated Zone Data:
{crowd_ctx}

Generate:
1. 🚨 ALERT STATUS (Green / Amber / Red) with brief justification
2. ⚡ IMMEDIATE ACTIONS (prioritised list — critical zones first)
3. 🔀 CROWD REDISTRIBUTION PLAN (specific zone-to-zone flow recommendations)
4. 👥 STAFF DEPLOYMENT ORDERS (which roles to where)
5. 📢 PUBLIC ANNOUNCEMENTS (suggested wording for PA system)
6. 🔮 15-MINUTE OUTLOOK

Format with clear sections. Be specific, operational, and authoritative."""

        with st.spinner("Generating operational alert with Groq Llama 3…"):
            alert_response = chat_completion(
                [{"role": "user", "content": prompt}],
                model="llama-3.3-70b-versatile",
                max_tokens=1000,
            )
        st.markdown(alert_response)

        # Download option
        st.download_button(
            "⬇️ Download Alert (.txt)",
            data=alert_response,
            file_name="stadium_operational_alert.txt",
            mime="text/plain",
            key="dl_alert",
        )

