# Gripper — Instance Descriptions

**Domain:** Gripper (robot transport)  
**Instances:** 30 (p01–p30)  
**Source:** IPC classical benchmarks  
**Requirements:** `:strips`

## Domain Overview

A robot with two grippers moves between two rooms (A and B), picking up
and putting down balls.  The robot can carry at most one ball per gripper
(i.e., two balls simultaneously).  All balls start in room A; the goal is
to move all balls to room B.

**Key predicates:** `at(ball, room)`, `at-robby(room)`, `carry(ball, gripper)`,
`free(gripper)`.

**Difficulty scaling:** Number of balls increases from 4 to 30.  Since the
robot carries 2 balls per trip, the optimal plan length is `ceil(N/2) * 3 + 1`
moves.

## Instance Table

| Instance | Balls | Moves (optimal) | Difficulty |
|----------|-------|-----------------|------------|
| p01 | 4 | 7 | Trivial |
| p05 | 12 | 19 | Easy |
| p10 | 22 | 34 | Medium |
| p15 | 32 | ? | Medium-Hard |
| p20 | 42 | ? | Hard |
| p25 | 52 | ? | Very Hard |
| p30 | 60 | ? | Very Hard |

## Training / Test Split

- **Training (p01–p05):** 4–12 balls, fast to solve
- **Test (all30):** Up to 30+ balls; later instances stress-test heuristics

## Plain-English Descriptions

- **p01–p05 (Trivial–Easy):** Small number of balls, the robot makes few round trips.  Nearly any heuristic solves these quickly.
- **p06–p15 (Easy–Medium):** The robot must make multiple trips; good heuristics count remaining balls and prefer states where the robot is loaded.
- **p16–p25 (Hard):** Many trips required; a heuristic that estimates transport cost scales better.
- **p26–p30 (Very Hard):** Largest instances; inadmissible heuristics can fail or be slow.

