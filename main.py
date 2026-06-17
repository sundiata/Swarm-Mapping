#!/usr/bin/env python3
"""Lab 3 – Approximating positions of mobile base stations."""

from __future__ import annotations

import json
from pathlib import Path

from data.measurements import MEASUREMENTS, TRANSMISSION_RADIUS_M
from src.noise import CHIPSET_NOISE, compare_with_noise, noisy_measurements, robust_estimate
from src.positioning import estimate_all_base_stations
from src.rssi import rssi_to_distance
from src.visualization import open_plot, plot_estimation, plot_interactive_html


def print_section(title: str) -> None:
    print(f"\n{'=' * 60}")
    print(title)
    print("=" * 60)


def verify_implementation(estimates) -> None:
    """Section 2.3 – verification against assignment tables."""
    print_section("2.3 Verification")
    print(f"Transmission radius r = {TRANSMISSION_RADIUS_M} m\n")

    print("RSSI → distance samples:")
    samples = [
        (10.0, 61), (53.0, 61), (176.0, 251), (201.0, 251), (9.0, 251),
    ]
    for rssi, max_rssi in samples:
        d = rssi_to_distance(rssi, max_rssi, TRANSMISSION_RADIUS_M)
        print(f"  RSSI={rssi:5.1f}, max={max_rssi:3d}  →  d = {d:.1f} m")

    print("\nEstimated base stations (CI → x, y):")
    for est in estimates:
        print(
            f"  CI {est.ci}: ({est.x:8.2f}, {est.y:8.2f})  "
            f"[residual={est.residual_error:.2f} m, circles={est.num_circles}]"
        )


def analyze_noise(estimates) -> None:
    """Section 2.4 – chipset noise impact."""
    print_section("2.4 RSSI Noise Consideration")

    print("Chipset noise profiles:")
    for p in CHIPSET_NOISE:
        print(f"  SP{p.smartphone_id} (max RSSI {p.max_rssi}): {p.notes}")

    noisy_meas = noisy_measurements(MEASUREMENTS, seed=42)
    noisy_est = estimate_all_base_stations(noisy_meas)
    robust = robust_estimate(MEASUREMENTS, noise_margin=0.08)

    print("\nPosition shift under simulated RSSI noise:")
    for row in compare_with_noise(estimates, noisy_est):
        print(
            f"  CI {row['ci']}: shift = {row['shift_m']:.2f} m  "
            f"({row['baseline_x']:.1f},{row['baseline_y']:.1f}) → "
            f"({row['noisy_x']:.1f},{row['noisy_y']:.1f})"
        )

    print("\nRobust estimate (8% radius inflation):")
    for est in robust:
        base = next(e for e in estimates if e.ci == est.ci)
        shift = ((est.x - base.x) ** 2 + (est.y - base.y) ** 2) ** 0.5
        print(
            f"  CI {est.ci}: ({est.x:.2f}, {est.y:.2f})  "
            f"shift from baseline = {shift:.2f} m"
        )


def analyze_time() -> None:
    """Section 2.5 – influence of unsynchronized measurement times."""
    print_section("2.5 Time of Measurement")
    print(
        """
If smartphone clocks are not synchronized, a recorded (x, y) position may not
match the RSSI sample taken at the given timestamp. A moving user introduces
geometric error: the circle is centered on the wrong point, shifting estimated
BS positions along the movement direction. Mitigations:
  • Reject or down-weight samples with large time skew between SPs
  • Estimate velocity and back-project positions to a common reference time
  • Prefer stationary measurements or cluster by time windows
  • Use robust fitting (e.g. median intersections) to reduce outlier impact
"""
    )


def approach_without_radius() -> None:
    """Section 2.6 – approximation without known transmission radius."""
    print_section("2.6 Approximation Without Transmission Radius")
    print(
        """
Without a fixed radius r:
  1. Treat RSSI only as a relative proximity indicator (ranking, not meters).
  2. Estimate r per CI from the maximum observed RSSI per chipset (strongest
     sample ≈ d = 0) and weakest in-range sample (≈ r).
  3. Use multi-lateration with unknown distance scale; solve via least squares
     over all CIs simultaneously.
  4. Cross-validate: pick r that minimizes intersection residual across all BS.
  5. Exploit exclusion constraints (RSSI=0) as upper bounds on distance to
     every known BS without needing an exact r.
"""
    )


def fake_bs_detection() -> None:
    """Section 2.7 – optional fake base station detection."""
    print_section("2.7 Optional: Fake Base Station Detection")
    print(
        """
Post-mortem detection ideas for the server:
  • Persistent geometry inconsistency: a CI whose circles never intersect in a
    stable region across many smartphones/times is suspicious.
  • Sudden CI appearance with high RSSI in areas where other CIs already explain
    coverage.
  • Duplicate/overlapping CIs with identical LAC but abnormal timing advance.
  • Compare estimated BS positions over time; fake BS “jump” between sessions.
  • Flag CIs seen only by a subset of devices (selective jamming/spoofing).
  • Correlate with known operator cell databases; unknown CI + strong signal =
    investigation candidate.
"""
    )


def main() -> None:
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    estimates = estimate_all_base_stations()

    print_section("2.2 Implementation Result")
    result = [
        {"ci": e.ci, "x": round(e.x, 2), "y": round(e.y, 2)}
        for e in estimates
    ]
    print(json.dumps(result, indent=2))

    verify_implementation(estimates)
    analyze_noise(estimates)
    analyze_time()
    approach_without_radius()
    fake_bs_detection()

    plot_path = plot_estimation(estimates, output_dir / "bs_estimation.png", show=True)
    html_path = plot_interactive_html(estimates, output_dir / "bs_estimation_interactive.html")
    print_section("Plots saved")
    print(f"Static image:  {plot_path.resolve()}")
    print(f"Interactive (zoomable): {html_path.resolve()}")

    results_path = output_dir / "results.json"
    results_path.write_text(
        json.dumps(
            {
                "base_stations": result,
                "details": [
                    {
                        "ci": e.ci,
                        "x": e.x,
                        "y": e.y,
                        "residual_error_m": e.residual_error,
                        "num_circles": e.num_circles,
                    }
                    for e in estimates
                ],
            },
            indent=2,
        )
    )
    print(f"Results written to {results_path.resolve()}")


if __name__ == "__main__":
    main()
