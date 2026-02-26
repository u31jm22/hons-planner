def h(state, goals):
    """
    Domain-specific heuristic for logistics planning domain.
    state: frozenset of tuples like ('at', obj, loc), ('in', pkg, vehicle)
    goals: (positive_goals, negative_goals), each a frozenset of tuples
    Returns: non-negative int or float heuristic estimate.
    """
    def is_goal_met(atom):
        return atom in goals[0] or atom in goals[1]

    def distance_to_goal(obj, loc):
        if ('at', obj, loc) in goals[0]:
            return 0
        elif ('at', obj, loc) in state:
            return 1
        else:
            min_distance = float('inf')
            for goal_loc in [g[2] for g in goals[0] if g[1] == obj]:
                if ('at', obj, goal_loc) in state:
                    continue
                locs_to_goal = [g[2] for g in state if g[1] == loc and g[2] in [goal_loc, loc]]
                distance = len(set(locs_to_goal))
                min_distance = min(min_distance, distance)
            return min_distance

    total_cost = 0
    for atom in state:
        if atom[0] == 'in':
            pkg, vehicle = atom[1], atom[2]
            if ('unload', pkg, vehicle) not in state and not is_goal_met(('at', pkg, vehicle)):
                total_cost += 2  # load + unload
                total_cost += distance_to_goal(pkg, vehicle)

    return total_cost