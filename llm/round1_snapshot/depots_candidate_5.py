def h(state, goals):
    """
    Domain-specific heuristic for this planning domain.
    state: frozenset of tuples like ('at-robby', 'rooma'), ('at', 'ball1', 'rooma'), ('carry', 'ball2', 'right'), ('free', 'left')
    goals: (positive_goals, negative_goals), each a frozenset of tuples
    Returns: non-negative int or float heuristic estimate.
    """
    unplaced_crates = sum(1 for atom in state if atom[0] == 'on' and atom[1] == 'crate')
    hoists_in_use = sum(1 for atom in state if atom[0] == 'lifting')
    trucks_at_different_place = sum(1 for atom in state if atom[0] == 'at' and atom[1] == 'truck' and ('at', 'truck', atom[2]) not in goals[0])

    return unplaced_crates + hoists_in_use + trucks_at_different_place