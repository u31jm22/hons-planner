def h(state, goals):
    positive_goals, negative_goals = goals
    steps_remaining = 0
    
    for goal in positive_goals:
        if goal not in state:
            steps_remaining += 1
    
    return steps_remaining