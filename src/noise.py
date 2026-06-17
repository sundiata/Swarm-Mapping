"""RSSI chipset noise models and robust re-estimation (section 2.4)."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from data.measurements import MEASUREMENTS, Measurement
from src.positioning import BaseStationEstimate, estimate_all_base_stations
from src.rssi import apply_noise, rssi_to_distance


@dataclass
class ChipsetNoiseProfile:
    smartphone_id: int
    max_rssi: int
    typical_noise_db: float
    distance_noise_std_m: float
    notes: str


# Chipset-specific RSSI noise (research summary for section 2.4).
# Different manufacturers use different scales and calibration offsets.
CHIPSET_NOISE: list[ChipsetNoiseProfile] = [
    ChipsetNoiseProfile(
        1, 61, 3.0, 45.0,
        "Low-range chipset (0–61): coarser quantization, ~±3 dB typical RSSI jitter.",
    ),
    ChipsetNoiseProfile(
        2, 251, 2.0, 30.0,
        "High-range chipset (0–251): finer steps but vendor-specific offset; ~±2 dB.",
    ),
    ChipsetNoiseProfile(
        3, 61, 3.0, 45.0,
        "Same range as SP1; multipath in urban GSM adds distance uncertainty.",
    ),
    ChipsetNoiseProfile(
        4, 251, 2.5, 35.0,
        "High-range chipset; shadowing can shift derived distance by tens of meters.",
    ),
]


def noisy_measurements(
    measurements: list[Measurement],
    rng: np.random.Generator | None = None,
    seed: int = 42,
) -> list[Measurement]:
    """Simulate chipset noise on RSSI-derived distances by perturbing RSSI values."""
    rng = rng or np.random.default_rng(seed)
    noise_by_sp = {p.smartphone_id: p.typical_noise_db for p in CHIPSET_NOISE}

    noisy: list[Measurement] = []
    for m in measurements:
        if m.ci is None or m.rssi <= 0:
            noisy.append(m)
            continue
        noise_db = noise_by_sp.get(m.smartphone_id, 2.0)
        # Perturb RSSI; clamp to valid range for the chipset.
        perturbed = m.rssi + rng.normal(0, noise_db)
        perturbed = max(1.0, min(float(m.max_rssi), perturbed))
        noisy.append(
            Measurement(
                smartphone_id=m.smartphone_id,
                max_rssi=m.max_rssi,
                ci=m.ci,
                rssi=perturbed,
                time=m.time,
                sp_x=m.sp_x,
                sp_y=m.sp_y,
            )
        )
    return noisy


def compare_with_noise(
    baseline: list[BaseStationEstimate],
    noisy: list[BaseStationEstimate],
) -> list[dict]:
    """Compare baseline vs noise-aware estimates."""
    baseline_map = {e.ci: e for e in baseline}
    rows = []
    for n in noisy:
        b = baseline_map.get(n.ci)
        if b is None:
            continue
        dx = n.x - b.x
        dy = n.y - b.y
        shift = (dx**2 + dy**2) ** 0.5
        rows.append(
            {
                "ci": n.ci,
                "baseline_x": b.x,
                "baseline_y": b.y,
                "noisy_x": n.x,
                "noisy_y": n.y,
                "shift_m": shift,
                "baseline_residual": b.residual_error,
                "noisy_residual": n.residual_error,
            }
        )
    return rows


def robust_estimate(
    measurements: list[Measurement] | None = None,
    noise_margin: float = 0.08,
) -> list[BaseStationEstimate]:
    """
    Noise-aware estimation: inflate circle radii slightly to absorb chipset jitter.

    An 8% radius inflation approximates typical urban RSSI uncertainty without
    over-smoothing intersections.
    """
    return estimate_all_base_stations(
        measurements=measurements,
        radius_scale=1.0 + noise_margin,
    )
