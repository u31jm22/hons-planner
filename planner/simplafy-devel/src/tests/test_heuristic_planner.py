#!/usr/bin/env python
# Four spaces as indentation [no tabs]

import unittest
import sys
sys.path.append('..')
from pddl.action import Action
from pddl.pddl_preprocessor import RPGReachabilityPreprocessor
from pddl.heuristic_planner import HeuristicPlanner, HeuristicRunner
from pddl.pddl_parser import PDDLParser
from pddl.val import Validator
from tests import test_pddl_constants as constants

# ==========================================
# Test Planner
# ==========================================


class TestHeuristicPlanner(unittest.TestCase):

    # def test_string_representation(self):
    #     planner = HeuristicPlanner()
    #     self.assertEqual(str(planner), "HeuristicPlanner(MaxHeuristic)")

    # ------------------------------------------
    # Test solve
    # ------------------------------------------

    def test_solve_dinner(self):
        planner = HeuristicPlanner()
        plan, time = planner.solve_file(constants.dinner, constants.pb1_dinner)
        parser = PDDLParser()
        self.assertEqual(
            [
                Action('cook', tuple(), parser.state_to_tuple([['clean']]), parser.state_to_tuple([]), parser.state_to_tuple([['dinner']]), parser.state_to_tuple([])),
                Action('wrap', tuple(), parser.state_to_tuple([['quiet']]), parser.state_to_tuple([]), parser.state_to_tuple([['present']]), parser.state_to_tuple([])),
                Action('carry', tuple(), parser.state_to_tuple([['garbage']]), parser.state_to_tuple([]), parser.state_to_tuple([]), parser.state_to_tuple([['garbage'], ['clean']]))
            ],
            plan
        )

    def test_heuristic_runner(self):
        runner = HeuristicRunner()
        result, _ = runner.solve_file(constants.dwr, constants.pb1_dwr, preprocessor=None)
        self.assertEqual(None, result)

    def test_solve_dwr(self):
        preprocessor = RPGReachabilityPreprocessor()
        planner = HeuristicPlanner()
        self.assertIn("HeuristicPlanner", str(planner))
        self.assertIn("MaxHeuristic", str(planner))
        plan, time = planner.solve_file(constants.dwr, constants.pb1_dwr, preprocessor=None)
        # print("Expected 17, got:", str(len(plan)) + ('. Correct!' if len(plan) == 17 else '. False!'))
        self.assertEqual(17, len(plan),msg="Expected 17, got:"+str(len(plan)))
        plan, time = planner.solve_file(constants.dwr, constants.pb2_dwr, preprocessor)
        # print("Expected 0, got:", str(len(plan)) + ('. Correct!' if len(plan) == 0 else '. False!'))
        self.assertEqual(0, len(plan),msg="Expected 0, got:"+str(len(plan)))

    def test_solve_blocks(self):
        planner = HeuristicPlanner()
        v = Validator()
        bpd_list = [constants.pb1_blk,
                    constants.pb2_blk,
                    constants.pb3_blk,
                    constants.pb4_blk,
                    constants.pb5_blk,
                    constants.pb6_blk]
        results = [2, 6, 4, 12, 8, 10]
        for b, r in zip(bpd_list, results):
            print("Solving %s" % b)
            plan, time = planner.solve_file(constants.blk, b)
            self.assertIsNotNone(plan, msg="Failed for %s" % b)
            self.assertEqual(r, len(plan))
            self.assertTrue(True, v.validate_plan(constants.blk, b, plan, False))

    # Simple test to check whether it's worth using namedtuple (so far, it's not)
    # def test_tuple(self):
    #     from collections import namedtuple
    #     import time
    #     node = namedtuple('node', 'x y z')

    #     start_time = time.time()
    #     test_list = [(i, i+1, i+2) for i in range(10000000)]
    #     total_time = time.time() - start_time
    #     self.assertIsNotNone(test_list)
    #     print(f"Tuple time: {total_time}")

    #     start_time = time.time()
    #     test_list = [node(i, i+1, i+2) for i in range(10000000)]
    #     total_time = time.time() - start_time
    #     self.assertIsNotNone(test_list)
    #     print(f"Named Tuple time: {total_time}")


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
