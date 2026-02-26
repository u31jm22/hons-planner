def h(state, goals):
    positive_goals, negative_goals = goals
    robot_room = None
    ball_pos = {}
    carried = {}
    free_grippers = 0
    for atom in state:
        if atom[0] == 'at-robby':
            robot_room = atom[1]
        elif atom[0] == 'at':
            ball_pos[atom[1]] = atom[2]
        elif atom[0] == 'carry':
            carried[atom[1]] = atom[2]
        elif atom[0] == 'free':
            free_grippers += 1
    goal_targets = {g[1]: g[2] for g in positive_goals if g[0] == 'at'}
    total_cost = 0
    for ball, target_room in goal_targets.items():
        if ball in carried:
            # Ball is carried in some gripper
            if robot_room == target_room:
                # Already at goal room, just drop
                total_cost += 1
            else:
                # Need to move to goal room and drop
                total_cost += 1 + 1
        else:
            current_room = ball_pos.get(ball)
            if current_room == target_room:
                # Ball already at goal room on floor
                continue
            # Need to move to ball if not there, pick, move to goal, drop
            move_to_ball = 0 if robot_room == current_room else 1
            total_cost += move_to_ball + 1 + 1 + 1
    # Discount for multiple free grippers to reflect parallelism
    if free_grippers >= 2 and total_cost > 0:
        total_cost -= 1
    return float(max(0, total_cost))