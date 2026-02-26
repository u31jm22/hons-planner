def h(state, goals):
    positive_goals, negative_goals = goals
    crate_at = {}
    crate_in = {}
    crate_on = {}
    truck_at = {}
    hoist_at = {}
    available_hoists = set()
    lifting = {}
    clear = set()
    for atom in state:
        if atom[0] == 'at':
            crate_at[atom[1]] = atom[2]
        elif atom[0] == 'in':
            crate_in[atom[1]] = atom[2]
        elif atom[0] == 'on':
            crate_on[atom[1]] = atom[2]
        elif atom[0] == 'at-truck':
            truck_at[atom[1]] = atom[2]
        elif atom[0] == 'at-hoist':
            hoist_at[atom[1]] = atom[2]
        elif atom[0] == 'available':
            available_hoists.add(atom[1])
        elif atom[0] == 'lifting':
            lifting[atom[1]] = atom[2]
        elif atom[0] == 'clear':
            clear.add(atom[1])
    # Group crates by current location for batching
    crates_by_loc = {}
    for c, loc in crate_at.items():
        crates_by_loc.setdefault(loc, set()).add(c)
    for c, truck in crate_in.items():
        # Treat truck as location for batching
        crates_by_loc.setdefault(truck, set()).add(c)
    for c, surf in crate_on.items():
        # For stacked crates, location is where the surface is located
        # Find surface location: if surface is crate, get its location recursively
        def surface_loc(s):
            if s in crate_at:
                return crate_at[s]
            if s in crate_in:
                return truck_at.get(crate_in[s], None)
            if s in crate_on:
                return surface_loc(crate_on[s])
            return None
        loc = surface_loc(surf)
        if loc is not None:
            crates_by_loc.setdefault(loc, set()).add(c)
    # Find hoist locations that are available
    avail_hoist_locs = {hoist_at[h] for h in available_hoists if h in hoist_at}
    # For each truck, find location
    truck_locations = set(truck_at.values())
    # Heuristic cost accumulator
    cost = 0.0
    #