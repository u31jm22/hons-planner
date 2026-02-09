```python
def h(state, goals):
    positive_goals, negative_goals = goals
    satisfied_goals = sum(1 for goal in positive_goals if goal in state)
    unsatisfied_goals = sum(1 for goal in negative_goals if goal