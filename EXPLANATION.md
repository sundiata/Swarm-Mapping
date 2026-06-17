# Project Explanation (Simple English)

This document explains what the Lab 3 project does and what each part of the code is for.

---

## What is this project about?

Imagine you have **4 smartphones** walking around a city. Each phone can:

- Know its own **GPS position** (x, y coordinates)
- Measure **signal strength (RSSI)** from nearby cell towers (base stations)
- Report which **cell tower** it hears (called **CI** = Cell ID)

The problem: **we do not know where the base stations are**.  
The goal: use all the phone reports together to **guess the base station locations**.

This is called **swarm mapping** — many phones work together like a swarm to map the towers.

---

## The main idea (in one sentence)

> If a phone is at position (x, y) and the signal strength tells us the tower is about 200 meters away, then the tower must be somewhere on a **circle** with radius 200 m around that phone.

When **many phones** report signals from the **same tower**, their circles should **overlap in one spot** — that spot is our best guess for the tower location.

---

## Important words

| Word | Simple meaning |
|------|----------------|
| **Base Station (BS)** | A cell tower that sends mobile signal |
| **CI (Cell ID)** | A number that identifies a specific tower |
| **RSSI** | Signal strength. Higher = stronger signal = phone is closer |
| **Smartphone (SP)** | A phone that sends measurements to the server |
| **Transmission radius (r)** | Max range of a tower = 600 meters in this lab |
| **max_rssi** | The strongest possible RSSI value for that phone's chip (61 or 251) |

---

## How the algorithm works (step by step)

1. **Collect data** from all smartphones (CI, RSSI, position, time).
2. **Convert RSSI to distance** using a simple formula.
3. **Draw a circle** around each phone position with that distance as the radius.
4. **Group circles** by Cell ID (all circles for tower 12801 together, etc.).
5. **Find where circles overlap** — those points are possible tower locations.
6. **Pick the best point** — the one that fits all circles most accurately.
7. **Check exclusion rules** — if a phone had RSSI = 0, it was outside all towers, so no tower should be too close to that phone.
8. **Output** the estimated (x, y) position for each tower.

---

## Results from the assignment data

| Tower (CI) | Estimated position |
|------------|-------------------|
| 12801 | (1000, 800) |
| 12802 | (1600, 2400) |
| 12803 | (2000, 1600) |
| 12804 | (800, 2000) |

---

## Project file structure

```
Lab3/
├── main.py                  ← Start here: runs everything
├── data/measurements.py     ← All the input data from the assignment
├── src/
│   ├── rssi.py              ← Converts signal strength to distance
│   ├── positioning.py       ← Main algorithm (finds tower positions)
│   ├── noise.py             ← Handles signal noise from different phone chips
│   └── visualization.py     ← Draws the map/chart
├── output/                  ← Results and plot saved here
├── PSEUDOCODE.md            ← Written algorithm (for section 2.1)
├── FLOWCHART.md             ← Visual flowchart of the algorithm
└── EXPLANATION.md           ← This file
```

---

## Each file explained

### `main.py` — The boss file

This is the **entry point**. When you run `python main.py`, it:

1. Runs the positioning algorithm
2. Prints the estimated tower positions
3. Verifies the results (section 2.3)
4. Analyzes signal noise (section 2.4)
5. Prints written answers for sections 2.5, 2.6, and 2.7
6. Creates a plot image (`output/bs_estimation.png`)
7. Saves results to `output/results.json`

**Key functions:**
- `main()` — runs the full program
- `verify_implementation()` — checks RSSI conversion and prints tower positions
- `analyze_noise()` — shows how noise affects the results
- `analyze_time()` — explains why measurement time matters
- `approach_without_radius()` — what to do if radius is unknown
- `fake_bs_detection()` — ideas for detecting fake towers

---

### `data/measurements.py` — The input data

This file stores **all measurement data** from the assignment PDF tables.

**`Measurement` class** — one row of data:
- `smartphone_id` — which phone (1, 2, 3, or 4)
- `max_rssi` — max signal value for that phone's chip (61 or 251)
- `ci` — cell tower ID (or `None` if no tower in range)
- `rssi` — signal strength reading
- `time` — when the measurement was taken
- `sp_x`, `sp_y` — phone's position

**`MEASUREMENTS`** — the full list of all 15 measurements from the assignment.

**`TRANSMISSION_RADIUS_M = 600`** — towers are assumed to reach 600 meters.

**`SMARTPHONE_MAX_RSSI`** — tells us which max_rssi each phone uses.

---

### `src/rssi.py` — Signal to distance converter

This is a small but important file. It answers: *"How far is the phone from the tower?"*

**`rssi_to_distance(rssi, max_rssi, radius)`**
- Takes a signal strength value
- Returns distance in meters
- Uses the formula from the assignment:
  ```
  distance = |(rssi - max_rssi) × (600 / (max_rssi - 1))|
  ```
- If RSSI is 0 or negative → returns `None` (phone is outside tower range)

**Example:**
- RSSI = 53, max_rssi = 61 → distance = 80 meters (phone is close)
- RSSI = 10, max_rssi = 61 → distance = 510 meters (phone is far)

**`apply_noise()`** — adds random noise to a distance (used in noise testing).

---

### `src/positioning.py` — The main algorithm

This is the **heart of the project**. It finds tower positions.

**Data classes:**
- `BSCircle` — a circle representing "tower could be here" (center = phone position, radius = distance)
- `BaseStationEstimate` — final result for one tower (CI, x, y, error, number of circles used)

**Functions:**

| Function | What it does |
|----------|-------------|
| `build_circles()` | Loops through all measurements and creates distance circles |
| `pairwise_intersections()` | Finds where two circles cross each other (using sympy) |
| `residual_error()` | Measures how well a point fits all circles (lower = better) |
| `estimate_position_from_circles()` | For one tower: finds the best position from its circles |
| `apply_exclusion_constraints()` | Removes bad estimates that conflict with RSSI=0 readings |
| `estimate_all_base_stations()` | Runs the full algorithm for all towers |

**How `estimate_position_from_circles()` works:**
1. Find all intersection points between circle pairs
2. If intersections exist → pick the one with smallest error
3. If no intersections → use weighted average of circle centers as fallback

---

### `src/noise.py` — Handling imperfect signals

Real phone chips are not perfect. Different manufacturers report RSSI differently.

**`ChipsetNoiseProfile`** — describes how noisy each phone type is.

**`CHIPSET_NOISE`** — noise settings for phones 1–4 (for section 2.4 of the assignment).

**Functions:**

| Function | What it does |
|----------|-------------|
| `noisy_measurements()` | Adds random noise to RSSI values to simulate real-world error |
| `compare_with_noise()` | Compares clean vs noisy results — shows how much positions shift |
| `robust_estimate()` | Re-runs the algorithm with slightly larger circles (8% bigger) to handle noise |

---

### `src/visualization.py` — Plotting with matplotlib.pyplot

The assignment says: *"If you want to plot you should use matplotlib.pyplot."*

This file does exactly that. At the top it imports:
```python
import matplotlib.pyplot as plt
```

All plotting is done through **pyplot** functions:

| pyplot function | What it draws |
|-----------------|---------------|
| `plt.figure()` | Creates the plot window |
| `plt.scatter()` | Smartphone positions, intersection points, base stations |
| `plt.annotate()` | Labels for phones and towers |
| `plt.Circle()` | RSSI distance circles and 600 m transmission radius |
| `plt.xlabel()` / `plt.ylabel()` | Axis labels |
| `plt.title()` | Plot title |
| `plt.grid()` | Background grid |
| `plt.legend()` | Legend explaining symbols |
| `plt.savefig()` | Saves the image to `output/bs_estimation.png` |
| `plt.show()` | Optional: display the plot on screen |

**`plot_estimation()`** — clean **2×2 grid**, one tower per panel:

| Panel | Tower | Position |
|-------|-------|----------|
| Top-left | CI 12801 | (1000, 800) |
| Top-right | CI 12802 | (1600, 2400) |
| Bottom-left | CI 12803 | (2000, 1600) |
| Bottom-right | CI 12804 | (800, 2000) |

**Symbols:**
- **▲** = smartphone (hover/labels show SP number)
- **○ dashed** = RSSI distance circle
- **★** = estimated tower

Details (RSSI values) appear on **hover** in the interactive HTML version.

---

### `output/results.json` — Saved results

Created automatically when you run `main.py`. Contains:
- Tower IDs and estimated coordinates
- Residual error (how well circles fit)
- Number of circles used per tower

---

### `PSEUDOCODE.md` — Written algorithm (Section 2.1)

Plain-text description of the algorithm for the lab report. Includes a diagram and step-by-step pseudocode.

---

### `FLOWCHART.md` — Visual flowchart

Mermaid diagrams showing the flow of the algorithm. Good for presentations or the lab report.

---

## RSSI conversion examples

| Phone type | RSSI | max_rssi | Distance |
|------------|------|----------|----------|
| SP1/SP3 | 10 | 61 | 510 m |
| SP1/SP3 | 53 | 61 | 80 m |
| SP2/SP4 | 176 | 251 | 180 m |
| SP2/SP4 | 201 | 251 | 120 m |
| SP2/SP4 | 9 | 251 | 581 m |

Stronger signal (higher RSSI) → shorter distance → smaller circle.

---

## Special cases in the data

**RSSI = 0 or CI = "-"**  
The phone was **outside all known towers**. These points are used as **exclusion constraints** — they help rule out wrong tower positions.

**Different max_rssi per phone**  
Phones 1 and 3 use range 0–61. Phones 2 and 4 use range 0–251. The formula must use the correct max for each phone, or distances will be wrong.

---

## How to run and what you will see

```bash
source .venv/bin/activate
python main.py
```

You will see:
1. Final tower positions (JSON)
2. Verification checks
3. Noise analysis
4. Written answers for sections 2.5–2.7
5. A **matplotlib plot window** pops up — use toolbar to zoom/pan
6. An **interactive HTML graph** opens in your browser — scroll to zoom
7. Results saved to `output/results.json`

### Zoom the graph

**Best option — interactive HTML (recommended):**
```bash
open output/bs_estimation_interactive.html
```
- **Scroll wheel** = zoom in/out
- **Click + drag** = pan/move
- **Double-click** = reset view
- **Hover** = see phone/tower details

**Matplotlib window** (also opens when you run `main.py`):
- Click **magnifying glass** → drag a box to zoom
- Click **cross arrows** → drag to pan
- Click **home icon** → reset view

---

## Which lab sections does each part cover?

| Lab section | Points | Covered by |
|-------------|--------|------------|
| 2.1 Pseudocode | 25 | `PSEUDOCODE.md`, `FLOWCHART.md` |
| 2.2 Implementation | 25 | `src/positioning.py`, `src/rssi.py`, `main.py` |
| 2.3 Verification | 25 | `main.py` → `verify_implementation()` |
| 2.4 RSSI noise | 15 | `src/noise.py`, `main.py` → `analyze_noise()` |
| 2.5 Time of measurement | 5 | `main.py` → `analyze_time()` |
| 2.6 No transmission radius | 5 | `main.py` → `approach_without_radius()` |
| 2.7 Fake base station (optional) | — | `main.py` → `fake_bs_detection()` |

---

## Assignment Answers (Sections 2.3–2.7)

Written answers you can use for your lab presentation and report.

---

### 2.3 Verification of the Implementation (25 points)

**What we verify**

1. RSSI → distance conversion matches the assignment formula
2. Estimated tower positions fit all measurement circles with low error

**Formula used**

```
d = |(rssi − max_rssi) × (600 / (max_rssi − 1))|
```

- `max_rssi = 61` for SP1 and SP3
- `max_rssi = 251` for SP2 and SP4
- `r = 600 m`

**Sample conversions (from assignment)**

| RSSI | max_rssi | Distance |
|------|----------|----------|
| 10 | 61 | 510 m |
| 53 | 61 | 80 m |
| 176 | 251 | 180 m |
| 201 | 251 | 120 m |
| 9 | 251 | 581 m |

**Estimated base station positions**

| CI | Position (x, y) | Circles used | Residual error |
|----|-----------------|--------------|----------------|
| 12801 | (1000, 800) | 6 | 0 m |
| 12802 | (1600, 2400) | 3 | 0 m |
| 12803 | (2000, 1600) | 2 | 0 m |
| 12804 | (800, 2000) | 2 | 0 m |

**Why this proves accuracy**

- For each tower, we draw circles around every phone that heard it.
- All circles for the same CI intersect at one point.
- That point has residual error = 0 — every phone’s distance matches its RSSI circle.
- Exclusion rules were applied: RSSI = 0 points (SP2 at 339, 2614 and SP4 at 162, 2749) mean “outside all towers.” None of our estimates fall within 600 m of those points.

**Conclusion:** The implementation is verified. All 4 towers are found with perfect geometric fit on the assignment data.

---

### 2.4 Consideration of RSSI Noise (15 points)

**What noise different chipsets add**

| Phone | RSSI range | Typical noise | Effect |
|-------|------------|---------------|--------|
| SP1, SP3 | 0–61 | ~±3 dB | Coarse steps → up to ~45 m distance error |
| SP2 | 0–251 | ~±2 dB | Finer scale but vendor offset → ~30 m |
| SP4 | 0–251 | ~±2.5 dB | Shadowing/multipath → ~35 m |

**Sources of noise:** different chip manufacturers, quantization (61 vs 251 scale), multipath, and shadowing in urban GSM.

**How we account for it in the code**

1. **Simulate noise** — add random jitter to RSSI values (`src/noise.py`)
2. **Re-run the algorithm** and compare to clean results
3. **Robust estimate** — inflate circle radii by 8% to absorb uncertainty

**How positions differ from section 2.3**

With simulated RSSI noise (seed=42):

| CI | Clean (2.3) | Noisy | Shift |
|----|-------------|-------|-------|
| 12801 | (1000, 800) | (1013, 796) | 13.5 m |
| 12802 | (1600, 2400) | (1606, 2403) | 6.5 m |
| 12803 | (2000, 1600) | (2034, 1592) | 35.3 m |
| 12804 | (800, 2000) | (799, 2000) | 0.7 m |

Residual error also rises (e.g. CI 12801: 0 → 11.5 m).

With 8% radius inflation (robust mode), positions shift 40–57 m from baseline — a deliberate trade-off for stability under noise.

**Conclusion:** Real-world chipset noise can move estimates by tens of meters. More measurements and robust fitting reduce the impact.

---

### 2.5 Consideration of the Time of Measurement (5 points)

**The problem**

Each measurement has a timestamp, but smartphone clocks are not synchronized. So:

- The (x, y) position may be from a different moment than the RSSI reading
- If the user is moving, the circle is centered on the wrong position

**Effect on results**

- Circles are drawn at the wrong place → intersections shift
- Error grows with speed × time skew
- Example: 5 m/s walking + 2 s clock error → circle center off by ~10 m

**What to do about it**

- Reject or down-weight samples with large time differences between phones
- Estimate velocity and back-project position to a common time
- Prefer stationary measurements
- Use robust fitting (median intersections) to reduce outlier impact

**Conclusion:** Unsynchronized clocks can falsify tower positions, especially for moving users. Time alignment matters as much as RSSI accuracy.

---

### 2.6 Approximation Without Transmission Radius (5 points)

If `r = 600 m` is unknown, you cannot convert RSSI directly to meters. Approaches:

1. **Treat RSSI as relative only** — rank by signal strength, not absolute distance
2. **Estimate r per tower** — strongest RSSI ≈ distance 0; weakest in-range RSSI ≈ r
3. **Multi-lateration with unknown scale** — solve positions and scale together via least squares across all towers
4. **Cross-validation** — try different r values; pick the one that minimizes residual error across all CIs
5. **Use RSSI = 0 exclusion points** — they prove “outside range” without needing exact r (upper bound only)

**Conclusion:** Without r, you lose absolute scale but can still estimate relative tower positions using ranking, joint optimization, and exclusion constraints.

---

### 2.7 Optional: Detection of Fake Base Stations

**Post-mortem detection ideas for the server**

A fake base station (IMSI catcher / rogue cell) may appear temporarily. Detection signals:

| Signal | Why it’s suspicious |
|--------|---------------------|
| Circles never intersect consistently | Fake CI geometry doesn’t match real measurements over time |
| Sudden new CI with strong RSSI | Appears in an area already covered by known towers |
| Position “jumps” between sessions | Real towers are fixed; fake ones move |
| Seen only by some phones | Selective spoofing / jamming pattern |
| Unknown CI + strong signal | Not in operator cell database |
| Duplicate LAC with abnormal timing | Clone of a real tower with wrong timing advance |

**Server adaptation**

- Store historical estimates per CI over time
- Flag CIs with high residual error or unstable position
- Cross-check against known operator cell maps
- Alert when a CI appears only briefly or only for a subset of devices

**Conclusion:** Fake towers leave geometric and temporal inconsistencies. The server should track CI behavior over time, not just single snapshots.

---

## Quick summary

This project takes signal strength reports from multiple phones, converts them into distance circles, finds where those circles overlap, and estimates where cell towers are located. The code is split into small files: data, conversion, algorithm, noise handling, visualization, and a main file that ties everything together.
