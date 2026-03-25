"""
Visitall candidate 4: Minimum spanning tree cost over unvisited cells.

Compute a minimum spanning tree (Prim's algorithm, Manhattan edges) over
the set of unvisited goal cells plus the robot's current position.  The
MST weight is a lower bound on the tour cost.
"""


def _parse_cell(name):
    try:
        r_part, c_part = name.split("c")
        return int(r_part[1:]), int(c_part)
    except Exception:
        return None


def _mst_weight(nodes):
    """Prim's MST with Manhattan metric.  Returns total edge weight."""
    if len(nodes) <= 1:
        return 0
    in_tree = {0}
    key = [10**9] * len(nodes)
    key[0] = 0
    total = 0
    for _ in range(len(nodes) - 1):
        # Pick minimum key not in tree
        u = min((i for i in range(len(nodes)) if i not in in_tree), key=lambda i: key[i])
        in_tree.add(u)
        total += key[u]
        # Update keys
        for v in range(len(nodes)):
            if v not in in_tree:
                d = abs(nodes[u][0] - nodes[v][0]) + abs(nodes[u][1] - nodes[v][1])
                if d < key[v]:
                    key[v] = d
    return total


def h(state, goals):
    positive_goals, _ = goals
    unvisited_names = [
        atom[1] for atom in positive_goals
        if atom[0] == "visited" and atom not in state
    ]
    if not unvisited_names:
        return 0

    robot_pos = None
    for atom in state:
        if atom[0] == "at-robot":
            robot_pos = _parse_cell(atom[1])
            break

    cells = [_parse_cell(c) for c in unvisited_names]
    cells = [c for c in cells if c is not None]
    if robot_pos:
        cells = [robot_pos] + cells
    return _mst_weight(cells)
