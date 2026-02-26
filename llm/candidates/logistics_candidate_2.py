def h(state, goals):
    """
    Domain-specific heuristic for the logistics domain.
    state: frozenset of tuples like ('at-robby', 'rooma'), ('at', 'ball1', 'rooma'), ('carry', 'ball2', 'right'), ('free', 'left')
    goals: (positive_goals, negative_goals), each a frozenset of tuples
    Returns: non-negative int or float heuristic estimate.
    """
    in_city_goals = {loc for pred in goals[0] if pred[0] == 'in-city' for loc in pred[1:]}
    at_goals = {pred[1] for pred in goals[0] if pred[0] == 'at'}

    total_cost = 0
    for pkg, veh in {(pred[1], pred[2]) for pred in state if pred[0] == 'in'}:
        if ('at', pkg, veh) in state:
            total_cost += 1
        elif ('at', pkg, place) in state and ('at', veh, place) in state and ('in-city', place, city) in state:
            if place in in_city_goals and place in at_goals:
                total_cost += 2
            elif place in in_city_goals:
                total_cost += 3
            else:
                total_cost += 4

    return total_cost