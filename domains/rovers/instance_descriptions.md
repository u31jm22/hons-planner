# Rovers — Instance Descriptions

**Domain:** Rovers (planetary exploration)  
**Instances:** 30 (p01–p30)  
**Source:** aibasel/downward-benchmarks (IPC 2002)  
**Requirements:** `:strips :typing`

## Domain Overview

Planetary rovers navigate a waypoint graph, collecting scientific data
(rock samples, soil samples, images of objectives and rock samples) and
communicating results to a lander.  Rovers have different equipment
capabilities; some can only take rock samples, others can take images.

**Key predicates:** `at(rover, waypoint)`, `have-rock-analysis(rover, waypoint)`,
`communicated-rock-data(waypoint)`, `communicated-image-data(objective, mode)`,
`visible(wp1, wp2)`, `can-traverse(rover, wp1, wp2)`.

**Difficulty scaling:** Instances grow rapidly — later instances have up to
100 objects and 1700+ initial atoms.  Large instances stress-test both the
parser and the heuristic.

## Instance Table

| Instance | Objects | Init atoms | Goal atoms | Difficulty |
|----------|---------|------------|------------|------------|
| p01 | 20 | ~50 | 3 | Easy |
| p05 | 25 | ~65 | 7 | Easy-Medium |
| p10 | ~35 | ~110 | ~8 | Medium |
| p15 | ~50 | ~200 | ~10 | Medium-Hard |
| p20 | ~65 | ~400 | ~14 | Hard |
| p25 | ~80 | ~900 | ~18 | Very Hard |
| p30 | 103 | 1757 | 25 | Extreme |

## Training / Test Split

- **Training (p01–p05):** Small rover crews, few waypoints
- **Test (all30):** Full benchmark including extremely large instances (p26–p30)

## Plain-English Descriptions

- **p01–p05:** One or two rovers navigate a handful of waypoints to collect 3–7 data items.  Almost any heuristic solves these.
- **p06–p15:** Multiple rovers with specialised equipment; planning must assign tasks to the right rover and sequence navigation to avoid dead ends.
- **p16–p25:** Large waypoint graphs with many data requirements; heuristics that account for rover-specific capabilities outperform generic goal-count estimates.
- **p26–p30:** Massive state spaces; only the best heuristics (FF or learned) can solve these within the 300s time limit.

