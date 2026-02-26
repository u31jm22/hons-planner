def h(state, goals):
    """
    Domain-specific heuristic for the logistics domain.
    state: frozenset of tuples like ('at-robby', 'rooma'), ('at', 'ball1', 'rooma'), ('carry', 'ball2', 'right'), ('free', 'left')
    goals: (positive_goals, negative_goals), each a frozenset of tuples
    Returns: non-negative int or float heuristic estimate.
    """

    def estimate_package_cost(package, loc, vehicle, goal_loc, goal_vehicle):
        cost = 0
        if loc == goal_loc:
            if vehicle == goal_vehicle:
                cost += 1  # Unload
            else:
                cost += 2  # Load + Unload
        else:
            cost += 3  # Load + Drive/Fly + Unload
        return cost

    total_cost = 0
    for package, loc in state:
        if ('at', package, loc) in goals[0]:  # Package already at the goal
            continue

        min_cost = float('inf')
        for goal_loc in [goal[1] for goal in goals[0] if goal[0] == 'at' and goal[1] != loc]:
            for goal_vehicle in [goal[1] for goal in goals[0] if goal[0] == 'in' and goal[2] == package]:
                cost = estimate_package_cost(package, loc, vehicle, goal_loc, goal_vehicle)
                if cost < min_cost:
                    min_cost = cost
        total_cost += min_cost

    return total_cost