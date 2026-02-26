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
        # If package already at goal location, no cost
        if at_map.get(pkg) == goal_loc:
            continue
        # Package is inside a vehicle
        if pkg in in_map:
            veh = in_map[pkg]
            veh_loc = at_map.get(veh)
            cost = 1  # unload
            if veh_loc != goal_loc:
                cost += 1  # move vehicle
            cost += 1  # drop package at goal
            total_cost += cost
        else:
            # Package on ground somewhere else
            pkg_loc = at_map.get(pkg)
            if pkg_loc is None:
                # Unknown location, assign high cost
                total_cost += 5
                continue
            cost = 1  # load package into vehicle
            if pkg_loc != goal_loc:
                cost += 1  # move vehicle
            cost += 1  # unload package at goal
            # If no vehicle at package location, add cost to bring one
            if not vehicles_at.get(pkg_loc):
                cost += 1
            total_cost += cost
    return float(total_cost)