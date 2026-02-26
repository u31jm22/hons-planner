def h(state, goals):
    """
    Domain-specific heuristic for the Depots domain.
    state: frozenset of ground predicates describing the current world.
    goals: (positive_goals, negative_goals), each a frozenset of ground predicates.
    Returns: a non-negative int or float estimating the remaining number of actions
             needed to reach a goal state from the current state.
    """
    positive_goals, negative_goals = goals
    crate_locations = {}
    truck_locations = {}
    hoist_available = set()

    for atom in state:
        if atom[0] == 'at':
            crate_locations[atom[1]] = atom[2]
        elif atom[0] == 'in':
            crate_locations[atom[1]] = 'in_truck'
        elif atom[0] == 'at-truck':
            truck_locations[atom[1]] = atom[2]
        elif atom[0] == 'available':
            hoist_available.add(atom[1])

    heuristic_cost = 0

    for goal in positive_goals:
        if goal[0] == 'at':
            crate = goal[1]
            destination = goal[2]
            current_location = crate_locations.get(crate, None)

            if current_location == destination:
                continue

            if current_location == 'in_truck':
                heuristic_cost += 1  # Unload the crate
                current_location = 'at_truck'  # Assume it needs to be at the truck

            if current_location is not None:
                if current_location != destination:
                    heuristic_cost += 1  # Move to the truck or clear the crate

            if current_location == 'at_truck':
                # Need to drive to the destination
                truck_needed = any(truck for truck, loc in truck_locations.items() if loc == current_location)
                if truck_needed:
                    heuristic_cost += 1  # Drive to destination
                heuristic_cost += 1  # Load the crate

            heuristic_cost += 1  # Finally, drop the crate at the destination

    return heuristic_cost