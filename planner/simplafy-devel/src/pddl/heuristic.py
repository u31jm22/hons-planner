#!/usr/bin/env python
# Four spaces as indentation [no tabs]

from pddl.benchmark import InstanceStats
import time


class Heuristic:

    def __init__(self, is_safe=False, is_goal_aware=True, is_consistent=False, stats=None):
        self.stats: InstanceStats = stats
        # Ensure that you document heuristics properties correctly
        self.is_safe = is_safe
        self.is_goal_aware = is_goal_aware
        self.is_consistent = is_consistent

    def reset(self, actions, initial_state, goals):
        """Resets and reinitialises a stateful heuristic function.
        """
        pass

    def __call__(self, actions, initial_state, goals, parent_node=None):
        if self.stats:
            self.stats.h_calls += 1
            start_time = time.time()
        v = self.h(actions, initial_state, goals, parent_node)
        if self.stats:
            h_time = time.time() - start_time
            self.stats.h_time += h_time
        return v

    def h(self, domain, initial_state, goals, parent_node=None):
        """
        :param domain: a list of actions
        :param initial_state: the initial state
        :param goals: the goals in the domain
        :return:
        :rtype float
        """
        raise NotImplementedError("Unimplemented")
