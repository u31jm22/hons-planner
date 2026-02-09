#!/usr/bin/env python
# Four spaces as indentation [no tabs]

from pddl.pddl_parser import PDDLParser
from pddl.state import applicable
from pddl.benchmark import PlanningBenchmark, InstanceStats
from pddl.visualiser import Visualiser
import time


class PDDLPlanner:

    planner_version = 'v2121.1'  # TODO Change this every year

    def __init__(self, verbose: bool = False,  collect_stats: bool = False, 
                 visualise: bool = False):
        self.verbose = verbose
        self.collect_benchmark = collect_stats
        self.stats: InstanceStats = None
        self.visualise = visualise
        self.visualiser = None

    # -----------------------------------------------
    # Solve
    # -----------------------------------------------

    def solve_file(self, domainfile, problemfile, preprocessor=None):
        if self.collect_benchmark:
            self.stats = PlanningBenchmark().get_instance(domainfile, problemfile)

        # Parser
        start_time = time.time()
        if self.verbose:
            print("Parsing domain: '%s' problem '%s" % (domainfile, problemfile))
        parser = PDDLParser(self.verbose)
        parser.parse_domain(domainfile)
        parser.parse_problem(problemfile)
        # Test if first state is not the goal
        if applicable(parser.state, parser.positive_goals, parser.negative_goals):
            return [], 0
        # Grounding process
        if self.verbose:
            print("Grounding")
        ground_actions = parser.grounding()
        if preprocessor:
            print("%d unprocessed actions" % len(ground_actions))
            ground_actions = preprocessor.preprocess_actions(ground_actions, parser.state, (parser.positive_goals, parser.negative_goals))
            print("%d preprocessed actions" % len(ground_actions))

        if self.visualise:
            self.visualiser = Visualiser(ground_actions, (parser.positive_goals, parser.negative_goals))

        if self.stats: self.stats.action_space = len(ground_actions)  # compute stats
        plan = self.solve(ground_actions, parser.state, (parser.positive_goals, parser.negative_goals))
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

    def solve(self, domain, initial_state, goals):
        raise NotImplementedError("PDDL Planners need to implement solve")
