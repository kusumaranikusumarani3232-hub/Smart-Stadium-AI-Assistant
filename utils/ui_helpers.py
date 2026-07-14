"""
Custom CSS design system and reusable UI components for Smart Stadium AI Assistant.
Provides a consistent dark stadium-themed look across all pages.
NO Groq API calls in this module.
"""
import streamlit as st

# ── Colour tokens ──────────────────────────────────────────────────────────────
ALERT_COLORS: dict[str, tuple[str, str]] = {
    "LOW":      ("#10b981", "#0a2a1c"),
    "MODERATE": ("#f59e0b", "#2a1f0a"),
    "HIGH":     ("#ef4444", "#2a0a0a"),
    "CRITICAL": ("#dc2626", "#1a0505"),
}

STATUS_COLORS: dict[str, tuple[str, str]] = {
    "On Duty":   ("#10b981", "#0a2a1c"),
    "On Break":  ("#f59e0b", "#2a1f0a"),
    "Off Shift": ("#94a3b8", "#1a1f35"),
    "Standby":   ("#8b5cf6", "#1a1030"),
    "Live":      ("#ef4444", "#2a0a0a"),
    "Upcoming":  ("#00d4ff", "#0a1e2a"),
    "Completed": ("#10b981", "#0a2a1c"),
}


# ══════════════════════════════════════════════════════════════════════════════
#  CSS INJECTION
# ══════════════════════════════════════════════════════════════════════════════

def inject_custom_css() -> None:
    """Inject the full dark-stadium CSS design system into Streamlit."""
    st.markdown("""
<style>
/* ─── Google Fonts ─────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@400;500;600;700&display=swap');

/* ─── Global Reset ─────────────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; }

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"] {
    background-color: #0a0e1a !important;
    color: #e2e8f0;
    font-family: 'Inter', sans-serif;
}

[data-testid="block-container"] {
    padding-top: 1.5rem !important;
    padding-bottom: 2rem !important;
    max-width: 1400px;
}

/* ─── Sidebar ───────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1124 0%, #151a2e 100%) !important;
    border-right: 1px solid #2d3748 !important;
}
[data-testid="stSidebar"] * { color: #e2e8f0 !important; }
section[data-testid="stSidebar"] > div:first-child { padding-top: 0.5rem; }

[data-testid="stSidebarNav"] a {
    border-radius: 10px !important;
    padding: 0.45rem 0.9rem !important;
    margin: 0.1rem 0 !important;
    transition: background 0.2s, border-left 0.2s;
}
[data-testid="stSidebarNav"] a:hover {
    background: rgba(0, 212, 255, 0.10) !important;
}
[data-testid="stSidebarNav"] a[aria-current="page"] {
    background: linear-gradient(90deg, rgba(0,212,255,0.18), rgba(0,212,255,0.04)) !important;
    border-left: 3px solid #00d4ff !important;
}

/* ─── Metric Widgets ────────────────────────────────────────── */
[data-testid="stMetric"] {
    background: #141929;
    border: 1px solid #2d3748;
    border-radius: 14px;
    padding: 1rem 1.2rem;
    transition: transform 0.2s, box-shadow 0.2s;
}
[data-testid="stMetric"]:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(0, 212, 255, 0.14);
}
[data-testid="stMetricLabel"] {
    color: #94a3b8 !important;
    font-size: 0.75rem !important;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    font-weight: 500 !important;
}
[data-testid="stMetricValue"] {
    color: #e2e8f0 !important;
    font-size: 1.9rem !important;
    font-weight: 700 !important;
    font-family: 'Space Grotesk', sans-serif !important;
}

/* ─── Buttons ───────────────────────────────────────────────── */
[data-testid="stButton"] > button {
    background: linear-gradient(135deg, rgba(0,212,255,0.14), rgba(0,212,255,0.06)) !important;
    border: 1px solid rgba(0,212,255,0.45) !important;
    color: #00d4ff !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-family: 'Inter', sans-serif !important;
    transition: all 0.22s !important;
}
[data-testid="stButton"] > button:hover {
    background: linear-gradient(135deg, rgba(0,212,255,0.30), rgba(0,212,255,0.15)) !important;
    border-color: #00d4ff !important;
    box-shadow: 0 4px 18px rgba(0, 212, 255, 0.28) !important;
    transform: translateY(-1px);
    color: #fff !important;
}
[data-testid="stButton"] > button:active { transform: translateY(0) !important; }

/* ─── Inputs / Selects ──────────────────────────────────────── */
[data-testid="stSelectbox"] > div > div,
[data-testid="stMultiSelect"] > div > div,
[data-testid="stTextInput"] > div > div,
[data-testid="stTextArea"] textarea {
    background: #1a1f35 !important;
    border: 1px solid #2d3748 !important;
    border-radius: 10px !important;
    color: #e2e8f0 !important;
}
.stTextArea textarea:focus {
    border-color: #00d4ff !important;
    box-shadow: 0 0 0 2px rgba(0,212,255,0.25) !important;
}

/* ─── Sliders ───────────────────────────────────────────────── */
[data-testid="stSlider"] > div > div > div > div {
    background: #00d4ff !important;
}

/* ─── DataFrames ────────────────────────────────────────────── */
[data-testid="stDataFrame"] {
    border: 1px solid #2d3748;
    border-radius: 12px;
    overflow: hidden;
}

/* ─── Expanders ─────────────────────────────────────────────── */
details[data-testid="stExpander"] {
    background: #141929 !important;
    border: 1px solid #2d3748 !important;
    border-radius: 12px !important;
}

/* ─── Chat messages ─────────────────────────────────────────── */
[data-testid="stChatMessage"] {
    border-radius: 12px !important;
    border: 1px solid #2d3748 !important;
    background: #141929 !important;
}

/* ─── Tabs ──────────────────────────────────────────────────── */
button[data-baseweb="tab"] {
    color: #94a3b8 !important;
    font-weight: 500 !important;
    background: transparent !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    color: #00d4ff !important;
}
[data-testid="stTabs"] [data-baseweb="tab-highlight"] {
    background: #00d4ff !important;
}

/* ─── Alert boxes ───────────────────────────────────────────── */
[data-testid="stAlert"] { border-radius: 10px !important; }

/* ─── Divider ───────────────────────────────────────────────── */
hr { border-color: #2d3748 !important; opacity: 0.5; }

/* ─── Scrollbar ─────────────────────────────────────────────── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: #0a0e1a; }
::-webkit-scrollbar-thumb { background: #2d3748; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(0,212,255,0.45); }

/* ─── Animations ────────────────────────────────────────────── */
@keyframes pulse-glow {
    0%, 100% { box-shadow: 0 0 8px rgba(0,212,255,0.35); }
    50%       { box-shadow: 0 0 20px rgba(0,212,255,0.65); }
}
.pulse { animation: pulse-glow 2s ease-in-out infinite; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  COMPONENT HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def page_header(title: str, subtitle: str = "", icon: str = "") -> None:
    """Render a gradient page header with optional subtitle."""
    icon_html = f'<span style="margin-right:10px;">{icon}</span>' if icon else ""
    sub_html = (
        f'<p style="color:#94a3b8;font-size:0.92rem;margin-top:0.25rem;font-weight:400;">{subtitle}</p>'
        if subtitle else ""
    )
    st.markdown(f"""
<div style="margin-bottom:1.4rem;">
  <h1 style="
      font-family:'Space Grotesk',sans-serif;
      font-size:2rem;font-weight:700;margin:0;
      background:linear-gradient(135deg,#00d4ff,#8b5cf6);
      -webkit-background-clip:text;-webkit-text-fill-color:transparent;
      background-clip:text;">
    {icon_html}{title}
  </h1>
  {sub_html}
  <div style="height:2px;background:linear-gradient(90deg,#00d4ff,transparent);
              margin-top:0.7rem;border-radius:2px;"></div>
</div>""", unsafe_allow_html=True)


def metric_card(
    title: str,
    value: str,
    delta: str = "",
    color: str = "#00d4ff",
    icon: str = "",
) -> None:
    """Render a custom HTML metric card (use inside st.columns)."""
    delta_html = ""
    if delta:
        d_color = "#10b981" if not delta.startswith("-") else "#ef4444"
        delta_html = f'<div style="font-size:0.76rem;color:{d_color};margin-top:4px;">{delta}</div>'
    st.markdown(f"""
<div style="
    background:linear-gradient(135deg,#141929,#1a1f35);
    border:1px solid #2d3748;border-top:2px solid {color};
    border-radius:14px;padding:1.1rem 1.3rem;
    transition:transform 0.2s,box-shadow 0.2s;">
  <div style="font-size:0.73rem;color:#94a3b8;text-transform:uppercase;
              letter-spacing:0.07em;font-weight:500;margin-bottom:0.35rem;">
    {icon}&nbsp;{title}
  </div>
  <div style="font-family:'Space Grotesk',sans-serif;font-size:1.85rem;
              font-weight:700;color:{color};">
    {value}
  </div>
  {delta_html}
</div>""", unsafe_allow_html=True)


def alert_badge(level: str, text: str = "") -> str:
    """Return inline HTML for a coloured alert-level badge."""
    color, bg = ALERT_COLORS.get(level, ("#94a3b8", "#1a1f35"))
    label = text or level
    return (
        f'<span style="background:{bg};color:{color};border:1px solid {color}55;'
        f'padding:3px 10px;border-radius:99px;font-size:0.7rem;'
        f'font-weight:600;letter-spacing:0.05em;text-transform:uppercase;">'
        f'{label}</span>'
    )


def status_badge(status: str) -> str:
    """Return inline HTML for a status badge (volunteers, events)."""
    color, bg = STATUS_COLORS.get(status, ("#e2e8f0", "#1a1f35"))
    return (
        f'<span style="background:{bg};color:{color};border:1px solid {color}55;'
        f'padding:3px 10px;border-radius:99px;font-size:0.7rem;font-weight:600;">'
        f'{status}</span>'
    )


def info_card(
    title: str,
    content: str,
    icon: str = "ℹ️",
    color: str = "#00d4ff",
) -> None:
    """Render a left-bordered info card."""
    st.markdown(f"""
<div style="
    background:linear-gradient(135deg,#141929,#1a1f35);
    border:1px solid #2d3748;border-left:3px solid {color};
    border-radius:12px;padding:1rem 1.2rem;margin:0.4rem 0;">
  <div style="font-weight:600;color:{color};margin-bottom:0.3rem;">{icon} {title}</div>
  <div style="color:#94a3b8;font-size:0.88rem;line-height:1.65;">{content}</div>
</div>""", unsafe_allow_html=True)


def zone_density_bar(zone_name: str, density_pct: float, occupancy: int, capacity: int, alert_level: str) -> None:
    """Render a compact zone density card with progress bar."""
    ALERT_COLORS_LOCAL = {
        "LOW": "#10b981", "MODERATE": "#f59e0b",
        "HIGH": "#ef4444", "CRITICAL": "#dc2626",
    }
    color = ALERT_COLORS_LOCAL.get(alert_level, "#94a3b8")
    st.markdown(f"""
<div style="
    background:linear-gradient(135deg,#141929,#1a1f35);
    border:1px solid #2d3748;border-top:2px solid {color};
    border-radius:14px;padding:1rem 1.1rem;margin-bottom:0.8rem;">
  <div style="font-weight:600;color:#e2e8f0;font-size:0.88rem;margin-bottom:0.55rem;">
    {zone_name}
  </div>
  <div style="background:#0a0e1a;border-radius:99px;height:5px;margin-bottom:0.55rem;">
    <div style="width:{min(density_pct,100)}%;background:{color};height:5px;
                border-radius:99px;transition:width 0.5s;"></div>
  </div>
  <div style="display:flex;justify-content:space-between;align-items:center;">
    <div style="font-family:'Space Grotesk',sans-serif;font-weight:700;
                color:{color};font-size:1.25rem;">{density_pct}%</div>
    <div style="font-size:0.7rem;color:#94a3b8;">{occupancy:,} / {capacity:,}</div>
  </div>
  <div style="margin-top:0.45rem;">{alert_badge(alert_level)}</div>
</div>""", unsafe_allow_html=True)


def ai_badge() -> None:
    """Render a small 'AI-Powered' pill badge."""
    st.markdown("""
<div style="display:inline-flex;align-items:center;gap:6px;
            background:rgba(139,92,246,0.12);
            border:1px solid rgba(139,92,246,0.35);
            border-radius:99px;padding:4px 12px;margin-bottom:0.9rem;">
  <span style="font-size:0.73rem;color:#8b5cf6;font-weight:600;">
    ⚡ AI-Powered · Groq Llama 3
  </span>
</div>""", unsafe_allow_html=True)


def sidebar_brand() -> None:
    """Render consistent sidebar branding on every page."""
    st.sidebar.markdown("""
<div style="text-align:center;padding:1rem 0 1.2rem;">
  <div style="font-size:2.6rem;">🏟️</div>
  <div style="font-family:'Space Grotesk',sans-serif;font-weight:700;font-size:1.05rem;
              background:linear-gradient(135deg,#00d4ff,#8b5cf6);
              -webkit-background-clip:text;-webkit-text-fill-color:transparent;
              background-clip:text;">Smart Stadium AI</div>
  <div style="font-size:0.68rem;color:#94a3b8;margin-top:2px;">
      Powered by Groq · Llama 3
  </div>
  <hr style="border-color:#2d3748;margin-top:0.9rem;">
</div>""", unsafe_allow_html=True)


def plotly_dark_layout(fig, title: str = "", height: int = 400) -> None:
    """Apply consistent dark theme to any Plotly figure in-place."""
    fig.update_layout(
        title=dict(text=title, font=dict(color="#e2e8f0", size=15)) if title else None,
        plot_bgcolor="#0a0e1a",
        paper_bgcolor="#141929",
        font=dict(color="#e2e8f0", family="Inter"),
        xaxis=dict(color="#94a3b8", gridcolor="#1e2540", zerolinecolor="#2d3748"),
        yaxis=dict(color="#94a3b8", gridcolor="#1e2540", zerolinecolor="#2d3748"),
        legend=dict(bgcolor="#1a1f35", bordercolor="#2d3748", borderwidth=1),
        height=height,
        margin=dict(l=10, r=15, t=45 if title else 15, b=15),
    )
