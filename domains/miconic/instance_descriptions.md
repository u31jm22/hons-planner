# Miconic — Instance Descriptions

**Domain:** Miconic / Elevator  
**Instances:** 30 (p01–p30)  
**Source:** IPC classical benchmarks (Miconic-STRIPS)  
**Requirements:** `:strips`

## Domain Overview

An elevator serves passengers in a multi-floor building.  Each passenger
boards at their origin floor and must be delivered to their destination floor.
The elevator can move between adjacent floors (up/down) and can board/alight
passengers.

**Key predicates:** `lift-at(floor)`, `boarded(passenger)`, `served(passenger)`,
`above(f1, f2)`, `origin(passenger, floor)`, `destin(passenger, floor)`.

**Difficulty scaling:** More floors and more passengers means longer plans and
more branching; passengers with interleaved origins/destinations are harder.

## Instance Table

| Instance | Passengers | Floors | Difficulty |
|----------|------------|--------|------------|
| p01–p05  | 1          | 4–5    | Trivial |
| p06–p10  | 2–3        | 4–6    | Easy |
| p11–p15  | 3–5        | 5–8    | Medium |
| p16–p20  | 5–8        | 6–10   | Medium-Hard |
| p21–p25  | 8–12       | 8–12   | Hard |
| p26–p30  | 12–16      | 10–14  | Very Hard |

## Training / Test Split

- **Training (p01–p05):** 1 passenger, 4–5 floors — used for candidate selection
- **Test (all30):** Up to 16 passengers across 14 floors

## Plain-English Descriptions

- **p01–p05:** A single passenger boards and alights once.  Optimal plan: move to origin, board, move to destination, alight.
- **p06–p10:** A few passengers; the elevator may need to serve some before backtracking for others.
- **p11–p20:** Many passengers scattered across floors; an efficient heuristic groups nearby passengers to minimise travel.
- **p21–p30:** Large instances with complex interleaving; poor ordering leads to many redundant floor traversals.

