def h(state, goals):
    """
    Domain-specific heuristic for this planning domain.
    state: frozenset of tuples like ('at', 'ball1', 'rooma')
    goals: (positive_goals, negative_goals), each a frozenset of tuples
    Returns: non-negative int or float heuristic estimate.
    """
    positive_goals, negative_goals = goals
    remaining_moves = 0
    balls_to_pick = 0
    balls_to_drop = 0

    # Count balls that need to be picked
    for g in positive_goals:
        if g[0] == 'at' and g[1] in state:
            continue
        if g[0] == 'carry':
            balls_to_drop += 1
        elif g[0] == 'at' and g[1][0:4] == 'ball':
            balls_to_pick += 1

    # Calculate moves needed to pick up balls
    for ball in state:
        if ball[0] == 'at' and ball[1][0:4] == 'ball':
            remaining_moves += 1  # Move to the ball's location to pick it up

    # Count moves to drop balls
    for g in state:
        if g[0] == 'carry':
            remaining_moves += 1  # Move to the drop location

    return balls_to_pick + balls_to_drop + remaining_moves