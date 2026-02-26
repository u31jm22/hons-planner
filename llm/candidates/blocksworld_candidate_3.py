def h(state, goals):
    """
    Domain-specific heuristic for the Blocks World planning domain.
    state: frozenset of tuples like ('on', 'blocka', 'blockb'), ('ontable', 'blockc'), ('clear', 'blockd'), ('holding', 'blocke')
    goals: (positive_goals, negative_goals), each a frozenset of tuples
    Returns: non-negative int or float heuristic estimate.
    """
    def is_goal_achieved(block, on_goal, on_top_goal):
        for goal in on_goal:
            if ('on', block, goal) not in state:
                return False
        for goal in on_top_goal:
            if ('on', goal, block) in state:
                return False
        return True

    def get_cost_to_reach_goal(block, on_goal, on_top_goal):
        cost = 0
        if ('clear', block) not in state:
            cost += 1
        for goal in on_goal:
            if ('on', block, goal) not in state:
                cost += 1
        for goal in on_top_goal:
            if ('on', goal, block) in state:
                cost += 1
        return cost

    total_cost = 0
    for block in {atom[1] for atom in state if atom[0] == 'on'}:
        on_goal = {atom[2] for atom in goals[0] if atom[0] == 'on' and atom[1] == block}
        on_top_goal = {atom[1] for atom in goals[0] if atom[0] == 'on' and atom[2] == block}
        if not is_goal_achieved(block, on_goal, on_top_goal):
            total_cost += get_cost_to_reach_goal(block, on_goal, on_top_goal)

    return total_cost