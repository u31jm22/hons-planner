#!/usr/bin/env python
# Four spaces as indentation [no tabs]

import os
import unittest
# import sys

from pddl.intention_parser import IntentionParser
from pddl.pddl_parser import PDDLParser
from tests import test_pddl_intention_constants as constants


class Test_PDDLIntentionParser(unittest.TestCase):

    def test_intention_problem(self):
        intention_parser = IntentionParser()
        self.assertIsNotNone(intention_parser)
        intention_parser.parse_domain(constants.blk)
        self.assertIsNotNone(intention_parser.domain_name)
        self.assertEqual(intention_parser.domain_name, "blocksworld")
        self.assertEqual(len(intention_parser.actions), 4)
        intention_parser.parse_problem(constants.pb1_blk)
        self.assertEqual(len(intention_parser.desires), 2)

    # @unittest.skipIf(sys.platform.startswith("linux"), "Do not test in Github since it takes a while do complete")
    @unittest.skipIf("GITHUB_RUN_ID" in os.environ, "Don't test this in Github")
    def test_intention_problem_from_gp(self):  # pragma: no cover
        intention_parser = IntentionParser()
        self.assertIsNotNone(intention_parser)
        intention_parser.parse_intention_planning_from_gp(constants.prodcell_gp0)
        self.assertIsNotNone(intention_parser.domain_name)
        self.assertEqual(intention_parser.domain_name, "prodcell")
        self.assertEqual(len(intention_parser.actions), 3)
        self.assertEqual(len(intention_parser.desires), 3)

        pddl_parser = PDDLParser()
        pddl_parser.parse_domain(constants.prodcell_gp0_dom)
        pddl_parser.parse_problem(constants.prodcell_gp0_pb3)
        self.assertIsNotNone(pddl_parser)
        self.assertIsNotNone(pddl_parser.state)
        for obj_type in intention_parser.objects:
            self.assertCountEqual(intention_parser.objects[obj_type], pddl_parser.objects[obj_type])
        self.assertEqual(intention_parser.state, pddl_parser.state)
        for desire in intention_parser.desires:
            self.assertIsNotNone(desire.desire)