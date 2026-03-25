# Logistics — Instance Descriptions

**Domain:** Logistics (package delivery)  
**Instances:** 30 (p01–p30)  
**Source:** IPC classical benchmarks (logistics-typed variant)  
**Requirements:** `:strips :typing`

## Domain Overview

Packages must be delivered from their initial locations to goal locations
using trucks (within cities) and airplanes (between cities).  Trucks move
within a city; planes fly between airports.  Packages must be loaded onto a
vehicle, transported, and unloaded.

**Key predicates:** `at(obj, loc)`, `in(pkg, vehicle)`, `incity(loc, city)`.

**Difficulty scaling:** Instances grow in number of cities, trucks, packages,
and the distance packages must travel.

## Instance Table

| Instance | Packages | Cities | Goal deliveries | Difficulty |
|----------|----------|--------|-----------------|------------|
| p01–p05  | 2–3      | 3      | 4–5             | Easy |
| p06–p10  | 3–5      | 3–4    | 5–7             | Easy-Medium |
| p11–p15  | 5–7      | 4–5    | 7–10            | Medium |
| p16–p20  | 7–10     | 5–6    | 10–13           | Medium-Hard |
| p21–p25  | 10–13    | 5–7    | 12–16           | Hard |
| p26–p30  | 13–18    | 6–8    | 14–20           | Very Hard |

## Training / Test Split

- **Training (p01–p05):** Small worlds with 2–3 packages across 3 cities
- **Test (all30):** Full range including multi-city, multi-package scenarios

## Plain-English Descriptions

- **p01–p05:** Simple city networks; each package moves at most once by truck or plane.  Quick to solve with any reasonable heuristic.
- **p06–p15:** Packages may require truck + plane + truck chains.  A heuristic counting undelivered packages or estimating transport steps is helpful.
- **p16–p25:** Multiple packages competing for vehicles; the planner must sequence vehicle usage efficiently.
- **p26–p30:** Large networks; naive heuristics scale poorly as the interaction graph between packages, trucks, and planes grows complex.

