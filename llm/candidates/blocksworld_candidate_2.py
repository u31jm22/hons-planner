def h(state, goals):
    positive_goals, negative_goals = goals
    on = {a[1]: a[2] for a in state if a[0] == 'on'}
    clear = {a[1] for a in state if a[0] == 'clear'}
    ontable = {a[1] for a in state if a[0] == 'ontable'}
    holding = None
    for a in state:
        if a[0] == 'holding':
            holding = a[1]
            break
    cost = 0
    # Helper: count blocks above x
    def blocks_above(x):
        count = 0
        stack_top = [b for b, s in on.items() if s == x]
        while stack_top:
            b = stack_top.pop()
            count += 1
            stack_top.extend([bb for bb, ss in on.items() if ss == b])
        return count
    for g in positive_goals:
        if g[0] == 'on':
            x, y = g[1], g[2]
            if on.get(x) == y:
                continue
            # Base cost: unstack x + stack x on y
            c = 2
            # If y is not clear and not ontable, need to clear y first
            if y not in clear and y not in ontable:
                c += 1
            # Add cost for blocks above x: each needs unstack + putdown (2 each)
            c += 2 * blocks_above(x)
            # If holding a block different from x, add cost to put it down first
            if holding is not None and holding != x:
                c += 1
            cost += c
        elif g[0] == 'ontable':
            x = g[1]
            if x in ontable:
                continue
            c = 2  # pick up + put down on table
            # Add cost for blocks above x
            c += 2 * blocks_above(x)
            # If holding a block different from x, add cost to put it down first
            if holding is not None and holding != x:
                c += 1
            cost += c
    return float(cost)