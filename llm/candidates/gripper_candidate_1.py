def h(state, goals):
    positive_goals, negative_goals = goals
    unsatisfied_goals = len(positive_goals - state) + len(state & negative_goals)
    return unsatisfied_goals