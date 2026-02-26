def h(state, goals):
    """
    Domain-specific heuristic for this planning domain.
    state: frozenset of tuples like ('at', 'ball1', 'rooma')
    goals: (positive_goals, negative_goals), each a frozenset of tuples
    Returns: non-negative int or float heuristic estimate.
    """
    positive_goals, negative_goals = goals

    # Extract robot location
    robby_loc = None
    for atom in state:
        if atom[0] == 'at-robby':
            robby_loc = atom[1]
            break

    # Extract balls currently carried and their grippers
    carried_balls = {}
    for atom in state:
        if atom[0] == 'carry':
            ball, gripper = atom[1], atom[2]
            carried_balls[ball] = gripper

    # Extract balls currently on floor and their locations
    balls_on_floor = {}
    for atom in state:
        if atom[0] == 'at':
            ball, room = atom[1], atom[2]
            balls_on_floor[ball] = room

    # Extract goal ball locations (only positive goals of form ('at', ball, room))
    goal_ball_locs = {}
    for g in positive_goals:
        if g[0] == 'at' and len(g) == 3:
            ball, room = g[1], g[2]
            goal_ball_locs[ball] = room

    # Rooms involved (from state and goals)
    rooms = set()
    for atom in state:
        if atom[0] == 'at-robby':
            rooms.add(atom[1])
        elif atom[0] == 'at' and len(atom) == 3:
            rooms.add(atom[2])
        elif atom[0] == 'carry' and len(atom) == 3:
            # carried balls have no room location
            pass
    for g in positive_goals:
        if g[0] == 'at' and len(g) == 3:
            rooms.add(g[2])

    # We know domain has exactly two rooms (rooma, roomb)
    # Define a simple room distance function: 0 if same room, else 1
    def room_dist(r1, r2):
        return 0 if r1 == r2 else 1

    # For each ball, estimate cost to