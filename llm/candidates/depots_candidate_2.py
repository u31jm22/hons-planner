def h(state, goals):
    """
    Domain-specific heuristic for the Depots domain.
    state: frozenset of ground predicates describing the current world.
    goals: (positive_goals, negative_goals), each a frozenset of ground predicates.
    Returns: a non-negative int or float estimating the remaining number of actions
             needed to reach a goal state from the current state.
    """
    positive_goals, negative_goals = goals
    heuristic_cost = 0

    # Map current locations of crates and their goals
    crate_locations = {g[1]: g[2] for g in positive_goals if g[0] == 'at'}
    crate_in_trucks = {g[1]: g[2] for g in state if g[0] == 'in'}
    crate_on = {g[1]: g[2] for g in state if g[0] == 'on'}

    for crate, goal_location in crate_locations.items():
        current_location = None

        if crate in crate_in_trucks:
            current_location = crate_in_trucks[crate]
            heuristic_cost += 1  # Need to unload
        elif crate in crate_on:
            current_location = crate_on[crate]
            heuristic_cost += 1  # Need to lift off
        else:
            current_location = next((g[2] for g in state if g[0] == 'at' and g[1] == crate), None)

        if current_location != goal_location:
            # Estimate the cost to move the crate to its goal
            if current_location is not None:
                # If the crate is on the ground or on another crate
                heuristic_cost += 1  # Need to load it onto a hoist
                heuristic_cost += 1  # Need to drive to the goal location
                heuristic_cost += 1  # Need to unload it at the goal location
            else:
                # If the crate is not found, assume it needs to be fetched
                heuristic_cost += 3  # Load, drive, unload

    # Add costs for any hoists that are not available or clear
    for hoist in (g[1] for g in state if g[0] == 'available'):
        if not any(g[0] == 'clear' and g[1] == hoist for g in state):
            heuristic_cost += 1  # Need to clear the ho