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
    carried = {}  # ball -> gripper
    for atom in state:
        if atom[0] == 'carry':
            carried[atom[1]] = atom[2]

    # Extract balls locations (only those on floor)
    ball_locs = {}  # ball -> room
    for atom in state:
        if atom[0] == 'at':
            ball_locs[atom[1]] = atom[2]

    # Extract goal ball locations (only positive goals of form ('at', ball, room))
    goal_ball_locs = {}
    for g in positive_goals:
        if g[0] == 'at' and len(g) == 3:
            goal_ball_locs[g[1]] = g[2]

    # Rooms in domain (from state and goals)
    rooms = set()
    for atom in state:
        if atom[0] == 'at-robby':
            rooms.add(atom[1])
        elif atom[0] == 'at' and len(atom) == 3:
            rooms.add(atom[2])
        elif atom[0] == 'carry':
            pass
    for g in positive_goals:
        if g[0] == 'at' and len(g) == 3:
            rooms.add(g[2])
    for g in negative_goals:
        if g[0] == 'at' and len(g) == 3:
            rooms.add(g[2])

    # Since domain has only two rooms, define distance between rooms as 0 if same, else 1
    def room_dist(r1, r2):
        return 0 if r1 == r2 else 1

    # For each ball that is not at its goal location, estimate cost
    # Balls can be:
    # -