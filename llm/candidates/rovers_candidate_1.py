def h(state, goals):
    """
    Rovers domain heuristic.
    Goals: (communicated_soil_data waypoint), (communicated_rock_data waypoint),
           (communicated_image_data objective mode).
    State atoms include: (at rover waypoint), (at_lander lander waypoint),
    (have_soil_analysis rover waypoint), (have_rock_analysis rover waypoint),
    (have_image rover objective mode), (communicated_soil_data waypoint),
    (communicated_rock_data waypoint), (communicated_image_data objective mode),
    (can_traverse rover wp1 wp2), (available rover), (equipped_for_soil_analysis rover),
    (equipped_for_rock_analysis rover), (equipped_for_imaging rover),
    (calibrated camera rover), (on_board camera rover), (channel_free lander).
    """
    positive_goals, negative_goals = goals

    # Parse state
    rover_at = {}         # rover -> waypoint
    lander_at = {}        # lander -> waypoint
    have_soil = set()     # (rover, waypoint)
    have_rock = set()     # (rover, waypoint)
    have_image = set()    # (rover, objective, mode)
    comm_soil = set()     # waypoint
    comm_rock = set()     # waypoint
    comm_image = set()    # (objective, mode)
    can_traverse = set()  # (rover, wp1, wp2)
    visible = set()       # (wp1, wp2)
    soil_sample = set()   # waypoint
    rock_sample = set()   # waypoint
    equipped_soil = set()
    equipped_rock = set()
    equipped_image = set()
    calibrated = set()    # (camera, rover)
    on_board = set()      # (camera, rover)
    calib_target = {}     # camera -> objective
    supports = {}         # (camera, mode)
    available = set()     # rovers
    channel_free = set()  # landers
    visible_from = {}     # (obj, waypoint)

    for atom in state:
        pred = atom[0]
        if pred == 'at' and len(atom) == 3:
            rover_at[atom[1]] = atom[2]
        elif pred == 'at_lander':
            lander_at[atom[1]] = atom[2]
        elif pred == 'have_soil_analysis':
            have_soil.add((atom[1], atom[2]))
        elif pred == 'have_rock_analysis':
            have_rock.add((atom[1], atom[2]))
        elif pred == 'have_image':
            have_image.add((atom[1], atom[2], atom[3]))
        elif pred == 'communicated_soil_data':
            comm_soil.add(atom[1])
        elif pred == 'communicated_rock_data':
            comm_rock.add(atom[1])
        elif pred == 'communicated_image_data':
            comm_image.add((atom[1], atom[2]))
        elif pred == 'can_traverse':
            can_traverse.add((atom[1], atom[2], atom[3]))
        elif pred == 'visible':
            visible.add((atom[1], atom[2]))
        elif pred == 'at_soil_sample':
            soil_sample.add(atom[1])
        elif pred == 'at_rock_sample':
            rock_sample.add(atom[1])
        elif pred == 'equipped_for_soil_analysis':
            equipped_soil.add(atom[1])
        elif pred == 'equipped_for_rock_analysis':
            equipped_rock.add(atom[1])
        elif pred == 'equipped_for_imaging':
            equipped_image.add(atom[1])
        elif pred == 'calibrated':
            calibrated.add((atom[1], atom[2]))
        elif pred == 'on_board':
            on_board.add((atom[1], atom[2]))
        elif pred == 'calibration_target':
            calib_target[atom[1]] = atom[2]
        elif pred == 'supports':
            supports[(atom[1], atom[2])] = True
        elif pred == 'available':
            available.add(atom[1])
        elif pred == 'channel_free':
            channel_free.add(atom[1])
        elif pred == 'visible_from':
            visible_from[(atom[1], atom[2])] = True

    cost = 0

    for g in positive_goals:
        pred = g[0]

        if pred == 'communicated_soil_data':
            wp = g[1]
            if wp in comm_soil:
                continue
            # Need: navigate to wp + sample_soil + navigate to lander-visible wp + communicate
            # Check if any rover already has analysis
            has_analysis = any(r for r in equipped_soil if (r, wp) in have_soil)
            if not has_analysis:
                cost += 2  # navigate to sample wp + sample
            cost += 2  # navigate to comm position + communicate

        elif pred == 'communicated_rock_data':
            wp = g[1]
            if wp in comm_rock:
                continue
            has_analysis = any(r for r in equipped_rock if (r, wp) in have_rock)
            if not has_analysis:
                cost += 2
            cost += 2

        elif pred == 'communicated_image_data':
            obj, mode = g[1], g[2]
            if (obj, mode) in comm_image:
                continue
            # Need: calibrate + take_image + communicate
            has_img = any(r for r in equipped_image if (r, obj, mode) in have_image)
            if not has_img:
                cost += 3  # calibrate + navigate to visible wp + take_image
            cost += 2  # navigate to lander-visible + communicate

    return float(cost)
