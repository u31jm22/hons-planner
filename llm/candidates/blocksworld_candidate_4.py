def h(state, goals):
    """
    Domain-specific heuristic for the BLOCKS domain.
    state: frozenset of tuples like ('on', 'blocka', 'blockb'), ('ontable', 'blockc'), ('clear', 'blockd'), ('holding', 'blocke')
    goals: (positive_goals, negative_goals), each a frozenset of tuples
    Returns: non-negative int or float heuristic estimate.
    """
    # Count blocks not in goal positions
    blocks_not_in_goal = sum(1 for block in state if ('on', block, _) not in goals[0] and ('ontable', block) not in goals[0])

    # Estimate number of moves to unstack/move blocks
    moves_estimate = 2 * blocks_not_in_goal

    return moves_estimate