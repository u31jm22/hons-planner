#!/usr/bin/env python
# Four spaces as indentation [no tabs]


# Felipe's implementation of A* using MaxH
import time
from pddl.delete_relaxation_h import MaxHeuristic
from pddl.pddl_planner import PDDLPlanner
from pddl.state import applicable, apply
from pddl.action import Action
# from pddl.benchmark import PlanningBenchmark
from heap_queue.priority_queue import PriorityQueue
from typing import List, Collection, Dict, Tuple


INF = float("inf")


class HeuristicPlanner(PDDLPlanner):

    def __init__(self, heuristic=MaxHeuristic(), verbose=False,
                 collect_stats=False, visualise=False,
                 PriorityQueue=PriorityQueue):
        super().__init__(verbose=verbose,
                         collect_stats=collect_stats,
                         visualise=visualise)
        self.h = heuristic
        self.PriorityQueue = PriorityQueue

        # Statistics
        self.init_h = 0
        self.expansions = 0
        self.plan_length = 0
        self.search_time = 0.0

    def get_path(self, node: Tuple) -> List[Action]:
        full_plan = []
        while node:
            act, node = node
            full_plan.insert(0, act)
        return full_plan

    def astar_search(self, fringe: PriorityQueue,
                     cost: Dict,
                     visited: set,
                     actions: Collection[Action],
                     state: frozenset[Tuple],
                     goals: Tuple,
                     parent: Tuple = None) -> Tuple[float, frozenset[Tuple], float, Tuple]:
        """An implementation of A star graph search that uses an externally
        provided fringe, table of costs, and set of visited states.
        """
        (goal_pos, goal_not) = goals
        fringe.put((0, 0, state, 0, parent))
        if self.visualiser:
            self.visualiser.add_node(
                None, (0, state, self.h(actions, state, goals), None)
            )
        while not fringe.empty():
            previous_f, previous_g, state, h1, parent = fringe.get(block=False)
            g = cost[state]
            if previous_g <= g:  # delayed duplicate detection
                cost[state] = previous_g

                # Count this expanded node
                self.expansions += 1

                if applicable(state, goal_pos, goal_not):
                    return state, parent
                for act in actions:
                    if applicable(state,
                                  act.positive_preconditions,
                                  act.negative_preconditions):
                        new_state = apply(state,
                                          act.add_effects,
                                          act.del_effects)
                        if new_state not in visited:
                            visited.add(new_state)
                            h2 = self.h(actions, new_state, goals, parent)
                            if self.visualiser:
                                self.visualiser.add_node(
                                    (previous_f, state, h1, parent),
                                    (g + h2, new_state, h2, (act, parent)),
                                )
                            if h2 != INF:
                                g = previous_g + 1
                                cost[new_state] = min(
                                    g, cost.get(new_state, float("inf"))
                                )
                                f = g + h2
                                fringe.put((f, g, new_state, h2, (act, parent)))
        return None, None

    def __str__(self):
        return f"{super().__str__()}({str(self.h)})"

    def solve(self,
              actions: Collection[Action],
              initial_state: frozenset[Tuple],
              goals: Tuple[frozenset[Tuple], frozenset[Tuple]]):
        # Parsed data
        state = initial_state

        # Record start time
        t_start = time.time()

        # Search
        cost = {state: 0}
        visited = set([state])
        # If we are collecting data, store cost and visited
        if self.collect_benchmark:
            self.cost = cost
            self.visited = visited

        fringe = self.PriorityQueue()
        if self.visualiser:
            self.visualiser.add_node(
                None, (0, state, self.h(actions, state, goals), None)
            )

        init_h = self.h(actions, state, goals)
        self.init_h = init_h
        fringe.put((0, 0, state, init_h, None))

        state, parent = initial_state, None
        state, parent = self.astar_search(
            fringe, cost, visited, actions, state, goals, parent
        )
        if state is not None:
            full_plan = self.get_path(parent)
            self.plan_length = len(full_plan)
        else:
            if self.verbose:
                print('No plan was found')
            full_plan = None
            self.plan_length = 0

        if self.stats:
            self.stats.nodes = len(visited)  # Collect stats

        # Record search time
        self.search_time = float(time.time() - t_start)

        # Output expanded nodes to console if -v flag is enabled
        if self.verbose:
            print(f"Initial H-val: {self.init_h}")
            print(f"# Expansions : {self.expansions}")
            print(f"Plan Length  : {self.plan_length}")
            print(f"Search Time  : {self.search_time}")

        return full_plan


class HeuristicRunner(PDDLPlanner):
    """A class that just loads a problem and outputs the heuristic value of this problem.
    """
    def __init__(self, heuristic=MaxHeuristic(), verbose=False,
                 collect_stats=False):
        super().__init__(verbose, collect_stats)
        self.h = heuristic

    def solve(self, actions, initial_state, goals):
        # Parsed data
        state = initial_state
        (goal_pos, goal_not) = goals
        h_value = self.h(actions, state, goals)
        print("Value of %s is: %f" % (type(self.h).__name__, h_value))
        return None


if __name__ == '__main__':  # pragma: no cover
    import sys
    domain = sys.argv[1]
    problem = sys.argv[2]
    planner = HeuristicPlanner()
    plan, _ = planner.solve_file(domain, problem)
