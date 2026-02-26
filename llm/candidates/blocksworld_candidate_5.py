def h(state, goals):
    positive_goals, negative_goals = goals
    on_map = {}
    clear_set = set()
    ontable_set = set()
    holding_set = set()
    handempty = False
    for atom in state:
        if atom[0] == 'on':
            on_map[atom[1]] = atom[2]
        elif atom[0] == 'clear':
            clear_set.add(atom[1])
        elif atom[0] == 'ontable':
            ontable_set.add(atom[1])
        elif atom[0] == 'holding':
            holding_set.add(atom[1])
        elif atom[0] == 'handempty':
            handempty = True

    # Helper: count blocks stacked above x
    def count_above(x):
        count = 0
        for b, below in on_map.items():
            if below == x:
                count += 1 + count_above(b)
        return count

    cost = 0
    for goal in positive_goals:
        if goal[0] == 'on':
            x, y = goal[1], goal[2]
            if on_map.get(x) == y:
                continue
            # Base cost: unstack x + stack x on y
            step_cost = 2
            # Add cost for blocks above x (each needs unstack + putdown)
            buried = count_above(x)
            step_cost += buried * 2
            # If y is not clear and not ontable, need to clear y first
            if y not in clear_set and y not in ontable_set:
                step_cost += 1
            cost += step_cost
        elif goal[0] == 'ontable':
            x = goal[1]
            if x in ontable_set:
                continue
            # Base cost: unstack x + put down
            step_cost = 2
            # Add cost for blocks above x
            buried = count_above(x)
            step_cost += buried * 2
            cost += step_cost
    return float(cost)