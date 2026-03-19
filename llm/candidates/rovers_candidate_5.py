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
        elif p == 'at' and len(atom) == 3:
            rover_at[atom[1]] = atom[2]

    num_rovers = max(len(rover_at), 1)
    cost = 0

    for g in positive_goals:
        p = g[0]

        if p == 'communicated_soil_data':
            wp = g[1]
            if wp in comm_soil:
                continue
            has = any((r, wp) in have_soil for r in equipped_soil)
            if has:
                cost += 1.5
            else:
                cost += 3.5

        elif p == 'communicated_rock_data':
            wp = g[1]
            if wp in comm_rock:
                continue
            has = any((r, wp) in have_rock for r in equipped_rock)
            if has:
                cost += 1.5
            else:
                cost += 3.5

        elif p == 'communicated_image_data':
            obj, mode = g[1], g[2]
            if (obj, mode) in comm_image:
                continue
            has = any((r, obj, mode) in have_image for r in equipped_image)
            if has:
                cost += 2.0
            else:
                cost += 4.5

    # Discount slightly for multiple rovers that can work in parallel
    if num_rovers > 1:
        cost = cost / num_rovers * 0.75 + cost * 0.25

    return float(max(0, cost))
