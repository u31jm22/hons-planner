def h(state, goals):
    """
    Domain-specific heuristic for the Gripper domain (manual Corrêa-style LLM design).
    state: frozenset of ground predicates.
    goals: (positive_goals, negative_goals), each a frozenset of ground predicates.
    Returns: non-negative int or float.
    """
    positive_goals, negative_goals = goals

    # Extract goal room for each ball: goal_room[ball] = room
    goal_room = {}
    for pred in positive_goals:
        # ('at', ball, room) in your state encoding
        if len(pred) == 3 and pred[0] in ("at", "at-ball", "at_ball"):
            _, ball, room = pred
            goal_room[ball] = room

    if not goal_room:
        return 0.0

    # Index current state
    ball_at = {}     # ball -> room
    carry = {}       # ball -> gripper
    at_robby = None  # room where the robot is

    for pred in state:
        if not pred:
            continue
        if pred[0] in ("at-robby", "at_robby") and len(pred) == 2:
            # ('at-robby', room)
            _, room = pred
            at_robby = room
        elif pred[0] in ("at", "at-ball", "at_ball") and len(pred) == 3:
            _, ball, room = pred
            ball_at[ball] = room
        elif pred[0] == "carry" and len(pred) == 3:
            # ('carry', ball, gripper)
            _, ball, grip = pred
            carry[ball] = grip

    heuristic = 0.0

    def room_distance(r1, r2):
        if r1 == r2:
            return 0
        # Two-room Gripper: treat different rooms as distance 1
        return 1

    for ball, g_room in goal_room.items():
        # Determine where the ball effectively is
        if ball in carry:
            # Ball is being carried: its "room" is the robot's room
            cur_room = at_robby
        else:
            cur_room = ball_at.get(ball)

        if cur_room is None:
            # Unknown; pessimistic default
            heuristic += 3.0
            continue

        if cur_room == g_room:
            # Already in goal room; may still need to be dropped if carried
            if ball in carry:
                heuristic += 1.0  # estimate a drop
            continue

        # Ball not yet in goal room:
        # Rough model: move robot to ball room (if needed), pick up, move to goal room, drop.
        d = room_distance(cur_room, g_room)
        # Move robot to ball (<=1), pick up (1), move to goal room (d), drop (1)
        cost = 1.0 + 1.0 + d + 1.0

        heuristic += cost

    if heuristic < 0:
        return 0.0
    return heuristic
