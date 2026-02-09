#!/usr/bin/env python
# Four spaces as indentation [no tabs]

import unittest
import sys
sys.path.append('..')
from pddl.action import Action
from pddl.bfs_planner import BFSPlanner
from pddl.pddl_parser import PDDLParser

# ==========================================
# Test Planner
# ==========================================


class TestBFSPlanner(unittest.TestCase):

    dinner = "examples/dinner/dinner.pddl"
    pb1_dinner = "examples/dinner/pb1.pddl"

    # ------------------------------------------
    # Test solve
    # ------------------------------------------

    def test_solve_dinner(self):
        planner = BFSPlanner()
        plan, time = planner.solve_file(TestBFSPlanner.dinner, TestBFSPlanner.pb1_dinner)
        parser = PDDLParser()
        self.assertEqual(
            [
                Action('cook', tuple(), parser.state_to_tuple([['clean']]), parser.state_to_tuple([]), parser.state_to_tuple([['dinner']]), parser.state_to_tuple([])),
                Action('wrap', tuple(), parser.state_to_tuple([['quiet']]), parser.state_to_tuple([]), parser.state_to_tuple([['present']]), parser.state_to_tuple([])),
                Action('carry', tuple(), parser.state_to_tuple([['garbage']]), parser.state_to_tuple([]), parser.state_to_tuple([]), parser.state_to_tuple([['garbage'], ['clean']]))
            ],
            plan
        )

    #-------------------------------------------
    # Split propositions
    #-------------------------------------------


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
