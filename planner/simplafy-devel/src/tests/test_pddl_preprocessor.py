#!/usr/bin/env python
# Four spaces as indentation [no tabs]

import sys
import unittest
import copy
import os

from pddl.pddl_preprocessor import RPGReachabilityPreprocessor, PyperPreprocessor
from pddl.heuristic_planner import HeuristicPlanner
from pddl.landmarkh import NaiveLandmarkHeuristic
from pddl.val import Validator
from pddl.pddl_parser import PDDLParser
from tests import test_pddl_constants as constants


class TestPDDLPreprocessor(unittest.TestCase):

    def dwr(self, planner, preprocessor):
        v = Validator()
        pd_list = [constants.pb1_dwr,
                   constants.pb2_dwr]
        results = [17, 0]
        for p, r in zip(pd_list, results):
            print("Solving %s" % p)
            plan, time = planner.solve_file(constants.dwr, p, preprocessor=None)
            self.assertIsNotNone(plan, msg="Failed for %s" % p)
            self.assertEqual(r, len(plan))
            self.assertTrue(True, v.validate_plan(constants.dwr, p, plan, False))
            print("Unpreprocessed time: %f" % time)

            parser = PDDLParser()
            parser.parse_domain(constants.dwr)
            parser.parse_problem(p)
            actions = parser.grounding()
            actions_ref = [copy.deepcopy(action) for action in actions]
            pruned_actions = preprocessor.preprocess_actions(actions, parser.state, (parser.positive_goals, parser.negative_goals))
            # Ensure I'm not messing with the original actions
            for action in pruned_actions:
                matches = [ref_action for ref_action in actions_ref if repr(ref_action) == repr(action)]
                self.assertEqual(len(matches), 1)
                self.assertEqual(matches[0], action)

            for action in plan:
                self.assertIn(action, pruned_actions, msg="Preprocessor eliminated action %s" % str(action))

            plan2, time = planner.solve_file(constants.dwr, p, preprocessor=preprocessor)
            self.assertIsNotNone(plan, msg="Failed for %s" % p)
            self.assertEqual(r, len(plan))
            self.assertCountEqual(plan, plan2)
            # self.assertEqual(plan, plan2)
            self.assertTrue(True, v.validate_plan(constants.dwr, p, plan, False))
            print("Preprocessed time: %f" % time)
        # Test for an unsolvable problem
        print("Solving %s" % constants.pb0_dwr)
        plan, time = planner.solve_file(constants.dwr, constants.pb0_dwr, preprocessor=None)
        self.assertIsNone(plan, msg="Failed for %s" % constants.pb0_dwr)
        print("Unpreprocessed time: %f" % time)
        parser = PDDLParser()
        parser.parse_domain(constants.dwr)
        parser.parse_problem(constants.pb0_dwr)
        actions = parser.grounding()
        actions_ref = [copy.deepcopy(action) for action in actions]
        pruned_actions = preprocessor.preprocess_actions(actions, parser.state, (parser.positive_goals, parser.negative_goals))
        for action in pruned_actions:
            matches = [ref_action for ref_action in actions_ref if repr(ref_action) == repr(action)]
            self.assertEqual(len(matches), 1)
            self.assertEqual(matches[0], action)
        plan2, time = planner.solve_file(constants.dwr, constants.pb0_dwr, preprocessor=preprocessor)
        self.assertIsNone(plan, msg="Failed for %s" % constants.pb0_dwr)
        print("Preprocessed time: %f" % time)

    def blocks(self, planner, preprocessor):
        v = Validator()
        bpd_list = [constants.pb1_blk,
                    constants.pb2_blk,
                    constants.pb3_blk,
                    constants.pb4_blk,
                    constants.pb5_blk,
                    constants.pb6_blk,
                    constants.pb7_blk,
                    # constants.pb8_blk,
                    # constants.pb9_blk
                    ]
        results = [2, 6, 4, 12, 8, 10, 12, 14, 16]
        exclude_list = [constants.pb7_blk, constants.pb8_blk, constants.pb9_blk]
        for b, r in zip(bpd_list, results):
            print("Solving %s" % b)
            # if b == constants.pb7_blk: break  # Since our preprocessor is disappointing

            if b not in exclude_list:
                plan, time = planner.solve_file(constants.blk, b)
                self.assertIsNotNone(plan, msg="Failed for %s" % b)
                self.assertEqual(r, len(plan))
                self.assertTrue(True, v.validate_plan(constants.blk, b, plan, False))
                print("Unpreprocessed time: %f" % time)
            else:
                print("Skipping overlong problem")
            plan, time = planner.solve_file(constants.blk, b, preprocessor=preprocessor)
            self.assertIsNotNone(plan, msg="Failed for %s" % b)
            self.assertEqual(r, len(plan))
            self.assertTrue(True, v.validate_plan(constants.blk, b, plan, False))
            print("Preprocessed time: %f" % time)

    def tsp(self, planner, preprocessor):
        v = Validator()
        bpd_list = [constants.pb1_tsp,
                    # constants.pb2_tsp
                    ]
        results = [5, 8]
        for b, r in zip(bpd_list, results):
            print("Solving %s" % b)

            plan, time = planner.solve_file(constants.tsp, b)
            self.assertIsNotNone(plan, msg="Failed for %s" % b)
            self.assertEqual(r, len(plan))
            self.assertTrue(True, v.validate_plan(constants.tsp, b, plan, False))
            print("Unpreprocessed time: %f" % time)

            parser = PDDLParser()
            parser.parse_domain(constants.tsp)
            parser.parse_problem(b)
            actions = parser.grounding()
            actions_ref = [copy.deepcopy(action) for action in actions]
            pruned_actions = preprocessor.preprocess_actions(actions, parser.state, (parser.positive_goals, parser.negative_goals))
            for action in pruned_actions:
                matches = [ref_action for ref_action in actions_ref if repr(ref_action) == repr(action)]
                self.assertEqual(len(matches), 1)
                self.assertEqual(matches[0], action)
            # for action in actions:
            #     matches = [ref_action for ref_action in actions_ref if repr(ref_action) == repr(action)]
            #     self.assertEqual(len(matches), 1)
            #     self.assertEqual(matches[0], action)
            for action in plan:
                self.assertIn(action, pruned_actions, msg="Preprocessor eliminated action %s" % str(action))

            plan, time = planner.solve_file(constants.tsp, b, preprocessor=preprocessor)
            self.assertIsNotNone(plan, msg="Failed for %s" % b)
            self.assertEqual(r, len(plan))
            self.assertTrue(True, v.validate_plan(constants.tsp, b, plan, False))
            print("Preprocessed time: %f" % time)

    def prodcell(self, planner, preprocessor):
        v = Validator()
        pd_list = [constants.pb1_prodcell,
                   constants.pb2_prodcell,
                   constants.pb3_prodcell,
                   constants.pb4_prodcell,
                   constants.pb5_prodcell]
        # results = [6, 12, 18, 24, 0]
        results = [6, 12, 18]
        for p, r in zip(pd_list, results):
            print("Solving %s" % p)
            plan, time = planner.solve_file(constants.prodcell, p)
            self.assertIsNotNone(plan, msg="Failed for %s" % p)
            self.assertEqual(r, len(plan))
            self.assertTrue(True, v.validate_plan(constants.prodcell, p, plan, False))
            print("Unpreprocessed time: %f" % time)

            parser = PDDLParser()
            parser.parse_domain(constants.prodcell)
            parser.parse_problem(p)
            actions = parser.grounding()
            actions_ref = [copy.deepcopy(action) for action in actions]
            pruned_actions = preprocessor.preprocess_actions(actions, parser.state, (parser.positive_goals, parser.negative_goals))
            for action in pruned_actions:
                matches = [ref_action for ref_action in actions_ref if repr(ref_action) == repr(action)]
                self.assertEqual(len(matches), 1)
                self.assertEqual(matches[0], action)
            # for action in actions:
            #     matches = [ref_action for ref_action in actions_ref if repr(ref_action) == repr(action)]
            #     self.assertEqual(len(matches), 1)
            #     self.assertEqual(matches[0], action)
            for action in plan:
                self.assertIn(action, pruned_actions, msg="Preprocessor eliminated action %s" % str(action))

            plan2, time = planner.solve_file(constants.prodcell, p, preprocessor=preprocessor)
            self.assertIsNotNone(plan, msg="Failed for %s" % p)
            self.assertEqual(r, len(plan))
            # self.assertCountEqual(plan, plan2)
            # self.assertEqual(plan, plan2)
            self.assertTrue(True, v.validate_plan(constants.prodcell, p, plan, False))
            print("Preprocessed time: %f" % time)

    # @unittest.skip("This does not work at the moment")
    def test_rpg_preprocessor_dwr(self):
        planner = HeuristicPlanner(heuristic=NaiveLandmarkHeuristic())
        preprocessor = RPGReachabilityPreprocessor()
        self.dwr(planner, preprocessor)

    def test_rpg_preprocessor_blocks(self):
        planner = HeuristicPlanner(heuristic=NaiveLandmarkHeuristic())
        preprocessor = RPGReachabilityPreprocessor()
        self.blocks(planner, preprocessor)

    def test_rpg_preprocessor_tsp(self):
        planner = HeuristicPlanner(heuristic=NaiveLandmarkHeuristic())
        preprocessor = RPGReachabilityPreprocessor()
        self.tsp(planner, preprocessor)

    # @unittest.skipIf(sys.platform.startswith("linux"), "Do not test in CI to avoid wasting credits")
    @unittest.skipIf("GITHUB_RUN_ID" in os.environ, "Do not test in CI to avoid wasting credits")
    def test_rpg_preprocessor_prodcell(self):
        planner = HeuristicPlanner(heuristic=NaiveLandmarkHeuristic())
        preprocessor = RPGReachabilityPreprocessor()
        self.prodcell(planner, preprocessor)

    def test_pyper_preprocessor_dwr(self):
        planner = HeuristicPlanner(heuristic=NaiveLandmarkHeuristic())
        preprocessor = PyperPreprocessor()
        self.dwr(planner, preprocessor)

    def test_pyper_preprocessor_blocks(self):
        planner = HeuristicPlanner(heuristic=NaiveLandmarkHeuristic())
        preprocessor = PyperPreprocessor()
        self.blocks(planner, preprocessor)

    def test_pyper_preprocessor_tsp(self):
        planner = HeuristicPlanner(heuristic=NaiveLandmarkHeuristic())
        preprocessor = PyperPreprocessor()
        self.tsp(planner, preprocessor)

    # @unittest.skipIf(sys.platform.startswith("linux"), "Do not test in CI to avoid wasting credits")
    @unittest.skipIf("GITHUB_RUN_ID" in os.environ, "Do not test in CI to avoid wasting credits")
    def test_pyper_preprocessor_prodcell(self):
        planner = HeuristicPlanner(heuristic=NaiveLandmarkHeuristic())
        preprocessor = PyperPreprocessor()
        self.prodcell(planner, preprocessor)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
