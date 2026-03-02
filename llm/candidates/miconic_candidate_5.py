def h(state, goals):
    positive_goals, negative_goals = goals
    lift_floor = None
    boarded = set()
    served = set()
    origins = {}
    destins = {}
    above = set()
    for atom in state:
        if atom[0] == 'lift-at':
            lift_floor = atom[1]
        elif atom[0] == 'boarded':
            boarded.add(atom[1])
        elif atom[0] == 'served':
            served.add(atom[1])
        elif atom[0] == 'origin':
            origins[atom[1]] = atom[2]
        elif atom[0] == 'destin':
            destins[atom[1]] = atom[2]
        elif atom[0] == 'above':
            above.add((atom[1], atom[2]))

    def floor_distance(f1, f2):
        if f1 == f2:
            return 0
        # Count steps going up or down using above relation
        # Try going up
        dist = 0
        current = f1
        while current != f2 and dist < 20:
            next_floors = [b for (a, b) in above if a == current]
            if not next_floors:
                break
            current = next_floors[0]
            dist += 1
        if current == f2:
            return dist
        # Try going down
        dist = 0
        current = f1
        while current != f2 and dist < 20:
            next_floors = [a for (a, b) in above if b == current]
            if not next_floors:
                break
            current = next_floors[0]
            dist += 1
        if current == f2:
            return dist
        # If no path found, return a default large cost
        return 10

    goal_passengers = [g[1] for g in positive_goals if g[0] == 'served']
    total_cost = 0
    for p in goal_passengers:
        if p in served:
            continue
        dest = destins.get(p)
        orig = origins.get(p)
        if p in boarded:
            # boarded: cost is distance to destination + 1 depart action
            dist = floor_distance(lift_floor, dest)
            total_cost += dist + 1
        else:
            # not boarded: cost is distance to origin + 1 board + distance origin->dest + 1 depart
            dist_to_orig = floor_distance(lift_floor, orig)
            dist_orig_to_dest = floor_distance(orig, dest)
            total_cost += dist_to_orig + 1 + dist_orig_to_dest + 1
    return float(total_cost)