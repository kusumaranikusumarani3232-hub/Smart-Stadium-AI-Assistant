"""
conftest.py — Shared pytest fixtures for Smart Stadium AI Assistant tests.

Placed at: tests/conftest.py

Provides:
  - Lightweight in-memory data fixtures (no CSV reads, no Streamlit context needed)
  - A mock for utils.groq_client.get_groq_client so real API calls are never made
"""
import pytest
import networkx as nx
import pandas as pd


# ── Navigation graph fixture ───────────────────────────────────────────────────

@pytest.fixture()
def simple_graph() -> nx.Graph:
    """
    A tiny 4-node graph with known distances for deterministic path tests.

        A --10-- B --20-- C
                 |
                15
                 |
                 D
    """
    G = nx.Graph()
    G.add_node("A", name="Node A", type="entrance", x=0.0, y=0.0)
    G.add_node("B", name="Node B", type="circulation", x=10.0, y=0.0)
    G.add_node("C", name="Node C", type="seating", x=30.0, y=0.0)
    G.add_node("D", name="Node D", type="amenity", x=10.0, y=15.0)
    # Isolated node — no edges
    G.add_node("X", name="Node X (isolated)", type="restroom", x=99.0, y=99.0)

    G.add_edge("A", "B", distance=10.0)
    G.add_edge("B", "C", distance=20.0)
    G.add_edge("B", "D", distance=15.0)
    return G


# ── Data fixtures ──────────────────────────────────────────────────────────────

@pytest.fixture()
def sample_crowd_df() -> pd.DataFrame:
    """Minimal crowd DataFrame matching the production schema."""
    return pd.DataFrame({
        "timestamp":         ["2024-07-14 15:00", "2024-07-14 15:00"],
        "zone_id":           ["Z1", "Z2"],
        "zone_name":         ["North Stand", "South Stand"],
        "capacity":          [8000, 8000],
        "current_occupancy": [6800, 3200],
        "density_pct":       [85.0, 40.0],
        "alert_level":       ["HIGH", "LOW"],
    })


@pytest.fixture()
def sample_volunteers_df() -> pd.DataFrame:
    """Minimal volunteers DataFrame matching the production schema."""
    return pd.DataFrame({
        "volunteer_id": ["V1000", "V1001", "V1002"],
        "name":         ["Alice Smith", "Bob Jones", "Carol Lee"],
        "role":         ["Crowd Marshal", "Medical First Responder", "Gate Scanner"],
        "zone":         ["Z1", "Z2", "Z3"],
        "shift_start":  ["07:00", "08:00", "09:00"],
        "shift_end":    ["14:00", "17:00", "20:00"],
        "status":       ["On Duty", "On Break", "Standby"],
    })


@pytest.fixture()
def sample_events_df() -> pd.DataFrame:
    """Minimal events DataFrame matching the production schema."""
    return pd.DataFrame({
        "event_id":            ["EVT001", "EVT002"],
        "match_name":          ["Group Stage – Match 1", "Group Stage – Match 2"],
        "teams":               ["India vs Australia", "England vs NZ"],
        "date":                ["2024-07-14", "2024-07-15"],
        "time":                ["09:00", "13:00"],
        "zones":               ["Z1,Z3", "Z2,Z4"],
        "expected_attendance": [28000, 25000],
        "status":              ["Completed", "Upcoming"],
    })


# ── Groq mock fixture ──────────────────────────────────────────────────────────

@pytest.fixture()
def mock_groq_client(mocker):
    """
    Patch utils.groq_client.get_groq_client to return a mock Groq client.
    The mock client's chat.completions.create() returns a fixed response.

    Usage in a test:
        def test_something(mock_groq_client):
            from utils.groq_client import chat_completion
            result = chat_completion([{"role": "user", "content": "Hello"}])
            assert result == "Mock AI response"
    """
    mock_choice = mocker.MagicMock()
    mock_choice.message.content = "Mock AI response"

    mock_response = mocker.MagicMock()
    mock_response.choices = [mock_choice]

    mock_client = mocker.MagicMock()
    mock_client.chat.completions.create.return_value = mock_response

    mocker.patch(
        "utils.groq_client.get_groq_client",
        return_value=mock_client,
    )
    return mock_client
