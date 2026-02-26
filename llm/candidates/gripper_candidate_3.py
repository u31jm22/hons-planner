def h(state, goals):
    positive_goals, negative_goals = goals
    robot_room = next((atom[1] for atom in state if atom[0] == 'at-robby'), None)
    ball_locations = {}
    carried_balls = {}
    free_grippers = 0
    for atom in state:
        if atom[0] == 'at':
            ball_locations[atom[1]] = atom[2]
        elif atom[0] == 'carry':
            carried_balls[atom[1]] = atom[2]
        elif atom[0] == 'free':
            free_grippers += 1
    goal_targets = {g[1]: g[2] for g in positive_goals if g[0] == 'at'}
    total_cost = 0.0
    for ball, target_room in goal_targets.items():
        if ball in carried_balls:
            # Ball is carried by a gripper
            # If robot not at target room, need to move there before dropping
            if robot_room != target_room:
                total_cost += 1  # move to target room
            total_cost += 1  # drop ball
        else:
            # Ball is on the floor somewhere
            current_room = ball_locations.get(ball)
            if current_room == target_room:
                # Already at goal room on floor, no cost
                continue
            # Need to move to ball's room if not already there
            if robot_room != current_room:
                total_cost += 1  # move to ball's room
            total_cost += 1  # pick ball
            if current_room != target_room:
                total_cost += 1  # move to target room
            total_cost += 1  # drop ball
    # Discount heuristic if multiple grippers free to simulate parallelism
    if free_grippers > 1 and total_cost > 0:
        total_cost -= 0.5 * (free_grippers - 1)
    return max(0.0, total_cost)