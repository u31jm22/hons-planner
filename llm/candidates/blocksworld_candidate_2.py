def h(state, goals):
    """
    Domain-specific heuristic for this planning domain.
    state: frozenset of tuples like ('at', 'ball1', 'rooma')
    goals: (positive_goals, negative_goals), each a frozenset of tuples
    Returns: non-negative int or float heuristic estimate.
    """
    positive_goals, negative_goals = goals
    heuristic = 0

    for g in positive_goals:
        if g[0] == 'on':
            block, surface = g[1], g[2]
            if not any((block == b and surface == s) for b, s in state if b == block and ('on', block, surface) in state):
                heuristic += 1  # Block is not on the correct surface
                if not any(('clear', surface) in state for b in state if ('on', block, b) in state):
                    heuristic += 1  # Surface is not clear
        elif g[0] == 'ontable':
            block = g[1]
            if not any(('ontable', block) in state):
                heuristic += 1  # Block is not on the table
        elif g[0] == 'clear':
            block = g[1]
            if not any(('clear', block) in state):
                heuristic += 1  # Block is not clear

    for g in negative_goals:
        if g[0] == 'on':
            block, surface = g[1], g[2]
            if any((block == b and surface == s) for b, s in state if b == block and ('on', block, surface) in state):
                heuristic += 1  # Block is incorrectly placed
        elif g[0] == 'ontable':
            block = g[1]
            if any(('ontable', block) in state):
                heuristic += 1  # Block should not be on the table
        elif g[0] == 'clear':
            block = g[1]
            if any(('clear', block) in state):
                heuristic += 1  # Block should not be clear

    return heuristic