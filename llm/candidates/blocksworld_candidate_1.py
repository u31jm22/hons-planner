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
    # Build inverse map: what is on top of what
    above = {}
    for b, s in on.items():
        above.setdefault(s, set()).add(b)
    # Compute how many blocks are above each block (recursively)
    def count_above(block):
        total = 0
        stack = [block]
        while stack:
            cur = stack.pop()
            tops = above.get(cur, set())
            total += len(tops)
            stack.extend(tops)
        return total
    cost = 0.0
    # If holding a block, consider cost to put it down first
    if holding is not None:
        # Cost to put down holding block: 1 action
        cost += 1
    # For each positive goal
    for g in positive_goals:
        if g[0] == 'on':
            x, y = g[1], g[2]
            if on.get(x) == y:
                continue
            # Base cost: unstack x + stack x on y = 2
            c = 2
            # Add cost for blocks above x (each needs unstack + putdown = 2)
            c += 2 * count_above(x)
            # If y is not clear and y is not on table, need to clear y first
            if y not in clear and y not in ontable:
                # Clearing y costs at least 2 (unstack + putdown)
                c += 2
            cost += c
        elif g[0] == 'ontable':
            x = g[1]
            if x in ontable:
                continue
            # If x is on another block, need to unstack + putdown = 2
            # Also add cost for blocks above x
            c = 2 + 2 * count_above(x)
            cost += c