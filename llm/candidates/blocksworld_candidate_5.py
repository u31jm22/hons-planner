def h(state, goals):
    """
    Domain-specific heuristic for the BLOCKS world planning domain.
    state: frozenset of tuples like ('on', 'block1', 'block2'), ('ontable', 'block3'), ('clear', 'block4'), ('holding', 'block5'), ('handempty',)
    goals: (positive_goals, negative_goals), each a frozenset of tuples
    Returns: non-negative int or float heuristic estimate.
    """

    # Count the number of blocks not in their goal positions
    blocks_not_in_goal = 0
    for block in state:
        if block[0] == 'on' and block[1] != block[2]:
            blocks_not_in_goal += 1

    # Estimate the remaining number of moves needed to unstack/move blocks
    remaining_moves = 0
    for block in state:
        if block[0] == 'on':
            remaining_moves += 1

    return max(blocks_not_in_goal, remaining_moves)