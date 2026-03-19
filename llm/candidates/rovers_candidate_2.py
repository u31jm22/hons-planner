def h(state, goals):
    positive_goals, negative_goals = goals

    comm_soil = set()
    comm_rock = set()
    comm_image = set()
    have_soil = set()
    have_rock = set()
    have_image = set()
    rover_at = {}
    lander_at = {}
    equipped_soil = set()
    equipped_rock = set()
    equipped_image = set()

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
        elif p == 'at' and len(atom) == 3:
            rover_at[atom[1]] = atom[2]
        elif p == 'at_lander':
            lander_at[atom[1]] = atom[2]
        elif p == 'equipped_for_soil_analysis':
            equipped_soil.add(atom[1])
        elif p == 'equipped_for_rock_analysis':
            equipped_rock.add(atom[1])
        elif p == 'equipped_for_imaging':
            equipped_image.add(atom[1])

    cost = 0

    for g in positive_goals:
        pred = g[0]

        if pred == 'communicated_soil_data':
            wp = g[1]
            if wp in comm_soil:
                continue
            # already have analysis?
            if any((r, wp) in have_soil for r in equipped_soil):
                cost += 2  # just navigate to comms position + communicate
            else:
                cost += 4  # navigate to sample + sample + navigate to comms + communicate

        elif pred == 'communicated_rock_data':
            wp = g[1]
            if wp in comm_rock:
                continue
            if any((r, wp) in have_rock for r in equipped_rock):
                cost += 2
            else:
                cost += 4

        elif pred == 'communicated_image_data':
            obj, mode = g[1], g[2]
            if (obj, mode) in comm_image:
                continue
            if any((r, obj, mode) in have_image for r in equipped_image):
                cost += 2
            else:
                cost += 5  # navigate to calib target + calibrate + navigate to visible wp + image + communicate

    return float(cost)
