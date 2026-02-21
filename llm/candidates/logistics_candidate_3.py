def h(state, goals):
    """
    Domain-specific heuristic for the logistics domain.
    state: frozenset of tuples like ('at', 'robby', 'rooma'), ('at', 'ball1', 'rooma'), ('in', 'ball2', 'right'), ('free', 'left')
    goals: (positive_goals, negative_goals), each a frozenset of tuples
    Returns: non-negative int or float heuristic estimate.
    """

    def get_objects(predicate):
        return {obj for pred, obj, _ in state if pred == predicate}

    def get_predicate_objects(predicate, obj):
        return {loc for pred, obj_name, loc in state if pred == predicate and obj_name == obj}

    def get_object_locations(obj):
        return {loc for _, obj_name, loc in state if obj_name == obj}

    def get_vehicle_carrying_count():
        return sum(1 for obj in get_objects('in') if obj.startswith('ball'))

    def get_vehicle_locations():
        return get_object_locations('truck') | get_object_locations('airplane')

    def get_package_locations():
        return get_object_locations('package')

    def is_goal_satisfied(predicate):
        return any(item in goals[0] for item in predicate) or any(item in goals[1] for item in predicate)

    # Heuristic logic starts here
    heuristic_cost = 0

    if not is_goal_satisfied(('in', 'package', 'truck')) and get_vehicle_carrying_count() > 0:
        heuristic_cost += 1

    if not is_goal_satisfied(('in', 'package', 'airplane')) and get_vehicle_carrying_count() > 0:
        heuristic_cost += 1

    if not is_goal_satisfied(('at', 'package', 'loc')):
        heuristic_cost += len(get_package_locations())

    if not is_goal_satisfied(('at', 'truck', 'loc')):
        heuristic_cost += len(get_vehicle_locations())

    if not is_goal_satisfied(('at', 'airplane', 'loc')):
        heuristic_cost += len(get_vehicle_locations())

    return heuristic_cost