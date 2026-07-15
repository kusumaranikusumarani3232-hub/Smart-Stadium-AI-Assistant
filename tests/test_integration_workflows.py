"""
tests/test_integration_workflows.py
====================================
Integration tests for the core user workflows of the Smart Stadium AI Assistant.
Ensures database loaders, graphs, algorithms, prompts, filters, and simulation state transitions
work together correctly. Runs completely offline.
"""
import pytest
import pandas as pd
import networkx as nx
from datetime import datetime
from unittest.mock import MagicMock, patch

from utils.data_loader import load_crowd_data, load_volunteers, load_events, load_zones
from utils.navigation_graph import build_graph, get_shortest_path, node_display_name
from utils.crowd_simulator import simulate_crowd_snapshot
from utils.groq_client import chat_completion

# ── 1. Crowd Monitoring Workflow Integration ──────────────────────────────────

def test_crowd_monitoring_workflow():
    """Tests loading real-time data, evaluating alerts, and building the AI recommendation prompt."""
    # 1. Load latest data
    df = load_crowd_data()
    latest_time = df["timestamp"].max()
    latest = df[df["timestamp"] == latest_time]
    
    assert len(latest) == 8  # 8 zones monitored
    
    # 2. Count alert distributions
    critical = latest[latest["alert_level"] == "CRITICAL"]
    high = latest[latest["alert_level"] == "HIGH"]
    
    # 3. Simulate building the context payload sent to the AI
    crowd_ctx = latest[
        ["zone_name", "density_pct", "alert_level", "current_occupancy", "capacity"]
    ].to_string(index=False)
    
    # Check that context formatting contains critical columns
    assert "zone_name" in crowd_ctx
    assert "alert_level" in crowd_ctx
    
    # 4. Inject a mock AI completions client to analyze crowd
    mock_choice = MagicMock()
    mock_choice.message.content = "Actionable AI Decision Support Recommendations:\n- Redeploy 5 Marshals to North Stand"
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_response

    with patch("utils.groq_client.get_groq_client", return_value=mock_client):
        ai_recommendation = chat_completion([
            {"role": "user", "content": f"Analyze: {crowd_ctx}"}
        ])
    
    assert "Actionable AI" in ai_recommendation
    assert "Redeploy" in ai_recommendation


# ── 2. Navigation Routing Workflow Integration ───────────────────────────────

def test_navigation_routing_workflow():
    """Tests loading the graph network and calculating shortest paths across waypoints."""
    # 1. Build navigation graph
    G = build_graph()
    assert len(G.nodes) > 0
    assert len(G.edges) > 0
    
    # 2. Select two valid nodes (e.g. Gate A to Medical Center)
    source = "gate_a"
    target = "medical"
    
    path_nodes, total_dist = get_shortest_path(G, source, target)
    
    # 3. Verify walking calculation results
    assert path_nodes is not None
    assert path_nodes[0] == source
    assert path_nodes[-1] == target
    assert total_dist > 0
    
    # 4. Walking time estimation check (~80 m/min pace)
    est_min = round(total_dist / 80, 1)
    assert est_min > 0
    
    # 5. Check names
    display_names = [node_display_name(G, nid) for nid in path_nodes]
    assert "Gate A" in display_names[0]
    assert "Medical" in display_names[-1]

    # 6. Check disconnected node handles gracefully
    # Add an isolated node to graph
    G.add_node("isolated_node")
    path_nodes_iso, total_dist_iso = get_shortest_path(G, "gate_a", "isolated_node")
    assert path_nodes_iso is None
    assert total_dist_iso is None


# ── 3. Incident Reporting Workflow Integration ────────────────────────────────

def test_incident_reporting_workflow():
    """Tests filling incident parameters, formatting the payload, and receiving the AI text report."""
    # 1. Prepare form payloads
    payload = {
        "inc_type": "Crowd Crush Risk",
        "zone_label": "Z1 – North Stand",
        "zone_id": "Z1",
        "date": datetime(2024, 7, 14),
        "hour": datetime(2024, 7, 14, 15, 30).time(),
        "severity": "Critical",
        "affected": 15,
        "reporter": "John Marshal",
        "action": "Opened gates to spill area",
        "witnesses": "V1002, V1004",
        "desc": "Sudden surge near gate entry. High crowding pressure.",
    }
    
    # 2. Build prompt context mapping
    incident_context = f"""
    Incident Type   : {payload['inc_type']}
    Zone            : {payload['zone_label']} ({payload['zone_id']})
    Date & Time     : {payload['date'].strftime('%Y-%m-%d')} {payload['hour'].strftime('%H:%M')}
    Severity        : {payload['severity']}
    Persons Affected: {payload['affected']}
    Reported By     : {payload['reporter']}
    Immediate Action: {payload['action']}
    Witnesses       : {payload['witnesses']}
    Description     : {payload['desc']}
    """
    
    assert "Crowd Crush Risk" in incident_context
    assert "Critical" in incident_context
    
    # 3. Fetch report via Mock API
    mock_choice = MagicMock()
    mock_choice.message.content = "SMART STADIUM — INCIDENT REPORT\nREPORT ID: INC-20240714-001\nSTATUS: Open"
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_response

    with patch("utils.groq_client.get_groq_client", return_value=mock_client):
        report = chat_completion([{"role": "user", "content": incident_context}])
        
    assert "SMART STADIUM" in report
    assert "STATUS: Open" in report


# ── 4. Volunteer Assistant Roster Filtering Integration ───────────────────────

def test_volunteer_filtering_workflow():
    """Tests loading the roster data and applying combined role, zone, and status filters."""
    # 1. Load volunteers
    vol_df = load_volunteers()
    assert len(vol_df) > 0
    
    # 2. Apply role filter
    role_filter = ["Crowd Marshal"]
    filtered_by_role = vol_df[vol_df["role"].isin(role_filter)]
    assert (filtered_by_role["role"] == "Crowd Marshal").all()
    
    # 3. Apply combined status filter
    status_filter = ["On Duty"]
    filtered_combined = filtered_by_role[filtered_by_role["status"].isin(status_filter)]
    assert (filtered_combined["status"] == "On Duty").all()
    
    # 4. Check status distribution mapping
    status_counts = vol_df.groupby("status").size().to_dict()
    assert "On Duty" in status_counts


# ── 5. Admin Panel Simulation Overrides Integration ──────────────────────────

def test_admin_simulation_workflow():
    """Tests setting manual slider overrides and simulating crowd states with noise variation."""
    # 1. Set manual override densities
    manual_overrides = {
        "Z1": 95.0,  # Critical limit
        "Z2": 25.0,  # Low limit
    }
    
    # 2. Run simulation snapshot with noise
    sim_df = simulate_crowd_snapshot(manual_overrides=manual_overrides, noise_level=0.05, seed=42)
    
    # 3. Verify overrides are respected within the background noise bounds
    # Zone 1 override 95.0 + noise (noise is in [-0.05, 0.05] for seed 42)
    z1_res = sim_df[sim_df["zone_id"] == "Z1"].iloc[0]
    assert abs(z1_res["density_pct"] - 95.0) <= 5.0
    assert z1_res["alert_level"] in ("HIGH", "CRITICAL")
    
    # Zone 2 override 25.0 + noise
    z2_res = sim_df[sim_df["zone_id"] == "Z2"].iloc[0]
    assert abs(z2_res["density_pct"] - 25.0) <= 5.0
    assert z2_res["alert_level"] == "LOW"
    
    # 4. Ensure non-overridden zones are still generated
    assert len(sim_df) == 8
