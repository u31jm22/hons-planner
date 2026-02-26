def h(state, goals):
    """
    Domain-specific heuristic for the logistics domain.
    state: frozenset of tuples like ('at', obj, loc), ('in', pkg, vehicle)
    goals: (positive_goals, negative_goals), each a frozenset of tuples
    Returns: non-negative int or float heuristic estimate.
    """
    # Extract positive goals
    positive_goals, _ = goals

    # Initialize heuristic cost
    cost = 0

    # Initialize sets to keep track of packages at their goal locations and in the correct vehicle but not yet unloaded
    packages_at_goal = set()
    packages_in_correct_vehicle = set()

    # Iterate over state to populate the sets
    for atom in state:
        if atom[0] == 'at' and atom in positive_goals:
            packages_at_goal.add(atom[1])
        if atom[0] == 'in' and atom[1] in positive_goals and ('at', atom[2], atom[1]) in state:
            packages_in_correct_vehicle.add(atom[1])

    # Count the number of loads/unloads and movements needed to bring packages closer to their goals
    for atom in state:
        if atom[0] == 'at' and atom[1] not in packages_at_goal:
            if ('in', atom[1], _) not in state:
                cost += 1  # Load the package
            if ('in', atom[1], _) in state and atom[1] not in packages_in_correct_vehicle:
                cost += 1  # Unload the package
            # Additional cost for moving the vehicle/plane
            if atom[2] != goals[0][goals[0].index(('at', atom[1], _))][2]:
                cost += 1

    return cost