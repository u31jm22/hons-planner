def h(state, goals):
    positive_goals, negative_goals = goals
    balls_to_pick = {g[1] for g in positive_goals if g[0] == 'at' and g[1] not in state}
    balls_to_drop = {g[1] for g in positive_goals if g[0] == 'at' and g[1] in state}
    grippers = {g[1] for g in state if g[0] == 'free'}
    robot_location = next((r[1] for r in state if r[0] == 'at-robby'), None)

    trips_needed = 0
    if balls_to_pick:
        for ball in balls_to_pick:
            ball_location = next((r[1] for r in state if r[0] == 'at' and r[1] == ball), None)
            if ball_location and ball_location != robot_location:
                trips_needed += 1
        trips_needed += (len(balls_to_pick) + 1) // 2  # Batch pickups

    if balls_to_drop:
        for ball in balls_to_drop:
            if ball not in state:
                trips_needed += 1
        trips_needed += (len(balls_to_drop) + 1) // 2  # Batch drops

    return trips_needed