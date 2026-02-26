def h(state, goals):
    positive_goals, negative_goals = goals
    at_map = {}
    in_map = {}
    vehicles_at = {}
    for atom in state:
        if atom[0] == 'at':
            at_map[atom[1]] = atom[2]
            if atom[1].startswith('truck') or atom[1].startswith('airplane'):
                vehicles_at.setdefault(atom[2], set()).add(atom[1])
        elif atom[0] == 'in':
            in_map[atom[1]] = atom[2]
    total_cost = 0
    for goal in positive_goals:
        if goal[0] != 'at':
            continue
        pkg, goal_loc = goal[1], goal[2]
        current_loc = at_map.get(pkg)
        if current_loc == goal_loc:
            continue
        if pkg in in_map:
            veh = in_map[pkg]
            veh_loc = at_map.get(veh)
            cost = 1  # unload
            if veh_loc != goal_loc:
                cost += 1  # move vehicle
            cost += 1  # drop package
            total_cost += cost
        else:
            if current_loc is None:
                total_cost += 5  # unknown location penalty
                continue
            cost = 1  # load package
            if current_loc != goal_loc:
                cost += 1  # move vehicle
            cost += 1  # drop package
            if not vehicles_at.get(current_loc):
                cost += 1  # bring vehicle to package location
            total_cost += cost
    return float(total_cost)