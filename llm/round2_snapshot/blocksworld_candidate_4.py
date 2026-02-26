def h(state, goals):
    """
    Domain-specific heuristic for this planning domain.
    state: frozenset of tuples like ('at-robby', 'rooma'), ('at', 'ball1', 'rooma'), ('carry', 'ball2', 'right'), ('free', 'left')
    goals: (positive_goals, negative_goals), each a frozenset of tuples
    Returns: non-negative int or float heuristic estimate.
    """
    # Count the number of blocks that are not in their goal position or have the wrong block on top
    heuristic_cost = 0
    for block in {atom[1] for atom in state if atom[0] in ['on', 'clear']}:
        on_goal_block = any(('on', block, goal_block) in state for goal_block in {atom[1] for atom in goals[0] if atom[0] == 'on'})
        clear_above = all(('clear', other_block) in state for other_block in {atom[2] for atom in state if atom[0] == 'on' and atom[1] == block})
        if not on_goal_block or not clear_above:
            heuristic_cost += 1

    return heuristic_cost