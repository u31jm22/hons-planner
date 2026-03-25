# Depots — Instance Descriptions

**Domain:** Depots (warehouse logistics)  
**Instances:** 19 (p01–p09, p11–p20; p10 missing from upstream IPC benchmark)  
**Source:** IPC 2002 classical benchmarks  
**Requirements:** `:strips :typing`

## Domain Overview

Forklifts move crates between locations in a warehouse network consisting of
depots and distributors.  Trucks transport crates between sites; forklifts
load/unload trucks and stack crates in pallets.

**Key predicates:** `on(crate, surface)`, `in(crate, truck)`,
`at(truck/forklift, place)`, `available(forklift)`, `clear(surface)`.

**Difficulty scaling:** Number of depots, trucks, forklifts, and crates grows
with instance number.  Later instances require longer transport chains and
more careful sequencing.

## Instance Table

| Instance | Crates | Trucks | Forklifts | Goal crates | Difficulty |
|----------|--------|--------|-----------|-------------|------------|
| p01 | 4 | 2 | 2 | 2 | Easy |
| p02 | 6 | 2 | 2 | 4 | Easy |
| p03 | 8 | 2 | 2 | 6 | Medium |
| p04 | 8 | 3 | 3 | 6 | Medium |
| p05 | 10 | 3 | 3 | 10 | Medium |
| p06–p09 | 10–14 | 3–4 | 3–4 | 6–10 | Medium-Hard |
| p11–p15 | 12–18 | 4–5 | 4–5 | 8–12 | Hard |
| p16–p20 | 18–26 | 5–6 | 5–6 | 12–16 | Very Hard |

## Training / Test Split

- **Training (p01–p05):** Small depots with 4–10 crates
- **Test (all, 19 instances):** Full range; note p10 is absent from the IPC benchmark

## Plain-English Descriptions

- **p01–p05:** Small warehouses; one or two trucks shuttle a handful of crates.  Direct loading, driving, and unloading suffices.
- **p06–p12:** Multiple depots; crates must be routed through intermediate sites.  Forklifts can become bottlenecks.
- **p13–p20:** Large warehouse networks with complex crate-stacking requirements.  Heuristics that account for truck-forklift handoff costs outperform simple goal-count estimates.

