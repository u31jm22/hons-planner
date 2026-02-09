#!/usr/bin/env python
# Four spaces as indentation [no tabs]

# Felipe's implementation of an intention planner based on A*
import time
from pddl.action import Action, EMPTY_SET
from pddl.benchmark import PlanningBenchmark
from pddl.delete_relaxation_h import MaxHeuristic
from pddl.heuristic_planner import HeuristicPlanner
from pddl.intention_parser import IntentionParser, AgentDesire, AgentIntention
from pddl.state import applicable, apply
from pddl.visualiser import Visualiser
from typing import List, Collection, Dict, Tuple
from heap_queue.priority_queue import PriorityQueue
from functools import reduce

INF = float("inf")


def merge_desires(desires: Collection[AgentDesire]) -> tuple:
    """Merges a collection of agent desires into a single goal."""
    positive_goals = set()
    negative_goals = set()
    for desire in desires:
        positive_goals |= desire.desire[0]
        negative_goals |= desire.desire[1]
    positive_goals = frozenset(positive_goals)
    negative_goals = frozenset(negative_goals)
    return (positive_goals, negative_goals)


class IntentionPlanner(HeuristicPlanner):

    def __init__(self, heuristic=MaxHeuristic(), verbose=False, 
                 collect_stats=False, visualise=False, PriorityQueue=PriorityQueue):
        super().__init__(heuristic=heuristic, verbose=verbose, collect_stats=collect_stats, visualise=visualise, PriorityQueue=PriorityQueue)
        self.added_actions = set()

    # -----------------------------------------------
    # Solve an intention planning problem
    # -----------------------------------------------
    def solve(self, actions: Collection[Action], initial_state: frozenset[tuple], goals: frozenset[tuple]):
        return self.intention_plan(actions, initial_state, (EMPTY_SET, goals, 0))

    def get_path(self, node: Tuple) -> List[Action]:
        full_plan = []
        while node:
            act, node = node
            # ignore dummy actions
            if act in self.added_actions:
                continue
            full_plan.insert(0, act)
        return full_plan

    def reorder_fringe(self, fringe: PriorityQueue, actions: List[Action], goals: Tuple, cost: Dict) -> PriorityQueue:
        if self.stats:
            start_time = time.time()

        new_fringe = self.PriorityQueue()
        # for old_state, old_h1, parent in fringe._heap:
        while not fringe.empty():
            previous_f, previous_g, old_state, old_h1, parent = fringe.get()
            h2 = self.h(actions, old_state, goals)
            g2 = previous_g # cost[old_state]
            f = g2 + h2
            new_fringe.put((f, g2, old_state, h2, parent))

        if self.stats:
            queue_time = time.time() - start_time
            self.stats.queue_time += queue_time
        return new_fringe

    def make_goal_achieved_action(self, goal):
        effect = str(goal)  # This should create a unique string for this goal
        add_effects = [(effect,)]
        action = Action("achieve"+effect, parameters=[],
                        positive_preconditions=goal[0], negative_preconditions=goal[1],
                        add_effects=add_effects, del_effects=EMPTY_SET)
        return action

    def solve_folder(self, domainfile, problemfolder, preprocessor=None) -> Collection:
        # TODO Sort out the nasty copy and pasting for the solve method
        if self.collect_benchmark: self.stats = PlanningBenchmark().get_instance(domainfile, problemfolder)
        # Parser
        start_time = time.time()
        parser = IntentionParser(self.verbose)
        parser.parse_intention_planning_from_gp(problemfolder, domainfile)
        # Test if first state is not the goal
        # TODO This test must include all desires
        # if applicable(parser.state, parser.positive_goals, parser.negative_goals):
        #     return [], time.time() - start_time

        # Grounding process
        ground_actions = parser.grounding()
        if preprocessor:
            if self.verbose:
                print("%d unprocessed actions" % len(ground_actions))
            ground_actions = preprocessor.preprocess_actions(ground_actions, parser.state, (parser.positive_goals, parser.negative_goals))
            if self.verbose:
                print("%d preprocessed actions" % len(ground_actions))
        if self.stats: self.stats.action_space = len(ground_actions)  # compute stats
        plan = self.intention_plan(ground_actions, parser.state, parser.desires)
        final_time = time.time() - start_time
        if self.verbose:
            print('Time: ' + str(final_time) + 's')
            if plan:
                print('plan:')
                for act in plan:
                    print('(' + act.name + ''.join(' ' + p for p in act.parameters) + ')')
            else:
                print('No plan was found')
        if self.stats: self.stats.time = final_time
        return plan, final_time

    def solve_file(self, domainfile, problemfile, preprocessor=None):
        # TODO Sort out this nasty copy and pasting
        if self.collect_benchmark: self.stats = PlanningBenchmark().get_instance(domainfile, problemfile)

        # Parser
        start_time = time.time()
        parser = IntentionParser(self.verbose)
        parser.parse_domain(domainfile)
        parser.parse_problem(problemfile)
        # Test if first state is not the goal
        # if applicable(parser.state, parser.positive_goals, parser.negative_goals):
        #     return [], 0
        # Grounding process
        ground_actions = parser.grounding()
        if preprocessor:
            positive_goals, negative_goals = merge_desires(parser.desires)
            if self.verbose:
                print("%d unprocessed actions" % len(ground_actions))
            ground_actions = preprocessor.preprocess_actions(ground_actions, parser.state, (positive_goals, negative_goals))
            if self.verbose:
                print("%d preprocessed actions" % len(ground_actions))
        
        if self.visualise:
            self.visualiser = Visualiser(ground_actions, (parser.positive_goals, parser.negative_goals))
        
        if self.stats: self.stats.action_space = len(ground_actions)  # compute stats
        intentions = self.intention_plan(ground_actions, parser.state, parser.desires)
        final_time = time.time() - start_time
        if self.stats and self.verbose:
            print('Nodes 1 %d' % self.stats.nodes_first)
            print('Nodes 2 %d' % self.stats.nodes)
        if self.verbose:
            print('Time: ' + str(final_time) + 's')
            if intentions:
                for intention in intentions:
                    print(intention.index)
                    print('plan:')
                    for act in intention.plan:
                        print('(' + act.name + ''.join(' ' + p for p in act.parameters) + ')')
            else:
                print('No plan was found')
        if self.stats: self.stats.time = final_time
        return intentions, final_time

    def intention_plan(self, actions: Collection[Action], initial_state: frozenset[Tuple], desires: List[AgentDesire]):
        # Parsed data
        state = initial_state
        intentions: List[AgentIntention] = []
        intentionJ = 0
        desireI = 0
        goals = desires[desireI].desire
        (goal_pos, goal_not) = goals
        # Search
        cost = {state: 0}
        visited = set([state])
        # If we are collecting data, store cost and visited
        if self.collect_benchmark:
            self.cost = cost
            self.visited = visited
        fringe = self.PriorityQueue()
        fringe.put((0, 0, state, self.h(actions, state, goals), None))
        if self.visualiser: self.visualiser.add_node(None, (0, state, self.h(actions, state, goals), None))
        
        state, parent = initial_state, None
        while state is not None:
            time_last = time.time()
            state, parent = self.astar_search(fringe, cost, visited, actions, state, goals, parent)
            if state is None: # State is none when we explored all the state space
                break
            full_plan = self.get_path(parent)
            if self.stats and desireI == 0:
                self.stats.nodes_first = len(visited)
            desire = desires[desireI]  # Recheck this
            intentions.append(AgentIntention(desire, full_plan))
            intentionJ += 1
            desireI += 1
            if desireI >= len(desires): # If we achieved all intentions, stop the search
                break
            new_action = self.make_goal_achieved_action(goals)
            actions = actions + [new_action]
            self.added_actions.add(new_action)
            goals = desires[desireI].desire
            new_goal_pos = reduce(frozenset.union, [goals[0], new_action.add_effects])
            goals = (new_goal_pos, goals[1])
            (goal_pos, goal_not) = goals
            # Update the fringe
            self.h.reset(actions, initial_state, goals)
            fringe = self.reorder_fringe(fringe, actions, goals, cost)

        if self.stats: 
            self.stats.nodes = len(visited)  # Collect stats
            self.stats.time_last = time.time() - time_last
        return intentions

class HeuristicPlannerWrapper(HeuristicPlanner):

    def __init__(self, heuristic=MaxHeuristic(), verbose=False, collect_stats=False, PriorityQueue=PriorityQueue):
        super().__init__(
            heuristic=heuristic,
            verbose=verbose, collect_stats=collect_stats)
        self.h = heuristic
        self.PriorityQueue = PriorityQueue
        self.added_actions = set()
    
    # TODO Refactor this nasty thing
    def make_goal_achieved_action(self, goal):
        effect = str(goal)  # This should create a unique string for this goal
        add_effects = [(effect,)]
        action = Action("achieve"+effect, parameters=[],
                        positive_preconditions=goal[0], negative_preconditions=goal[1],
                        add_effects=add_effects, del_effects=EMPTY_SET)
        return action

    # TODO Refactor this nasty thing
    def get_path(self, node: Tuple) -> List[Action]:
        full_plan = []
        while node:
            act, node = node
            # ignore dummy actions
            if act in self.added_actions:
                continue
            full_plan.insert(0, act)
        return full_plan

    # flake8: noqa: C901
    def solve_file(self, domainfile, problemfile, preprocessor=None):
        if self.collect_benchmark: self.stats = PlanningBenchmark().get_instance(domainfile, problemfile)

        # Parser
        start_time = time.time()
        parser = IntentionParser(verbose=self.verbose)
        parser.parse_domain(domainfile)
        parser.parse_problem(problemfile)
        # Transform the desires into a single goal
        positive_goals, negative_goals = merge_desires(parser.desires)

        # if self.verbose:
        #     print('Resulting goal is %s, (not) %s' % (positive_goals, negative_goals))
        # Test if first state is not the goal
        # if applicable(parser.state, parser.positive_goals, parser.negative_goals):
        #     return [], 0
        # Grounding process
        ground_actions = parser.grounding()
        if preprocessor:
            if self.verbose:
                print("%d unprocessed actions" % len(ground_actions))
            ground_actions = preprocessor.preprocess_actions(ground_actions, parser.state, (positive_goals, negative_goals))
            if self.verbose:
                print("%d preprocessed actions" % len(ground_actions))
        if self.stats: self.stats.action_space = len(ground_actions)  # compute stats

        intentions: List[AgentIntention] = []
        desires = [desire for desire in parser.desires]
        desires.sort(key=lambda d: len(d.desire[0]))
        # print("Desires %s " % desires[1].desire[0])
        # print("Cheapest Desire %s " % desires[0].desire[0])
        plan = self.solve(ground_actions, parser.state, desires[0].desire)
        intentions.append(AgentIntention(desires[0], plan))
        if self.stats:
            self.stats.nodes_first = self.stats.nodes
            if self.verbose:
                print('Nodes 1 %d' % self.stats.nodes)
        # plan = self.solve(ground_actions, parser.state, (positive_goals, negative_goals))
        new_action = self.make_goal_achieved_action(desires[0].desire)
        ground_actions = ground_actions + [new_action]
        self.added_actions.add(new_action)
        new_goal_pos = reduce(frozenset.union, [desires[1].desire[0], new_action.add_effects])
        # plan = self.solve(ground_actions, parser.state, desires[1].desire)
        self.h.reset(ground_actions, parser.state, (new_goal_pos, desires[1].desire[1]))
        # TODO: There is a corner case that this wrapper does not handle 
        # TODO: which is a second goal that requires no further actions from the first one
        
        time_last = time.time()
        plan = self.solve(ground_actions, parser.state, (new_goal_pos, desires[1].desire[1]))
        intentions.append(AgentIntention(desires[0], plan))
        if self.stats:
            # self.stats.nodes += self.stats.nodes_first
            if self.verbose:
                print('Nodes 2 %d' % self.stats.nodes)
        final_time = time.time() - start_time
        time_last = time.time() - time_last
        if self.verbose:
            print('Time: ' + str(final_time) + 's')
            if plan:
                print('plan:')
                for act in plan:
                    print('(' + act.name + ''.join(' ' + p for p in act.parameters) + ')')
            else:
                print('No plan was found')
        if self.stats: 
            self.stats.time = final_time
            self.stats.time_last = time_last
        return intentions, final_time
