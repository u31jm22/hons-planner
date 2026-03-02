def h(state, goals):
    positive_goals, negative_goals = goals
    lift_floor = None
    boarded = set()
    served = set()
    origins = {}
    destins = {}
    above = set()
    floors = set()
    for atom in state:
        if atom[0] == 'lift-at':
            lift_floor = atom[1]
            floors.add(atom[1])
        elif atom[0] == 'boarded':
            boarded.add(atom[1])
        elif atom[0] == 'served':
            served.add(atom[1])
        elif atom[0] == 'origin':
            origins[atom[1]] = atom[2]
            floors.add(atom[2])
        elif atom[0] == 'destin':
            destins[atom[1]] = atom[2]
            floors.add(atom[2])
        elif atom[0] == 'above':
            above.add((atom[1], atom[2]))
            floors.add(atom[1])
            floors.add(atom[2])
    # Precompute adjacency for floor graph (both up and down)
    up_map = {}
    down_map = {}
    for f1, f2 in above:
        up_map.setdefault(f1, set()).add(f2)
        down_map.setdefault(f2, set()).add(f1)
    def floor_distance(f_start, f_goal):
        if f_start == f_goal:
            return 0
        # Use bidirectional BFS limited to 10 steps
        visited_start = {f_start}
        visited_goal = {f_goal}
        frontier_start = {f_start}
        frontier_goal = {f_goal}
        dist = 0
        while frontier_start and frontier_goal and dist < 10:
            dist += 1
            # Expand from start side
            next_start = set()
            for f in frontier_start:
                next_start.update(up_map.get(f, set()))
                next_start.update(down_map.get(f, set()))
            next_start -= visited_start
            if next_start & visited_goal:
                return dist
            visited_start |= next_start
            frontier_start = next_start
            dist += 1
            # Expand from goal side
            next_goal = set()
            for f in frontier_goal:
                next_goal.update(up_map.get(f, set()))
                next_goal.update(down_map.get(f, set()))
            next_goal -= visited_goal
            if next_goal & visited_start:
                return dist
            visited_goal |= next_goal
            frontier_goal = next_goal
        return 10
    goal_passengers = {g[1] for g in positive_goals if g[0] == 'served'}
    total_cost = 0.0
    for p in goal_passengers:
        if p in served:
            continue
        origin = origins.get(p)
        dest = destins.get(p)
        if origin is None or dest is None:
            continue
        if p in boarded:
            # Passenger is on board: cost = floors to destination + 1 depart
            dist = floor_distance(lift_floor, dest)
            total_cost += dist + 1
        else:
            # Passenger not boarded: cost = floors to origin + 1 board + floors to dest + 1 depart
            dist_to_origin = floor_distance(lift_floor, origin)
            dist_origin_to_dest = floor_distance(origin, dest)
            total_cost += dist_to_origin + 1 + dist_origin_to_dest + 1
    # Add a small penalty if lift is not at any passenger origin or destination to encourage moving towards passengers
    passenger_floors = {origins[p] for p in goal_passengers if p not in served and p in origins}
    passenger_floors |= {destins[p] for p in goal_passengers if p not in served and p in destins}
    if lift_floor not in passenger_floors and passenger_floors:
        min_dist = min(floor_distance(lift_floor, f) for f in passenger_floors)
        total_cost += 0.5 * min_dist
    return total_cost