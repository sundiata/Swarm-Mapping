"""Measurement data from the lab assignment (section 2)."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Measurement:
    smartphone_id: int
    max_rssi: int
    ci: int | None  # None when CI is "-" (outside all known BS)
    rssi: float
    time: int
    sp_x: float
    sp_y: float


TRANSMISSION_RADIUS_M = 600

# Smartphone chipsets use different RSSI value ranges.
SMARTPHONE_MAX_RSSI = {
    1: 61,
    2: 251,
    3: 61,
    4: 251,
}

MEASUREMENTS: list[Measurement] = [
    # Smartphone 1 (RSSI range 0–61)
    Measurement(1, 61, 12801, 10.0, 100045, 1450.0, 1040.0),
    Measurement(1, 61, 12801, 53.0, 100230, 936.0, 752.0),
    Measurement(1, 61, 12801, 36.0, 110002, 850.0, 600.0),
    # Smartphone 2 (RSSI range 0–251)
    Measurement(2, 251, 12801, 176.0, 129885, 827.2, 850.4),
    Measurement(2, 251, 12801, 201.0, 134546, 904.0, 728.0),
    Measurement(2, 251, 12802, 108.0, 156778, 1468.0, 2716.8),
    Measurement(2, 251, 12804, 9.0, 164747, 219.2, 2000.0),
    Measurement(2, 251, None, 0.0, 169567, 339.2, 2614.4),
    # Smartphone 3 (RSSI range 0–61)
    Measurement(3, 61, 12801, 10.0, 4725, 784.0, 1262.0),
    Measurement(3, 61, 12802, 24.0, 7321, 1720.0, 2050.0),
    Measurement(3, 61, 12803, 8.0, 7321, 1720.0, 2050.0),
    # Smartphone 4 (RSSI range 0–251)
    Measurement(4, 251, 12802, 87.0, 94521, 1984.0, 2313.6),
    Measurement(4, 251, 12803, 17.0, 136744, 2216.0, 2118.4),
    Measurement(4, 251, 12804, 70.0, 156554, 800.0, 2434.4),
    Measurement(4, 251, None, 0.0, 174677, 161.6, 2748.8),
]
