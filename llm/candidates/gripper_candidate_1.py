def h(state, goals):
    positive_goals, negative_goals = goals
    robot_room = next((a[1] for a in state if a[0] == 'at-robby'), None)
    ball_pos = {}
    carried = {}
    free_grippers = 0
    for atom in state:
        if atom[0] == 'at':
            ball_pos[atom[1]] = atom[2]
        elif atom[0] == 'carry':
            carried[atom[1]] = atom[2]
        elif atom[0] == 'free':
            free_grippers += 1
    goal_targets = {g[1]: g[2] for g in positive_goals if g[0] == 'at'}
    cost = 0
    balls_to_move = []
    for ball, target in goal_targets.items():
        if ball in carried:
            # Ball is carried
            if robot_room == target:
                # Already at target room, just drop
                cost += 1
            else:
                # Need to move to target room and drop
                cost += 1 + 1
        else:
            cur_room = ball_pos.get(ball)
            if cur_room == target:
                # Already at target room on floor, no cost
                continue
            else:
                # Need to move to ball room if not there, pick, move to target, drop
                move_to_ball = 0 if robot_room == cur_room else 1
                cost += move_to_ball + 1 + 1 + 1
                balls_to_move.append(ball)
    # Batch discount: if multiple balls need moving and at least one gripper free, reduce cost
    if len(balls_to_move) > 1 and free_grippers > 0:
        cost -= min(free_grippers, len(balls_to_move))
    return float(max(0, cost))