"""
🚨 Incident Report Generator
Form-based input → Groq generates a structured professional incident report.
Groq is called ONLY when the user clicks 'Generate Report'.
"""
import streamlit as st
from datetime import datetime

from utils.ui_helpers import inject_custom_css, page_header, ai_badge, info_card, sidebar_brand
from utils.groq_client import chat_completion, is_api_available

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Incident Report | Smart Stadium",
    page_icon="🚨",
    layout="wide",
)
inject_custom_css()
sidebar_brand()
page_header("Incident Report Generator", "AI-generated structured incident reports for staff", "🚨")

# ── Constants ──────────────────────────────────────────────────────────────────
INCIDENT_TYPES = [
    "Crowd Crush Risk", "Medical Emergency", "Unauthorized Access",
    "Fire / Smoke Alarm", "Lost Child / Person", "Equipment Failure",
    "Aggressive Behaviour", "Slip / Fall", "Electrical Fault",
    "Suspicious Package", "Other",
]
ZONES = {
    "Z1 – North Stand":          "Z1",
    "Z2 – South Stand":          "Z2",
    "Z3 – East Stand":           "Z3",
    "Z4 – West Stand":           "Z4",
    "Z5 – VIP Lounge":           "Z5",
    "Z6 – Press Box":            "Z6",
    "Z7 – Food Court A":         "Z7",
    "Z8 – Food Court B":         "Z8",
    "Z9 – Medical Center":       "Z9",
    "Z10 – Concourse L1 North":  "Z10",
    "Z11 – Concourse L1 South":  "Z11",
    "Z14 – Gate A":              "Z14",
    "Z15 – Gate B":              "Z15",
}
SEVERITIES = ["Low", "Medium", "High", "Critical"]
SEV_COLORS  = {"Low": "#10b981", "Medium": "#f59e0b", "High": "#ef4444", "Critical": "#dc2626"}

# ── Form ───────────────────────────────────────────────────────────────────────
ai_badge()
st.markdown("### 📋 Incident Details")

left, right = st.columns([1.1, 1])

with left:
    inc_type = st.selectbox("Incident Type", INCIDENT_TYPES, key="inc_type")
    zone_label = st.selectbox("Location / Zone", list(ZONES.keys()), key="inc_zone")
    severity  = st.select_slider(
        "Severity", options=SEVERITIES, value="Medium", key="inc_sev"
    )
    reported_by = st.text_input("Reported By (name / role)", placeholder="e.g. John Smith – Crowd Marshal", key="inc_reporter")

with right:
    inc_time = st.date_input("Incident Date", value=datetime.today(), key="inc_date")
    inc_hour = st.time_input("Incident Time", value=datetime.now().time(), key="inc_time")
    num_affected = st.number_input("Est. Persons Affected", min_value=0, value=1, step=1, key="inc_affected")
    action_taken = st.text_input("Immediate Action Taken", placeholder="e.g. Area cordoned, medics notified", key="inc_action")

description = st.text_area(
    "Incident Description",
    placeholder="Describe what happened in detail — circumstances, observations, any witness accounts…",
    height=130,
    key="inc_desc",
)

witnesses = st.text_input("Witnesses (optional)", placeholder="Names or volunteer IDs", key="inc_witnesses")

st.markdown("<br>", unsafe_allow_html=True)

# ── Severity indicator ─────────────────────────────────────────────────────────
sev_color = SEV_COLORS.get(severity, "#94a3b8")
st.markdown(
    f'<div style="display:inline-flex;align-items:center;gap:8px;margin-bottom:1rem;">'
    f'<span style="font-size:0.85rem;color:#94a3b8;">Selected Severity:</span>'
    f'<span style="background:{sev_color}22;color:{sev_color};border:1px solid {sev_color}55;'
    f'padding:4px 14px;border-radius:99px;font-weight:600;font-size:0.85rem;">{severity}</span>'
    f'</div>',
    unsafe_allow_html=True,
)

generate_btn = st.button(
    "🤖 Generate Incident Report with AI",
    key="gen_report",
    use_container_width=False,
    type="primary",
)

if not is_api_available():
    st.info("💡 Add GROQ_API_KEY to Streamlit Secrets to enable AI report generation.")

# ── Report Generation (Groq called HERE only) ──────────────────────────────────
if generate_btn:
    if not description.strip():
        st.warning("⚠️ Please add an incident description before generating the report.")
    else:
        zone_id = ZONES.get(zone_label, "Unknown")
        incident_context = f"""
Incident Type   : {inc_type}
Zone            : {zone_label} ({zone_id})
Date & Time     : {inc_time.strftime('%Y-%m-%d')} {inc_hour.strftime('%H:%M')}
Severity        : {severity}
Persons Affected: {num_affected}
Reported By     : {reported_by or 'Not specified'}
Immediate Action: {action_taken or 'None recorded'}
Witnesses       : {witnesses or 'None recorded'}
Description     : {description}
"""

        prompt = f"""You are a professional stadium operations AI. Generate a formal, structured 
incident report based on the details below. 

{incident_context}

Generate the report in this EXACT format:

---
SMART STADIUM — INCIDENT REPORT
================================

REPORT ID       : [auto-generate a realistic ID like INC-YYYYMMDD-XXX]
DATE & TIME     : [from input]
REPORTED BY     : [from input]
ZONE            : [from input]
INCIDENT TYPE   : [from input]
SEVERITY        : [from input]
STATUS          : Open

1. INCIDENT SUMMARY
   [2-3 sentence professional summary]

2. DETAILED DESCRIPTION
   [Expand the description into a professional, factual account]

3. PERSONS AFFECTED
   Count: [number]
   [Any relevant notes]

4. IMMEDIATE ACTIONS TAKEN
   [List actions taken, or note if none were recorded]

5. RECOMMENDED FOLLOW-UP ACTIONS
   [3-5 specific, actionable next steps based on incident type and severity]

6. RISK ASSESSMENT
   Probability of Recurrence : [Low / Medium / High]
   Potential Impact           : [assessment]
   Recommended Alert Level    : [GREEN / AMBER / RED]

7. WITNESSES / ADDITIONAL NOTES
   [From input, or 'None recorded']

---
Report generated by Smart Stadium AI · {datetime.now().strftime('%Y-%m-%d %H:%M')}
"""

        with st.spinner("Generating professional incident report…"):
            report = chat_completion(
                [{"role": "user", "content": prompt}],
                model="llama-3.3-70b-versatile",
                temperature=0.3,
                max_tokens=1200,
            )

        st.markdown("---")
        st.subheader("📄 Generated Incident Report")

        # Display in a styled box
        st.markdown(
            f'<div style="background:#0d1124;border:1px solid #2d3748;border-left:3px solid #ef4444;'
            f'border-radius:12px;padding:1.5rem;font-family:monospace;font-size:0.83rem;'
            f'color:#e2e8f0;white-space:pre-wrap;line-height:1.7;">{report}</div>',
            unsafe_allow_html=True,
        )

        # Download button
        st.download_button(
            label="⬇️ Download Report (.txt)",
            data=report,
            file_name=f"incident_report_{inc_time.strftime('%Y%m%d')}_{inc_type.replace(' ','_')}.txt",
            mime="text/plain",
            key="download_report",
        )

        # Store in session for reference
        st.session_state["last_report"] = report

info_card(
    "When to Use This Tool",
    "Generate official incident reports for any safety or operational event. "
    "The AI expands your description into a professional document ready for submission. "
    "Always review AI-generated reports before official submission.",
    "📋", "#f59e0b",
)
