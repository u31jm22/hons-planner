def h(state, goals):
    """
    Domain-specific heuristic for this planning domain.
    state: frozenset of tuples like ('at', 'ball1', 'rooma')
    goals: (positive_goals, negative_goals), each a frozenset of tuples
    Returns: non-negative int or float heuristic estimate.
    """
    positive_goals, negative_goals = goals
    remaining_picks = 0
    remaining_drops = 0
    room_locations = {}

    for g in positive_goals:
        if g[0] == 'at':
            ball = g[1]
            room = g[2]
            room_locations[ball] = room
            if ('at', ball, room) not in state:
                remaining_picks += 1
        elif g[0] == 'at-robby':
            goal_room = g[1]
            if ('at-robby', goal_room) not in state:
                remaining_moves = 1
            else:
                remaining_moves = 0

    for carry in state:
        if carry[0] == 'carry':
            ball = carry[1]
            if ball in room_locations:
                if room_locations[ball] != carry[2]:
                    remaining_drops += 1
                    remaining_moves += 1

    return remaining_picks + remaining_drops + remaining_moves