"""
Visitall candidate 5: BFS-based min-distance from current robot position to
each unvisited goal, summed.  Uses connected-predicate graph from state.

This is an inadmissible but informative heuristic that rewards states where
the robot is near many unvisited goal cells.
"""
from collections import deque


def h(state, goals):
    positive_goals, _ = goals
    unvisited = frozenset(
        atom[1] for atom in positive_goals
        if atom[0] == "visited" and atom not in state
    )
    if not unvisited:
        return 0

    # Build adjacency from (connected, a, b) atoms in state
    adj: dict[str, list[str]] = {}
    for atom in state:
        if atom[0] == "connected":
            a, b = atom[1], atom[2]
            adj.setdefault(a, []).append(b)

    # Find robot position
    robot = None
    for atom in state:
        if atom[0] == "at-robot":
            robot = atom[1]
            break
    if robot is None:
        return len(unvisited)

    # BFS from robot to all reachable cells, sum distances to unvisited goals
    dist: dict[str, int] = {robot: 0}
    q = deque([robot])
    while q:
        cur = q.popleft()
        for nb in adj.get(cur, []):
            if nb not in dist:
                dist[nb] = dist[cur] + 1
                q.append(nb)

    total = 0
    for cell in unvisited:
        total += dist.get(cell, len(unvisited) * 10)
    return total
