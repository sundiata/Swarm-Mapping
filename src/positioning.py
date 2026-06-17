"""Swarm mapping algorithm: approximate base station positions from RSSI circles."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from sympy.geometry import Circle, Point, intersection

from data.measurements import MEASUREMENTS, TRANSMISSION_RADIUS_M, Measurement
from src.rssi import rssi_to_distance


@dataclass
class BSCircle:
    ci: int
    center_x: float
    center_y: float
    radius: float
    measurement: Measurement


@dataclass
class BaseStationEstimate:
    ci: int
    x: float
    y: float
    residual_error: float
    num_circles: int


def _to_point(value) -> tuple[float, float] | None:
    """Convert a sympy geometry result to (x, y)."""
    if isinstance(value, Point):
        return float(value.x), float(value.y)
    return None


def build_circles(
    measurements: list[Measurement],
    radius_scale: float = 1.0,
) -> list[BSCircle]:
    """Create distance circles for all valid RSSI measurements."""
    circles: list[BSCircle] = []
    for m in measurements:
        if m.ci is None or m.rssi <= 0:
            continue
        distance = rssi_to_distance(m.rssi, m.max_rssi, TRANSMISSION_RADIUS_M)
        if distance is None:
            continue
        circles.append(
            BSCircle(
                ci=m.ci,
                center_x=m.sp_x,
                center_y=m.sp_y,
                radius=distance * radius_scale,
                measurement=m,
            )
        )
    return circles


def pairwise_intersections(circles: list[BSCircle]) -> list[tuple[float, float]]:
    """Compute intersection points for all circle pairs of the same CI."""
    points: list[tuple[float, float]] = []
    for i in range(len(circles)):
        for j in range(i + 1, len(circles)):
            c1 = Circle(
                Point(circles[i].center_x, circles[i].center_y),
                circles[i].radius,
            )
            c2 = Circle(
                Point(circles[j].center_x, circles[j].center_y),
                circles[j].radius,
            )
            result = intersection(c1, c2)
            for item in result:
                pt = _to_point(item)
                if pt is not None:
                    points.append(pt)
    return points


def residual_error(point: tuple[float, float], circles: list[BSCircle]) -> float:
    """Mean absolute deviation from each circle boundary."""
    errors = []
    for c in circles:
        dist = Point(point[0], point[1]).distance(
            Point(c.center_x, c.center_y)
        )
        errors.append(abs(float(dist) - c.radius))
    return float(np.mean(errors))


def estimate_position_from_circles(circles: list[BSCircle]) -> tuple[float, float, float]:
    """
    Estimate BS position from circles of one CI.

    Strategy:
    1. Collect pairwise circle intersections.
    2. If intersections exist, pick the point with lowest residual error.
    3. Otherwise fall back to weighted least-squares on circle centers.
    """
    if not circles:
        raise ValueError("No circles provided")

    candidates = pairwise_intersections(circles)

    if not candidates:
        # Single circle or non-intersecting circles: use inverse-distance weighting.
        weights = [1.0 / max(c.radius, 1.0) for c in circles]
        x = sum(c.center_x * w for c, w in zip(circles, weights)) / sum(weights)
        y = sum(c.center_y * w for c, w in zip(circles, weights)) / sum(weights)
        err = residual_error((x, y), circles)
        return x, y, err

    best = min(candidates, key=lambda p: residual_error(p, circles))
    return best[0], best[1], residual_error(best, circles)


def apply_exclusion_constraints(
    estimates: dict[int, BaseStationEstimate],
    measurements: list[Measurement],
) -> dict[int, BaseStationEstimate]:
    """
    Use RSSI=0 / outside-all-BS measurements to filter implausible positions.

    A measurement with RSSI=0 means the smartphone was outside every known BS
    radius at measurement time. Any estimated BS closer than TRANSMISSION_RADIUS_M
    to such a point would contradict the data.
    """
    outside_points = [
        (m.sp_x, m.sp_y)
        for m in measurements
        if m.rssi == 0 or m.ci is None
    ]
    if not outside_points:
        return estimates

    filtered: dict[int, BaseStationEstimate] = {}
    for ci, est in estimates.items():
        valid = True
        for px, py in outside_points:
            dist = Point(est.x, est.y).distance(Point(px, py))
            if float(dist) < TRANSMISSION_RADIUS_M * 0.95:
                valid = False
                break
        if valid:
            filtered[ci] = est
    return filtered


def estimate_all_base_stations(
    measurements: list[Measurement] | None = None,
    radius_scale: float = 1.0,
) -> list[BaseStationEstimate]:
    """Run the full swarm mapping algorithm."""
    measurements = measurements or MEASUREMENTS
    circles = build_circles(measurements, radius_scale=radius_scale)

    by_ci: dict[int, list[BSCircle]] = {}
    for c in circles:
        by_ci.setdefault(c.ci, []).append(c)

    estimates: dict[int, BaseStationEstimate] = {}
    for ci, ci_circles in sorted(by_ci.items()):
        x, y, err = estimate_position_from_circles(ci_circles)
        estimates[ci] = BaseStationEstimate(
            ci=ci,
            x=x,
            y=y,
            residual_error=err,
            num_circles=len(ci_circles),
        )

    estimates = apply_exclusion_constraints(estimates, measurements)
    return sorted(estimates.values(), key=lambda e: e.ci)
