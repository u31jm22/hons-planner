def h(state, goals):
    """
    Domain-specific heuristic for the logistics planning domain.
    state: frozenset of tuples like ('at-robby', 'rooma'), ('at', 'ball1', 'rooma'), ('carry', 'ball2', 'right'), ('free', 'left')
    goals: (positive_goals, negative_goals), each a frozenset of tuples
    Returns: non-negative int or float heuristic estimate.
    """

    positive_goals, _ = goals

    # Define a heuristic value based on the number of positive goals not satisfied in the state
    heuristic = sum(1 for goal in positive_goals if goal not in state)

    return heuristic