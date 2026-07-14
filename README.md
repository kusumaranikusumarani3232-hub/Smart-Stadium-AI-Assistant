# 🏟️ Smart Stadium AI Assistant

> A hackathon-ready GenAI platform that improves stadium operations and tournament experience for fans, organizers, volunteers, and staff.

[![Streamlit](https://img.shields.io/badge/Built%20with-Streamlit-FF4B4B?logo=streamlit)](https://streamlit.io)
[![Groq](https://img.shields.io/badge/AI-Groq%20Llama%203-00C7B7)](https://console.groq.com)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python)](https://python.org)

---

## ✨ Features

| Feature | Description | AI Required? |
|---------|-------------|:---:|
| 🎯 **Crowd Monitoring** | Real-time zone density cards, Plotly charts, alert banners | Decision Support only |
| 🗺️ **Smart Navigation** | NetworkX Dijkstra shortest-path + Plotly graph viz | ❌ No |
| 🌐 **Multilingual Assistant** | Chat in 10+ languages via Groq Llama 3 | ✅ Yes |
| 🤝 **Volunteer Assistant** | Roster management, analytics, AI shift Q&A | Chat only |
| 🏟️ **Fan Assistant** | Match-day companion for fans | ✅ Yes |
| 🚨 **Incident Reports** | Form → AI-generated structured report + download | ✅ Yes |
| 📊 **Analytics Dashboard** | 10+ Plotly charts (attendance, incidents, volunteers) | ❌ No |
| ⚙️ **Admin Panel** | Crowd simulation sliders + AI operational alerts | Alert button only |

---

## 🚀 Quick Start

### 1. Clone the repo
```bash
git clone https://github.com/your-username/smart-stadium-ai
cd smart-stadium-ai
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure your Groq API key
```bash
# Copy the example file
cp .streamlit/secrets.toml.example .streamlit/secrets.toml

# Edit secrets.toml and add your key
# Get a free key at https://console.groq.com
```
`.streamlit/secrets.toml`:
```toml
GROQ_API_KEY = "gsk_your_key_here"
```

> **Note:** Analytics, Navigation, and all dashboards work without an API key.  
> Only AI chat features (multilingual, fan/volunteer Q&A, incident reports, decision support) require Groq.

### 4. Run the app
```bash
streamlit run app.py
```

---

## ☁️ Deploy to Streamlit Cloud

1. Push this repository to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io) → **New app**
3. Select your repo, set **Main file**: `app.py`
4. In **App Settings → Secrets**, add:
   ```toml
   GROQ_API_KEY = "gsk_your_key_here"
   ```
5. Click **Deploy** — done!

> Synthetic CSV data is auto-generated on first run — no pre-committed data files needed.

---

## 🏗️ Project Structure

```
Smart Stadium AI Assistant/
├── app.py                          # 🏠 Home page & entry point
├── requirements.txt                # Dependencies
├── README.md
│
├── .streamlit/
│   ├── config.toml                 # Dark theme configuration
│   └── secrets.toml.example        # API key template
│
├── pages/                          # Streamlit multipage pages
│   ├── 1_Crowd_Monitoring.py       # 🎯 Zone density + AI decisions
│   ├── 2_Navigation.py             # 🗺️ NetworkX pathfinding
│   ├── 3_Multilingual_Assistant.py # 🌐 10-language AI chat
│   ├── 4_Volunteer_Assistant.py    # 🤝 Roster + AI Q&A
│   ├── 5_Fan_Assistant.py          # 🏟️ Fan chat
│   ├── 6_Incident_Report.py        # 🚨 AI report generator
│   ├── 7_Analytics.py              # 📊 Plotly dashboards
│   └── 8_Admin_Panel.py            # ⚙️ Crowd sim + AI alerts
│
├── utils/
│   ├── __init__.py
│   ├── groq_client.py              # Groq API wrapper (lazy init)
│   ├── data_loader.py              # CSV loaders + synthetic data gen
│   ├── ui_helpers.py               # CSS, card components, Plotly theme
│   ├── crowd_simulator.py          # Algorithmic crowd simulation
│   └── navigation_graph.py         # NetworkX graph + Dijkstra
│
└── data/                           # Auto-generated CSVs (first run)
    ├── crowd_data.csv              # 48 snapshots × 8 zones
    ├── zones.csv                   # 15 stadium zones
    ├── incidents.csv               # 50 historical incidents
    ├── volunteers.csv              # 30 volunteers
    ├── navigation_nodes.csv        # 29 nav nodes with adjacency
    └── events.csv                  # 15 tournament events
```

---

## 🤖 AI Usage Policy

| Module | Calls Groq? | Reason |
|--------|:-----------:|--------|
| Home dashboard | ❌ | Static metrics & charts |
| Crowd charts | ❌ | Plotly rendering |
| Navigation algorithm | ❌ | NetworkX Dijkstra (pure code) |
| Analytics dashboards | ❌ | Plotly visualisations |
| **Crowd Decision Support** | ✅ | AI reasoning required |
| **Multilingual Chat** | ✅ | Language translation & response |
| **Fan/Volunteer Chat** | ✅ | Contextual AI answers |
| **Incident Report Gen** | ✅ | Document generation |
| **Admin AI Alert** | ✅ | Operational recommendations |

Models used:
- `llama-3.3-70b-versatile` — heavy reasoning (reports, decision support)
- `llama-3.1-8b-instant` — fast real-time chat (fan, volunteer)

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Streamlit 1.35+ |
| AI | Groq API (Llama 3) |
| Navigation | NetworkX (Dijkstra) |
| Charts | Plotly Express + Graph Objects |
| Data | Pandas + NumPy (synthetic, seeded) |
| Styling | Custom CSS (dark stadium theme) |
| Fonts | Google Fonts — Inter + Space Grotesk |

---

## 📊 Synthetic Data

All data is procedurally generated with fixed seeds (`numpy.random.seed(42)`) for reproducibility.  
No real personal data is used. CSVs are created automatically on first run and cached.

---

## 📜 License

MIT — free to use, modify, and deploy for hackathons, demos, and production.

