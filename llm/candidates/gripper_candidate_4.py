def h(state, goals):
    """
    Domain-specific heuristic for this planning domain.
    state: frozenset of tuples like ('at-robby', 'rooma'), ('at', 'ball1', 'rooma'), ('carry', 'ball2', 'right'), ('free', 'left')
    goals: (positive_goals, negative_goals), each a frozenset of tuples
    Returns: non-negative int or float heuristic estimate.
    """
    positive_goals, negative_goals = goals

    # Extract robot current room
    robby_room = None
    for atom in state:
        if atom[0] == 'at-robby':
            robby_room = atom[1]
            break
    if robby_room is None:
        # no robot location known, heuristic fallback
        return 0

    # Extract balls currently carried and by which gripper
    carried_balls = {}
    for atom in state:
        if atom[0] == 'carry':
            ball, gripper = atom[1], atom[2]
            carried_balls[ball] = gripper

    # Extract balls current location (only those on floor)
    ball_locations = {}
    for atom in state:
        if atom[0] == 'at':
            ball, room = atom[1], atom[2]
            ball_locations[ball] = room

    # Extract goal ball locations (only positive goals of form ('at', ball, room))
    goal_ball_locations = {}
    for atom in positive_goals:
        if atom[0] == 'at':
            ball, room = atom[1], atom[2]
            goal_ball_locations[ball] = room

    # Rooms in domain (from state and goals)
    rooms = set()
    for atom in state:
        if atom[0] == 'at-robby':
            rooms.add(atom[1])
        elif atom[0] == 'at':
            rooms.add(atom[2])
        elif atom[0] == 'carry':
            pass
        elif atom[0] == 'free':
            pass
    for atom in positive_goals:
        if atom[0] == 'at':
            rooms.add(atom[2])
    for atom in negative_goals:
        if atom[0] == 'at':
            rooms.add(atom[2])

    # Since domain has only two rooms, define a simple distance function
    # distance between rooms: