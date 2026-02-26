def h(state, goals):
    """
    Domain-specific heuristic for this planning domain.
    state: frozenset of tuples like ('at-robby', 'rooma')
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

    # Extract balls currently carried and by which gripper
    carried = {}  # ball -> gripper
    for atom in state:
        if atom[0] == 'carry':
            carried[atom[1]] = atom[2]

    # Extract balls locations on floor
    ball_locs = {}  # ball -> room
    for atom in state:
        if atom[0] == 'at':
            ball_locs[atom[1]] = atom[2]

    # Extract goal ball locations (positive goals of form ('at', ball, room))
    goal_ball_locs = {}
    for g in positive_goals:
        if g[0] == 'at' and len(g) == 3:
            goal_ball_locs[g[1]] = g[2]

    # Rooms in problem (from state and goals)
    rooms = set()
    for atom in state:
        if atom[0] == 'room':
            rooms.add(atom[1])
    for g in positive_goals:
        if g[0] == 'room':
            rooms.add(g[1])
    for g in negative_goals:
        if g[0] == 'room':
            rooms.add(g[1])
    # fallback if no explicit room predicates: gather from at-robby and balls
    if not rooms:
        if robby_loc is not None:
            rooms.add(robby_loc)
        rooms.update(ball_locs.values())
        rooms.update(goal_ball_locs.values())

    # Since domain has only two rooms (rooma, roomb), define distance between rooms:
    # 0 if same room, 1 if different room
    def room_dist(r1, r2):
        return 0 if r1 == r2 else 1

    # Group balls by (source_room, goal_room) and carried status
    #