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
    calibrated = set()
    channel_free = set()

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
        elif p == 'calibrated':
            calibrated.add((atom[1], atom[2]))
        elif p == 'channel_free':
            channel_free.add(atom[1])

    channel_available = len(channel_free) > 0
    cost = 0

    for g in positive_goals:
        p = g[0]

        if p == 'communicated_soil_data':
            wp = g[1]
            if wp in comm_soil:
                continue
            has_analysis = any((r, wp) in have_soil for r in equipped_soil)
            # Steps: [sample if needed] + navigate to visible lander pos + communicate
            step_cost = 0 if has_analysis else 2  # navigate to sample wp + sample
            step_cost += 1  # navigate to comms waypoint
            step_cost += 1  # communicate
            if not channel_available:
                step_cost += 1
            cost += step_cost

        elif p == 'communicated_rock_data':
            wp = g[1]
            if wp in comm_rock:
                continue
            has_analysis = any((r, wp) in have_rock for r in equipped_rock)
            step_cost = 0 if has_analysis else 2
            step_cost += 1
            step_cost += 1
            if not channel_available:
                step_cost += 1
            cost += step_cost

        elif p == 'communicated_image_data':
            obj, mode = g[1], g[2]
            if (obj, mode) in comm_image:
                continue
            has_img = any((r, obj, mode) in have_image for r in equipped_image)
            step_cost = 0 if has_img else 3  # calibrate + navigate + take_image
            step_cost += 2  # navigate to lander + communicate
            if not channel_available:
                step_cost += 1
            cost += step_cost

    return float(cost)
