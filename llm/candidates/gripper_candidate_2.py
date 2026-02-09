def h(state, goals):
    positive_goals, negative_goals = goals
    remaining_goals = positive_goals - state
    return len(remaining_goals)