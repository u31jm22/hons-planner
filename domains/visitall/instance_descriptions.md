# Visitall — Instance Descriptions

**Domain:** Visitall (grid coverage)  
**Instances:** 30 (p01–p30)  
**Source:** Programmatically generated for this thesis  
**Requirements:** `:typing`

## Domain Overview

A robot navigates a rectangular grid graph.  Each cell is a `place` object;
cells are connected to their immediate neighbours (up/down/left/right).  The
robot starts at the top-left cell (r0c0, already visited) and must visit a
specified subset of cells by moving through the grid.

**Key predicates:** `at-robot(place)`, `visited(place)`, `connected(p1, p2)`.  
**Single action:** `move(curpos, nextpos)` — robot moves along a connected edge,
marking the destination as visited.

**Difficulty scaling:** Grid size (rows × cols) increases and the number of
cells that must be visited (k) grows from a small subset to the full grid.
The search space is exponential in k — the planner must find a walk that
covers all required cells efficiently.

## Instance Table

| Instance | Grid | Cells | Must Visit (k) | Difficulty |
|----------|------|-------|----------------|------------|
| p01 | 2×2 | 4 | 4 (full) | Trivial |
| p02 | 3×2 | 6 | 5 | Trivial |
| p03 | 3×3 | 9 | 6 | Easy |
| p04 | 3×3 | 9 | 7 | Easy |
| p05 | 3×3 | 9 | 9 (full) | Easy |
| p06 | 4×3 | 12 | 8 | Easy |
| p07 | 4×3 | 12 | 10 | Easy |
| p08 | 4×3 | 12 | 12 (full) | Easy |
| p09 | 4×4 | 16 | 10 | Easy-Medium |
| p10 | 4×4 | 16 | 12 | Easy-Medium |
| p11 | 4×4 | 16 | 16 (full) | Medium |
| p12 | 5×4 | 20 | 11 | Medium |
| p13 | 5×4 | 20 | 14 | Medium |
| p14 | 5×4 | 20 | 17 | Medium |
| p15 | 5×4 | 20 | 20 (full) | Medium |
| p16 | 5×5 | 25 | 13 | Medium-Hard |
| p17 | 5×5 | 25 | 16 | Medium-Hard |
| p18 | 5×5 | 25 | 19 | Medium-Hard |
| p19 | 5×5 | 25 | 22 | Hard |
| p20 | 5×5 | 25 | 25 (full) | Hard |
| p21 | 6×5 | 30 | 15 | Hard |
| p22 | 6×5 | 30 | 18 | Hard |
| p23 | 6×5 | 30 | 22 | Hard |
| p24 | 6×5 | 30 | 26 | Very Hard |
| p25 | 6×5 | 30 | 30 (full) | Very Hard |
| p26 | 6×6 | 36 | 18 | Very Hard |
| p27 | 6×6 | 36 | 22 | Very Hard |
| p28 | 6×6 | 36 | 26 | Very Hard |
| p29 | 6×6 | 36 | 30 | Extreme |
| p30 | 6×6 | 36 | 36 (full) | Extreme |

## Training / Test Split

- **Training (p01–p05):** Tiny grids (2×2 to 3×3), used for candidate selection
- **Test (all30):** Full range from trivial to extreme

## LLM Heuristic Design Notes

Good heuristics for visitall exploit the grid structure:

1. **Unvisited count** (`h = |unvisited ∩ goals|`) — simple lower bound
2. **Nearest-neighbour tour cost** — greedy Hamiltonian estimate from robot position
3. **MST weight** — minimum spanning tree over unvisited goal cells (admissible lower bound)
4. **BFS distance sum** — sum of shortest-path distances from robot to each unvisited goal

The selected candidate (BFS distance sum) achieved the lowest total expansions
on the training set, rewarding states where the robot is near many unvisited goals.

## Plain-English Problem Descriptions

- **p01–p05 (Trivial–Easy):** The grid is tiny (4–9 cells); any walk that zig-zags through the required cells works.  Even the trivial heuristic solves these in milliseconds.
- **p06–p11 (Easy–Medium):** Grids of 12–16 cells; partial visit requirements mean the robot can skip some cells.  The planner must choose which cells to visit in what order.
- **p12–p20 (Medium–Hard):** 20–25 cell grids with growing visit requirements.  A poor heuristic (e.g., uniform cost) explores thousands of states; a good heuristic (BFS distance) solves in <2s.
- **p21–p25 (Hard):** 30-cell grids; A* with a weak heuristic may time out.  A heuristic that estimates the remaining tour cost is essential.
- **p26–p30 (Extreme):** Full 6×6 coverage problems; these are NP-hard variants of the Hamiltonian path problem.  Only the best heuristics (BFS-guided or learned) consistently solve within the 300s limit.

