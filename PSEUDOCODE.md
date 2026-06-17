# Lab 3 – Pseudocode

## Main Algorithm

```
START SwarmMapping

INPUT:  all smartphone measurements
        each row has: tower ID (CI), signal (RSSI), phone x, phone y, max_rssi
OUTPUT: list of towers with their x, y positions

SET tower_range = 600 metres

CREATE empty list: exclusion_points
CREATE empty map:   circles_by_tower

// STEP 1: Read data and build circles
FOR each measurement:

    IF tower ID is missing OR RSSI is 0:
        save phone position to exclusion_points
        skip this measurement

    distance = |(RSSI - max_rssi) × (tower_range / (max_rssi - 1))|

    circle = phone position as centre, distance as radius
    add circle to circles_by_tower[same tower ID]

// STEP 2: Find each tower position
CREATE empty list: results

FOR each tower ID and its circles:

    candidates = find where circle pairs cross (PairwiseIntersections)

    IF candidates is not empty:
        best = the candidate with the smallest error (ResidualError)
    ELSE:
        best = weighted average of circle centres (WeightedCentroid)

    save (tower ID, best x, best y) to results

// STEP 3: Remove bad answers using RSSI = 0 points
CREATE empty list: final_results

FOR each tower in results:

    reject = false

    FOR each exclusion point (phone that heard no tower):
        IF tower is closer than 600 m to that phone:
            reject = true
            stop checking

    IF reject is false:
        add tower to final_results

RETURN final_results

END
```

---

## Find Circle Crossings

```
FUNCTION PairwiseIntersections(circles)

INPUT:  all circles for one tower
OUTPUT: list of crossing points (x, y)

CREATE empty list: candidates

FOR each pair of circles (i, j):
    points = where circle i and circle j meet
    add all points to candidates

RETURN candidates

END FUNCTION
```

---

## Measure How Good a Point Is

```
FUNCTION ResidualError(point, circles)

INPUT:  one candidate point, all circles for one tower
OUTPUT: average mistake in metres (smaller = better)

CREATE empty list: errors

FOR each circle:
    actual_distance = distance from point to phone (circle centre)
    error = |actual_distance - circle radius|
    add error to errors

RETURN average of all errors

END FUNCTION
```

---

## Backup When Circles Do Not Cross

```
FUNCTION WeightedCentroid(circles)

INPUT:  all circles for one tower
OUTPUT: estimated x, y (used only when no crossings found)

FOR each circle:
    weight = 1 / radius    // smaller circle = closer phone = more weight

tower_x = sum of (phone_x × weight) / sum of weights
tower_y = sum of (phone_y × weight) / sum of weights

RETURN (tower_x, tower_y)

END FUNCTION
```
