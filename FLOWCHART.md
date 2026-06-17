# Lab 3 – Algorithm Flowchart

Flowchart for the swarm mapping algorithm (sections 2.1–2.2).

## Main Process Flow

```mermaid
flowchart TD
    Start([Start: Server receives measurements]) --> Input[/Input per smartphone:<br/>CI, RSSI, time, x, y, max_rssi/]

    Input --> Loop{For each<br/>measurement m}

    Loop --> CheckCI{CI is null<br/>OR RSSI = 0?}
    CheckCI -->|Yes| Exclusion[Add smartphone position<br/>to exclusion_points list]
    CheckCI -->|No| Convert[Convert RSSI to distance:<br/>d = abs rssi - max_rssi × r / max_rssi - 1]

    Exclusion --> Loop
    Convert --> CreateCircle[Create circle:<br/>center = SP x,y<br/>radius = d]
    CreateCircle --> GroupByCI[Group circle by Cell ID CI]
    GroupByCI --> Loop

    Loop -->|All processed| PerCI{For each CI<br/>with circles}

    PerCI --> PairLoop{For each pair<br/>of circles}
    PairLoop --> Intersect[Compute intersection points<br/>using sympy.geometry]
    Intersect --> Collect[Collect candidate points]
    Collect --> PairLoop

    PairLoop -->|Done| HasCandidates{Any intersection<br/>points found?}
    HasCandidates -->|Yes| BestPoint[Select point with lowest<br/>mean residual error to all circles]
    HasCandidates -->|No| Fallback[Use weighted centroid<br/>of circle centers as fallback]
    BestPoint --> StoreEst[Store estimate: CI, x, y]
    Fallback --> StoreEst
    StoreEst --> PerCI

    PerCI -->|All CIs done| ExclCheck{For each estimate,<br/>check exclusion_points}
    ExclCheck --> InRange{BS closer than r=600m<br/>to any exclusion point?}
    InRange -->|Yes| Discard[Discard inconsistent estimate]
    InRange -->|No| Keep[Keep estimate]
    Discard --> ExclCheck
    Keep --> ExclCheck

    ExclCheck -->|Done| Output[/Output: list of base stations<br/>CI, x, y coordinates/]
    Output --> OptionalNoise{Apply noise<br/>model? Section 2.4}
    OptionalNoise -->|Yes| Inflate[Inflate circle radii<br/>or perturb RSSI values]
    Inflate --> ReRun[Re-run estimation]
    ReRun --> Plot[Plot with matplotlib]
    OptionalNoise -->|No| Plot
    Plot --> End([End])
```

## RSSI to Distance Conversion

```mermaid
flowchart LR
    A[RSSI value] --> B{RSSI ≤ 0?}
    B -->|Yes| C[Invalid:<br/>outside transmission radius]
    B -->|No| D[Read max_rssi<br/>61 or 251 per chipset]
    D --> E["d = |(rssi - max_rssi) × (600 / (max_rssi - 1))|"]
    E --> F[Distance circle radius d]
```

## Per-CI Position Estimation

```mermaid
flowchart TD
    A[Circles for one CI] --> B[Pairwise circle intersections]
    B --> C{Intersection<br/>points exist?}
    C -->|Yes| D[Compute residual error<br/>for each candidate point]
    D --> E[Pick point with<br/>minimum residual]
    C -->|No| F[Weighted centroid<br/>1/radius weighting]
    E --> G[Estimated BS position]
    F --> G
```

## Data Flow Overview

```mermaid
flowchart LR
    SP1[Smartphone 1<br/>max_rssi=61] --> Server[Server]
    SP2[Smartphone 2<br/>max_rssi=251] --> Server
    SP3[Smartphone 3<br/>max_rssi=61] --> Server
    SP4[Smartphone 4<br/>max_rssi=251] --> Server

    Server --> Circles[Distance circles<br/>grouped by CI]
    Circles --> Intersections[Circle intersections<br/>sympy.geometry]
    Intersections --> Estimates[BS position estimates]
    Estimates --> Results[results.json]
    Estimates --> Plot[bs_estimation.png]
```

## Legend

| Symbol | Meaning |
|--------|---------|
| `r` | Transmission radius = 600 m (urban GSM) |
| `max_rssi` | 61 (SP1, SP3) or 251 (SP2, SP4) |
| `RSSI = 0` | Smartphone outside all known base stations |
| `CI = "-"` | No base station in range; used as exclusion point |
| Residual error | Mean absolute deviation from each circle boundary |
