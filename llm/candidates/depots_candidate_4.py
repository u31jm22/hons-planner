def h(state, goals):
    positive_goals, negative_goals = goals
    # Extract relevant predicates from state
    at_robby = None
    at = {}
    carry = set()
    free = set()
    for atom in state:
        if atom[0] == 'at-robby':
            at_robby = atom[1]
        elif atom[0] == 'at' and len(atom) == 3:
            at[atom[1]] = atom[2]
        elif atom[0] == 'carry':
            carry.add(atom[1])
        elif atom[0] == 'free':
            free.add(atom[1])
    # Count how many balls need to be moved to their goal locations
    balls_to_move = 0
    for g in positive_goals:
        if g[0] == 'at' and len(g) == 3:
            ball, goal_room = g[1], g[2]
            current_room = at.get(ball)
            if current_room != goal_room:
                balls_to_move += 1
    # Count how many balls are currently carried but should not be
    carry_wrong = 0
    for ball in carry:
        # If ball is carried but its goal is to be at some room, count as needing drop
        goal_rooms = [g[2] for g in positive_goals if g[0] == 'at' and g[1] == ball]
        if goal_rooms and at.get(ball) != goal_rooms[0]:
            carry_wrong += 1
    # Estimate moves: each ball to move requires at least one pick and one drop
    # Also estimate robby moves: assume robby must move to ball location and goal location
    # Approximate robby moves as number of balls to move times 2 (go to ball and go to goal)
    robby_moves = balls_to_move * 2
    # If robby is not free, add penalty for freeing robby (assuming one free action)
    free_penalty = 0 if 'robby' in free else 1
    # Heuristic is sum of pick/drop actions plus robby moves plus free penalty
    heuristic = balls_to_move * 2 + robby_moves + carry_wrong + free_penalty
    return heuristic