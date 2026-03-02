def h(state, goals):
    positive_goals, negative_goals = goals
    lift_floor = next((a[1] for a in state if a[0] == 'lift-at'), None)
    boarded = {a[1] for a in state if a[0] == 'boarded'}
    served = {a[1] for a in state if a[0] == 'served'}
    origins = {a[1]: a[2] for a in state if a[0] == 'origin'}
    destins = {a[1]: a[2] for a in state if a[0] == 'destin'}
    above = {(a[1], a[2]) for a in state if a[0] == 'above'}

    # Build adjacency for floors (both directions)
    adj = {}
    floors = set()
    for f1, f2 in above:
        floors.add(f1)
        floors.add(f2)
        adj.setdefault(f1, set()).add(f2)
        adj.setdefault(f2, set()).add(f1)

    def floor_dist(f1, f2):
        if f1 == f2:
            return 0
        visited = {f1}
        frontier = {f1}
        dist = 0
        while frontier and dist < 20:
            dist += 1
            next_frontier = set()
            for f in frontier:
                next_frontier |= adj.get(f, set())
            next_frontier -= visited
            if f2 in next_frontier:
                return dist
            visited |= next_frontier
            frontier = next_frontier
        return 10  # fallback max distance

    goal_passengers = {g[1] for g in positive_goals if g[0] == 'served'}
    unserved = [p for p in goal_passengers if p not in served]

    # Separate passengers by boarded status
    boarded_passengers = [p for p in unserved if p in boarded]
    not_boarded_passengers = [p for p in unserved if p not in boarded]

    cost = 0

    # If no unserved passengers, heuristic is zero
    if not unserved:
        return 0

    # Estimate cost for boarded passengers: depart + travel to destination
    # We batch them by grouping destinations to minimize repeated travel
    dest_floors = {}
    for p in boarded_passengers:
        d = destins.get(p)
        if d is not None:
            dest_floors.setdefault(d, []).append(p)

    # For boarded passengers, estimate cost as:
    # travel from lift to closest destination floor + 1 depart per passenger + travel between destinations
    if boarded_passengers:
        # Find closest destination floor from lift
        min_dist = min(floor_dist(lift_floor, d) for d in dest_floors)
        # Sum depart actions (1 per passenger)
        depart_cost = len(boarded_passengers)
        # Approximate travel between destination floors as number of distinct destination floors - 1
        travel_between = max(len(dest_floors) - 1, 0)
        cost += min_dist + depart_cost + travel_between

    # For not boarded passengers:
    # For each passenger: travel to origin + 1 board + travel origin->dest + 1 depart
    # Batch origins to reduce travel cost: estimate travel to closest origin + travel between origins + sum boarding
    if not_boarded_passengers:
        origin_floors = {}
        for p in not_boarded_passengers:
            o = origins.get(p)
            if o is not None:
                origin_floors.setdefault(o, []).append(p)

        # Travel from lift to closest origin floor
        min_dist_to_origin = min(floor_dist(lift_floor, o) for o in origin_floors)
        # Travel between origins (approximate as number of distinct origins -1)
        travel_between_origins = max(len(origin_floors) - 1, 0)
        # Boarding cost: 1 per passenger
        boarding_cost = len(not_boarded_passengers)

        # Travel from origins to destinations: sum minimal distances per passenger
        origin_to_dest = 0
        for o, ps in origin_floors.items():
            for p in ps:
                d = destins.get(p)
                if d is not None:
                    origin_to_dest += floor_dist(o, d)

        # Depart cost: 1 per passenger
        depart_cost = len(not_boarded_passengers)

        cost += min_dist_to_origin + travel_between_origins + boarding_cost + origin_to_dest + depart_cost

    return float(cost)