def h(state, goals):
    """
    Domain-specific heuristic for this planning domain.
    state: frozenset of tuples like ('at-robby', 'rooma'), ('at', 'ball1', 'rooma'), ('carry', 'ball2', 'right'), ('free', 'left')
    goals: (positive_goals, negative_goals), each a frozenset of tuples
    Returns: non-negative int or float heuristic estimate.
    """
    # Crates that are not yet on their goal surface or at their goal location
    remaining_crates = set()
    for crate in state:
        if ('on', crate, _) not in goals[0] or ('in', crate, _) not in goals[0]:
            remaining_crates.add(crate)

    # Heuristic estimate based on lifts, drops, loads, and drives
    heuristic_cost = 0
    for crate in remaining_crates:
        if ('on', crate, _) in goals[0]:  # Crate is already at its goal surface
            heuristic_cost += 1  # Cost of 1 drop
        elif ('at', 'truck', _) in state:  # If truck is available
            heuristic_cost += 3  # Cost of 1 lift, some drives, and 1 drop
        else:
            heuristic_cost += 2  # Cost of 1 lift and 1 drop

    return heuristic_cost