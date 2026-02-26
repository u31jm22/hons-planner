def h(state, goals):
    """
    Domain-specific heuristic for the BLOCKS planning domain.
    state: frozenset of tuples like ('on', 'blocka', 'blockb'), ('ontable', 'blockc'), ('clear', 'blockd'), ('holding', 'blocke'), ('handempty',)
    goals: (positive_goals, negative_goals), each a frozenset of tuples
    Returns: non-negative int or float heuristic estimate.
    """
    def get_top_block(blocks, block):
        supported_block = None
        for b in blocks:
            if ('on', block, b) in state:
                supported_block = b
        return supported_block

    def is_goal_satisfied(goal):
        return goal in state

    def get_blocks_to_move():
        blocks_to_move = set()
        for goal in goals[0]:
            if goal[0] == 'on':
                block, support = goal[1], goal[2]
                top_block = get_top_block(goals[0], support)
                if top_block != block:
                    blocks_to_move.add(block)
        return blocks_to_move

    def estimate_block_moves(block):
        moves = 0
        while block not in goals[0]:
            moves += 1
            block = get_top_block(goals[0], block)
        return moves

    blocks_to_move = get_blocks_to_move()
    total_moves = sum(estimate_block_moves(block) for block in blocks_to_move)
    return total_moves