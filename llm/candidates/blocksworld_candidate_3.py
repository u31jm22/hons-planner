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

    # Precompute stacks above each block
    # For each block, count how many blocks are stacked above it (directly or indirectly)
    above_count = {}
    def count_above(b):
        count = 0
        for blk, below in on.items():
            if below == b:
                count += 1 + count_above(blk)
        return count
    for b in set(on.keys()).union(ontable):
        above_count[b] = count_above(b)

    cost = 0
    for g in positive_goals:
        if g[0] == 'on':
            x, y = g[1], g[2]
            if on.get(x) == y:
                continue
            # Base cost: unstack x and stack on y
            c = 2
            # Add cost for blocks above x (each needs unstack + putdown)
            c += 2 * above_count.get(x, 0)
            # If y is not clear and y is not on table, need to clear y first
            if y not in clear and y not in ontable:
                # Clearing y means unstacking blocks above y
                c += 2 * above_count.get(y, 0)
            cost += c
        elif g[0] == 'ontable':
            x = g[1]
            if x in ontable:
                continue
            # If x is not on table, it must be held or on another block
            # Cost at least 1 to put down if holding, else unstack + putdown
            if holding == x:
                cost += 1
            else:
                # Unstack x plus put down
                c = 2
                # Add cost for blocks above x