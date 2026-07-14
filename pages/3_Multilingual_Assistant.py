"""
🌐 Multi-language AI Assistant
Powered by Groq Llama 3 — responds in the user's chosen language.
Groq is called for EVERY chat message (required AI reasoning feature).
"""
import streamlit as st

from utils.ui_helpers import inject_custom_css, page_header, ai_badge, info_card, sidebar_brand
from utils.groq_client import chat_completion, is_api_available

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Multilingual Assistant | Smart Stadium",
    page_icon="🌐",
    layout="wide",
)
inject_custom_css()
sidebar_brand()
page_header(
    "Multilingual AI Assistant",
    "Get stadium help in your preferred language — powered by Groq Llama 3",
    "🌐",
)

# ── Language Config ────────────────────────────────────────────────────────────
LANGUAGES = {
    "🇬🇧 English":    "English",
    "🇮🇳 Hindi":      "Hindi",
    "🇪🇸 Spanish":    "Spanish",
    "🇫🇷 French":     "French",
    "🇩🇪 German":     "German",
    "🇸🇦 Arabic":     "Arabic",
    "🇨🇳 Chinese":    "Simplified Chinese",
    "🇯🇵 Japanese":   "Japanese",
    "🇵🇹 Portuguese": "Portuguese",
    "🇰🇷 Korean":     "Korean",
}

SYSTEM_PROMPT = """You are a friendly, professional stadium AI assistant for Smart Stadium — 
a world-class cricket/sports venue hosting an international tournament.

You help fans, visitors, and staff with:
- Finding seats, gates, and facilities
- Food & beverage options
- Match schedules and event information
- Transportation and parking
- Safety, medical, and accessibility services
- Lost items and general queries

CRITICAL INSTRUCTION: Always respond ENTIRELY in {language}. 
Do not mix languages. Keep responses helpful, concise, and warm.
If the user writes in a different language, still respond in {language}."""

# ── Sidebar controls ───────────────────────────────────────────────────────────
st.sidebar.markdown("### 🌐 Language Settings")
lang_display = st.sidebar.selectbox(
    "Select Language", list(LANGUAGES.keys()), key="lang_select"
)
selected_lang = LANGUAGES[lang_display]

st.sidebar.markdown("---")
st.sidebar.markdown("### 💡 Quick Questions")
quick_questions = [
    "Where are the nearest restrooms?",
    "What food options are available?",
    "How do I find my seat?",
    "What time does the match start?",
    "Where is the medical center?",
    "How do I get to Gate A?",
]
for q in quick_questions:
    if st.sidebar.button(q, key=f"quick_{q[:20]}", use_container_width=True):
        st.session_state["prefill_msg"] = q

# ── Session State ──────────────────────────────────────────────────────────────
if "ml_messages" not in st.session_state:
    st.session_state.ml_messages = []
if "ml_language" not in st.session_state:
    st.session_state.ml_language = selected_lang

# Reset history when language changes
if st.session_state.ml_language != selected_lang:
    st.session_state.ml_messages = []
    st.session_state.ml_language = selected_lang
    st.rerun()

# ── Header area ────────────────────────────────────────────────────────────────
ai_badge()

col_info, col_lang_badge = st.columns([3, 1])
with col_info:
    st.markdown(
        f"Currently responding in **{lang_display}**. "
        "Change language in the sidebar — history resets on language switch."
    )
with col_lang_badge:
    st.markdown(
        f'<div style="background:#1a1f35;border:1px solid #2d3748;border-radius:10px;'
        f'padding:0.5rem 0.8rem;text-align:center;font-size:1.4rem;">{lang_display[:2]}</div>',
        unsafe_allow_html=True,
    )

if not is_api_available():
    st.warning(
        "⚠️ **GROQ_API_KEY not configured.** "
        "The chat will return a placeholder. Add your key to Streamlit Secrets.",
        icon="⚠️",
    )

st.markdown("---")

# ── Chat History ───────────────────────────────────────────────────────────────
for msg in st.session_state.ml_messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ── Chat Input ─────────────────────────────────────────────────────────────────
prefill = st.session_state.pop("prefill_msg", None)
user_input = st.chat_input(
    f"Ask anything in any language — I'll reply in {selected_lang}…",
    key="ml_chat_input",
) or prefill

if user_input:
    # Show user message immediately
    st.session_state.ml_messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Build messages list with system prompt
    lang_specific_system = SYSTEM_PROMPT.format(language=selected_lang)
    api_messages = [{"role": "system", "content": lang_specific_system}]
    # Include conversation history (last 8 turns to stay within token limits)
    api_messages += st.session_state.ml_messages[-8:]

    # AI call (required — user is requesting a language-specific response)
    with st.chat_message("assistant"):
        with st.spinner(f"Thinking in {selected_lang}…"):
            reply = chat_completion(
                api_messages,
                model="llama-3.3-70b-versatile",
                temperature=0.65,
                max_tokens=512,
            )
        st.markdown(reply)

    st.session_state.ml_messages.append({"role": "assistant", "content": reply})

# ── Clear history ──────────────────────────────────────────────────────────────
if st.session_state.ml_messages:
    if st.button("🗑️ Clear Conversation", key="clear_ml"):
        st.session_state.ml_messages = []
        st.rerun()

# ── Info footer ────────────────────────────────────────────────────────────────
info_card(
    "Supported Languages",
    " · ".join(LANGUAGES.keys()),
    "🌍", "#8b5cf6",
)
