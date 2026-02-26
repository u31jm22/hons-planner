def h(state, goals):
    positive_goals, negative_goals = goals
    robot_room = None
    ball_locations = {}
    carried_balls = {}
    free_grippers = 0
    for atom in state:
        if atom[0] == 'at-robby':
            robot_room = atom[1]
        elif atom[0] == 'at':
            ball_locations[atom[1]] = atom[2]
        elif atom[0] == 'carry':
            carried_balls[atom[1]] = atom[2]
        elif atom[0] == 'free':
            free_grippers += 1
    goal_positions = {}
    for g in positive_goals:
        if g[0] == 'at':
            goal_positions[g[1]] = g[2]
    total_cost = 0.0
    for ball, goal_room in goal_positions.items():
        if ball in carried_balls:
            # Ball is carried
            if robot_room == goal_room:
                # Already at goal room, just drop
                total_cost += 1
            else:
                # Need to move to goal room and drop
                total_cost += 2
        else:
            current_room = ball_locations.get(ball)
            if current_room == goal_room:
                # Ball already at goal room on floor
                continue
            # Ball on floor in some room
            # Move to ball if needed
            if robot_room != current_room:
                total_cost += 1
            # Pick ball
            total_cost += 1
            # Move to goal room
            if current_room != goal_room:
                total_cost += 1
            # Drop ball
            total_cost += 1
    # Discount for multiple free grippers (batching)
    if free_grippers > 1 and total_cost > 0:
        total_cost -= 0.5 * (free_grippers - 1)
        if total_cost < 0:
            total_cost = 0
    return total_cost