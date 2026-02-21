def h(state, goals):
    """
    Domain-specific heuristic for the logistics planning domain.
    state: frozenset of tuples like ('at-robby', 'rooma'), ('at', 'ball1', 'rooma'), ('carry', 'ball2', 'right'), ('free', 'left')
    goals: (positive_goals, negative_goals), each a frozenset of tuples
    Returns: non-negative int or float heuristic estimate.
    """

    def pick_drop_count(state, goals):
        pick_count = 0
        drop_count = 0

        for goal in goals:
            if ('in', goal[0], goal[1]) in state:
                pick_count += 1
            else:
                drop_count += 1

        return pick_count + drop_count

    def move_count(state, goals):
        move_count = 0

        for goal in goals:
            if ('at', goal[0], goal[1]) not in state:
                move_count += 1

        return move_count

    return max(pick_drop_count(state, goals), move_count(state, goals))