def h(state, goals):
    """
    Domain-specific heuristic for Depot planning domain.
    state: frozenset of ground atoms tuples like ('at-robby', 'rooma'), ('at', 'ball1', 'rooma'), ('carry', 'ball2', 'right'), ('free', 'left')
    goals: (positive_goals, negative_goals), each a frozenset of tuples
    Returns: non-negative int or float heuristic estimate.
    """
    num_remaining_steps = 0

    for goal in goals[0]:
        if ('on', goal[1], goal[2]) not in state:
            num_remaining_steps += 2  # 1 lift + 1 drop

    for goal in goals[1]:
        if ('on', goal[1], goal[2]) in state:
            num_remaining_steps += 2  # 1 lift + 1 drop
        elif ('in', goal[1], goal[2]) in state:
            num_remaining_steps += 5  # 1 lift + 1 load + some drives + 1 unload + 1 drop
        else:
            num_remaining_steps += 10  # Penalize crates at completely wrong locations

    return num_remaining_steps