"""
Visitall candidate 2: Manhattan distance + unvisited count.

Adds a rough connectivity estimate: on a grid the robot must traverse at
least (unvisited - 1) extra edges to collect scattered cells, so we use
2 * unvisited as an admissible-ish heuristic.
"""


def h(state, goals):
    positive_goals, _ = goals
    unvisited = [
        atom for atom in positive_goals
        if atom[0] == "visited" and atom not in state
    ]
    n = len(unvisited)
    if n == 0:
        return 0
    # Conservative: at least n moves to visit n cells (they might be adjacent)
    # More aggressive: 2*n to account for backtracking
    return n
