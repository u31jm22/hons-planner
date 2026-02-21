def h(state, goals):
    """
    Domain-specific heuristic for this planning domain.
    state: frozenset of tuples like ('at', 'ball1', 'rooma')
    goals: (positive_goals, negative_goals), each a frozenset of tuples
    Returns: non-negative int or float heuristic estimate.
    """
    positive_goals, negative_goals = goals
    carried_balls = {obj for obj in state if obj[0] == 'carry'}
    at_balls = {obj for obj in state if obj[0] == 'at'}
    at_robby = next((r for r in state if r[0] == 'at-robby'), None)

    heuristic_cost = 0

    for goal in positive_goals:
        if goal[0] == 'at':
            ball, room = goal[1], goal[2]
            if (ball, room) not in at_balls:
                if carried_balls:
                    heuristic_cost += 1  # Need to drop a carried ball
                else:
                    heuristic_cost += 2  # Need to pick up the ball and move to the room
        elif goal[0] == 'free':
            gripper = goal[1]
            if (gripper,) not in state:
                heuristic_cost += 1  # Need to drop a ball to free the gripper

    return heuristic_cost + len(carried_balls) + (1 if at_robby is None else 0)