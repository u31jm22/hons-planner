def h(state, goals):
    positive_goals, negative_goals = goals
    at_map = {}
    in_map = {}
    vehicles = set()
    for atom in state:
        if atom[0] == 'at':
            at_map[atom[1]] = atom[2]
            if atom[1].startswith('truck') or atom[1].startswith('airplane'):
                vehicles.add(atom[1])
        elif atom[0] == 'in':
            in_map[atom[1]] = atom[2]
    vehicle_locations = {v: at_map.get(v) for v in vehicles}
    cost = 0
    for goal in positive_goals:
        if goal[0] != 'at':
            continue
        pkg, goal_loc = goal[1], goal[2]
        pkg_loc = at_map.get(pkg)
        if pkg_loc == goal_loc:
            continue
        if pkg in in_map:
            veh = in_map[pkg]
            veh_loc = vehicle_locations.get(veh)
            # unload cost
            step_cost = 1
            # if vehicle not at goal location, need to move vehicle
            if veh_loc != goal_loc:
                step_cost += 1
            # drop cost
            step_cost += 1
            cost += step_cost
        else:
            # package on ground
            if pkg_loc is None:
                # unknown location, high penalty
                cost += 5
                continue
            step_cost = 1  # load package onto vehicle
            # check if any vehicle at package location
            vehicles_here = [v for v, loc in vehicle_locations.items() if loc == pkg_loc]
            if not vehicles_here:
                # need to bring a vehicle here
                step_cost += 1
            # move vehicle to goal location if different
            if pkg_loc != goal_loc:
                step_cost += 1
            # unload package at goal location
            step_cost += 1
            cost += step_cost
    return float(cost)