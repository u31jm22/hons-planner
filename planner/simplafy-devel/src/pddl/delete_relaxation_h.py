#!/usr/bin/env python
# Four spaces as indentation [no tabs]

# Felipe's implementation of MaxH
from pddl.heuristic import Heuristic
from pddl.state import apply, applicable, regress, regressable
from pddl.action import Action
from pddl.pddl_preprocessor import compute_all_facts

from itertools import combinations


class DeleteRelaxationHeuristic(Heuristic):
    """Optimal Delete Relaxation Heuristic"""
    # TODO Consider subclassing from a common relaxation class like FD does

    def __init__(self, stats=None):
        super().__init__(is_safe=True, is_goal_aware=True, is_consistent=True, stats=stats)

    def h(self, actions, initial_state, goal, parent_node=None):
        # TODO Consider having an actual class for the state
        #  TODO and use overloading for apply instead of pasting search code
        (positive_goals, negative_goals) = goal
        # Parsed data
        import queue
        localh = MaxHeuristic()
        state = initial_state
        (goal_pos, goal_not) = goal
        # Search
        if applicable(initial_state, goal_pos, goal_not):
            return 0
        cost = {state: 0}
        visited = set([state])
        fringe = queue.PriorityQueue()
        fringe.put((0, state, localh.h(actions, state, goal), None))
        while not fringe.empty():  # NB the fringe (only) check sometimes lets it slip
            previous_f, state, h1, plan = fringe.get(block=False)  # to avoid failing silently
            g = cost[state] + 1
            for act in actions:
                if applicable(state, act.positive_preconditions, set([])):
                    new_state = apply(state, act.add_effects, set([]))
                    if new_state not in visited:
                        # if applicable(new_state, goal_pos, set([])):
                        if applicable(new_state, goal_pos, goal_not):
                            full_plan = [act]
                            while plan:
                                act, plan = plan
                                full_plan.insert(0, act)
                            print("Relaxed plan: {}".format(full_plan))
                            return len(full_plan)
                        h2 = localh.h(actions, new_state, goal)
                        if h1 >= h2:  # Monotonic trick
                            visited.add(new_state)
                            cost[new_state] = g
                            f = g + h2
                            fringe.put((f, new_state, h2, (act, plan)))
        return float("inf")
        # # Search
        # visited = set([initial_state])
        # fringe = [initial_state, None]
        # while fringe:
        #     initial_state = fringe.pop(0)
        #     plan = fringe.pop(0)
        #     for act in actions:
        #         if applicable(initial_state, act.positive_preconditions, frozenset([])):
        #             new_initial_state = apply(initial_state, act.add_effects, frozenset([]))
        #             if new_initial_state not in visited:
        #                 if applicable(new_initial_state, positive_goals, frozenset([])):
        #                     full_plan = [act]
        #                     while plan:
        #                         act, plan = plan
        #                         full_plan.insert(0, act)
        #                     return len(full_plan)
        #                 visited.add(new_initial_state)
        #                 fringe.append(new_initial_state)
        #                 fringe.append((act, plan))
        # return float("inf")


class MaxHeuristic(Heuristic):
    def __init__(self, stats=None):
        super().__init__(is_safe=True, is_goal_aware=True, is_consistent=True, stats=stats)

    def solvable(self, actions, initial_state, positive_g, negative_g):
        positive_effects = frozenset()
        negative_effects = frozenset()
        for a in actions:
            positive_effects = positive_effects.union(a.add_effects)
            negative_effects = negative_effects.union(a.del_effects)
        # First check the obvious stuff
        for p in positive_g:
            if p not in initial_state and p not in positive_effects:
                return False
        for p in negative_g:
            if p in initial_state and p not in negative_effects:
                return False
        return True

    def h(self, actions, initial_state, goal, parent_node=None):
        positive_g, negative_g = goal
        reachable_literals = initial_state
        last_state = None
        maxL = 0
        remaining_actions = set(actions)
        used_actions = [None]
        while used_actions:
            if positive_g.issubset(reachable_literals):
                return maxL
            maxL += 1
            last_state = reachable_literals
            used_actions.clear()
            for a in remaining_actions:
                # if applicable(last_state, a.positive_preconditions, a.negative_preconditions): ## This was a stupid mistake...
                if a.positive_preconditions.issubset(last_state):
                    used_actions.append(a)
                    reachable_literals = reachable_literals.union(a.add_effects)
            remaining_actions.difference_update(used_actions)

        return float("inf")


class AdditiveHeuristic(Heuristic):
    def __init__(self, stats=None):
        super().__init__(is_safe=True, is_goal_aware=True, is_consistent=True, stats=stats)

    def h(self, actions, initial_state, goal, parent_node=None):
        # if self.stats and self.stats.h_calls % 100 == 0: print('.', end="")
        positive_g, negative_g = goal
        if not positive_g:
            return 0
        reachable = set(initial_state)
        missing_positive_g = set(positive_g)
        # missing_negative_g = set(negative_g)  # TODO Do something about this unused variable
        last_state = None
        t_add = {p: 0 for p in initial_state}  # Everything in the initial state costs 0
        add = 0
        while last_state != reachable:
            g_reached = missing_positive_g.intersection(reachable)
            if g_reached:
                add += sum(t_add[g] for g in g_reached)
                missing_positive_g -= g_reached
                if not missing_positive_g:
                    return add
            last_state = set(reachable)
            for a in actions:
                if a.positive_preconditions.issubset(last_state):
                    new_reachable = a.add_effects - reachable
                    for eff in new_reachable:
                        if eff in t_add:
                            t_add[eff] = min(sum(t_add[pre] for pre in a.positive_preconditions)+1, t_add[eff])
                        else:
                            t_add[eff] = sum(t_add[pre] for pre in a.positive_preconditions)+1
                    reachable.update(new_reachable)
        return float("inf")


class CriticalPathHeuristic(Heuristic):
    """Haslum's H^m Heuristic"""

    def __init__(self, m, is_safe=True, is_goal_aware=True, is_consistent=True, stats=None):
        super().__init__(is_safe=True, is_goal_aware=True, is_consistent=True, stats=stats)
        self.m = m
        self.facts_at = []
        self.mutexes_at = []
        self.all_facts = None

    def reached(self, i, g):
        if g.issubset(self.facts_at[i]) and not [gp for gp in self.mutexes_at[i] if gp.issubset(g)]:
            return True
        else:
            return False

    def regr(self, goal, action):
        return regress(goal, action)

    def regressable(self, goal, action):
        return regressable(goal, action.add_effects, action.del_effects)

    def is_mutex_at(self, i, actions, goal):
        g = set(goal)
        for a in actions:
            if self.reached(i, self.regr(g, a)):
                return True
        return True

    def compute_all_facts(self, actions):
        self.all_facts = compute_all_facts(actions)

    def expand_rpg(self, i, actions):
        self.facts_at.append(set(self.facts_at[i]))
        aI = []
        for a in actions:
            if self.reached(i, a.positive_preconditions):
                aI.append(a)
                self.facts_at[i+1] |= a.add_effects
        return aI

    def rpg_fixpoint(self, i):
        return len(self.facts_at[i]) == len(self.facts_at[i+1]) and self.mutexes_at[i] == self.mutexes_at[i+1]

    def h(self, actions, initial_state, goal, parent_node=None):
        if not self.all_facts:  # Cache all facts the first time this this is called
            self.compute_all_facts(actions)
        positive_g, negative_g = goal
        self.facts_at.clear()
        self.mutexes_at.clear()
        self.facts_at.append(frozenset(initial_state))  # F_0 = s
        self.mutexes_at.append(frozenset())  # F_0 = {}
        i = 0
        while not self.reached(i, positive_g):
            aI = self.expand_rpg(i, actions)

            self.mutexes_at.append(set())

            for m in range(1, self.m+1):
                self.mutexes_at[i+1] |= set([frozenset(g) for g in combinations(self.all_facts, m) if self.is_mutex_at(i, aI, g)])

            if self.rpg_fixpoint(i):  # Convergence
                return float("inf")
            i += 1
        return i


class NaiveCriticalPathHeuristic(CriticalPathHeuristic):
    """Naive implementation of the Critical Path Heuristic (Graphplan Like)"""

    def __init__(self, m, stats=None):
        super().__init__(m, is_safe=True, is_goal_aware=True, is_consistent=True, stats=stats)
        self.action_mutexes = None

    def compute_action_mutexes(self, actions):
        """This computes the action mutexes statically"""
        self.action_mutexes = dict()
        for action in actions:
            self.action_mutexes[action] = set([])
        for (a1, a2) in combinations(actions, 2):
            if a1.is_mutex(a2):
                self.action_mutexes[a1].add(a2)

    def contains_mutexes(self, action_set):
        for a1, a2 in combinations(action_set, 2):
            if a2 in self.action_mutexes[a1]:
                return True
        return False

    def expand_rpg(self, i, actions):
        self.facts_at.append(set(self.facts_at[i]))
        aI = []
        for a in actions:
            if a.positive_preconditions.issubset(self.facts_at[i]):
                aI.append(a)
                self.facts_at[i+1] |= a.add_effects
        return aI

    def solution_extraction_at(self, i, actions, goal):
        if i == 0:
            return i
        # if self.contains_mutexes(goal):
        #     return float("inf")
        for a in actions:
            if self.regressable(goal, a):
                new_g = self.regr(goal, a)
                if self.solution_extraction_at(i-1, actions, new_g) != float("inf"):
                    return i
        return float("inf")

    def h(self, actions, initial_state, goal, parent_node=None):

        if not self.all_facts:  # Cache all facts the first time the heuristic is called
            self.compute_all_facts(actions)
        if not self.action_mutexes:  # Cache all mutexes the first time the heuristic is called
            self.compute_action_mutexes(actions)

        positive_g, negative_g = goal
        self.facts_at.clear()
        self.mutexes_at.clear()
        self.facts_at.append(frozenset(initial_state))  # F_0 = s
        self.mutexes_at.append(frozenset())  # F_0 = {}
        costs = {frozenset(g): 0 for g in combinations(self.all_facts, self.m)}
        i = 0
        while True:  #not positive_g <= self.facts_at[i]:  # not self.reached(i, positive_g):
            aI = self.expand_rpg(i, actions)
            #  Graphplan style solution extraction
            newcosts = costs.copy()
            for g in combinations(positive_g, self.m):
                #  Check these are not mutexes
                gs = frozenset(g)
                hm = self.solution_extraction_at(i+1, actions, gs)
                newcosts[frozenset(g)] = hm
                # if hm != float("inf"):
                #     return hm

            # print(costs)
            # print(newcosts)
            if costs == newcosts:
                max(costs.values())
            else:
                costs = newcosts
            if len(self.facts_at[i]) == len(self.facts_at[i+1]):  # Convergence
                return float("inf")
            i += 1

        return max(costs.values())


class FastForwardHeuristic(Heuristic):

    def __init__(self, stats=None):
        super().__init__(is_safe=True, is_goal_aware=True, is_consistent=False, stats=stats)

    def build_bs_table(self, actions, initial_state, goal):
        self.empty_action = Action('nop', frozenset(), frozenset(), frozenset(), frozenset(), frozenset())
        self.bs_table = dict()
        self.update_bs_table(actions, initial_state, goal)

    def update_bs_table(self, actions, initial_state, goal):
        # TODO Ideally do not replicate the code for additive heuristic here
        positive_g, negative_g = goal
        if not positive_g:
            return 0
        reachable = set(initial_state)
        missing_positive_g = set(positive_g)
        # missing_negative_g = set(negative_g)  # TODO Do something about this unused variable
        last_state = None
        t_add = {p: 0 for p in initial_state}  # Everything in the initial state costs 0
        add = 0
        while last_state != reachable:
            g_reached = missing_positive_g.intersection(reachable)
            if g_reached:
                add += sum(t_add[g] for g in g_reached)
                missing_positive_g -= g_reached
                if not missing_positive_g:
                    return add
            last_state = set(reachable)
            for a in actions:
                if a.positive_preconditions.issubset(last_state):
                    new_reachable = a.add_effects - reachable
                    for eff in new_reachable:
                        if eff in t_add:
                            old_t_add = t_add[eff]
                            t_add[eff] = min(sum(t_add[pre] for pre in a.positive_preconditions)+1, t_add[eff])
                            if t_add[eff] != old_t_add:
                                self.bs_table[eff] = a  # best supporter changed
                        else:
                            t_add[eff] = sum(t_add[pre] for pre in a.positive_preconditions)+1
                            self.bs_table[eff] = a
                    reachable.update(new_reachable)
        return float("inf")

    def best_supporter(self, actions, initial_state, g):
        if g not in self.bs_table.keys():
            # self.update_bs_table(actions, initial_state, (set([g]), set()))
            return self.empty_action
        return self.bs_table[g]

    def h(self, actions, initial_state, goal, parent_node=None):
        # Build best supporter
        self.build_bs_table(actions, initial_state, goal)
        open_g = set(goal[0]) - initial_state
        closed_g = set()
        r_plan = set()
        while open_g:
            g = open_g.pop()
            closed_g.add(g)
            bsg = self.best_supporter(actions, initial_state, g)
            r_plan.add(bsg)
            open_g.update(bsg.positive_preconditions - (closed_g | initial_state))

        return len(r_plan)


import importlib
from pathlib import Path

class LLMHeuristic(Heuristic):
    """
    Wrapper heuristic that delegates to a domain-specific heuristic module
    in llm/{domain_name}_heuristic.py if it exists, otherwise falls back
    to a trivial 0-valued heuristic.
    """

    def __init__(self, stats=None, model_name: str = "gpt-4.1-mini",
                 domain_name: str | None = None):
        super().__init__(is_safe=True, is_goal_aware=True,
                         is_consistent=True, stats=stats)
        self.model_name = model_name
        self.domain_name = domain_name
        self._fallback_value = 0.0

        self._generated = None
        if domain_name is not None:
            # Expect a module like llm/blocksworld_heuristic.py
            module_name = f"llm.{domain_name}_heuristic"
            try:
                module = importlib.import_module(module_name)
                # Module is expected to expose LLMGeneratedHeuristic
                self._generated = module.LLMGeneratedHeuristic(stats=stats)
            except Exception:
                # If module is missing or broken, stay in fallback mode
                self._generated = None

    def h(self, actions, initial_state, goal, parent_node=None):
        if self._generated is not None:
            try:
                return self._generated.h(actions, initial_state, goal, parent_node)
            except Exception:
                # Any error in generated code: fall back safely
                return self._fallback_value
        return self._fallback_value
