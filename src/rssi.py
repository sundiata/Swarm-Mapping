"""RSSI to distance conversion (linear model from the assignment)."""


def rssi_to_distance(
    rssi: float,
    max_rssi: int,
    radius: float = 600.0,
) -> float | None:
    """
    Convert RSSI to estimated distance in meters.

    Formula from the assignment:
        d = |(rssi - max_rssi) * (radius / (max_rssi - 1))|

    RSSI = 0 means the smartphone is outside the transmission radius.
    """
    if rssi <= 0:
        return None
    return abs((rssi - max_rssi) * (radius / (max_rssi - 1)))


def apply_noise(distance: float, noise_std: float, rng) -> float:
    """Add Gaussian measurement noise to a derived distance."""
    return max(0.0, distance + rng.normal(0.0, noise_std))
