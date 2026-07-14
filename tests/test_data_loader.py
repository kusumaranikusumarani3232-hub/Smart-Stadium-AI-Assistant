"""
tests/test_data_loader.py
=========================
Unit tests for utils/data_loader.py

Strategy
--------
* We test the *private* helper `_alert_str()` and the *private* generator
  functions `_gen_*()` directly, because they are pure Python with no
  Streamlit decorators and no network calls.

* The public `load_*()` functions are decorated with @st.cache_data and
  require a Streamlit runtime, so they are intentionally NOT tested here.
  Their logic is covered indirectly through the generator tests.

* `_path()` and `_ensure_dir()` are light filesystem helpers — we verify
  `_path()` returns the expected joined path without touching the disk.
"""
import os
import sys
import pytest

# ---------------------------------------------------------------------------
# Make the project root importable when pytest is run from the project dir.
# ---------------------------------------------------------------------------
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from utils.data_loader import (
    _alert_str,
    _gen_crowd_data,
    _gen_zones,
    _gen_incidents,
    _gen_volunteers,
    _gen_navigation_nodes,
    _gen_events,
    _path,
)


# ── _alert_str ─────────────────────────────────────────────────────────────────

class TestAlertStr:
    """Tests for the density → alert level mapping helper."""

    def test_low_below_50(self):
        assert _alert_str(0.0) == "LOW"
        assert _alert_str(49.9) == "LOW"

    def test_moderate_at_50(self):
        """Boundary: exactly 50 → MODERATE."""
        assert _alert_str(50.0) == "MODERATE"

    def test_moderate_range(self):
        assert _alert_str(60.0) == "MODERATE"
        assert _alert_str(74.9) == "MODERATE"

    def test_high_at_75(self):
        """Boundary: exactly 75 → HIGH."""
        assert _alert_str(75.0) == "HIGH"

    def test_high_range(self):
        assert _alert_str(80.0) == "HIGH"
        assert _alert_str(89.9) == "HIGH"

    def test_critical_at_90(self):
        """Boundary: exactly 90 → CRITICAL."""
        assert _alert_str(90.0) == "CRITICAL"

    def test_critical_above_90(self):
        assert _alert_str(95.0) == "CRITICAL"
        assert _alert_str(100.0) == "CRITICAL"

    def test_returns_string(self):
        """Return value must always be a non-empty string."""
        for density in [0, 30, 50, 75, 90, 100]:
            result = _alert_str(density)
            assert isinstance(result, str) and len(result) > 0

    def test_only_valid_levels_returned(self):
        """Only the 4 defined levels should ever be returned."""
        valid_levels = {"LOW", "MODERATE", "HIGH", "CRITICAL"}
        for density in range(0, 101, 5):
            assert _alert_str(float(density)) in valid_levels


# ── _gen_crowd_data ────────────────────────────────────────────────────────────

class TestGenCrowdData:
    """Tests for the crowd data generator (no disk writes needed — just call it)."""

    @pytest.fixture(scope="class")
    def crowd_df(self, tmp_path_factory):
        """
        Generate crowd data into a temp directory so we don't pollute the
        real data/ folder and don't depend on it already existing.
        """
        import utils.data_loader as dl
        original = dl.DATA_DIR
        dl.DATA_DIR = str(tmp_path_factory.mktemp("data"))
        df = _gen_crowd_data()
        dl.DATA_DIR = original
        return df

    def test_row_count(self, crowd_df):
        """48 timestamps × 8 zones = 384 rows."""
        assert len(crowd_df) == 384

    def test_columns(self, crowd_df):
        expected = {
            "timestamp", "zone_id", "zone_name",
            "capacity", "current_occupancy", "density_pct", "alert_level",
        }
        assert set(crowd_df.columns) == expected

    def test_density_in_range(self, crowd_df):
        """All density values must be in [0, 100]."""
        assert crowd_df["density_pct"].between(0, 100).all()

    def test_alert_level_values(self, crowd_df):
        valid = {"LOW", "MODERATE", "HIGH", "CRITICAL"}
        assert set(crowd_df["alert_level"].unique()).issubset(valid)

    def test_eight_unique_zones(self, crowd_df):
        assert crowd_df["zone_id"].nunique() == 8


# ── _gen_zones ─────────────────────────────────────────────────────────────────

class TestGenZones:
    @pytest.fixture(scope="class")
    def zones_df(self, tmp_path_factory):
        import utils.data_loader as dl
        original = dl.DATA_DIR
        dl.DATA_DIR = str(tmp_path_factory.mktemp("data"))
        df = _gen_zones()
        dl.DATA_DIR = original
        return df

    def test_row_count(self, zones_df):
        """15 zones defined."""
        assert len(zones_df) == 15

    def test_required_columns(self, zones_df):
        required = {"zone_id", "name", "type", "capacity", "x_coord", "y_coord", "facilities"}
        assert required.issubset(set(zones_df.columns))

    def test_unique_zone_ids(self, zones_df):
        assert zones_df["zone_id"].is_unique

    def test_coordinates_in_range(self, zones_df):
        """Spatial coordinates must be in the 0–100 grid."""
        assert zones_df["x_coord"].between(0, 100).all()
        assert zones_df["y_coord"].between(0, 100).all()


# ── _gen_incidents ─────────────────────────────────────────────────────────────

class TestGenIncidents:
    @pytest.fixture(scope="class")
    def incidents_df(self, tmp_path_factory):
        import utils.data_loader as dl
        original = dl.DATA_DIR
        dl.DATA_DIR = str(tmp_path_factory.mktemp("data"))
        df = _gen_incidents()
        dl.DATA_DIR = original
        return df

    def test_row_count(self, incidents_df):
        """50 historical incidents."""
        assert len(incidents_df) == 50

    def test_required_columns(self, incidents_df):
        required = {
            "incident_id", "timestamp", "zone_id", "zone_name",
            "type", "severity", "description", "resolved",
        }
        assert required.issubset(set(incidents_df.columns))

    def test_severity_values(self, incidents_df):
        valid = {"Low", "Medium", "High", "Critical"}
        assert set(incidents_df["severity"].unique()).issubset(valid)

    def test_unique_incident_ids(self, incidents_df):
        assert incidents_df["incident_id"].is_unique


# ── _gen_volunteers ────────────────────────────────────────────────────────────

class TestGenVolunteers:
    @pytest.fixture(scope="class")
    def volunteers_df(self, tmp_path_factory):
        import utils.data_loader as dl
        original = dl.DATA_DIR
        dl.DATA_DIR = str(tmp_path_factory.mktemp("data"))
        df = _gen_volunteers()
        dl.DATA_DIR = original
        return df

    def test_row_count(self, volunteers_df):
        """30 volunteers."""
        assert len(volunteers_df) == 30

    def test_required_columns(self, volunteers_df):
        required = {
            "volunteer_id", "name", "role",
            "zone", "shift_start", "shift_end", "status",
        }
        assert required.issubset(set(volunteers_df.columns))

    def test_status_values(self, volunteers_df):
        valid = {"On Duty", "On Break", "Off Shift", "Standby"}
        assert set(volunteers_df["status"].unique()).issubset(valid)

    def test_unique_volunteer_ids(self, volunteers_df):
        assert volunteers_df["volunteer_id"].is_unique


# ── _gen_navigation_nodes ──────────────────────────────────────────────────────

class TestGenNavigationNodes:
    @pytest.fixture(scope="class")
    def nav_df(self, tmp_path_factory):
        import utils.data_loader as dl
        original = dl.DATA_DIR
        dl.DATA_DIR = str(tmp_path_factory.mktemp("data"))
        df = _gen_navigation_nodes()
        dl.DATA_DIR = original
        return df

    def test_row_count(self, nav_df):
        """29 navigation nodes."""
        assert len(nav_df) == 29

    def test_required_columns(self, nav_df):
        assert set(nav_df.columns) == {"node_id", "name", "type", "x", "y", "neighbors"}

    def test_unique_node_ids(self, nav_df):
        assert nav_df["node_id"].is_unique

    def test_coordinates_in_range(self, nav_df):
        assert nav_df["x"].between(0, 100).all()
        assert nav_df["y"].between(0, 100).all()


# ── _gen_events ────────────────────────────────────────────────────────────────

class TestGenEvents:
    @pytest.fixture(scope="class")
    def events_df(self, tmp_path_factory):
        import utils.data_loader as dl
        original = dl.DATA_DIR
        dl.DATA_DIR = str(tmp_path_factory.mktemp("data"))
        df = _gen_events()
        dl.DATA_DIR = original
        return df

    def test_row_count(self, events_df):
        """15 events."""
        assert len(events_df) == 15

    def test_required_columns(self, events_df):
        required = {
            "event_id", "match_name", "teams",
            "date", "time", "zones", "expected_attendance", "status",
        }
        assert required.issubset(set(events_df.columns))

    def test_status_values(self, events_df):
        valid = {"Live", "Upcoming", "Completed"}
        assert set(events_df["status"].unique()).issubset(valid)

    def test_unique_event_ids(self, events_df):
        assert events_df["event_id"].is_unique


# ── _path helper ───────────────────────────────────────────────────────────────

class TestPathHelper:
    def test_path_returns_string(self):
        result = _path("crowd_data.csv")
        assert isinstance(result, str)

    def test_path_ends_with_filename(self):
        result = _path("crowd_data.csv")
        assert result.endswith("crowd_data.csv")

    def test_path_contains_data_segment(self):
        """The returned path must include a 'data' directory component."""
        result = _path("zones.csv")
        # normalise separators before checking
        normalised = result.replace("\\", "/")
        assert "/data/" in normalised or normalised.endswith("/data")
