def h(state, goals):
    """
    Domain-specific heuristic for the Depot planning domain.
    state: frozenset of ground atoms tuples like ('at-robby', 'rooma'), ('at', 'ball1', 'rooma'), ('carry', 'ball2', 'right'), ('free', 'left')
    goals: (positive_goals, negative_goals), each a frozenset of tuples
    Returns: non-negative int or float heuristic estimate.
    """

    def estimate_crate_operations(crate_state, goal_surface):
        if crate_state == goal_surface:
            return 0
        elif crate_state[0] == goal_surface[0]:
            return 2  # lift + drop within the same place
        else:
            return 4  # lift + load + drive + unload + drop

    heuristic_cost = 0

    for goal in goals[0]:
        if ('on', goal[1], goal[2]) not in state:
            for obj in state:
                if obj[0] == 'on' and obj[2] == goal[2]:
                    heuristic_cost += 1  # Penalize crates buried under other crates
            heuristic_cost += estimate_crate_operations(('on', goal[1], goal[2]), goal)

    for goal in goals[1]:
        if goal not in state:
            heuristic_cost += 1

    return heuristic_cost