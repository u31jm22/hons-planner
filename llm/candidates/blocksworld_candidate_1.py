def h(state, goals):
    """
    Domain-specific heuristic for the BLOCKS domain.
    state: frozenset of tuples like ('on', 'blocka', 'blockb'), ('ontable', 'blockc'), ('clear', 'blockd'), ('holding', 'blocke'), ('handempty',)
    goals: (positive_goals, negative_goals), each a frozenset of tuples
    Returns: non-negative int or float heuristic estimate.
    """
    def is_goal_achieved(block, support, above_block):
        return ('on', block, support) in goals[0] and ('clear', block) in goals[0] and (('ontable', block) in goals[0] or ('on', block, above_block) in goals[0])

    def estimate_moves_to_correct(block, support, above_block):
        if is_goal_achieved(block, support, above_block):
            return 0
        else:
            return 2  # Need at least one unstack and one stack move

    total_cost = 0
    for fact in state:
        if fact[0] == 'on':
            block, support = fact[1], fact[2]
            above_block = next((b for (b, s) in state if s == block), None)
            total_cost += estimate_moves_to_correct(block, support, above_block)

    return total_cost