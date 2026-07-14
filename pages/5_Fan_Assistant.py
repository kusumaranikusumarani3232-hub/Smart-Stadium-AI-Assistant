"""
🏟️ Fan Assistant
A friendly AI chatbot for fans — food, seats, events, transport, and more.
Groq is called for every chat message (required AI feature).
"""
import streamlit as st

from utils.ui_helpers import inject_custom_css, page_header, ai_badge, info_card, sidebar_brand
from utils.data_loader import load_events
from utils.groq_client import chat_completion, is_api_available

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Fan Assistant | Smart Stadium",
    page_icon="🏟️",
    layout="wide",
)
inject_custom_css()
sidebar_brand()
page_header(
    "Fan Assistant",
    "Your personal stadium companion — ask anything about your match day experience",
    "🏟️",
)

# ── Sidebar: Today's Events (no API) ───────────────────────────────────────────
st.sidebar.markdown("### 📅 Today's Events")
events_df = load_events()
today_events = events_df[events_df["date"] == "2024-07-14"]

STATUS_EMOJI = {"Live": "🔴", "Upcoming": "🕐", "Completed": "✅"}

for _, ev in today_events.iterrows():
    emoji = STATUS_EMOJI.get(ev["status"], "📅")
    st.sidebar.markdown(
        f"{emoji} **{ev['time']}** — {ev['match_name']}  \n"
        f"<span style='font-size:0.75rem;color:#94a3b8;'>{ev['teams']}</span>",
        unsafe_allow_html=True,
    )

st.sidebar.markdown("---")
st.sidebar.markdown("### 💡 Quick Topics")
fan_quick = [
    "🍔 Food & drinks near Gate A",
    "🪑 How to find my seat",
    "🅿️ Parking and transport",
    "🚻 Nearest restrooms",
    "🏥 Medical / first aid",
    "♿ Accessibility services",
    "📸 Photography rules",
    "🎟️ Ticket issues",
]
for q in fan_quick:
    if st.sidebar.button(q, key=f"fan_quick_{q[:15]}", use_container_width=True):
        st.session_state["fan_prefill"] = q.split(" ", 1)[1]  # strip emoji

# ── Events context (for AI system prompt) ─────────────────────────────────────
events_context = "\n".join(
    f"- {r['time']} {r['match_name']} ({r['teams']}) — Status: {r['status']}"
    for _, r in today_events.iterrows()
)

FAN_SYSTEM = f"""You are a warm, enthusiastic, and super-helpful fan assistant for Smart Stadium — 
a world-class sports venue hosting an international cricket tournament.

Today's events:
{events_context}

Stadium facilities:
- Gates: A (North, Main), B (South), C (East), D (West)
- Seating: North Stand (Z1), South Stand (Z2), East Stand (Z3), West Stand (Z4)
- VIP Lounge (Z5) · Press Box (Z6) · Food Court A (Z7, near Gate C) · Food Court B (Z8, near Gate D)
- Medical Center near Gate B · Information Desk at stadium centre

Help fans with: finding seats, food options, transport, schedules, 
lost items, accessibility, rules, and general enjoyment tips.
Be friendly, upbeat, and use emojis appropriately. Keep answers concise and practical."""

# ── Session state ──────────────────────────────────────────────────────────────
if "fan_chat" not in st.session_state:
    st.session_state.fan_chat = []

# ── Welcome card ───────────────────────────────────────────────────────────────
ai_badge()

if not st.session_state.fan_chat:
    st.markdown("""
<div style="background:linear-gradient(135deg,#141929,#1a1f35);
            border:1px solid #2d3748;border-radius:16px;
            padding:1.5rem;margin-bottom:1rem;text-align:center;">
    <div style="font-size:2.5rem;margin-bottom:0.5rem;">👋</div>
    <div style="font-family:'Space Grotesk',sans-serif;font-size:1.2rem;
                font-weight:600;color:#e2e8f0;margin-bottom:0.4rem;">
        Welcome to Smart Stadium!
    </div>
    <div style="color:#94a3b8;font-size:0.9rem;">
        I'm your personal fan assistant. Ask me anything about your match day experience — 
        from finding your seat to the best food stalls! Use the quick topics in the sidebar 
        or type your question below.
    </div>
</div>
""", unsafe_allow_html=True)

if not is_api_available():
    st.warning("⚠️ GROQ_API_KEY not configured — AI responses disabled.", icon="⚠️")

# ── Chat history ───────────────────────────────────────────────────────────────
for msg in st.session_state.fan_chat:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ── Chat input ─────────────────────────────────────────────────────────────────
user_input = (
    st.chat_input("Ask me anything about your stadium experience…", key="fan_chat_input")
    or st.session_state.pop("fan_prefill", None)
)

if user_input:
    st.session_state.fan_chat.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    api_msgs = [{"role": "system", "content": FAN_SYSTEM}]
    api_msgs += st.session_state.fan_chat[-8:]

    with st.chat_message("assistant"):
        with st.spinner("Finding the best answer for you…"):
            reply = chat_completion(
                api_msgs,
                model="llama3-8b-8192",
                temperature=0.75,
                max_tokens=400,
            )
        st.markdown(reply)

    st.session_state.fan_chat.append({"role": "assistant", "content": reply})

# ── Clear / footer ─────────────────────────────────────────────────────────────
if st.session_state.fan_chat:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🗑️ New Conversation", key="clear_fan"):
        st.session_state.fan_chat = []
        st.rerun()

info_card(
    "Stadium Quick Facts",
    "📍 Total Capacity: 30,000 · 🚪 4 Entry Gates · 🍔 2 Food Courts · 🏥 Medical Centre at Gate B · "
    "♿ Accessible seating in all stands · 📶 Free Wi-Fi throughout the venue",
    "🏟️", "#f59e0b",
)
