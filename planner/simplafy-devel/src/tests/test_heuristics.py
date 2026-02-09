#!/usr/bin/env python
# Four spaces as indentation [no tabs]

import sys
import unittest
from pddl.pddl_planner import PDDLPlanner
from pddl.pddl_parser import PDDLParser
from pddl.bfs_planner import BFSPlanner
from pddl.heuristic_planner import HeuristicPlanner
from pddl.heuristic import Heuristic
from pddl.delete_relaxation_h import MaxHeuristic, AdditiveHeuristic, DeleteRelaxationHeuristic, CriticalPathHeuristic, NaiveCriticalPathHeuristic, FastForwardHeuristic
from pddl.benchmark import PlanningBenchmark, InstanceStats
from pddl.landmarkh import NaiveLandmarkHeuristic, LMCutHeuristic
from pddl.state import apply, applicable, stateToLisp


class TestHeuristics(unittest.TestCase):
    blocks = 'examples/blocksworld/blocksworld.pddl'
    blocks_pb = ['examples/blocksworld/pb%d.pddl' % i for i in range(1, 16)]
    pb2lecture_blocksworld = "examples/blocksworld/pb2lecture.pddl"

    dinner = "examples/dinner/dinner.pddl"
    pb1_dinner = "examples/dinner/pb1.pddl"

    dwr = "examples/dwr/dwr.pddl"
    pb1_dwr = "examples/dwr/pb1.pddl"
    pb2_dwr = "examples/dwr/pb2.pddl"

    tsp = "examples/tsp/tsp.pddl"
    pb1_tsp = "examples/tsp/pb1.pddl"
    pb2_tsp = "examples/tsp/pb2.pddl"

    dinner = "examples/dinner/dinner.pddl"
    pb1_dinner = "examples/dinner/pb1.pddl"

    dompteur = "examples/dompteur/dompteur.pddl"
    pb1_dompteur = "examples/dompteur/pb1.pddl"

    logistics = "examples/logistics/logistics.pddl"
    pb1_logistics = "examples/logistics/pb1.pddl"
    pb2_logistics = "examples/logistics/pb2.pddl"

    hanoi = "examples/hanoi/hanoi.pddl"
    hanoi_pb = ['examples/hanoi/pb%d.pddl' % i for i in range(1, 6)]    

    prodcell = "examples/prodcell/domain.pddl"
    pb1_prodcell = "examples/prodcell/pb01.pddl"

    def parse_domain_problem(self, domain, problem):
        parser = PDDLParser()
        parser.parse_domain(domain)
        parser.parse_problem(problem)
        # Grounding process
        actions = []
        for action in parser.actions:
            for act in action.groundify(parser.objects, parser.types):
                actions.append(act)
        return parser, actions

    def check_heuristic(self, domain, problem, h, expected):
        parser, actions = self.parse_domain_problem(domain, problem)
        v = h.h(actions, parser.state, (parser.positive_goals, parser.negative_goals))
        print("Expected " + str(expected) + ", got:", str(v) + ('. Correct!' if v == expected else '. False!'))
        self.assertEqual(expected, v)

    def check_float_heuristic(self, domain, problem, h, expected):
        parser, actions = self.parse_domain_problem(domain, problem)
        v = h.h(actions, parser.state, (parser.positive_goals, parser.negative_goals))
        print("Expected " + str(expected) + ", got:", str(v) + ('. Correct!' if v == expected else '. False!'))
        self.assertAlmostEqual(expected, v, 1)

    def run_bfs_benchmark(self, probs=15):
        benchmark = PlanningBenchmark()
        for i in range(0, probs):
            planner = BFSPlanner()
            planner.collect_benchmark = True
            print("Benchmarking Blocks world pb%i.pddl" % (i + 1))
            planner.solve_file(TestHeuristics.blocks, TestHeuristics.blocks_pb[i])

        hActions, hTime = benchmark.get_stats(TestHeuristics.blocks, xaxis='action', stat='time', approach='BFS')
        hActions, hNodes = benchmark.get_stats(TestHeuristics.blocks, xaxis='action', stat='nodes', approach='BFS')
        hActions, hCalls = benchmark.get_stats(TestHeuristics.blocks, xaxis='action', stat='h_calls', approach='BFS')
        print('Actions x Time: %s' % [p for p in zip(hActions, hTime)])
        print('Actions x Nodes: %s' % [p for p in zip(hActions, hNodes)])
        print('Actions x Calls: %s' % [p for p in zip(hActions, hCalls)])

        return hActions, hTime, hNodes, hCalls

    def run_h_benchmark(self, probs=15, HeuristicClass=MaxHeuristic, name="MaxH"):
        benchmark = PlanningBenchmark()
        for i in range(0, probs):
            planner = HeuristicPlanner(heuristic=HeuristicClass(
                stats=benchmark.get_instance(domain_name=TestHeuristics.blocks, 
                                             problem_name=TestHeuristics.blocks_pb[i - 1])))
            planner.collect_benchmark = True
            print("Benchmarking Blocks world pb%i.pddl" % (i+1))
            planner.solve_file(TestHeuristics.blocks, TestHeuristics.blocks_pb[i])

        hActions, hTime = benchmark.get_stats(TestHeuristics.blocks, xaxis='action', stat='time',
                                              approach=name)
        hActions, hNodes = benchmark.get_stats(TestHeuristics.blocks, xaxis='action', stat='nodes',
                                               approach=name)
        hActions, hCalls = benchmark.get_stats(TestHeuristics.blocks, xaxis='action',
                                               stat='h_calls', approach=name)
        print('Actions x Time ({name}): %s' % [p for p in zip(hActions, hTime)])
        print('Actions x Nodes ({name}): %s' % [p for p in zip(hActions, hNodes)])
        print('Actions x Calls ({name}): %s' % [p for p in zip(hActions, hCalls)])

        return hActions, hTime, hNodes, hCalls

    def run_maxh_benchmark(self, probs=15):
        benchmark = PlanningBenchmark()
        for i in range(0, probs):
            planner = HeuristicPlanner(heuristic=MaxHeuristic(
                stats=benchmark.get_instance(domain_name=TestHeuristics.blocks, 
                                             problem_name=TestHeuristics.blocks_pb[i - 1])))
            planner.collect_benchmark = True
            print("Benchmarking Blocks world pb%i.pddl" % (i+1))
            planner.solve_file(TestHeuristics.blocks, TestHeuristics.blocks_pb[i])

        hActions, hTime = benchmark.get_stats(TestHeuristics.blocks, xaxis='action', stat='time',
                                              approach='MaxH')
        hActions, hNodes = benchmark.get_stats(TestHeuristics.blocks, xaxis='action', stat='nodes',
                                               approach='MaxH')
        hActions, hCalls = benchmark.get_stats(TestHeuristics.blocks, xaxis='action',
                                               stat='h_calls', approach='MaxH')
        print('Actions x Time (MaxH): %s' % [p for p in zip(hActions, hTime)])
        print('Actions x Nodes (MaxH): %s' % [p for p in zip(hActions, hNodes)])
        print('Actions x Calls (MaxH): %s' % [p for p in zip(hActions, hCalls)])

        return hActions, hTime, hNodes, hCalls

    def run_addh_benchmark(self, probs=15):
        benchmark = PlanningBenchmark()
        for i in range(0, probs):
            planner = HeuristicPlanner(heuristic=AdditiveHeuristic(
                stats=benchmark.get_instance(domain_name=TestHeuristics.blocks,
                                             problem_name=TestHeuristics.blocks_pb[i - 1])))
            planner.collect_benchmark = True
            print("Benchmarking Blocks world pb%i.pddl" % (i + 1))
            planner.solve_file(TestHeuristics.blocks, TestHeuristics.blocks_pb[i])

        hActions, hTime = benchmark.get_stats(TestHeuristics.blocks, xaxis='action', stat='time',
                                              approach='AddH')
        hActions, hNodes = benchmark.get_stats(TestHeuristics.blocks, xaxis='action', stat='nodes',
                                               approach='AddH')
        hActions, hCalls = benchmark.get_stats(TestHeuristics.blocks, xaxis='action',
                                               stat='h_calls', approach='AddH')
        print('Actions x Time (AddH): %s' % [p for p in zip(hActions, hTime)])
        print('Actions x Nodes (AddH): %s' % [p for p in zip(hActions, hNodes)])
        print('Actions x Calls (AddH): %s ' % [p for p in zip(hActions, hCalls)])

        return hActions, hTime, hNodes, hCalls

    def test_bfs_baseline_stats(self):
        hActionsBFS, hTimeBFS, hNodesBFS, hCallsBFS = self.run_bfs_benchmark(5)

    def test_maxh_stats(self):
        hActionsMaxH, hTimeMaxH, hNodesMaxH, hCallsMaxH = self.run_maxh_benchmark(6)

    def test_addh_stats(self):
        hActionsAddH, hTimeAddH, hNodesAddH, hCallsAddH = self.run_addh_benchmark(6)

    @unittest.skipUnless(sys.platform.startswith("darwin"), "This long test is only meant to be done locally")
    def test_all_heuristics_stats(self):
        self.run_h_benchmark(probs=7, HeuristicClass=MaxHeuristic, name="MaxH")
        self.run_h_benchmark(probs=7, HeuristicClass=AdditiveHeuristic, name="AddH")
        self.run_h_benchmark(probs=7, HeuristicClass=FastForwardHeuristic, name="FFH")

    def test_max_h(self):
        h = MaxHeuristic()
        self.check_heuristic(TestHeuristics.dwr, TestHeuristics.pb1_dwr, h, 6)
        self.check_heuristic(TestHeuristics.dwr, TestHeuristics.pb2_dwr, h, 0)
        self.check_heuristic(TestHeuristics.tsp, TestHeuristics.pb1_tsp, h, 2)
        self.check_heuristic(TestHeuristics.tsp, TestHeuristics.pb2_tsp, h, 2)
        self.check_heuristic(TestHeuristics.dompteur, TestHeuristics.pb1_dompteur, h, 2)
        self.check_heuristic(TestHeuristics.logistics, TestHeuristics.pb1_logistics, h, 4)
        self.check_heuristic(TestHeuristics.dinner, TestHeuristics.pb1_dinner, h, 1)
        self.check_heuristic(TestHeuristics.blocks, TestHeuristics.blocks_pb[0], h, 2)
        self.check_heuristic(TestHeuristics.blocks, TestHeuristics.blocks_pb[1], h, 3)
        self.check_heuristic(TestHeuristics.blocks, TestHeuristics.blocks_pb[2], h, 2)
        self.check_heuristic(TestHeuristics.blocks, TestHeuristics.blocks_pb[3], h, 5)
        self.check_heuristic(TestHeuristics.blocks, TestHeuristics.blocks_pb[4], h, 2)
        self.check_heuristic(TestHeuristics.blocks, TestHeuristics.blocks_pb[5], h, 2)
        self.check_heuristic(TestHeuristics.prodcell, TestHeuristics.pb1_prodcell, h, 3)

    def test_additive_h(self):
        h = AdditiveHeuristic()
        self.check_heuristic(TestHeuristics.dwr, TestHeuristics.pb1_dwr, h, 38)
        self.check_heuristic(TestHeuristics.dwr, TestHeuristics.pb2_dwr, h, 0)
        self.check_heuristic(TestHeuristics.tsp, TestHeuristics.pb1_tsp, h, 8)
        self.check_heuristic(TestHeuristics.tsp, TestHeuristics.pb2_tsp, h, 8)
        self.check_heuristic(TestHeuristics.dompteur, TestHeuristics.pb1_dompteur, h, 2)
        self.check_heuristic(TestHeuristics.logistics, TestHeuristics.pb1_logistics, h, 7)
        self.check_heuristic(TestHeuristics.logistics, TestHeuristics.pb2_logistics, h, 10)
        self.check_heuristic(TestHeuristics.dinner, TestHeuristics.pb1_dinner, h, 2)
        self.check_heuristic(TestHeuristics.blocks, TestHeuristics.blocks_pb[0], h, 2)
        self.check_heuristic(TestHeuristics.blocks, TestHeuristics.blocks_pb[1], h, 6)
        self.check_heuristic(TestHeuristics.blocks, TestHeuristics.blocks_pb[2], h, 4)
        self.check_heuristic(TestHeuristics.blocks, TestHeuristics.blocks_pb[3], h, 5)
        self.check_heuristic(TestHeuristics.blocks, TestHeuristics.blocks_pb[4], h, 8)
        self.check_heuristic(TestHeuristics.blocks, TestHeuristics.blocks_pb[5], h, 10)

    # @unittest.skipIf(sys.platform.startswith("linux"), "Do not test in Travis since I know this is broken")
    # @unittest.skip
    @unittest.expectedFailure
    def test_critical_path_h(self):  # NB: This heuristic caches stuff, so you need to reinstantiate it for every problem you aim to call it
        # First, sanity test ot
        h = CriticalPathHeuristic(2)
        parser, actions = self.parse_domain_problem(TestHeuristics.dwr, TestHeuristics.pb2_dwr)
        # print(repr(actions[0]))
        v = h.h(actions, parser.state, (parser.positive_goals, parser.negative_goals))
        self.assertTrue(h.reached(0, parser.positive_goals))
        self.check_heuristic(TestHeuristics.dwr, TestHeuristics.pb2_dwr, h, 0)

        h = CriticalPathHeuristic(2)
        parser, actions = self.parse_domain_problem(TestHeuristics.dwr, TestHeuristics.pb2_dwr)
        v = h.h(actions, parser.state, (parser.positive_goals, parser.negative_goals))
        print("Critical Path = %f" % v)
        h = NaiveCriticalPathHeuristic(2)
        v = h.h(actions, parser.state, (parser.positive_goals, parser.negative_goals))
        print("Naive Critical Path = %f" % v)
        self.check_heuristic(TestHeuristics.dwr, TestHeuristics.pb1_dwr, h, 15)

        h = CriticalPathHeuristic(2)
        self.check_heuristic(TestHeuristics.dwr, TestHeuristics.pb2_dwr, h, 0)
        h = CriticalPathHeuristic(2)
        self.check_heuristic(TestHeuristics.tsp, TestHeuristics.pb1_tsp, h, 2)
        h = CriticalPathHeuristic(2)
        self.check_heuristic(TestHeuristics.tsp, TestHeuristics.pb2_tsp, h, 2)
        h = CriticalPathHeuristic(2)
        self.check_heuristic(TestHeuristics.dompteur, TestHeuristics.pb1_dompteur, h, 3)
        h = CriticalPathHeuristic(1)
        self.check_heuristic(TestHeuristics.logistics, TestHeuristics.pb1_logistics, h, 4)
        h = CriticalPathHeuristic(2)
        self.check_heuristic(TestHeuristics.dinner, TestHeuristics.pb1_dinner, h, 2)
        h = CriticalPathHeuristic(2)
        self.check_heuristic(TestHeuristics.blocks, TestHeuristics.blocks_pb[0], h, 2)
        h = CriticalPathHeuristic(2)
        self.check_heuristic(TestHeuristics.blocks, TestHeuristics.blocks_pb[1], h, 5)
        h = CriticalPathHeuristic(2)
        self.check_heuristic(TestHeuristics.blocks, TestHeuristics.blocks_pb[2], h, 4)
        h = CriticalPathHeuristic(2)
        self.check_heuristic(TestHeuristics.blocks, TestHeuristics.blocks_pb[3], h, 5)
        h = CriticalPathHeuristic(2)
        self.check_heuristic(TestHeuristics.blocks, TestHeuristics.blocks_pb[4], h, 8)
        h = CriticalPathHeuristic(2)
        self.check_heuristic(TestHeuristics.blocks, TestHeuristics.blocks_pb[5], h, 10)

    # @unittest.skip
    def test_delete_relaxation_heuristic(self):
        h = DeleteRelaxationHeuristic()
        # self.check_heuristic(TestHeuristics.dwr, TestHeuristics.pb1_dwr, h, 6)  # TODO This gets the heuristic in a loop somehow
        self.check_heuristic(TestHeuristics.dwr, TestHeuristics.pb2_dwr, h, 0)
        self.check_heuristic(TestHeuristics.tsp, TestHeuristics.pb1_tsp, h, 5)
        self.check_heuristic(TestHeuristics.tsp, TestHeuristics.pb2_tsp, h, 5)
        self.check_heuristic(TestHeuristics.dompteur, TestHeuristics.pb1_dompteur, h, 2)
        self.check_heuristic(TestHeuristics.logistics, TestHeuristics.pb1_logistics, h, 5)
        self.check_heuristic(TestHeuristics.logistics, TestHeuristics.pb2_logistics, h, 5)
        self.check_heuristic(TestHeuristics.dinner, TestHeuristics.pb1_dinner, h, float("inf"))
        self.check_heuristic(TestHeuristics.blocks, TestHeuristics.blocks_pb[0], h, 2)
        self.check_heuristic(TestHeuristics.blocks, TestHeuristics.blocks_pb[1], h, 5)
        self.check_heuristic(TestHeuristics.blocks, TestHeuristics.blocks_pb[2], h, 4)
        self.check_heuristic(TestHeuristics.blocks, TestHeuristics.blocks_pb[3], h, 5)
        self.check_heuristic(TestHeuristics.blocks, TestHeuristics.blocks_pb[4], h, 8)
        # self.check_heuristic(TestHeuristics.blocks, TestHeuristics.blocks_pb[5], h, 2)  # Loop?
        self.check_heuristic(TestHeuristics.hanoi, TestHeuristics.hanoi_pb[2], h, 5)

    def test_delete_relaxation_heuristic_neighbourhood(self):
        """"Test the blocks world example for the delete relaxation heuristics classes """
        parser = PDDLParser()
        parser.parse_domain(TestHeuristics.blocks)
        parser.parse_problem(TestHeuristics.pb2lecture_blocksworld)
        self.assertEqual(parser.problem_name, 'pb2lecture')
        print(parser.types)
        # planner = HeuristicPlanner()
        h = DeleteRelaxationHeuristic()
        grounded_actions = parser.grounding()
        state = parser.state
        hv = h.h(grounded_actions, state, (parser.positive_goals, parser.negative_goals))
        print("Original state {}, h+={}".format(stateToLisp(state), hv))
        for act in grounded_actions:
            if applicable(state, act.positive_preconditions, act.negative_preconditions):
                new_state = apply(state, act.add_effects, act.del_effects)
                hv = h.h(grounded_actions, new_state, (parser.positive_goals, parser.negative_goals))
                print("Action: {} State: {} h+={}".format(act, stateToLisp(new_state), hv))

    def test_fast_forward_heuristic(self):
        h = FastForwardHeuristic()
        self.check_heuristic(TestHeuristics.dwr, TestHeuristics.pb1_dwr, h, 16)
        self.check_heuristic(TestHeuristics.dwr, TestHeuristics.pb2_dwr, h, 0)
        self.check_heuristic(TestHeuristics.tsp, TestHeuristics.pb1_tsp, h, 5)
        self.check_heuristic(TestHeuristics.tsp, TestHeuristics.pb2_tsp, h, 5)
        self.check_heuristic(TestHeuristics.dompteur, TestHeuristics.pb1_dompteur, h, 2)
        self.check_heuristic(TestHeuristics.logistics, TestHeuristics.pb1_logistics, h, 5)
        self.check_heuristic(TestHeuristics.logistics, TestHeuristics.pb2_logistics, h, 5)
        self.check_heuristic(TestHeuristics.dinner, TestHeuristics.pb1_dinner, h, 2)
        self.check_heuristic(TestHeuristics.blocks, TestHeuristics.blocks_pb[0], h, 2)
        self.check_heuristic(TestHeuristics.blocks, TestHeuristics.blocks_pb[1], h, 5)
        self.check_heuristic(TestHeuristics.blocks, TestHeuristics.blocks_pb[2], h, 4)
        self.check_heuristic(TestHeuristics.blocks, TestHeuristics.blocks_pb[3], h, 5)
        self.check_heuristic(TestHeuristics.blocks, TestHeuristics.blocks_pb[4], h, 8)
        self.check_heuristic(TestHeuristics.blocks, TestHeuristics.blocks_pb[5], h, 10)

    def test_naive_landmark_heuristic(self):
        # TODO These tests are plain evil (and the implementation is probably wrong)
        h = NaiveLandmarkHeuristic()
        self.check_float_heuristic(TestHeuristics.dwr, TestHeuristics.pb1_dwr, h, 9)

        h = NaiveLandmarkHeuristic()
        self.check_float_heuristic(TestHeuristics.blocks, TestHeuristics.blocks_pb[1], h, 2.5)
        h = NaiveLandmarkHeuristic()
        self.check_float_heuristic(TestHeuristics.blocks, TestHeuristics.blocks_pb[2], h, 1.66)
        h = NaiveLandmarkHeuristic()
        self.check_float_heuristic(TestHeuristics.blocks, TestHeuristics.blocks_pb[3], h, 3.33)
        h = NaiveLandmarkHeuristic()
        self.check_float_heuristic(TestHeuristics.blocks, TestHeuristics.blocks_pb[4], h, 3.33)
        h = NaiveLandmarkHeuristic()
        self.check_float_heuristic(TestHeuristics.blocks, TestHeuristics.blocks_pb[5], h, 4.16)

    def test_landmark_cut_heuristic(self):
        # NOTE: I have written these test cases with the expected output based on what 
        # Pyperplan produces for the same domain and problem specification.

        h = LMCutHeuristic()
        # Dinner problem (this is to check how LMcut handles absence of preconditions)
        self.check_heuristic(TestHeuristics.dinner, TestHeuristics.pb1_dinner, h, 2)

        # DWR problems
        h = LMCutHeuristic()
        self.check_float_heuristic(TestHeuristics.dwr, TestHeuristics.pb1_dwr, h, 10.0)
        self.check_float_heuristic(TestHeuristics.dwr, TestHeuristics.pb2_dwr, h, 0.0)

        # Blocksworld problems (note the index refers to problem pb{i+1}.pddl)
        self.check_heuristic(TestHeuristics.blocks, TestHeuristics.blocks_pb[0], h, 2)
        self.check_heuristic(TestHeuristics.blocks, TestHeuristics.blocks_pb[1], h, 5)
        self.check_heuristic(TestHeuristics.blocks, TestHeuristics.blocks_pb[2], h, 4)
        self.check_heuristic(TestHeuristics.blocks, TestHeuristics.blocks_pb[3], h, 5)
        self.check_heuristic(TestHeuristics.blocks, TestHeuristics.blocks_pb[4], h, 8)
        self.check_heuristic(TestHeuristics.blocks, TestHeuristics.blocks_pb[5], h, 10)
        self.check_heuristic(TestHeuristics.blocks, TestHeuristics.blocks_pb[6], h, 12)
        self.check_heuristic(TestHeuristics.blocks, TestHeuristics.blocks_pb[7], h, 14)
        self.check_heuristic(TestHeuristics.blocks, TestHeuristics.blocks_pb[8], h, 16)
        self.check_heuristic(TestHeuristics.blocks, TestHeuristics.blocks_pb[9], h, 18)
        self.check_heuristic(TestHeuristics.blocks, TestHeuristics.blocks_pb[10], h, 20)

        # Logistics problems
        self.check_heuristic(TestHeuristics.logistics, TestHeuristics.pb1_logistics, h, 5)
        self.check_heuristic(TestHeuristics.logistics, TestHeuristics.pb2_logistics, h, 5)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
