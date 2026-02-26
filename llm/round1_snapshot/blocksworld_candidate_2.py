def h(state, goals):
    """
    Domain-specific heuristic for the Blocks World planning domain.
    state: frozenset of tuples like ('on', 'blocka', 'blockb'), ('ontable', 'blockc'), ('clear', 'blocka'), ('holding', 'blockd')
    goals: (positive_goals, negative_goals), each a frozenset of tuples
    Returns: non-negative int or float heuristic estimate.
    """
    def count_moves_to_clear(block, goals):
        if ('ontable', block) in goals:
            return 1
        elif any(('clear', b) in goals for b in [x for x, y in goals if y == block]):
            return 1 + max(count_moves_to_clear(x, goals) for x, y in goals if y == block)
        else:
            return 0

    remaining_moves = sum(count_moves_to_clear(b, goals) for b in {x for x, _ in goals if x in [b for b, _ in state]})

    return remaining_moves