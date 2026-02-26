def h(state, goals):
    """
    Domain-specific heuristic for Gripper planning domain.
    state: frozenset of tuples like ('at-robby', 'rooma'), ('at', 'ball1', 'rooma'), ('carry', 'ball2', 'right'), ('free', 'left')
    goals: (positive_goals, negative_goals), each a frozenset of tuples
    Returns: non-negative int or float heuristic estimate.
    """
    at_robby_goals = {g for g in goals[0] if g[0] == 'at-robby'}
    carry_goals = {g for g in goals[0] if g[0] == 'carry'}
    at_goals = {g for g in goals[0] if g[0] == 'at'}

    at_robby_state = {s for s in state if s[0] == 'at-robby'}
    carry_state = {s for s in state if s[0] == 'carry'}
    at_state = {s for s in state if s[0] == 'at'}

    h_estimate = len(at_robby_goals - at_robby_state) + len(carry_goals - carry_state)

    for goal in at_goals:
        ball, room = goal[1], goal[2]
        if ('at', ball, room) not in at_state and ('carry', ball, _) not in carry_state:
            h_estimate += 1

    return h_estimate