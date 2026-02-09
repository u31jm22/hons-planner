#!/usr/bin/env python
# Four spaces as indentation [no tabs]

import sys
import os
import unittest

from pddl.pddl_parser import PDDLParser
from pddl.pddl_preprocessor import RPGReachabilityPreprocessor
from pddl.val import Validator
from pddl.intention import IntentionPlanner, AgentDesire, HeuristicPlannerWrapper, merge_desires
from pddl.intention_parser import IntentionParser
from pddl.heuristic_planner import HeuristicPlanner
from pddl.delete_relaxation_h import AdditiveHeuristic
from pddl.landmarkh import LMCutHeuristic, NaiveLandmarkHeuristic
from tests import test_pddl_constants as pddl_constants
from tests import test_pddl_intention_constants as constants


class TestIntentionPlanner(unittest.TestCase):

    def test_solve_folder(self):
        planner = IntentionPlanner(collect_stats=True, heuristic=AdditiveHeuristic())
        # TODO Refactor the following method to use the constants properly
        plan, time = planner.solve_folder("domain.pddl", constants.prodcell_gp0)
        self.assertIsNotNone(plan)
        self.assertGreater(time, 0)
        # TODO Add tests for the plans as well

    def test_solve_file(self):
        planner = IntentionPlanner(collect_stats=True, heuristic=AdditiveHeuristic())
        ints, time = planner.solve_file(constants.blk, constants.pb1_blk)
        self.assertIsNotNone(ints)
        self.assertGreater(time, 0)

        planner = IntentionPlanner(collect_stats=True, heuristic=AdditiveHeuristic())
        ints, time = planner.solve_file(constants.blk, constants.pb3_blk)
        self.assertIsNotNone(ints)
        self.assertEqual(len(ints[0].plan), 0)

    def test_solve_with_preprocessor(self):
        preprocessor = RPGReachabilityPreprocessor()
        planner = IntentionPlanner(collect_stats=True, heuristic=AdditiveHeuristic())
        ints, time = planner.solve_file(constants.blk, constants.pb1_blk, preprocessor=preprocessor)
        self.assertIsNotNone(ints)
        self.assertGreater(time, 0)

        preprocessor = RPGReachabilityPreprocessor()
        planner = IntentionPlanner(collect_stats=True, heuristic=AdditiveHeuristic())
        ints, time = planner.solve_file(constants.blk, constants.pb3_blk, preprocessor=preprocessor)
        self.assertIsNotNone(ints)
        self.assertEqual(len(ints[0].plan), 0)

    def test_solve_dinner_intentions(self):
        parser = PDDLParser()
        parser.parse_domain(pddl_constants.dinner)
        parser.parse_problem(pddl_constants.pb1_dinner)
        # Add asserts here
        ground_actions = parser.grounding()
        self.assertIsNotNone(ground_actions)
        goals = (parser.positive_goals, parser.negative_goals)
        desire1 = AgentDesire(frozenset([]), (goals[0], frozenset([])), 1)  # One desire is dinner and present
        desire2 = AgentDesire(frozenset([]), (frozenset([]), goals[1]), 2)  # Another desire is not garbage
        desires = [desire1, desire2]

        planner = IntentionPlanner(collect_stats=True)
        intentions = planner.intention_plan(ground_actions, parser.state, desires)
        self.assertIsNotNone(intentions)
        self.assertIsInstance(intentions, list)
        # Check that we got plans for every intentions
        self.assertEqual(len(intentions), 2)
        val = Validator()
        # Check that all intentions are valid
        for intention in intentions:
            self.assertIn(intention.desire, desires)
            valid_intention = val.validate(ground_actions, parser.state, intention.desire.desire[0], intention.desire.desire[1], intention.plan)
            self.assertTrue(valid_intention)

        # Test proper intention problem
        parser = IntentionParser()
        parser.parse_domain(constants.dinner)
        parser.parse_problem(constants.pb1_dinner)
        # Add asserts here
        ground_actions = parser.grounding()
        self.assertIsNotNone(ground_actions)
        
        planner = IntentionPlanner(collect_stats=True)
        intentions = planner.intention_plan(ground_actions, parser.state, parser.desires)
        self.assertIsNotNone(intentions)
        self.assertIsInstance(intentions, list)
        # Check that we got plans for every intentions
        self.assertEqual(len(intentions), 2)
        val = Validator()
        # Check that all intentions are valid
        for intention in intentions:
            self.assertIn(intention.desire, parser.desires)
            valid_intention = val.validate(ground_actions, parser.state, intention.desire.desire[0], intention.desire.desire[1], intention.plan)
            self.assertTrue(valid_intention)

        # Testing conflicting intentions
        # Reset parser
        parser = PDDLParser()
        parser.parse_domain(pddl_constants.dinner)
        parser.parse_problem(pddl_constants.pb1_dinner)
        ground_actions = parser.grounding()
        # Having dinner, present, not garbage, quiet and clean is not possible
        desire3 = AgentDesire(frozenset(), parser.string_to_formula("(and (clean) (quiet))"), 2)
        desires.append(desire3)
        planner = IntentionPlanner()
        intentions = planner.intention_plan(ground_actions, parser.state, desires)
        self.assertEqual(len(intentions), 2)
        for intention in intentions:
            self.assertNotEqual(desire3, intention.desire)  # The inconsistent intention should not be there
            self.assertIn(intention.desire, desires)
            valid_intention = val.validate(ground_actions, parser.state, intention.desire.desire[0], intention.desire.desire[1], intention.plan)
            self.assertTrue(valid_intention)

    @unittest.skipIf("GITHUB_RUN_ID" in os.environ, "Don't test this in Github")
    def test_solve_satellite_intentions(self):  # pragma: no cover
        parser = IntentionParser()
        parser.parse_domain(constants.satellite)
        parser.parse_problem(constants.pb1_satellite)
        # Add asserts here
        ground_actions = parser.grounding()
        self.assertIsNotNone(ground_actions)

        planner = IntentionPlanner(collect_stats=True, heuristic=NaiveLandmarkHeuristic())
        intentions = planner.intention_plan(ground_actions, parser.state, parser.desires)
        self.assertIsNotNone(intentions)
        self.assertIsInstance(intentions, list)
        # Check that we got plans for every intentions
        self.assertEqual(len(intentions), 2)
        val = Validator()
        # Check that all intentions are valid
        for intention in intentions:
            self.assertIn(intention.desire, parser.desires)
            valid_intention = val.validate(ground_actions, parser.state, intention.desire.desire[0], intention.desire.desire[1], intention.plan)
            self.assertTrue(valid_intention)

        # Reset for problem 2
        parser = IntentionParser()
        parser.parse_domain(constants.satellite)
        parser.parse_problem(constants.pb2_satellite)
        # Add asserts here
        ground_actions = parser.grounding()
        self.assertIsNotNone(ground_actions)

        planner = IntentionPlanner(collect_stats=True, heuristic=NaiveLandmarkHeuristic())
        intentions = planner.intention_plan(ground_actions, parser.state, parser.desires)
        self.assertIsNotNone(intentions)
        self.assertIsInstance(intentions, list)
        # Check that we got plans for every intentions
        self.assertEqual(len(intentions), 2)
        val = Validator()
        # Check that all intentions are valid
        for intention in intentions:
            self.assertIn(intention.desire, parser.desires)
            valid_intention = val.validate(ground_actions, parser.state, intention.desire.desire[0], intention.desire.desire[1], intention.plan)
            self.assertTrue(valid_intention)

    def test_solve_dwr_intentions(self):
        parser = PDDLParser()
        parser.parse_domain(pddl_constants.dwr)
        parser.parse_problem(pddl_constants.pb1_dwr)
        # Add asserts here
        ground_actions = parser.grounding()
        self.assertIsNotNone(ground_actions)
        goals = (parser.positive_goals, parser.negative_goals)
        desire1 = AgentDesire(frozenset([]), goals, 1)  # One desire is all containers on pallet 2

        parser.parse_problem(pddl_constants.pb2_dwr)
        desire2 = AgentDesire(frozenset([]), goals, 2)  # Another desire is all containers on pallet 1
        desires = [desire1, desire2]

        planner = IntentionPlanner()
        intentions = planner.intention_plan(ground_actions, parser.state, desires)
        self.assertIsNotNone(intentions)
        self.assertIsInstance(intentions, list)
        # Check that we got plans for every intentions
        self.assertEqual(len(intentions), 2)
        planner = IntentionPlanner(collect_stats=True, heuristic=NaiveLandmarkHeuristic())
        intentions = planner.intention_plan(ground_actions, parser.state, desires)

        val = Validator()
        # Check that all intentions are valid
        for intention in intentions:
            self.assertIn(intention.desire, desires)
            valid_intention = val.validate(ground_actions, parser.state, intention.desire.desire[0], intention.desire.desire[1], intention.plan)
            self.assertTrue(valid_intention)

    def test_solve_blocks_intentions(self):
        parser = PDDLParser()
        parser.parse_domain(pddl_constants.blk)
        parser.parse_problem(pddl_constants.pb3_blk)
        # Add asserts here
        ground_actions = parser.grounding()
        self.assertIsNotNone(ground_actions)
        goals = (parser.positive_goals, parser.negative_goals)
        desire1 = AgentDesire(frozenset([]), goals, 1)  # Original desire
        desire2 = AgentDesire(frozenset([]), parser.string_to_formula("(and (on b c) (on c a))"), 1)  # Second desire
        desires = [desire1, desire2]

        planner = IntentionPlanner()
        intentions = planner.intention_plan(ground_actions, parser.state, desires)
        self.assertIsNotNone(intentions)
        self.assertIsInstance(intentions, list)
        # Check that we got plans for every intentions
        self.assertEqual(len(intentions), 2)
        print(intentions)

        val = Validator()
        # Check that all intentions are valid
        for intention in intentions:
            self.assertIn(intention.desire, desires)
            valid_intention = val.validate(ground_actions, parser.state, intention.desire.desire[0], intention.desire.desire[1], intention.plan)
            self.assertTrue(valid_intention)

    # @unittest.skipIf(sys.platform.startswith("linux"), "Do not test in CI to avoid wasting credits")
    @unittest.skipIf("GITHUB_RUN_ID" in os.environ, "Don't test this in Github")
    def test_solve_prodcell_intentions(self):  # pragma: no cover
        parser = IntentionParser()
        parser.parse_intention_planning_from_gp(constants.prodcell_gp0)
        ground_actions = parser.grounding()
        self.assertIsNotNone(ground_actions)

        # planner = IntentionPlanner(heuristic=LMCutHeuristic())
        planner = IntentionPlanner(heuristic=NaiveLandmarkHeuristic())
        # planner = IntentionPlanner()
        intentions = planner.intention_plan(ground_actions, parser.state, parser.desires)
        self.assertIsNotNone(intentions)
        self.assertEqual(len(intentions), 3)
        print(intentions)

    def test_heuristic_planner_wrapper(self):
        planner_wrapper = HeuristicPlannerWrapper(verbose=True, collect_stats=True)
        intentions, time = planner_wrapper.solve_file(constants.prodcell, constants.prodcell_pb2)
        self.assertIsNotNone(intentions)
        self.assertGreater(len(intentions), 0)

        intention_planner = IntentionPlanner(verbose=True, collect_stats=True)
        intentions2, time2 = intention_planner.solve_file(constants.prodcell, constants.prodcell_pb2)

        self.assertIsNotNone(intentions2)
        self.assertGreater(len(intentions2), 0)

        print(intentions)
        print(intentions2)
        self.assertEqual(len(intentions), len(intentions2))

        self.assertEqual(len(intentions[0].plan), len(intentions2[0].plan))
        for action1, action2 in zip(intentions[0].plan, intentions2[0].plan):
            self.assertEqual(action1, action2)

        self.assertEqual(len(intentions[1].plan), len(intentions2[1].plan))
        print(intentions[1].plan)
        print(intentions2[1].plan)
        # for action1, action2 in zip(intentions[1].plan, intentions2[1].plan):
        #     self.assertEqual(action1, action2)
        # plan, time = planner.solve_file(constants.prodcell, constants.prodcell_pb4)
        # self.assertIsNotNone(plan)
        # self.assertGreater(len(plan), 0)

    @unittest.skipIf("GITHUB_RUN_ID" in os.environ, "Don't test this in Github")
    def test_compare_priority_queues_dinner(self):  # pragma: no cover
        parser = PDDLParser()
        parser.parse_domain(pddl_constants.dinner)
        parser.parse_problem(pddl_constants.pb1_dinner)
        # Add asserts here
        ground_actions = parser.grounding()
        self.assertIsNotNone(ground_actions)
        goals = (parser.positive_goals, parser.negative_goals)
        desire1 = AgentDesire(frozenset([]), (goals[0], frozenset([])), 1)  # One desire is the regular goal

        desire2 = AgentDesire(frozenset(), parser.string_to_formula("(and (clean) (quiet))"), 2)
        desires = [desire1, desire2]

        intention_planner = IntentionPlanner(collect_stats=True)
        intentions = intention_planner.intention_plan(ground_actions, parser.state, desires)
        self.assertIsNotNone(intentions)
        self.assertIsInstance(intentions, list)

        all_goals = merge_desires(desires)
        heuristic_planner = HeuristicPlanner(collect_stats=True)
        plan = heuristic_planner.solve(ground_actions, parser.state, all_goals)
        self.assertIsNotNone(plan)
        self.assertIsInstance(plan, list)

        diff = intention_planner.visited - heuristic_planner.visited
        print("Different visited states %s" % diff)

    @unittest.skipIf("GITHUB_RUN_ID" in os.environ, "Don't test this in Github")
    def test_compare_priority_queues_blocks(self):  # pragma: no cover
        parser = IntentionParser()
        parser.parse_domain(constants.blk)
        parser.parse_problem(constants.pb2_blk)
        # Add asserts here
        ground_actions = parser.grounding()
        self.assertIsNotNone(ground_actions)

        desires = parser.desires

        intention_planner = IntentionPlanner(collect_stats=True)
        intentions = intention_planner.intention_plan(ground_actions, parser.state, desires)
        self.assertIsNotNone(intentions)
        self.assertIsInstance(intentions, list)

        all_goals = merge_desires(desires)
        heuristic_planner = HeuristicPlanner(collect_stats=True)
        plan = heuristic_planner.solve(ground_actions, parser.state, all_goals)
        self.assertIsNotNone(plan)
        self.assertIsInstance(plan, list)

        diff = intention_planner.visited - heuristic_planner.visited
        print("Different visited states %s" % diff)

    # @unittest.skipIf("GITHUB_RUN_ID" in os.environ, "Don't test this in Github")
    # def test_intention_plan_refactor_long(self):
    #     parser = IntentionParser()
    #     parser.parse_intention_planning_from_gp(constants.prodcell_gp0)
    #     ground_actions = parser.grounding()
    #     self.assertIsNotNone(ground_actions)

    #     planner = IntentionPlanner(collect_stats=True)
    #     planner.stats = PlanningBenchmark().get_instance("mono-domain", "mono-problem")
    #     intentions = planner.mono_intention_plan(ground_actions, parser.state, parser.desires)
    #     self.assertIsNotNone(intentions)
    #     self.assertEqual(len(intentions), 3)
    #     print(intentions)

    #     refactored_planner = IntentionPlanner(collect_stats=True)
    #     refactored_planner.stats = PlanningBenchmark().get_instance("refac-domain", "refac-problem")
    #     intentions2 = refactored_planner.intention_plan(ground_actions, parser.state, parser.desires)
    #     self.assertIsNotNone(intentions2)
    #     self.assertEqual(len(intentions2), 3)
    #     print(intentions2)

    #     self.assertEqual(intentions, intentions2)
    #     self.assertEqual(planner.stats.nodes_first, refactored_planner.stats.nodes_first)
    #     self.assertEqual(planner.stats.nodes, refactored_planner.stats.nodes)

    # For posterity I kept the tests as well as the commented out code.

    # def test_intention_plan_refactor(self):
    #     parser = PDDLParser()
    #     parser.parse_domain(pddl_constants.blk)
    #     parser.parse_problem(pddl_constants.pb3_blk)
    #     # Add asserts here
    #     ground_actions = parser.grounding()
    #     self.assertIsNotNone(ground_actions)
    #     goals = (parser.positive_goals, parser.negative_goals)
    #     desire1 = AgentDesire(frozenset([]), goals, 1)  # Original desire
    #     desire2 = AgentDesire(frozenset([]), parser.string_to_formula("(and (on b c) (on c a))"), 1)  # Second desire
    #     desires = [desire1, desire2]

    #     planner = IntentionPlanner(collect_stats=True)
    #     planner.stats = PlanningBenchmark().get_instance("mono-domain", "mono-problem")
    #     intentions = planner.mono_intention_plan(ground_actions, parser.state, desires)
    #     self.assertIsNotNone(intentions)
    #     self.assertEqual(len(intentions), 2)
    #     print(intentions)

    #     refactored_planner = IntentionPlanner(collect_stats=True)
    #     refactored_planner.stats = PlanningBenchmark().get_instance("refac-domain", "refac-problem")
    #     intentions2 = refactored_planner.intention_plan(ground_actions, parser.state, desires)
    #     self.assertIsNotNone(intentions2)
    #     self.assertEqual(len(intentions2), 2)
    #     print(intentions2)

    #     self.assertFalse(intentions is intentions2)
    #     self.assertEqual(intentions, intentions2)
    #     self.assertEqual(planner.stats.nodes_first, refactored_planner.stats.nodes_first)
    #     self.assertEqual(planner.stats.nodes, refactored_planner.stats.nodes)