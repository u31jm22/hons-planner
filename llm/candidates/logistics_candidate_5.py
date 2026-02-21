def h(state, goals):
    """
    Domain-specific heuristic for the logistics domain.
    state: frozenset of tuples like ('at-robby', 'rooma'), ('at', 'ball1', 'rooma'), ('carry', 'ball2', 'right'), ('free', 'left')
    goals: (positive_goals, negative_goals), each a frozenset of tuples
    Returns: non-negative int or float heuristic estimate.
    """
    # Heuristic function based on the number of unsatisfied positive goals
    positive_goals, _ = goals
    unsatisfied_goals = sum(1 for goal in positive_goals if goal not in state)
    return unsatisfied_goals