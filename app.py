"""
Smart Stadium AI Assistant — Main Entry Point
==============================================
Run with:  streamlit run app.py

Architecture:
- app.py          → Home page (landing dashboard, KPIs, live event card)
- pages/          → 8 feature pages
- utils/          → Shared utilities (Groq client, data loader, UI helpers, etc.)
- data/           → Synthetic CSV datasets (auto-generated on first run)
- .streamlit/     → Theme config & secrets template
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

from utils.ui_helpers import inject_custom_css, page_header, metric_card, info_card, sidebar_brand
from utils.data_loader import ensure_all_data, load_crowd_data, load_events

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Smart Stadium AI Assistant",
    page_icon="🏟️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get help": "https://github.com",
        "About": "Smart Stadium AI Assistant — Hackathon Project powered by Groq Llama 3",
    },
)

# ── One-time data generation (fast — cached by Streamlit) ─────────────────────
with st.spinner("Initialising Smart Stadium AI…"):
    ensure_all_data()

inject_custom_css()
sidebar_brand()

# ── Sidebar navigation guide ───────────────────────────────────────────────────
st.sidebar.markdown("### 🗂️ Navigation")
nav_items = [
    ("🎯", "Crowd Monitoring",      "Real-time crowd density & AI decision support"),
    ("🗺️", "Navigation",            "Indoor pathfinding with NetworkX Dijkstra"),
    ("🌐", "Multilingual Assistant","Chat in 10+ languages via Groq Llama 3"),
    ("🤝", "Volunteer Assistant",   "Roster management & AI shift Q&A"),
    ("🏟️", "Fan Assistant",         "Friendly fan chat powered by Groq"),
    ("🚨", "Incident Report",       "AI-generated structured incident reports"),
    ("📊", "Analytics",             "10+ Plotly charts — zero API calls"),
    ("⚙️", "Admin Panel",           "Simulate crowd & generate AI alerts"),
]
for icon, name, desc in nav_items:
    st.sidebar.markdown(
        f"<div style='padding:0.3rem 0;'>"
        f"<span style='font-size:0.85rem;font-weight:600;color:#e2e8f0;'>{icon} {name}</span><br>"
        f"<span style='font-size:0.72rem;color:#94a3b8;'>{desc}</span></div>",
        unsafe_allow_html=True,
    )

st.sidebar.markdown("---")
st.sidebar.markdown(
    "<div style='font-size:0.72rem;color:#64748b;text-align:center;'>"
    "Smart Stadium AI Assistant<br>Hackathon Edition · Groq Llama 3</div>",
    unsafe_allow_html=True,
)

# ── Hero Header ────────────────────────────────────────────────────────────────
st.markdown("""
<div style="
    background: linear-gradient(135deg, #0d1124 0%, #1a1f35 50%, #0d1124 100%);
    border: 1px solid #2d3748;
    border-radius: 20px;
    padding: 2.5rem 2rem 2rem;
    margin-bottom: 1.5rem;
    text-align: center;
    position: relative;
    overflow: hidden;
">
    <div style="
        position: absolute; top: 0; left: 0; right: 0; bottom: 0;
        background: radial-gradient(ellipse at 50% -20%, rgba(0,212,255,0.12) 0%, transparent 65%);
        pointer-events: none;
    "></div>
    <div style="font-size: 3.5rem; margin-bottom: 0.6rem; position: relative;">🏟️</div>
    <h1 style="
        font-family: 'Space Grotesk', sans-serif;
        font-size: 2.6rem; font-weight: 800; margin: 0 0 0.4rem;
        background: linear-gradient(135deg, #00d4ff 0%, #8b5cf6 50%, #f59e0b 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        background-clip: text; position: relative;
    ">Smart Stadium AI Assistant</h1>
    <p style="color: #94a3b8; font-size: 1rem; margin: 0; position: relative;">
        GenAI-powered operations platform for fans, volunteers, organizers & staff
        &nbsp;·&nbsp; Powered by <strong style="color:#00d4ff;">Groq Llama 3</strong>
    </p>
    <div style="
        display: flex; justify-content: center; gap: 10px;
        flex-wrap: wrap; margin-top: 1.2rem; position: relative;
    ">
        <span style="background:rgba(0,212,255,0.12);border:1px solid rgba(0,212,255,0.35);
                     color:#00d4ff;padding:4px 14px;border-radius:99px;font-size:0.75rem;font-weight:600;">
            ⚡ Groq API
        </span>
        <span style="background:rgba(139,92,246,0.12);border:1px solid rgba(139,92,246,0.35);
                     color:#8b5cf6;padding:4px 14px;border-radius:99px;font-size:0.75rem;font-weight:600;">
            🔗 NetworkX Navigation
        </span>
        <span style="background:rgba(245,158,11,0.12);border:1px solid rgba(245,158,11,0.35);
                     color:#f59e0b;padding:4px 14px;border-radius:99px;font-size:0.75rem;font-weight:600;">
            📊 Plotly Analytics
        </span>
        <span style="background:rgba(16,185,129,0.12);border:1px solid rgba(16,185,129,0.35);
                     color:#10b981;padding:4px 14px;border-radius:99px;font-size:0.75rem;font-weight:600;">
            🌐 10+ Languages
        </span>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Live Crowd Snapshot ────────────────────────────────────────────────────────
crowd_df = load_crowd_data()
latest_time = crowd_df["timestamp"].max()
latest = crowd_df[crowd_df["timestamp"] == latest_time]

total_cap = int(latest["capacity"].sum())
total_occ = int(latest["current_occupancy"].sum())
overall   = round(total_occ / total_cap * 100, 1)
n_critical = int((latest["alert_level"] == "CRITICAL").sum())
n_high     = int((latest["alert_level"] == "HIGH").sum())

# Live alert banner
if n_critical > 0:
    st.error(f"🚨 **{n_critical} CRITICAL zone(s)** detected — visit Crowd Monitoring for details.", icon="🚨")
elif n_high > 0:
    st.warning(f"⚠️ **{n_high} HIGH-density zone(s)** — elevated crowd levels detected.", icon="⚠️")
else:
    st.success("✅ All stadium zones are operating within safe density limits.", icon="✅")

# ── KPI Dashboard ──────────────────────────────────────────────────────────────
st.markdown("### 📊 Live Stadium Overview")
k1, k2, k3, k4, k5, k6 = st.columns(6)

metric_card_data = [
    (k1, "Venue Capacity",   f"{total_cap:,}",    "",                          "#00d4ff", "🏟️"),
    (k2, "Current Occupancy",f"{total_occ:,}",    f"{overall}% full",          "#8b5cf6", "👥"),
    (k3, "Critical Zones",   str(n_critical),      "",                          "#dc2626", "🔴"),
    (k4, "High Alert Zones", str(n_high),           "",                          "#ef4444", "🟠"),
    (k5, "Safe Zones",       str(int((latest["alert_level"] == "LOW").sum())), "", "#10b981", "🟢"),
    (k6, "Monitored Zones",  str(len(latest)),      "",                          "#f59e0b", "📍"),
]

for col, title, value, delta, color, icon in metric_card_data:
    with col:
        metric_card(title, value, delta, color, icon)

st.markdown("<br>", unsafe_allow_html=True)

# ── Today's Events & Quick Charts ─────────────────────────────────────────────
col_events, col_chart = st.columns([1, 1.6])

with col_events:
    st.markdown("### 📅 Today's Events")
    events_df = load_events()
    today = events_df[events_df["date"] == "2024-07-14"]

    STATUS_EMOJI = {"Live": "🔴 LIVE", "Upcoming": "🕐", "Completed": "✅"}
    STATUS_COLORS = {"Live": "#ef4444", "Upcoming": "#00d4ff", "Completed": "#10b981"}

    for _, ev in today.iterrows():
        color = STATUS_COLORS.get(ev["status"], "#94a3b8")
        emoji = STATUS_EMOJI.get(ev["status"], "📅")
        st.markdown(f"""
<div style="background:#141929;border:1px solid #2d3748;border-left:3px solid {color};
            border-radius:10px;padding:0.75rem 1rem;margin-bottom:0.5rem;">
    <div style="display:flex;justify-content:space-between;align-items:center;">
        <div>
            <div style="font-weight:600;color:#e2e8f0;font-size:0.88rem;">
                {ev['time']} — {ev['match_name']}
            </div>
            <div style="font-size:0.75rem;color:#94a3b8;margin-top:2px;">{ev['teams']}</div>
        </div>
        <span style="background:{color}22;color:{color};border:1px solid {color}55;
                     padding:3px 10px;border-radius:99px;font-size:0.7rem;font-weight:600;">
            {emoji}
        </span>
    </div>
</div>""", unsafe_allow_html=True)

with col_chart:
    st.markdown("### 📈 Zone Density Snapshot")
    ALERT_PALETTE = {
        "LOW": "#10b981", "MODERATE": "#f59e0b",
        "HIGH": "#ef4444", "CRITICAL": "#dc2626",
    }
    sorted_zones = latest.sort_values("density_pct", ascending=True)
    fig = go.Figure(go.Bar(
        x=sorted_zones["density_pct"],
        y=sorted_zones["zone_name"],
        orientation="h",
        marker_color=[ALERT_PALETTE.get(a, "#94a3b8") for a in sorted_zones["alert_level"]],
        text=[f"{d}%" for d in sorted_zones["density_pct"]],
        textposition="outside",
        textfont=dict(color="#e2e8f0", size=10),
        hovertemplate="<b>%{y}</b><br>%{x:.1f}%<extra></extra>",
    ))
    fig.add_vline(x=75, line_dash="dot", line_color="#f59e0b")
    fig.add_vline(x=90, line_dash="dot", line_color="#dc2626")
    fig.update_layout(
        plot_bgcolor="#0a0e1a", paper_bgcolor="#141929",
        font=dict(color="#e2e8f0"),
        xaxis=dict(range=[0, 115], color="#94a3b8", gridcolor="#1e2540"),
        yaxis=dict(color="#94a3b8"),
        height=350,
        margin=dict(l=5, r=15, t=10, b=10),
    )
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ── Feature Cards ──────────────────────────────────────────────────────────────
st.markdown("### 🚀 Features")

features = [
    ("🎯", "Crowd Monitoring",       "Real-time zone density heatmaps, alert badges, time-series charts, and AI Decision Support.",        "#00d4ff", "AI + Charts"),
    ("🗺️", "Smart Navigation",       "NetworkX Dijkstra shortest-path routing with full Plotly graph visualization — works offline.",       "#8b5cf6", "Algorithm"),
    ("🌐", "Multilingual Assistant", "Chat with the stadium AI in English, Hindi, Spanish, French, Arabic, Chinese & 4 more.",              "#10b981", "Groq AI"),
    ("🤝", "Volunteer Assistant",    "Role-filtered roster table, status analytics, and AI-powered Q&A for shift & protocol queries.",      "#f59e0b", "AI + Data"),
    ("🏟️", "Fan Assistant",          "Friendly match-day companion — food, seating, transport, accessibility, and stadium rules.",          "#06b6d4", "Groq AI"),
    ("🚨", "Incident Reports",       "Fill a form and get a structured, downloadable professional incident report generated by AI.",         "#ef4444", "Groq AI"),
    ("📊", "Analytics Dashboard",    "10+ interactive Plotly charts: attendance, incidents, volunteer distribution, crowd heatmaps.",       "#a78bfa", "Plotly Only"),
    ("⚙️", "Admin Panel",            "Simulate any crowd scenario with sliders, view algorithmic results, and generate AI operational alerts.", "#fb923c", "AI + Sim"),
]

row1, row2 = features[:4], features[4:]
for row in [row1, row2]:
    cols = st.columns(4)
    for col, (icon, name, desc, color, badge) in zip(cols, row):
        with col:
            st.markdown(f"""
<div style="background:linear-gradient(135deg,#141929,#1a1f35);
            border:1px solid #2d3748;border-top:2px solid {color};
            border-radius:14px;padding:1.1rem;height:100%;
            transition:transform 0.2s;margin-bottom:0.8rem;">
    <div style="font-size:1.7rem;margin-bottom:0.5rem;">{icon}</div>
    <div style="font-weight:700;color:#e2e8f0;font-size:0.95rem;margin-bottom:0.3rem;">{name}</div>
    <div style="font-size:0.78rem;color:#94a3b8;line-height:1.55;margin-bottom:0.6rem;">{desc}</div>
    <span style="background:{color}18;color:{color};border:1px solid {color}44;
                 padding:2px 10px;border-radius:99px;font-size:0.67rem;font-weight:600;">
        {badge}
    </span>
</div>""", unsafe_allow_html=True)

st.markdown("---")

# ── Setup guide ────────────────────────────────────────────────────────────────
info_card(
    "Quick Setup",
    "<b>1.</b> Get a free API key at <code>console.groq.com</code> &nbsp;·&nbsp; "
    "<b>2.</b> Add it to <code>.streamlit/secrets.toml</code> as <code>GROQ_API_KEY = \"gsk_...\"</code> &nbsp;·&nbsp; "
    "<b>3.</b> Run <code>streamlit run app.py</code> &nbsp;·&nbsp; "
    "All analytics and navigation work <b>without</b> an API key.",
    "⚡", "#00d4ff",
)
