def h(state, goals):
    positive_goals, negative_goals = goals

    comm_soil = set()
    comm_rock = set()
    comm_image = set()
    have_soil = set()
    have_rock = set()
    have_image = set()
    equipped_soil = set()
    equipped_rock = set()
    equipped_image = set()
    available = set()
    can_traverse = set()
    rover_at = {}

    for atom in state:
        p = atom[0]
        if p == 'communicated_soil_data':
            comm_soil.add(atom[1])
        elif p == 'communicated_rock_data':
            comm_rock.add(atom[1])
        elif p == 'communicated_image_data':
            comm_image.add((atom[1], atom[2]))
        elif p == 'have_soil_analysis':
            have_soil.add((atom[1], atom[2]))
        elif p == 'have_rock_analysis':
            have_rock.add((atom[1], atom[2]))
        elif p == 'have_image':
            have_image.add((atom[1], atom[2], atom[3]))
        elif p == 'equipped_for_soil_analysis':
            equipped_soil.add(atom[1])
        elif p == 'equipped_for_rock_analysis':
            equipped_rock.add(atom[1])
        elif p == 'equipped_for_imaging':
            equipped_image.add(atom[1])
        elif p == 'available':
            available.add(atom[1])
        elif p == 'can_traverse':
            can_traverse.add((atom[1], atom[2], atom[3]))
        elif p == 'at' and len(atom) == 3:
            rover_at[atom[1]] = atom[2]

    # Count unsatisfied goals by type
    unsatisfied_soil = 0
    unsatisfied_rock = 0
    unsatisfied_image = 0

    for g in positive_goals:
        p = g[0]
        if p == 'communicated_soil_data' and g[1] not in comm_soil:
            unsatisfied_soil += 1
        elif p == 'communicated_rock_data' and g[1] not in comm_rock:
            unsatisfied_rock += 1
        elif p == 'communicated_image_data' and (g[1], g[2]) not in comm_image:
            unsatisfied_image += 1

    # Each soil/rock data: ~3 actions if analysis not available, ~2 if it is
    # Each image: ~4 actions
    cost = 0
    for g in positive_goals:
        p = g[0]
        if p == 'communicated_soil_data':
            if g[1] in comm_soil:
                continue
            has = any((r, g[1]) in have_soil for r in equipped_soil)
            cost += (2 if has else 3)
        elif p == 'communicated_rock_data':
            if g[1] in comm_rock:
                continue
            has = any((r, g[1]) in have_rock for r in equipped_rock)
            cost += (2 if has else 3)
        elif p == 'communicated_image_data':
            obj, mode = g[1], g[2]
            if (obj, mode) in comm_image:
                continue
            has = any((r, obj, mode) in have_image for r in equipped_image)
            cost += (2 if has else 4)

    return float(cost)
