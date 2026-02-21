def h(state, goals):
    """
    Domain-specific heuristic for this planning domain.
    state: frozenset of tuples like ('at-robby', 'rooma'), ('at', 'ball1', 'rooma'), ('carry', 'ball2', 'right'), ('free', 'left')
    goals: (positive_goals, negative_goals), each a frozenset of tuples
    Returns: non-negative int or float heuristic estimate.
    """
    num_moves = 0
    for goal in goals[0]:
        if ('on', goal, 'table') not in state:
            num_moves += 1
    for block in {atom[1] for atom in state if atom[0] == 'on'}:
        if ('on', block, 'table') not in goals[0]:
            num_moves += 1
    return num_moves