def h(state, goals):
    robot_at_room = next(obj[1] for obj in state if obj[0] == 'at-robby')
    ball_locations = {obj[1]: obj[2] for obj in state if obj[0] == 'at'}
    carried_balls = {obj[1]: obj[2] for obj in state if obj[0] == 'carry'}

    remaining_cost = 0
    for goal in goals[0]:
        ball = goal[1]
        goal_room = goal[2]
        if ball in ball_locations and ball_locations[ball] != goal_room:
            if ball not in carried_balls:
                remaining_cost += 2  # move + pick
            remaining_cost += 2  # move + drop
            remaining_cost += abs(ord(robot_at_room) - ord(ball_locations[ball]))  # room-to-room move

    return remaining_cost