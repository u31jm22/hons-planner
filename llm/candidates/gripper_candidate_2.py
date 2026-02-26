def h(state, goals):
    """
    Domain-specific heuristic for this planning domain.
    state: frozenset of tuples like ('at-robby', 'rooma'), ('at', 'ball1', 'rooma'), ('carry', 'ball2', 'right'), ('free', 'left')
    goals: (positive_goals, negative_goals), each a frozenset of tuples
    Returns: non-negative int or float heuristic estimate.
    """
    positive_goals, negative_goals = goals

    # Extract robot current room
    robot_room = None
    for atom in state:
        if atom[0] == 'at-robby':
            robot_room = atom[1]
            break
    if robot_room is None:
        # Should not happen, but heuristic must be total
        return 0

    # Extract all rooms from state and goals (to define room graph)
    rooms = set()
    for atom in state:
        if atom[0] == 'at-robby':
            rooms.add(atom[1])
        elif atom[0] == 'at':
            rooms.add(atom[2])
        elif atom[0] == 'carry':
            # carry does not give room info
            pass
    for g in positive_goals:
        if g[0] == 'at-robby':
            rooms.add(g[1])
        elif g[0] == 'at':
            rooms.add(g[2])

    # In gripper domain, rooms are fully connected, distance between any two distinct rooms is 1 move
    # Distance function between rooms:
    def room_dist(r1, r2):
        return 0 if r1 == r2 else 1

    # Map balls to their current location or carried gripper
    ball_locations = {}
    for atom in state:
        if atom[0] == 'at':
            ball_locations[atom[1]] = ('floor', atom[2])
        elif atom[0] == 'carry':
            ball_locations[atom[1]] = ('carry', atom[2])

    # Map balls to their goal location (only consider positive goals of form ('at', ball, room))
    goal_locations = {}
    for g in positive_goals:
        if g[0] == 'at':
            goal_locations[g[1]] = g[2]

    # Balls that have a goal location but are not yet there
    balls_to_move = []