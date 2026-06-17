# Lab 3 – Flowchart

One complete flowchart for the swarm mapping algorithm (Section 2.1).

**Shapes used (standard flowchart symbols):**

| Shape | Meaning |
|-------|---------|
| Oval `([ ])` | Start / End |
| Rectangle `[ ]` | Process step — do something |
| Diamond `{ }` | Decision — Yes or No |
| Parallelogram `[/ /]` | Input / Output |

---

```mermaid
flowchart TD
    Start([Start]) --> Input[/Input: measurements from all phones<br/>CI, RSSI, x, y, max_rssi/]

    Input --> Init[Set tower range = 600 m]
    Init --> Init2[Create empty exclusion list<br/>and circle map]

    Init2 --> MoreMeas{More measurements?}

    MoreMeas -->|Yes| CheckRSSI{RSSI = 0<br/>or no tower ID?}
    CheckRSSI -->|Yes| SaveExcl[Save phone position<br/>to exclusion list]
    SaveExcl --> MoreMeas

    CheckRSSI -->|No| CalcDist[Convert RSSI to distance<br/>d = abs RSSI - max_rssi x 600 / max_rssi - 1]
    CalcDist --> DrawCircle[Draw circle around phone<br/>centre = phone position, radius = d]
    DrawCircle --> GroupCircle[Add circle to map<br/>grouped by tower ID]
    GroupCircle --> MoreMeas

    MoreMeas -->|No| MoreTower{More tower IDs?}

    MoreTower -->|Yes| FindCross[Find where circle pairs cross<br/>for this tower]
    FindCross --> HasCross{Any crossing<br/>points found?}

    HasCross -->|Yes| CalcError[For each crossing point:<br/>average error to all circles]
    CalcError --> PickBest[Pick point with<br/>smallest average error]

    HasCross -->|No| WeightedAvg[Use weighted average<br/>of circle centres<br/>closer phone = more weight]

    PickBest --> SaveTower[Save tower ID, x, y]
    WeightedAvg --> SaveTower
    SaveTower --> MoreTower

    MoreTower -->|No| MoreCheck{More estimated<br/>towers to check?}

    MoreCheck -->|Yes| ExclCheck{Tower within 600 m<br/>of an exclusion point?}
    ExclCheck -->|Yes| Reject[Reject this tower]
    ExclCheck -->|No| Keep[Keep this tower]
    Reject --> MoreCheck
    Keep --> MoreCheck

    MoreCheck -->|No| Output[/Output: list of towers<br/>CI, x, y/]
    Output --> End([End])
```

---

## Shape Legend

| Symbol in diagram | Name | Used for |
|-------------------|------|----------|
| Oval | Terminal | Start and End |
| Rectangle | Process | Actions: convert, draw, save, reject |
| Diamond | Decision | Questions with Yes / No paths |
| Parallelogram | Input/Output | Data going in or results going out |

## Term Legend

| Term | Meaning |
|------|---------|
| **CI** | Tower ID (Cell ID) |
| **RSSI** | Signal strength — higher means closer |
| **max_rssi** | Max signal for that phone chip (61 or 251) |
| **600 m** | Tower transmission range |
| **Exclusion point** | Phone with RSSI = 0 — heard no tower |
| **Average error** | Mean of abs distance to phone minus circle radius |
