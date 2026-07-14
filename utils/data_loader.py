"""
Data loading utilities for Smart Stadium AI Assistant.

All synthetic CSV datasets are generated here with a fixed seed so the app
works out-of-the-box on Streamlit Cloud without any pre-committed data files.
CSVs are written to the `data/` folder on first run and cached by Streamlit.
NO Groq API calls in this module.
"""
from __future__ import annotations

import os
import random
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import streamlit as st

# ── Paths ──────────────────────────────────────────────────────────────────────
_HERE = os.path.dirname(__file__)
DATA_DIR = os.path.join(_HERE, "..", "data")


def _ensure_dir() -> None:
    os.makedirs(DATA_DIR, exist_ok=True)


def _path(filename: str) -> str:
    return os.path.join(DATA_DIR, filename)


# ══════════════════════════════════════════════════════════════════════════════
#  GENERATORS  (private — called automatically when CSVs are absent)
# ══════════════════════════════════════════════════════════════════════════════

def _gen_crowd_data() -> pd.DataFrame:
    """
    48 half-hourly snapshots × 8 zones = 384 rows.
    Simulates a match day with kickoff at 15:00.
    """
    np.random.seed(42)
    zones = [
        ("Z1", "North Stand",   8000),
        ("Z2", "South Stand",   8000),
        ("Z3", "East Stand",    6000),
        ("Z4", "West Stand",    6000),
        ("Z5", "VIP Lounge",    500),
        ("Z6", "Press Box",     200),
        ("Z7", "Food Court A",  1000),
        ("Z8", "Food Court B",  1000),
    ]
    base_time = datetime(2024, 7, 14, 8, 0)
    timestamps = [base_time + timedelta(minutes=30 * i) for i in range(48)]

    rows = []
    for ts in timestamps:
        h = ts.hour
        # crowd ramp: pre-match → peak → post-match
        if 15 <= h <= 19:
            peak = 0.83
        elif 13 <= h <= 21:
            peak = 0.58
        elif 10 <= h <= 12:
            peak = 0.28
        else:
            peak = 0.10

        for zone_id, zone_name, capacity in zones:
            # VIP & Press Box fill differently
            zone_factor = {"Z5": 0.92, "Z6": 0.88, "Z7": 1.10, "Z8": 1.06}.get(zone_id, 1.0)
            if zone_id == "Z6" and h < 13:
                occ = np.random.uniform(0.35, 0.60)
            else:
                noise = np.random.uniform(-0.07, 0.07)
                occ = min(1.0, max(0.02, peak * zone_factor + noise))

            current = int(capacity * occ)
            density = round(occ * 100, 1)
            alert = _alert_str(density)
            rows.append([ts.strftime("%Y-%m-%d %H:%M"), zone_id, zone_name,
                         capacity, current, density, alert])

    df = pd.DataFrame(rows, columns=[
        "timestamp", "zone_id", "zone_name",
        "capacity", "current_occupancy", "density_pct", "alert_level",
    ])
    df.to_csv(_path("crowd_data.csv"), index=False)
    return df


def _gen_zones() -> pd.DataFrame:
    """15 stadium zones with spatial coordinates (0–100 grid)."""
    data = [
        ("Z1",  "North Stand",          "seating",     8000,  50,  15, "Toilets, Refreshments, Emergency Exit"),
        ("Z2",  "South Stand",          "seating",     8000,  50,  85, "Toilets, Refreshments, First Aid"),
        ("Z3",  "East Stand",           "seating",     6000,  85,  50, "Toilets, Refreshments"),
        ("Z4",  "West Stand",           "seating",     6000,  15,  50, "Toilets, Refreshments, Viewing Platform"),
        ("Z5",  "VIP Lounge",           "premium",     500,   62,  40, "Private Bar, Lounge Seating, Toilets, Catering"),
        ("Z6",  "Press Box",            "media",       200,   40,  33, "Media Desks, Commentary Booths, Toilets"),
        ("Z7",  "Food Court A",         "amenity",     1000,  72,  20, "Multiple Food Stalls, Seating, ATM"),
        ("Z8",  "Food Court B",         "amenity",     1000,  28,  80, "Multiple Food Stalls, Seating, ATM"),
        ("Z9",  "Medical Center",       "emergency",   100,   50,  90, "First Aid, Ambulance Bay, Defibrillator"),
        ("Z10", "Concourse L1 North",   "circulation", 2000,  50,  22, "Toilets, Info Desk, Sponsor Zone"),
        ("Z11", "Concourse L1 South",   "circulation", 2000,  50,  78, "Toilets, Merchandise Shop"),
        ("Z12", "Concourse L1 East",    "circulation", 1500,  78,  50, "Toilets, Souvenir Shop"),
        ("Z13", "Concourse L1 West",    "circulation", 1500,  22,  50, "Toilets, Fan Zone"),
        ("Z14", "Gate A – Main Entry",  "entrance",    5000,  50,   3, "Ticket Scanners, Security, Bag Check"),
        ("Z15", "Gate B – South Entry", "entrance",    3000,  50,  97, "Ticket Scanners, Security"),
    ]
    df = pd.DataFrame(data, columns=[
        "zone_id", "name", "type", "capacity",
        "x_coord", "y_coord", "facilities",
    ])
    df.to_csv(_path("zones.csv"), index=False)
    return df


def _gen_incidents() -> pd.DataFrame:
    """50 historical incidents across 4 match days."""
    np.random.seed(123)
    random.seed(123)
    types = [
        "Crowd Crush Risk", "Medical Emergency", "Unauthorized Access",
        "Fire Alarm", "Lost Child", "Equipment Failure",
        "Aggressive Behavior", "Slip / Fall",
    ]
    zone_map = {
        "Z1": "North Stand", "Z2": "South Stand",
        "Z3": "East Stand",  "Z4": "West Stand",
        "Z7": "Food Court A", "Z8": "Food Court B",
        "Z10": "Concourse L1 North", "Z11": "Concourse L1 South",
    }
    zones = list(zone_map.keys())
    severities = ["Low", "Medium", "High", "Critical"]
    sev_weights = [0.40, 0.35, 0.20, 0.05]

    base = datetime(2024, 7, 10, 8, 0)
    rows = []
    for i in range(50):
        ts = base + timedelta(
            hours=random.randint(0, 96),
            minutes=random.choice([0, 15, 30, 45]),
        )
        zone_id = random.choice(zones)
        inc_type = random.choice(types)
        sev = random.choices(severities, weights=sev_weights)[0]
        desc = (
            f"{inc_type} reported at {zone_map[zone_id]}. "
            "Response team notified. Situation being monitored."
        )
        resolved = random.random() > 0.15
        rows.append([
            f"INC-{1000 + i}",
            ts.strftime("%Y-%m-%d %H:%M"),
            zone_id, zone_map[zone_id],
            inc_type, sev, desc, resolved,
        ])
    df = pd.DataFrame(rows, columns=[
        "incident_id", "timestamp", "zone_id", "zone_name",
        "type", "severity", "description", "resolved",
    ])
    df.to_csv(_path("incidents.csv"), index=False)
    return df


def _gen_volunteers() -> pd.DataFrame:
    """30 volunteers with roles, zones, shifts, and current status."""
    np.random.seed(7)
    names = [
        "Aditya Sharma", "Priya Patel",  "Rahul Verma",   "Sneha Iyer",
        "Vikram Singh",  "Anjali Nair",  "Rohan Mehta",   "Deepika Rao",
        "Arjun Gupta",   "Kavya Menon",  "Suresh Kumar",  "Meera Pillai",
        "Nikhil Joshi",  "Pooja Desai",  "Karthik Reddy", "Asha Thomas",
        "Mohan Naidu",   "Radha Krishnan","Sanjay Bose",  "Lakshmi Devi",
        "Dev Malhotra",  "Uma Sharma",   "Rajesh Tiwari", "Sunita Yadav",
        "Varun Chopra",  "Nalini Shetty","Prakash Goud",  "Divya Nambiar",
        "Harish Chand",  "Geeta Bhatt",
    ]
    roles = [
        "Crowd Marshal", "Medical First Responder", "Gate Scanner",
        "Info Desk",     "Security Patrol",          "Accessibility Guide",
        "Food Court Supervisor", "Incident Coordinator",
    ]
    zones = ["Z1", "Z2", "Z3", "Z4", "Z7", "Z8", "Z10", "Z14"]
    statuses = ["On Duty", "On Break", "Off Shift", "Standby"]
    sw = [0.55, 0.15, 0.15, 0.15]
    shift_starts = ["07:00", "08:00", "09:00", "12:00", "14:00"]
    shift_ends   = ["14:00", "17:00", "20:00", "22:00", "23:00"]

    rows = []
    for i, name in enumerate(names):
        role   = roles[i % len(roles)]
        zone   = np.random.choice(zones)
        start  = np.random.choice(shift_starts)
        end    = np.random.choice(shift_ends)
        status = np.random.choice(statuses, p=sw)
        rows.append([f"V{1000 + i}", name, role, zone, start, end, status])

    df = pd.DataFrame(rows, columns=[
        "volunteer_id", "name", "role",
        "zone", "shift_start", "shift_end", "status",
    ])
    df.to_csv(_path("volunteers.csv"), index=False)
    return df


def _gen_navigation_nodes() -> pd.DataFrame:
    """
    29 stadium navigation nodes with x/y coords (0–100 grid) and
    pipe-separated neighbors in 'node_id:distance_metres' format.
    The NetworkX graph is built from this in utils/navigation_graph.py.
    """
    nodes = [
        # id                  name                              type           x    y   neighbors
        ("gate_a",        "Gate A – Main Entrance",       "entrance",    50,   3,  "ticket_north:30|emergency_n:8"),
        ("gate_b",        "Gate B – South Entrance",      "entrance",    50,  97,  "ticket_south:30|medical:20"),
        ("gate_c",        "Gate C – East Entrance",       "entrance",    93,  50,  "concourse_e:40"),
        ("gate_d",        "Gate D – West Entrance",       "entrance",     7,  50,  "concourse_w:40"),
        ("emergency_n",   "Emergency Exit – North",       "emergency",   50,   1,  "gate_a:8"),
        ("ticket_north",  "Ticket Counter North",         "service",     50,  10,  "gate_a:30|concourse_n:45"),
        ("ticket_south",  "Ticket Counter South",         "service",     50,  90,  "gate_b:30|concourse_s:35"),
        ("concourse_n",   "Concourse North Hub",          "circulation", 50,  22,  "ticket_north:45|concourse_ne:55|concourse_nw:55|north_stand:35"),
        ("concourse_s",   "Concourse South Hub",          "circulation", 50,  78,  "ticket_south:35|concourse_se:55|concourse_sw:55|south_stand:35"),
        ("concourse_e",   "Concourse East Hub",           "circulation", 78,  50,  "gate_c:40|concourse_ne:65|concourse_se:65|east_stand:30"),
        ("concourse_w",   "Concourse West Hub",           "circulation", 22,  50,  "gate_d:40|concourse_nw:65|concourse_sw:65|west_stand:30"),
        ("concourse_ne",  "Concourse NE Junction",        "circulation", 68,  22,  "concourse_n:55|concourse_e:65|food_court_a:25|restroom_ne:18"),
        ("concourse_nw",  "Concourse NW Junction",        "circulation", 32,  22,  "concourse_n:55|concourse_w:65|press_box:28|restroom_nw:18"),
        ("concourse_se",  "Concourse SE Junction",        "circulation", 68,  78,  "concourse_s:55|concourse_e:65|restroom_se:18"),
        ("concourse_sw",  "Concourse SW Junction",        "circulation", 32,  78,  "concourse_s:55|concourse_w:65|food_court_b:25|restroom_sw:18"),
        ("north_stand",   "North Stand Entry",            "seating",     50,  30,  "concourse_n:35|vip_lounge:45|press_box:38|info_desk:55"),
        ("south_stand",   "South Stand Entry",            "seating",     50,  70,  "concourse_s:35|info_desk:55"),
        ("east_stand",    "East Stand Entry",             "seating",     70,  50,  "concourse_e:30|vip_lounge:35|info_desk:55"),
        ("west_stand",    "West Stand Entry",             "seating",     30,  50,  "concourse_w:30|info_desk:55"),
        ("vip_lounge",    "VIP Lounge",                   "premium",     62,  40,  "north_stand:45|east_stand:35"),
        ("press_box",     "Press Box",                    "media",       40,  32,  "north_stand:38|concourse_nw:28"),
        ("food_court_a",  "Food Court A",                 "amenity",     72,  20,  "concourse_ne:25|restroom_ne:20"),
        ("food_court_b",  "Food Court B",                 "amenity",     28,  80,  "concourse_sw:25|restroom_sw:20"),
        ("medical",       "Medical Center",               "emergency",   50,  88,  "gate_b:20|concourse_s:30"),
        ("info_desk",     "Information Desk",             "service",     50,  50,  "north_stand:55|south_stand:55|east_stand:55|west_stand:55"),
        ("restroom_ne",   "Restroom – NE",                "restroom",    74,  26,  "concourse_ne:18|food_court_a:20"),
        ("restroom_nw",   "Restroom – NW",                "restroom",    26,  26,  "concourse_nw:18"),
        ("restroom_se",   "Restroom – SE",                "restroom",    74,  74,  "concourse_se:18"),
        ("restroom_sw",   "Restroom – SW",                "restroom",    26,  74,  "concourse_sw:18|food_court_b:20"),
    ]
    df = pd.DataFrame(nodes, columns=["node_id", "name", "type", "x", "y", "neighbors"])
    df.to_csv(_path("navigation_nodes.csv"), index=False)
    return df


def _gen_events() -> pd.DataFrame:
    """15 tournament events across a week."""
    data = [
        ("EVT001", "Group Stage – Match 1", "India vs Australia",        "2024-07-14", "09:00", "Z1,Z3",           28000, "Completed"),
        ("EVT002", "Group Stage – Match 2", "England vs New Zealand",    "2024-07-14", "13:00", "Z2,Z4",           25000, "Completed"),
        ("EVT003", "Group Stage – Match 3", "Pakistan vs South Africa",  "2024-07-14", "17:00", "Z1,Z2,Z3,Z4",    32000, "Live"),
        ("EVT004", "Group Stage – Match 4", "West Indies vs Sri Lanka",  "2024-07-15", "09:30", "Z1,Z3",           22000, "Upcoming"),
        ("EVT005", "Group Stage – Match 5", "Bangladesh vs Afghanistan", "2024-07-15", "14:00", "Z2,Z4",           20000, "Upcoming"),
        ("EVT006", "Quarter Final 1",       "India vs England",          "2024-07-17", "14:00", "Z1,Z2,Z3,Z4",    38000, "Upcoming"),
        ("EVT007", "Quarter Final 2",       "Australia vs Pakistan",     "2024-07-18", "14:00", "Z1,Z2,Z3,Z4",    36000, "Upcoming"),
        ("EVT008", "Semi Final 1",          "TBD vs TBD",                "2024-07-20", "14:00", "Z1,Z2,Z3,Z4",    40000, "Upcoming"),
        ("EVT009", "Semi Final 2",          "TBD vs TBD",                "2024-07-21", "14:00", "Z1,Z2,Z3,Z4",    40000, "Upcoming"),
        ("EVT010", "FINAL",                 "TBD vs TBD",                "2024-07-23", "16:00", "Z1,Z2,Z3,Z4",    42000, "Upcoming"),
        ("EVT011", "Training Session",      "India Practice",            "2024-07-13", "08:00", "Z3",              5000,  "Completed"),
        ("EVT012", "Fan Meet & Greet",      "Fan Zone Event",            "2024-07-14", "11:00", "Z13",             2000,  "Live"),
        ("EVT013", "Press Conference",      "Post-Match Briefing",       "2024-07-14", "20:00", "Z6",               200,  "Upcoming"),
        ("EVT014", "Sponsor Activation",    "Brand Expo",                "2024-07-14", "10:00", "Z10",              800,  "Live"),
        ("EVT015", "Medical Briefing",      "Staff Health Update",       "2024-07-14", "07:00", "Z9",                50,  "Completed"),
    ]
    df = pd.DataFrame(data, columns=[
        "event_id", "match_name", "teams",
        "date", "time", "zones",
        "expected_attendance", "status",
    ])
    df.to_csv(_path("events.csv"), index=False)
    return df


# ══════════════════════════════════════════════════════════════════════════════
#  PUBLIC LOADERS  (cached by Streamlit — only reads disk / generates once)
# ══════════════════════════════════════════════════════════════════════════════

@st.cache_data(show_spinner=False)
def load_crowd_data() -> pd.DataFrame:
    _ensure_dir()
    p = _path("crowd_data.csv")
    return pd.read_csv(p) if os.path.exists(p) else _gen_crowd_data()


@st.cache_data(show_spinner=False)
def load_zones() -> pd.DataFrame:
    _ensure_dir()
    p = _path("zones.csv")
    return pd.read_csv(p) if os.path.exists(p) else _gen_zones()


@st.cache_data(show_spinner=False)
def load_incidents() -> pd.DataFrame:
    _ensure_dir()
    p = _path("incidents.csv")
    return pd.read_csv(p) if os.path.exists(p) else _gen_incidents()


@st.cache_data(show_spinner=False)
def load_volunteers() -> pd.DataFrame:
    _ensure_dir()
    p = _path("volunteers.csv")
    return pd.read_csv(p) if os.path.exists(p) else _gen_volunteers()


@st.cache_data(show_spinner=False)
def load_navigation_nodes() -> pd.DataFrame:
    _ensure_dir()
    p = _path("navigation_nodes.csv")
    return pd.read_csv(p) if os.path.exists(p) else _gen_navigation_nodes()


@st.cache_data(show_spinner=False)
def load_events() -> pd.DataFrame:
    _ensure_dir()
    p = _path("events.csv")
    return pd.read_csv(p) if os.path.exists(p) else _gen_events()


def ensure_all_data() -> None:
    """Pre-generate and cache all datasets on first app start."""
    for loader in (
        load_crowd_data, load_zones, load_incidents,
        load_volunteers, load_navigation_nodes, load_events,
    ):
        loader()


# ── Helpers ────────────────────────────────────────────────────────────────────
def _alert_str(density_pct: float) -> str:
    if density_pct >= 90:
        return "CRITICAL"
    if density_pct >= 75:
        return "HIGH"
    if density_pct >= 50:
        return "MODERATE"
    return "LOW"
