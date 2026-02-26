def h(state, goals):
    positive_goals, negative_goals = goals
    # Heuristic for a logistics-like domain with trucks, planes, packages, and locations.
    # Estimate cost based on number of packages not at goal location,
    # considering transport modes and distances.
    # State atoms example: ('at', 'pkg1', 'loc1'), ('in', 'pkg1', 'truck1'), ('at', 'truck1', 'loc2'), ('road', 'loc1', 'loc2')
    # Goals example: positive goals like ('at', 'pkg1', 'loc3')
    # Negative goals ignored for heuristic cost.

    # Extract locations of trucks and planes
    vehicle_locations = {}
    for atom in state:
        if atom[0] == 'at' and (atom[1].startswith('truck') or atom[1].startswith('plane')):
            vehicle_locations[atom[1]] = atom[2]

    # Extract package locations or vehicles they are in
    package_positions = {}
    for atom in state:
        if atom[0] == 'at' and atom[1].startswith('pkg'):
            package_positions[atom[1]] = atom[2]
        elif atom[0] == 'in' and atom[1].startswith('pkg'):
            package_positions[atom[1]] = atom[2]

    # Build adjacency for road and air routes
    adjacency = {}
    for atom in state:
        if atom[0] == 'road':
            adjacency.setdefault(atom[1], set()).add(atom[2])
            adjacency.setdefault(atom[2], set()).add(atom[1])
        elif atom[0] == 'air':
            adjacency.setdefault(atom[1], set()).add(atom[2])
            adjacency.setdefault(atom[2], set()).add(atom[1])

    # Simple distance estimate: number of hops between locations ignoring direction
    def distance(loc1, loc2):
        if loc1 == loc2:
            return 0
        visited = set()
        frontier = [(loc1, 0)]
        while frontier:
            current, dist = frontier.pop(0)
            if current == loc2:
                return dist
            visited.add(current)
            for neigh in adjacency.get(current, []):
                if neigh not in visited:
                    frontier.append((neigh, dist + 1))
        # If no path, return large cost
        return 10

    cost = 0.0