def h(state, goals):
    positive_goals, negative_goals = goals
    on = {}
    clear = set()
    ontable = set()
    holding = None
    handempty = False
    for atom in state:
        if atom[0] == 'on':
            on[atom[1]] = atom[2]
        elif atom[0] == 'clear':
            clear.add(atom[1])
        elif atom[0] == 'ontable':
            ontable.add(atom[1])
        elif atom[0] == 'holding':
            holding = atom[1]
        elif atom[0] == 'handempty':
            handempty = True

    # Build inverse map: what is on top of a block
    above = {}
    for b, s in on.items():
        above.setdefault(s, set()).add(b)

    # Count how many blocks are stacked above a block recursively
    def buried_count(block):
        count = 0
        stack = [block]
        while stack:
            current = stack.pop()
            for b in above.get(current, []):
                count += 1
                stack.append(b)
        return count

    cost = 0.0

    # If holding a block, add cost to put it down first (1)
    if holding is not None:
        cost += 1.0

    for g in positive_goals:
        if g[0] == 'on':
            x, y = g[1], g[2]
            if on.get(x) == y:
                continue
            # Base cost: unstack x + stack x on y
            base = 2.0
            # Add cost for blocks above x (each needs unstack + putdown)
            buried = buried_count(x)
            base += buried * 2.0
            # If y is not clear and y is not on table, need to clear y first
            if y not in clear and y not in ontable:
                base += 1.0
            cost += base
        elif g[0] == 'ontable':
            x = g[1]
            if x in ontable:
                continue
            # If x is on something else, need to unstack + putdown
            base = 2.0
            buried = buried_count(x)
            base += buried * 2.0
            cost += base

    return cost