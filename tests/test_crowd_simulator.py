"""
tests/test_crowd_simulator.py
==============================
Unit tests for utils/crowd_simulator.py

All functions in this module are pure Python (no Streamlit, no Groq) so every
one of them can be tested directly.
"""
import pytest
import pandas as pd

from utils.crowd_simulator import (
    simulate_crowd_snapshot,
    get_default_densities,
    _alert_level,
    ZONE_METADATA,
)


# ── _alert_level ───────────────────────────────────────────────────────────────

class TestAlertLevel:
    """Tests for the internal crowd_simulator._alert_level() helper."""

    def test_low_below_50(self):
        assert _alert_level(0.0) == "LOW"
        assert _alert_level(49.9) == "LOW"

    def test_moderate_at_boundary(self):
        """Exactly 50 → MODERATE."""
        assert _alert_level(50.0) == "MODERATE"

    def test_moderate_range(self):
        assert _alert_level(60.0) == "MODERATE"
        assert _alert_level(74.9) == "MODERATE"

    def test_high_at_boundary(self):
        """Exactly 75 → HIGH."""
        assert _alert_level(75.0) == "HIGH"

    def test_high_range(self):
        assert _alert_level(80.0) == "HIGH"
        assert _alert_level(89.9) == "HIGH"

    def test_critical_at_boundary(self):
        """Exactly 90 → CRITICAL."""
        assert _alert_level(90.0) == "CRITICAL"

    def test_critical_above_90(self):
        assert _alert_level(100.0) == "CRITICAL"

    def test_all_values_are_valid_levels(self):
        valid = {"LOW", "MODERATE", "HIGH", "CRITICAL"}
        for density in range(0, 101, 5):
            assert _alert_level(float(density)) in valid


# ── simulate_crowd_snapshot ────────────────────────────────────────────────────

class TestSimulateCrowdSnapshot:
    """Tests for the main simulation function."""

    EXPECTED_COLUMNS = {
        "zone_id", "zone_name", "capacity",
        "current_occupancy", "density_pct", "alert_level",
    }

    def test_returns_dataframe(self):
        result = simulate_crowd_snapshot(seed=42)
        assert isinstance(result, pd.DataFrame)

    def test_correct_number_of_rows(self):
        """One row per zone — 8 rows total."""
        result = simulate_crowd_snapshot(seed=42)
        assert len(result) == len(ZONE_METADATA)

    def test_correct_columns(self):
        result = simulate_crowd_snapshot(seed=42)
        assert set(result.columns) == self.EXPECTED_COLUMNS

    def test_density_in_valid_range(self):
        """All density values must be in [0, 100]."""
        result = simulate_crowd_snapshot(seed=42)
        assert result["density_pct"].between(0.0, 100.0).all(), (
            "density_pct contains values outside [0, 100]"
        )

    def test_current_occupancy_is_non_negative(self):
        result = simulate_crowd_snapshot(seed=42)
        assert (result["current_occupancy"] >= 0).all()

    def test_current_occupancy_does_not_exceed_capacity(self):
        """Occupancy should not exceed zone capacity."""
        result = simulate_crowd_snapshot(seed=42)
        assert (result["current_occupancy"] <= result["capacity"]).all()

    def test_alert_levels_are_valid(self):
        valid = {"LOW", "MODERATE", "HIGH", "CRITICAL"}
        result = simulate_crowd_snapshot(seed=42)
        assert set(result["alert_level"].unique()).issubset(valid)

    def test_zone_ids_match_metadata(self):
        """All zone_ids must come from ZONE_METADATA."""
        expected_ids = {zm[0] for zm in ZONE_METADATA}
        result = simulate_crowd_snapshot(seed=42)
        assert set(result["zone_id"]) == expected_ids

    def test_manual_override_applied(self):
        """A manual override must set that zone's density to the given value."""
        overrides = {"Z1": 95.0, "Z3": 20.0}
        result = simulate_crowd_snapshot(manual_overrides=overrides, seed=42)

        z1_row = result[result["zone_id"] == "Z1"].iloc[0]
        assert z1_row["density_pct"] == pytest.approx(95.0)
        assert z1_row["alert_level"] == "CRITICAL"

        z3_row = result[result["zone_id"] == "Z3"].iloc[0]
        assert z3_row["density_pct"] == pytest.approx(20.0)
        assert z3_row["alert_level"] == "LOW"

    def test_override_only_affects_specified_zones(self):
        """Non-overridden zones should still appear and have valid data."""
        result = simulate_crowd_snapshot(manual_overrides={"Z1": 50.0}, seed=42)
        non_overridden = result[result["zone_id"] != "Z1"]
        assert not non_overridden.empty
        assert non_overridden["density_pct"].between(0.0, 100.0).all()

    def test_reproducibility_with_seed(self):
        """Same seed must produce the same output."""
        result_a = simulate_crowd_snapshot(seed=99)
        result_b = simulate_crowd_snapshot(seed=99)
        pd.testing.assert_frame_equal(result_a, result_b)

    def test_different_seeds_produce_different_results(self):
        """Different seeds should (with high probability) produce different outputs."""
        result_a = simulate_crowd_snapshot(seed=1)
        result_b = simulate_crowd_snapshot(seed=999)
        # They may occasionally match — check the density column varies at least sometimes
        assert not result_a["density_pct"].equals(result_b["density_pct"])


# ── get_default_densities ──────────────────────────────────────────────────────

class TestGetDefaultDensities:
    """Tests for get_default_densities()."""

    def test_returns_dict(self):
        result = get_default_densities()
        assert isinstance(result, dict)

    def test_has_all_zone_ids(self):
        expected_ids = {zm[0] for zm in ZONE_METADATA}
        result = get_default_densities()
        assert set(result.keys()) == expected_ids

    def test_values_are_numeric(self):
        result = get_default_densities()
        for zone_id, value in result.items():
            assert isinstance(value, (int, float)), (
                f"Value for {zone_id} is not numeric: {type(value)}"
            )

    def test_values_in_valid_range(self):
        """Default densities must be between 0 and 100 (percent)."""
        result = get_default_densities()
        for zone_id, value in result.items():
            assert 0 <= value <= 100, (
                f"{zone_id} default density {value} is out of [0, 100]"
            )


# ── ZONE_METADATA ──────────────────────────────────────────────────────────────

class TestZoneMetadata:
    """Sanity checks on the ZONE_METADATA constant."""

    def test_has_eight_zones(self):
        assert len(ZONE_METADATA) == 8

    def test_each_entry_has_four_fields(self):
        for entry in ZONE_METADATA:
            assert len(entry) == 4, f"Entry {entry} does not have 4 fields"

    def test_capacities_are_positive(self):
        for zone_id, zone_name, capacity, base_fill in ZONE_METADATA:
            assert capacity > 0, f"{zone_id} has non-positive capacity {capacity}"

    def test_base_fill_between_0_and_1(self):
        for zone_id, zone_name, capacity, base_fill in ZONE_METADATA:
            assert 0.0 <= base_fill <= 1.0, (
                f"{zone_id} base_fill {base_fill} is outside [0, 1]"
            )
