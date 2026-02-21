def h(state, goals):
    """
    Domain-specific heuristic for this planning domain.
    state: frozenset of tuples like ('at', 'ball1', 'rooma')
    goals: (positive_goals, negative_goals), each a frozenset of tuples
    Returns: non-negative int or float heuristic estimate.
    """
    positive_goals, negative_goals = goals
    robot_room = next((r for r in state if r[0] == 'at-robby'), None)
    robot_room = robot_room[1] if robot_room else None

    remaining_moves = 0
    remaining_picks = 0
    remaining_drops = 0

    for goal in positive_goals:
        if goal[0] == 'at':
            ball, target_room = goal[1], goal[2]
            if not any((ball == b[1] and target_room == b[2]) for b in state if b[0] == 'at'):
                remaining_picks += 1
                if robot_room != target_room:
                    remaining_moves += 1
            elif any((ball == b[1] for b in state if b[0] == 'carry')):
                remaining_drops += 1
        elif goal[0] == 'carry':
            ball, gripper = goal[1], goal[2]
            if not any((ball == b[1] and gripper == b[2]) for b in state if b[0] == 'carry'):
                remaining_picks += 1

    return remaining_moves + remaining_picks + remaining_drops