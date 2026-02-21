def h(state, goals):
    """
    Domain-specific heuristic for the logistics domain.
    state: frozenset of tuples like ('at-robby', 'rooma'), ('at', 'ball1', 'rooma'), ('carry', 'ball2', 'right'), ('free', 'left')
    goals: (positive_goals, negative_goals), each a frozenset of tuples
    Returns: non-negative int or float heuristic estimate.
    """
    return max(len(goals[0]), 0) * 2 + len(goals[1]) - len(state)