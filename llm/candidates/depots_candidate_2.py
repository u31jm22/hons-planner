def h(state, goals):
    positive_goals, negative_goals = goals
    # Extract robot location
    robot_loc = None
    for atom in state:
        if atom[0] == 'at-robby':
            robot_loc = atom[1]
            break
    if robot_loc is None:
        # If robot location unknown, return a high heuristic
        return 1000

    # Extract locations of balls in state
    ball_locs = {}
    for atom in state:
        if atom[0] == 'at' and len(atom) == 3:
            ball_locs[atom[1]] = atom[2]

    # Extract goal locations for balls
    goal_ball_locs = {}
    for g in positive_goals:
        if g[0] == 'at' and len(g) == 3:
            goal_ball_locs[g[1]] = g[2]

    # Heuristic: sum over balls of
    # distance from robot to ball + distance from ball to goal location
    # distance is approximated as 1 if locations differ, 0 if same
    # plus 1 for each pick/drop action needed
    # Also add penalty for balls not at goal location

    def dist(loc1, loc2):
        return 0 if loc1 == loc2 else 1

    h_val = 0
    for ball, goal_loc in goal_ball_locs.items():
        current_loc = ball_locs.get(ball)
        if current_loc is None:
            # Ball location unknown, add penalty
            h_val += 3
            continue
        if current_loc != goal_loc:
            # Need to move robot to ball location
            h_val += dist(robot_loc, current_loc)
            # Pick ball
            h_val += 1
            # Move ball to goal location
            h_val += dist(current_loc, goal_loc)
            # Drop ball
            h_val += 1
        # else ball already at goal, no cost

    # Also consider negative goals: if any negative goal is true in state, add penalty
    for ng in negative_goals:
        if ng in state:
            h_val += 5

    return h_val