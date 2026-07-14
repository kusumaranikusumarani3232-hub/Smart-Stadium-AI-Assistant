"""
Crowd simulator utility for the Admin Panel.
Generates realistic synthetic crowd fluctuations based on a base state.
NO Groq API calls here — pure algorithmic simulation.
"""
import numpy as np
import pandas as pd


# Zone metadata: (zone_id, zone_name, capacity, base_peak_fill)
ZONE_METADATA = [
    ("Z1",  "North Stand",          8000,  0.82),
    ("Z2",  "South Stand",          8000,  0.78),
    ("Z3",  "East Stand",           6000,  0.74),
    ("Z4",  "West Stand",           6000,  0.70),
    ("Z5",  "VIP Lounge",           500,   0.88),
    ("Z6",  "Press Box",            200,   0.92),
    ("Z7",  "Food Court A",         1000,  0.65),
    ("Z8",  "Food Court B",         1000,  0.60),
]


def simulate_crowd_snapshot(
    manual_overrides: dict | None = None,
    noise_level: float = 0.05,
    seed: int | None = None,
) -> pd.DataFrame:
    """
    Generate a single crowd snapshot for all zones.

    Args:
        manual_overrides: Dict mapping zone_id → density_pct (0-100).
                          Values supplied by the Admin Panel sliders.
        noise_level     : Gaussian noise σ applied on top of base fill.
        seed            : Optional random seed for reproducibility.

    Returns:
        DataFrame with columns:
        zone_id, zone_name, capacity, current_occupancy, density_pct, alert_level
    """
    rng = np.random.default_rng(seed)
    rows = []
    for zone_id, zone_name, capacity, base_fill in ZONE_METADATA:
        if manual_overrides and zone_id in manual_overrides:
            # Admin has manually set this zone's density
            density_pct = float(manual_overrides[zone_id])
        else:
            noise = rng.normal(0, noise_level)
            density_pct = round(min(100.0, max(1.0, (base_fill + noise) * 100)), 1)

        current = int(capacity * density_pct / 100)
        alert = _alert_level(density_pct)
        rows.append([zone_id, zone_name, capacity, current, density_pct, alert])

    return pd.DataFrame(
        rows,
        columns=["zone_id", "zone_name", "capacity", "current_occupancy", "density_pct", "alert_level"],
    )


def get_default_densities() -> dict:
    """Return the default peak densities keyed by zone_id."""
    return {zm[0]: round(zm[3] * 100) for zm in ZONE_METADATA}


def _alert_level(density_pct: float) -> str:
    """Map a density percentage to an alert level string."""
    if density_pct >= 90:
        return "CRITICAL"
    if density_pct >= 75:
        return "HIGH"
    if density_pct >= 50:
        return "MODERATE"
    return "LOW"
