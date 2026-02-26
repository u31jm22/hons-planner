def h(state, goals):
    """
    Domain-specific heuristic for Depot planning domain.
    state: frozenset of tuples like ('at-robby', 'rooma'), ('at', 'ball1', 'rooma'), ('carry', 'ball2', 'right'), ('free', 'left')
    goals: (positive_goals, negative_goals), each a frozenset of tuples
    Returns: non-negative int or float heuristic estimate.
    """
    lifts_needed = 0
    loads_needed = 0
    unloads_needed = 0
    drives_needed = 0

    for goal in goals[0]:
        if ('on', goal[1], goal[2]) not in state:
            lifts_needed += 1
            loads_needed += 1
            unloads_needed += 1
            drives_needed += 2

    for goal in goals[1]:
        if ('on', goal[1], goal[2]) in state:
            lifts_needed += 1
            unloads_needed += 1
            drives_needed += 2

    return lifts_needed + loads_needed + unloads_needed + drives_needed