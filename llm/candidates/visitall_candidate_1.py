"""
Visitall candidate 1: Count unvisited goal cells.

The visitall goal is to visit a set of cells.  A lower bound on the number
of actions remaining is the number of goal cells that have not yet been
visited (each unvisited goal cell needs at least one move action).
"""


def h(state, goals):
    """
    state  : frozenset of (predicate, *args) ground atoms currently true
    goals  : (positive_goals, negative_goals) — both frozensets
    """
    positive_goals, _ = goals
    # Count goal atoms of the form (visited, <cell>) not yet in state
    unvisited = sum(
        1 for atom in positive_goals
        if atom[0] == "visited" and atom not in state
    )
    return unvisited
