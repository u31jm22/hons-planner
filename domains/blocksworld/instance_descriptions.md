# Blocksworld — Instance Descriptions

**Domain:** Blocksworld (stack manipulation)  
**Instances:** 30 (p01–p30)  
**Source:** IPC classical benchmarks  
**Requirements:** `:strips`

## Domain Overview

The blocksworld domain involves a robot arm that can pick up and put down
coloured blocks.  Blocks can be stacked on top of each other or placed on a
table.  The robot arm can only hold one block at a time and can only pick up
a block that has nothing on top of it (i.e., is "clear").

The state is described by `on(x, y)`, `ontable(x)`, `clear(x)`, and
`handempty` predicates.  The goal is typically to rearrange blocks from a
random initial configuration into a target stacking.

**Difficulty scaling:** Larger instances have more blocks and more complex
goal configurations, requiring longer plans and more search effort.

## Instance Table

| Instance | Blocks | Init atoms | Goal atoms | Difficulty |
|----------|--------|------------|------------|------------|
| p01 | 5 | ~10 | 3 | Easy |
| p02 | 5 | ~9 | 3 | Easy |
| p03 | 5 | ~9 | 3 | Easy |
| p04 | 6 | ~10 | 4 | Easy |
| p05 | 6 | ~10 | 4 | Easy |
| p06 | 7 | ~12 | 5 | Easy-Medium |
| p07 | 7 | ~12 | 5 | Easy-Medium |
| p08 | 7 | ~12 | 5 | Easy-Medium |
| p09 | 8 | ~14 | 6 | Medium |
| p10 | 8 | ~14 | 6 | Medium |
| p11 | 9 | ~16 | 7 | Medium |
| p12 | 9 | ~16 | 7 | Medium |
| p13 | 10 | ~18 | 8 | Medium |
| p14 | 10 | ~18 | 8 | Medium |
| p15 | 10 | ~18 | 8 | Medium |
| p16 | 11 | ~20 | 9 | Medium-Hard |
| p17 | 11 | ~20 | 9 | Medium-Hard |
| p18 | 11 | ~20 | 9 | Medium-Hard |
| p19 | 12 | ~22 | 10 | Hard |
| p20 | 12 | ~22 | 10 | Hard |
| p21 | 12 | ~22 | 10 | Hard |
| p22 | 13 | ~24 | 11 | Hard |
| p23 | 13 | ~24 | 11 | Hard |
| p24 | 13 | ~24 | 11 | Hard |
| p25 | 14 | ~26 | 12 | Very Hard |
| p26 | 14 | ~26 | 12 | Very Hard |
| p27 | 14 | ~26 | 12 | Very Hard |
| p28 | 14 | ~26 | 12 | Very Hard |
| p29 | 15 | ~28 | 13 | Very Hard |
| p30 | 15 | ~28 | 13 | Very Hard |

## Training / Test Split

- **Training (p01–p05):** 5 blocks, simple stacking goals, used for candidate selection
- **Test (all30):** Full range for final evaluation

## Plain-English Problem Descriptions

- **p01–p05 (Easy):** 5–6 blocks in a small random pile; goal is to build a specific tower.  A simple heuristic of counting misplaced blocks works well.
- **p06–p15 (Medium):** 7–10 blocks; goals require restructuring multiple stacks.  The robot must unstack and restack carefully to avoid blocking pieces.
- **p16–p24 (Hard):** 11–13 blocks; multiple interdependencies between stacks.  Poor heuristics will visit many dead-end states.
- **p25–p30 (Very Hard):** 14–15 blocks; complex goal configurations that require long plans (~50+ steps) and careful search.
