def h(state, goals):
    """
    Domain-specific heuristic for the logistics domain.
    state: frozenset of tuples like ('at', obj, loc), ('in', pkg, vehicle)
    goals: (positive_goals, negative_goals), each a frozenset of tuples
    Returns: non-negative int or float heuristic estimate.
    """
    def is_goal_state(pkg, loc, goals):
        for goal in goals:
            if ('at', pkg, loc) in goal:
                return True
        return False

    def find_closest_vehicle(truck_locs, airplane_locs, loc):
        closest_truck = min(truck_locs, key=lambda x: abs(x - loc))
        closest_airplane = min(airplane_locs, key=lambda x: abs(x - loc))
        return closest_truck, closest_airplane

    def estimate_cost(pkg, pkg_loc, goals, truck_locs, airplane_locs):
        if is_goal_state(pkg, pkg_loc, goals):
            return 0

        truck_loc, airplane_loc = find_closest_vehicle(truck_locs, airplane_locs, pkg_loc)

        if ('truck', truck_loc, pkg_loc) in state or ('airplane', airplane_loc, pkg_loc) in state:
            return 2  # Load + Unload

        return 2 + abs(truck_loc - pkg_loc) + abs(airplane_loc - truck_loc)

    truck_locs = {loc for _, loc in state if 'truck' in _}
    airplane_locs = {loc for _, loc in state if 'airplane' in _}

    total_cost = 0
    for pkg, pkg_loc in {(obj, loc) for _, obj, loc in state if 'package' in _}:
        total_cost += estimate_cost(pkg, pkg_loc, goals[0], truck_locs, airplane_locs)

    return total_cost