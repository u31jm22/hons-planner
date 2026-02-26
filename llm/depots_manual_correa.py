def h(state, goals):
    """
    Domain-specific heuristic for the Depots domain (manual Corrêa-style LLM design).
    state: frozenset of ground predicates.
    goals: (positive_goals, negative_goals), each a frozenset of ground predicates.
    Returns: non-negative int or float.
    """
    positive_goals, negative_goals = goals

    # Extract goal locations for each crate: goal_locs[crate] = loc
    goal_locs = {}
    for pred in positive_goals:
        # Expect ('at', obj, loc)
        if len(pred) == 3 and pred[0] == "at":
            _, obj, loc = pred
            # We do not know types; assume anything in at/3 that appears in goals is a crate goal.
            goal_locs[obj] = loc

    if not goal_locs:
        return 0.0

    # Index current state
    crate_at = {}        # crate -> place
    crate_in = {}        # crate -> truck
    crate_on = {}        # crate -> below
    below_to_above = {}  # crate/surface -> above crate
    clear = set()
    truck_at = {}        # truck -> place
    hoist_at = {}        # hoist -> place
    hoist_available = set()

    for pred in state:
        if not pred:
            continue

        if pred[0] == "at" and len(pred) == 3:
            _, obj, place = pred
            # Generic location; we later distinguish trucks/hoists via other predicates.
            crate_at[obj] = place
        elif pred[0] == "in" and len(pred) == 3:
            _, crate, truck = pred
            crate_in[crate] = truck
        elif pred[0] == "on" and len(pred) == 3:
            _, crate, below = pred
            crate_on[crate] = below
            below_to_above[below] = crate
        elif pred[0] == "clear" and len(pred) == 2:
            _, x = pred
            clear.add(x)
        elif pred[0] in ("at-truck", "at_truck") and len(pred) == 3:
            _, truck, place = pred
            truck_at[truck] = place
        elif pred[0] in ("at-hoist", "at_hoist") and len(pred) == 3:
            _, hoist, place = pred
            hoist_at[hoist] = place
        elif pred[0] == "available" and len(pred) == 2:
            _, h = pred
            hoist_available.add(h)

    # Some encodings use only 'at' for trucks/hoists. If a truck has no at-truck, infer from 'at'.
    trucks = set(truck_at.keys())
    for crate, truck in crate_in.items():
        trucks.add(truck)
    for t in trucks:
        if t not in truck_at and t in crate_at:
            truck_at[t] = crate_at[t]

    # Similarly hoists: any object in hoist_at or hoist_available is a hoist, location from hoist_at or crate_at.
    hoists = set(hoist_at.keys()) | hoist_available
    for h in hoists:
        if h not in hoist_at and h in crate_at:
            hoist_at[h] = crate_at[h]

    # Precompute which places currently have a truck and/or an available hoist.
    trucks_at_place = {}
    for t, place in truck_at.items():
        trucks_at_place[place] = trucks_at_place.get(place, 0) + 1

    avail_hoist_at_place = {}
    for h in hoist_available:
        place = hoist_at.get(h)
        if place is not None:
            avail_hoist_at_place[place] = avail_hoist_at_place.get(place, 0) + 1

    def any_truck_at(place):
        return trucks_at_place.get(place, 0) > 0

    def any_avail_hoist_at(place):
        return avail_hoist_at_place.get(place, 0) > 0

    # Estimate stack height above a crate: number of crates on top that must be moved
    def height_above(crate):
        h_val = 0
        cur = crate
        while cur in below_to_above:
            above = below_to_above[cur]
            h_val += 1
            cur = above
        return h_val

    # Simple categorical distance between locations
    def place_distance(p1, p2):
        if p1 == p2:
            return 0

        def prefix(x):
            i = 0
            n = len(x)
            while i < n and not x[i].isdigit():
                i += 1
            return x[:i]

        if prefix(p1) == prefix(p2):
            return 1
        return 2

    heuristic = 0.0

    for crate, goal_loc in goal_locs.items():
        # Determine current "effective" location of crate.
        if crate in crate_at:
            cur_place = crate_at[crate]
            in_truck = False
        elif crate in crate_in:
            # Crate is inside a truck.
            truck = crate_in[crate]
            cur_place = truck_at.get(truck, None)
            in_truck = True
        else:
            # Crate might be in a stack: trace down to base and use its place.
            base = crate
            while base in crate_on:
                base = crate_on[base]
            cur_place = crate_at.get(base, None)
            in_truck = False

        # If already at its goal place and not inside a truck, consider it done.
        if (not in_truck) and cur_place == goal_loc:
            continue

        cost = 0.0

        # Base cost: any crate that still needs to move contributes at least 1.
        cost += 1.0

        # Add cost for being buried under other crates.
        buried = height_above(crate)
        cost += 1.5 * buried

        # Cost for location mismatch and transport.
        if in_truck:
            # Crate is already in a truck.
            if cur_place is None:
                # Unknown truck location: pessimistic.
                cost += 6.0
            else:
                d = place_distance(cur_place, goal_loc)
                # One unload plus some number of drive actions.
                cost += 2.0 + 3.0 * d
        else:
            # Crate is on ground or in a stack.
            if cur_place is None:
                cost += 8.0
            else:
                if cur_place == goal_loc:
                    # At correct place but may need stacking.
                    cost += 1.0
                else:
                    d = place_distance(cur_place, goal_loc)
                    # Approximate: lift + load, drives, unload.
                    cost += 5.0 + 3.0 * d
                    # If there is no truck at current place, we must bring one.
                    if not any_truck_at(cur_place):
                        cost += 3.0

        # Hoist availability: crates require hoists to be moved.
        if cur_place is not None and not any_avail_hoist_at(cur_place):
            cost += 1.0

        heuristic += cost

    if heuristic < 0:
        return 0.0
    return heuristic
