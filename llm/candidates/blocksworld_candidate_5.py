def h(state, goals):
    """
    Domain-specific heuristic for the BLOCKS world planning domain.
    state: frozenset of tuples like ('on', 'blocka', 'blockb'), ('ontable', 'blockc'), ('clear', 'blockd'), ('holding', 'blocke')
    goals: (positive_goals, negative_goals), each a frozenset of tuples
    Returns: non-negative int or float heuristic estimate.
    """
    def is_goal_achieved(block, target):
        return any((('on', block, target) in goals[0], ('ontable', block) in goals[0], ('clear', block) in goals[0]))

    def blocks_to_move(block):
        if is_goal_achieved(block, 'table'):
            return 0

        on_block = [b for b in state if b[0] == 'on' and b[1] == block]
        if on_block:
            return 1 + max([blocks_to_move(b[2]) for b in on_block])
        else:
            return float('inf')

    total_cost = sum(blocks_to_move(block[1]) for block in state if block[0] == 'on')
    return total_cost