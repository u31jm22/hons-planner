def h(state, goals):
    """
    Domain-specific heuristic for this planning domain.
    state: frozenset of tuples like ('at', 'ball1', 'rooma')
    goals: (positive_goals, negative_goals), each a frozenset of tuples
    Returns: non-negative int or float heuristic estimate.
    """
    positive_goals, negative_goals = goals
    heuristic_cost = 0

    # Count blocks that are not in their goal positions
    for g in positive_goals:
        if g[0] == 'on':
            block, target = g[1], g[2]
            if not any((block == b and target == t) for b, t in state if b == 'on'):
                heuristic_cost += 1  # Needs to be moved to the target position
        elif g[0] == 'ontable':
            block = g[1]
            if not any((block == b) for b in state if b == 'ontable'):
                heuristic_cost += 1  # Needs to be placed on the table
        elif g[0] == 'clear':
            block = g[1]
            if not any((block == b) for b in state if b == 'clear'):
                heuristic_cost += 1  # Needs to be made clear

    # Estimate the number of actions needed to achieve the remaining goals
    # Each block requires at least one action to pick up and one to place down
    heuristic_cost *= 2  # Each block typically requires two actions (pick and place)

    return heuristic_cost