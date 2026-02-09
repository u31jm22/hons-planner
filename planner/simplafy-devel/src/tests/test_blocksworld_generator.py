import unittest
# import sys
import os
import glob

from tests.test_pddl_constants import TMP_FOLDER
from tests.utils import erase_tmp_files
from pddl.pddl_parser import PDDLParser
from pddl.intention_parser import IntentionParser
from generators.blocksworld.blocksworld import main, BlocksWorld
from pddl.heuristic_planner import HeuristicPlanner
from pddl.delete_relaxation_h import FastForwardHeuristic
from pddl.pddl_preprocessor import PyperPreprocessor


class Test_BlocksworldGenerator(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        if not os.path.exists(TMP_FOLDER):  # Check we have the output folder created
            os.mkdir(TMP_FOLDER)
        erase_tmp_files()

    def test_blocksworld_generator_class(self):
        generator = BlocksWorld()
        self.assertIsNotNone(generator)

    def test_blocksworld_command_line(self):
        argv = []
        try:
            main(argv)
            self.assertFalse(True, "This should error")
        except Exception as e:
            self.assertIsNotNone(e)

        try:
            args = "blocksworld.py -fb 3 -tb 8 -st 3 -g 2 "+TMP_FOLDER
            argv = args.split()
            main(argv)
            self.assertTrue(True, "This should not error")
            domain_file = TMP_FOLDER+"domain.pddl"
            self.assertTrue(os.path.exists(domain_file))
            for filename in sorted(glob.glob(os.path.join(TMP_FOLDER, '*.pddl'))):
                if domain_file in filename:
                    # Skip the domain file
                    continue
                parser = PDDLParser(verbose=True)
                parser.parse_domain(domain_file)
                parser.parse_problem(filename)
                self.assertEqual(parser.domain_name, "blocksworld")
                actions = parser.grounding()
                self.assertIsNotNone(actions)
                initial_state = parser.state
                self.assertIsNotNone(initial_state)
                self.assertGreater(len(initial_state), 0)
                planner = HeuristicPlanner(heuristic=FastForwardHeuristic())
                plan, time = planner.solve_file(domain_file, filename, PyperPreprocessor())
                self.assertIsNotNone(plan)

        except Exception as e:
            self.assertFalse(True, "Exception %s should not happen on problem %s" % (e, filename))

    def test_blocksworld_command_line_intention(self):
        try:
            args = "blocksworld.py -fb 4 -tb 8 -st 3 -g 2 -i -f intention "+TMP_FOLDER
            argv = args.split()
            main(argv)
            self.assertTrue(True, "This should not error")
            domain_file = TMP_FOLDER+"domain.pddl"
            self.assertTrue(os.path.exists(domain_file))
            for filename in sorted(glob.glob(os.path.join(TMP_FOLDER, '*.pddl'))):
                if domain_file in filename:
                    # Skip the domain file
                    continue
                parser = IntentionParser(verbose=True)
                parser.parse_domain(domain_file)
                parser.parse_problem(filename)
                self.assertEqual(parser.domain_name, "blocksworld")
                actions = parser.grounding()
                self.assertIsNotNone(actions)
                initial_state = parser.state
                self.assertIsNotNone(initial_state)
                self.assertGreater(len(initial_state), 0)
                planner = HeuristicPlanner(heuristic=FastForwardHeuristic())
                plan, time = planner.solve_file(domain_file, filename, PyperPreprocessor())
                self.assertIsNotNone(plan)
        except Exception as e:
            self.assertFalse(True, "Exception %s should not happen" % e)