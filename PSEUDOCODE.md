# Lab 3 – Pseudocode (Section 2.1)

## What is the problem?

We know where the **phones** are, but we do **not** know where the **towers** are.

Each phone sends:
- **CI** = which tower it hears
- **RSSI** = how strong the signal is
- **(x, y)** = phone position

Stronger signal → phone is closer to the tower.

---

## Simple picture

```
        Tower? (*)
           |
    distance from RSSI
           |
    Phone A ----○----○---- Phone B
           circle   circle
           (tower must be where circles overlap)
```

- Each phone draws a **circle** around itself.
- The circle radius = estimated distance to the tower.
- The tower should be where circles for the **same CI** cross each other.

---

## Assignment data grouped by CI

Values from the assignment PDF (section 2). Each row is one measurement: which phone (SP), signal strength (RSSI), time, and phone coordinates (x, y).

### CI 12801

| SP | RSSI | Time | SP x | SP y | max_rssi | Distance (m) |
|----|------|------|------|------|----------|--------------|
| 1 | 10.0 | 100045 | 1450.0 | 1040.0 | 61 | 510.0 |
| 1 | 53.0 | 100230 | 936.0 | 752.0 | 61 | 80.0 |
| 1 | 36.0 | 110002 | 850.0 | 600.0 | 61 | 250.0 |
| 2 | 176.0 | 129885 | 827.2 | 850.4 | 251 | 180.0 |
| 2 | 201.0 | 134546 | 904.0 | 728.0 | 251 | 120.0 |
| 3 | 10.0 | 004725 | 784.0 | 1262.0 | 61 | 510.0 |

**6 measurements** from SP1, SP2, and SP3 → 6 circles used to find tower 12801.

---

### CI 12802

| SP | RSSI | Time | SP x | SP y | max_rssi | Distance (m) |
|----|------|------|------|------|----------|--------------|
| 2 | 108.0 | 156778 | 1468.0 | 2716.8 | 251 | 343.2 |
| 3 | 24.0 | 007321 | 1720.0 | 2050.0 | 61 | 370.0 |
| 4 | 87.0 | 094521 | 1984.0 | 2313.6 | 251 | 393.6 |

**3 measurements** from SP2, SP3, and SP4 → 3 circles used to find tower 12802.

---

### CI 12803

| SP | RSSI | Time | SP x | SP y | max_rssi | Distance (m) |
|----|------|------|------|------|----------|--------------|
| 3 | 8.0 | 007321 | 1720.0 | 2050.0 | 61 | 530.0 |
| 4 | 17.0 | 136744 | 2216.0 | 2118.4 | 251 | 561.6 |

**2 measurements** from SP3 and SP4 → 2 circles used to find tower 12803.

---

### CI 12804

| SP | RSSI | Time | SP x | SP y | max_rssi | Distance (m) |
|----|------|------|------|------|----------|--------------|
| 2 | 9.0 | 164747 | 219.2 | 2000.0 | 251 | 580.8 |
| 4 | 70.0 | 156554 | 800.0 | 2434.4 | 251 | 434.4 |

**2 measurements** from SP2 and SP4 → 2 circles used to find tower 12804.

---

### Exclusion points (CI = "-", RSSI = 0)

Phone was **outside all known towers**. Used to rule out wrong tower positions.

| SP | RSSI | Time | SP x | SP y |
|----|------|------|------|------|
| 2 | 0.0 | 169567 | 339.2 | 2614.4 |
| 4 | 0.0 | 174677 | 161.6 | 2748.8 |

---

### Quick summary

| CI | # of measurements | Smartphones | Estimated tower position |
|----|-------------------|-------------|--------------------------|
| 12801 | 6 | SP1, SP2, SP3 | (1000, 800) |
| 12802 | 3 | SP2, SP3, SP4 | (1600, 2400) |
| 12803 | 2 | SP3, SP4 | (2000, 1600) |
| 12804 | 2 | SP2, SP4 | (800, 2000) |
| — (exclusion) | 2 | SP2, SP4 | (not a tower) |

**Distance formula:** `|(RSSI - max_rssi) × (600 / (max_rssi - 1))|`

---

## Step-by-step (in plain English)

### Step 1: Read the data
```
FOR each measurement from each smartphone:
    read CI, RSSI, time, phone_x, phone_y, max_rssi
```

### Step 2: Convert RSSI to distance
```
IF RSSI is 0 OR CI is "-":
    phone is outside all towers
    save this phone position as an EXCLUSION point
    skip to next measurement

ELSE:
    distance = |(RSSI - max_rssi) × (600 / (max_rssi - 1))|
```

**Notes:**
- `max_rssi` = 61 for phones 1 and 3, 251 for phones 2 and 4
- `600` = max tower range in meters
- Higher RSSI → smaller distance

**Examples:**
- RSSI = 53, max = 61 → distance = 80 m (close)
- RSSI = 10, max = 61 → distance = 510 m (far)

### Step 3: Draw circles
```
FOR each valid measurement:
    draw a circle
        center = phone position (x, y)
        radius = distance from Step 2
    group circles by CI (same tower ID together)
```

### Step 4: Find tower position for each CI
```
FOR each CI (e.g. 12801, 12802, ...):
    find where its circles intersect

    IF intersection points exist:
        pick the point that best fits all circles
    ELSE:
        use average of circle centers as backup

    save result as (CI, tower_x, tower_y)
```

### Step 5: Check exclusion points
```
FOR each estimated tower position:
    FOR each exclusion point (RSSI = 0):
        IF tower is closer than 600 m to that point:
            this estimate is wrong → remove it
```

### Step 6: Return results
```
RETURN list of all towers:
    CI 12801 → (x, y)
    CI 12802 → (x, y)
    ...
```

### Step 7: Plot (optional, using matplotlib.pyplot)
```
draw phone positions with plt.scatter()
draw circles with plt.Circle()
draw tower positions with plt.scatter()
save image with plt.savefig()
show graph with plt.show()
```

---

## Full pseudocode (simple version)

```
START

SET tower_range = 600 meters

CREATE empty list: exclusion_points
CREATE empty map: circles_by_tower

// --- Step 1 & 2 & 3: process all measurements ---
FOR EACH measurement:
    IF CI is missing OR RSSI is 0:
        ADD phone position TO exclusion_points
    ELSE:
        distance = |(RSSI - max_rssi) × (600 / (max_rssi - 1))|
        ADD circle(phone_x, phone_y, distance) TO circles_by_tower[CI]

// --- Step 4: estimate each tower ---
CREATE empty list: results

FOR EACH tower_id, circles IN circles_by_tower:
    points = find all places where circles cross

    IF points is not empty:
        best_point = point with smallest error to all circles
    ELSE:
        best_point = average of circle centers

    ADD (tower_id, best_point) TO results

// --- Step 5: exclusion check ---
FOR EACH (tower_id, position) IN results:
    FOR EACH exclusion_point:
        IF distance(position, exclusion_point) < 600:
            REMOVE this result

// --- Step 6: output ---
PRINT results

// --- Step 7: plot ---
PLOT phones, circles, and towers using matplotlib.pyplot
SAVE plot to file

END
```

---

## Key ideas (short)

1. **Different phones use different RSSI scales** → always use the right `max_rssi`.
2. **Same CI = same tower** → group circles by CI.
3. **Circles overlap** → overlap point ≈ tower location.
4. **RSSI = 0** → phone was outside all towers → use to reject bad answers.
5. **Pick best intersection** → choose the point that fits all circles best.
