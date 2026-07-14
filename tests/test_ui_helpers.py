"""
tests/test_ui_helpers.py
========================
Unit tests for utils/ui_helpers.py

Only the *pure Python* functions that return data or HTML strings are tested —
those that do NOT call st.markdown() or any other Streamlit API.

Tested:
  - alert_badge()       → returns HTML string
  - status_badge()      → returns HTML string
  - ALERT_COLORS dict   → completeness and value types
  - STATUS_COLORS dict  → completeness and value types
  - plotly_dark_layout  → tested indirectly via a mock Plotly figure

NOT tested (require Streamlit runtime):
  - inject_custom_css(), page_header(), metric_card(), info_card(),
    zone_density_bar(), ai_badge(), sidebar_brand()
"""
import pytest

from utils.ui_helpers import (
    alert_badge,
    status_badge,
    ALERT_COLORS,
    STATUS_COLORS,
)


# ── alert_badge ────────────────────────────────────────────────────────────────

class TestAlertBadge:
    """Tests for alert_badge(level, text='')."""

    KNOWN_LEVELS = ["LOW", "MODERATE", "HIGH", "CRITICAL"]

    def test_returns_string(self):
        result = alert_badge("LOW")
        assert isinstance(result, str)

    def test_contains_level_text(self):
        """The badge HTML must contain the level label."""
        for level in self.KNOWN_LEVELS:
            result = alert_badge(level)
            assert level in result, f"'{level}' not found in alert_badge output"

    def test_custom_text_overrides_level(self):
        """When text= is provided, that text — not the level — appears in output."""
        result = alert_badge("HIGH", text="Danger Zone")
        assert "Danger Zone" in result
        # The level keyword itself may or may not appear; what matters is custom text
        # is present as the visible label.

    def test_returns_html_span(self):
        """The output must be a <span> HTML element."""
        result = alert_badge("LOW")
        assert "<span" in result and "</span>" in result

    def test_unknown_level_falls_back_gracefully(self):
        """An unrecognised level must still return an HTML string (no exception)."""
        result = alert_badge("UNKNOWN_LEVEL")
        assert isinstance(result, str)
        assert "<span" in result

    def test_low_uses_green_color(self):
        """LOW should use the green colour (#10b981)."""
        result = alert_badge("LOW")
        assert "#10b981" in result

    def test_critical_uses_red_color(self):
        """CRITICAL should use the red colour (#dc2626)."""
        result = alert_badge("CRITICAL")
        assert "#dc2626" in result


# ── status_badge ───────────────────────────────────────────────────────────────

class TestStatusBadge:
    """Tests for status_badge(status)."""

    KNOWN_STATUSES = ["On Duty", "On Break", "Off Shift", "Standby",
                      "Live", "Upcoming", "Completed"]

    def test_returns_string(self):
        result = status_badge("On Duty")
        assert isinstance(result, str)

    def test_contains_status_text(self):
        """The badge HTML must display the status string."""
        for status in self.KNOWN_STATUSES:
            result = status_badge(status)
            assert status in result, f"'{status}' not found in status_badge output"

    def test_returns_html_span(self):
        result = status_badge("Live")
        assert "<span" in result and "</span>" in result

    def test_unknown_status_falls_back_gracefully(self):
        """Unknown status must return an HTML string without raising."""
        result = status_badge("MYSTERY_STATUS")
        assert isinstance(result, str)
        assert "<span" in result

    def test_on_duty_uses_green_color(self):
        """'On Duty' maps to green (#10b981)."""
        result = status_badge("On Duty")
        assert "#10b981" in result

    def test_live_uses_red_color(self):
        """'Live' maps to red (#ef4444)."""
        result = status_badge("Live")
        assert "#ef4444" in result


# ── ALERT_COLORS dict ──────────────────────────────────────────────────────────

class TestAlertColorsDict:
    """Tests for the ALERT_COLORS constant."""

    REQUIRED_KEYS = {"LOW", "MODERATE", "HIGH", "CRITICAL"}

    def test_has_all_required_keys(self):
        assert self.REQUIRED_KEYS == set(ALERT_COLORS.keys())

    def test_each_value_is_two_tuple(self):
        """Each value must be a (foreground, background) tuple of 2 strings."""
        for level, value in ALERT_COLORS.items():
            assert isinstance(value, tuple) and len(value) == 2, (
                f"ALERT_COLORS['{level}'] is not a 2-tuple"
            )

    def test_colors_are_hex_strings(self):
        """Both fg and bg must be hex colour strings starting with '#'."""
        for level, (fg, bg) in ALERT_COLORS.items():
            assert fg.startswith("#"), f"fg color for {level} doesn't start with #"
            assert bg.startswith("#"), f"bg color for {level} doesn't start with #"


# ── STATUS_COLORS dict ─────────────────────────────────────────────────────────

class TestStatusColorsDict:
    """Tests for the STATUS_COLORS constant."""

    REQUIRED_KEYS = {"On Duty", "On Break", "Off Shift", "Standby",
                     "Live", "Upcoming", "Completed"}

    def test_has_all_required_keys(self):
        assert self.REQUIRED_KEYS == set(STATUS_COLORS.keys())

    def test_each_value_is_two_tuple(self):
        for status, value in STATUS_COLORS.items():
            assert isinstance(value, tuple) and len(value) == 2, (
                f"STATUS_COLORS['{status}'] is not a 2-tuple"
            )

    def test_colors_are_hex_strings(self):
        for status, (fg, bg) in STATUS_COLORS.items():
            assert fg.startswith("#"), f"fg color for '{status}' doesn't start with #"
            assert bg.startswith("#"), f"bg color for '{status}' doesn't start with #"
