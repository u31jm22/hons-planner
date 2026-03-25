"""
Visitall candidate 3: Spanning-tree estimate via BFS on goal cells.

Extract row/col indices from cell names (r<i>c<j>) and estimate the cost
of a Hamiltonian path through the unvisited goal cells using a nearest-
neighbour greedy tour.  This gives a good (inadmissible) estimate that
helps the planner prioritise efficient routes.
"""
import math


def _parse_cell(name):
    """Parse 'r2c3' → (2, 3). Returns None on failure."""
    try:
        r_part, c_part = name.split("c")
        return int(r_part[1:]), int(c_part)
    except Exception:
        return None


def h(state, goals):
    positive_goals, _ = goals
    unvisited = [
        atom[1] for atom in positive_goals
        if atom[0] == "visited" and atom not in state
    ]
    if not unvisited:
        return 0

    # Find current robot position from state
    robot_pos = None
    for atom in state:
        if atom[0] == "at-robot":
            robot_pos = _parse_cell(atom[1])
            break

    cells = [_parse_cell(c) for c in unvisited]
    cells = [c for c in cells if c is not None]
    if not cells:
        return len(unvisited)

    # Greedy nearest-neighbour tour cost from robot position
    start = robot_pos if robot_pos else cells[0]
    remaining = cells[:]
    total = 0
    cur = start
    while remaining:
        nearest = min(remaining, key=lambda c: abs(c[0] - cur[0]) + abs(c[1] - cur[1]))
        total += abs(nearest[0] - cur[0]) + abs(nearest[1] - cur[1])
        cur = nearest
        remaining.remove(nearest)
    return total
