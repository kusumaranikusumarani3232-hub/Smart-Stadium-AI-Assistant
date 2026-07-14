"""
🤝 Volunteer Assistant
Shows the volunteer roster and provides an AI-powered Q&A for shift/protocol queries.
Groq is called ONLY for the AI Q&A chat — roster table and metrics use no API.
"""
import streamlit as st
import plotly.express as px

from utils.ui_helpers import (
    inject_custom_css, page_header, status_badge,
    ai_badge, info_card, sidebar_brand, plotly_dark_layout,
)
from utils.data_loader import load_volunteers
from utils.groq_client import chat_completion, is_api_available

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Volunteer Assistant | Smart Stadium",
    page_icon="🤝",
    layout="wide",
)
inject_custom_css()
sidebar_brand()
page_header("Volunteer Assistant", "Roster management and AI-powered shift Q&A", "🤝")

# ── Load data (no API) ─────────────────────────────────────────────────────────
vol_df = load_volunteers()

# ── KPI Metrics ────────────────────────────────────────────────────────────────
on_duty  = (vol_df["status"] == "On Duty").sum()
on_break = (vol_df["status"] == "On Break").sum()
off_shift= (vol_df["status"] == "Off Shift").sum()
standby  = (vol_df["status"] == "Standby").sum()

k1, k2, k3, k4 = st.columns(4)
k1.metric("🟢 On Duty",   on_duty)
k2.metric("🟡 On Break",  on_break)
k3.metric("🔵 Standby",   standby)
k4.metric("⚫ Off Shift", off_shift)

st.markdown("<br>", unsafe_allow_html=True)

# ── Filters ────────────────────────────────────────────────────────────────────
c1, c2, c3 = st.columns(3)
with c1:
    role_filter = st.multiselect(
        "Filter by Role", vol_df["role"].unique().tolist(), key="vol_role"
    )
with c2:
    zone_filter = st.multiselect(
        "Filter by Zone", vol_df["zone"].unique().tolist(), key="vol_zone"
    )
with c3:
    status_filter = st.multiselect(
        "Filter by Status", vol_df["status"].unique().tolist(), key="vol_status"
    )

filtered = vol_df.copy()
if role_filter:
    filtered = filtered[filtered["role"].isin(role_filter)]
if zone_filter:
    filtered = filtered[filtered["zone"].isin(zone_filter)]
if status_filter:
    filtered = filtered[filtered["status"].isin(status_filter)]

# ── Roster Table ───────────────────────────────────────────────────────────────
st.subheader(f"Volunteer Roster ({len(filtered)} volunteers)")

# Render with HTML badges
table_rows = []
for _, r in filtered.iterrows():
    table_rows.append({
        "ID":       r["volunteer_id"],
        "Name":     r["name"],
        "Role":     r["role"],
        "Zone":     r["zone"],
        "Shift":    f"{r['shift_start']} – {r['shift_end']}",
        "Status":   r["status"],
    })

if table_rows:
    # Render table with status badges via markdown
    header = "| ID | Name | Role | Zone | Shift | Status |"
    sep    = "|---|---|---|---|---|---|"
    rows_md = "\n".join(
        f"| {r['ID']} | {r['Name']} | {r['Role']} | {r['Zone']} | {r['Shift']} | {r['Status']} |"
        for r in table_rows
    )
    st.markdown(f"{header}\n{sep}\n{rows_md}")
else:
    st.info("No volunteers match the selected filters.")

st.markdown("---")

# ── Charts (no API) ────────────────────────────────────────────────────────────
tab1, tab2 = st.tabs(["📊 By Role", "📊 By Status"])

with tab1:
    role_counts = vol_df.groupby("role").size().reset_index(name="count")
    fig_role = px.bar(
        role_counts, x="count", y="role", orientation="h",
        color="count", color_continuous_scale=["#1a1f35", "#00d4ff"],
        labels={"count": "Volunteers", "role": ""},
        text="count",
    )
    fig_role.update_traces(textposition="outside", textfont_color="#e2e8f0")
    plotly_dark_layout(fig_role, "Volunteers by Role", height=320)
    st.plotly_chart(fig_role, use_container_width=True)

with tab2:
    status_counts = vol_df.groupby("status").size().reset_index(name="count")
    STATUS_PIE_COLORS = {
        "On Duty": "#10b981", "On Break": "#f59e0b",
        "Off Shift": "#475569", "Standby": "#8b5cf6",
    }
    fig_status = px.pie(
        status_counts, names="status", values="count",
        color="status",
        color_discrete_map=STATUS_PIE_COLORS,
        hole=0.55,
    )
    plotly_dark_layout(fig_status, "Volunteer Status Distribution", height=320)
    st.plotly_chart(fig_status, use_container_width=True)

st.markdown("---")

# ── AI Q&A (Groq called HERE only) ─────────────────────────────────────────────
st.subheader("🤖 AI Volunteer Support")
ai_badge()

if not is_api_available():
    st.info("💡 Add GROQ_API_KEY to Streamlit Secrets to enable AI Q&A.")

if "vol_chat" not in st.session_state:
    st.session_state.vol_chat = []

# Quick-action buttons
st.markdown("**Quick questions:**")
qcols = st.columns(3)
vol_quick_qs = [
    "What are today's shift timings?",
    "What should I do in a crowd emergency?",
    "How do I escalate a medical incident?",
    "What is the protocol for a lost child?",
    "Where are the volunteer briefing points?",
    "Who do I contact if I need backup?",
]
for i, q in enumerate(vol_quick_qs):
    if qcols[i % 3].button(q, key=f"vq_{i}", use_container_width=True):
        st.session_state["vol_prefill"] = q

for msg in st.session_state.vol_chat:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_q = (
    st.chat_input("Ask about shifts, protocols, responsibilities…", key="vol_chat_input")
    or st.session_state.pop("vol_prefill", None)
)

if user_q:
    st.session_state.vol_chat.append({"role": "user", "content": user_q})
    with st.chat_message("user"):
        st.markdown(user_q)

    roster_summary = (
        f"Total volunteers: {len(vol_df)}. "
        f"On Duty: {on_duty}, On Break: {on_break}, Standby: {standby}, Off Shift: {off_shift}. "
        f"Roles: {', '.join(vol_df['role'].unique())}."
    )
    system_msg = f"""You are a knowledgeable volunteer coordinator assistant for Smart Stadium, 
hosting an international cricket tournament. You have access to volunteer roster data.

Roster summary: {roster_summary}

Help volunteers with: shift schedules, protocols, emergency procedures, 
zone assignments, escalation paths, and general event guidelines.
Be concise, professional, and supportive."""

    api_msgs = [{"role": "system", "content": system_msg}]
    api_msgs += st.session_state.vol_chat[-6:]

    with st.chat_message("assistant"):
        with st.spinner("Thinking…"):
            reply = chat_completion(api_msgs, model="llama3-8b-8192", max_tokens=512)
        st.markdown(reply)

    st.session_state.vol_chat.append({"role": "assistant", "content": reply})

if st.session_state.vol_chat:
    if st.button("🗑️ Clear Chat", key="clear_vol"):
        st.session_state.vol_chat = []
        st.rerun()
