def h(state, goals):
    positive_goals, negative_goals = goals
    # Extract locations of robby and vehicles
    robby_loc = None
    vehicle_locs = {}
    object_in_vehicle = set()
    object_on_ground = set()
    object_locs = {}
    for atom in state:
        if atom[0] == 'at-robby':
            robby_loc = atom[1]
        elif atom[0] == 'at-vehicle':
            vehicle_locs[atom[1]] = atom[2]
        elif atom[0] == 'in':
            object_in_vehicle.add(atom[1])
        elif atom[0] == 'at':
            object_on_ground.add(atom[1])
            object_locs[atom[1]] = atom[2]
    # Heuristic cost accumulator
    cost = 0.0
    # Helper: estimate cost to move robby from loc1 to loc2 (assume cost 1 if different, 0 if same)
    def move_cost(loc1, loc2):
        return 0 if loc1 == loc2 else 1
    # For each positive goal, estimate cost to achieve it
    for g in positive_goals:
        pred = g[0]
        if pred == 'at-robby':
            # robby must be at location g[1]
            if robby_loc != g[1]:
                cost += 1
        elif pred == 'at-vehicle':
            # vehicle must be at location g[2]
            v = g[1]
            loc = g[2]
            if vehicle_locs.get(v) != loc:
                # cost to move vehicle: assume 1 if not at location
                cost += 1
        elif pred == 'at':
            # object must be at location g[2]
            obj = g[1]
            loc = g[2]
            if obj in object_in_vehicle:
                # object inside vehicle, need to unload first
                # find vehicle location
                veh_loc = None
                for atom in state:
                    if atom[0] == 'in' and atom[1] == obj:
                        # find vehicle location
                        for v, vloc in vehicle_locs.items():
                            if v == atom[2]:
                                veh_loc = vloc
                                break
                        break
                # cost: unload (1) + move vehicle if needed (1 if veh_loc !=