# Lab 3 – Approximating Positions of Mobile Base Stations

Mobile Security laboratory (SoSe26): swarm mapping from smartphone RSSI measurements.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
python main.py
```

This prints:
- Estimated base station positions (section 2.2)
- Verification output (section 2.3)
- Noise analysis (section 2.4)
- Written answers for sections 2.5–2.7

Outputs:
- `output/bs_estimation.png` – static image
- `output/bs_estimation_interactive.html` – **zoomable** interactive graph (scroll to zoom)
- `output/results.json` – numeric results

## Project Structure

```
Lab3/
├── main.py                 # Entry point
├── PSEUDOCODE.md           # Section 2.1
├── FLOWCHART.md            # Algorithm flowchart diagrams
├── EXPLANATION.md          # Simple English guide to the project
├── data/measurements.py    # Assignment measurement tables
├── src/
│   ├── rssi.py             # RSSI → distance conversion
│   ├── positioning.py      # Circle intersection algorithm (sympy)
│   ├── noise.py            # Chipset noise models (section 2.4)
│   └── visualization.py    # Matplotlib plots
└── output/
```

## Algorithm Summary

1. Convert each RSSI sample to a distance circle using the linear model and chipset-specific `max_rssi`.
2. Group circles by Cell ID (CI).
3. Find pairwise circle intersections with `sympy.geometry`.
4. Select the intersection point with the lowest residual error.
5. Apply exclusion constraints from RSSI=0 measurements.
6. Plot results with `matplotlib.pyplot` (see `src/visualization.py`).
