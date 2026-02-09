import unittest
# import sys
import os
import glob

from tests.test_pddl_constants import TMP_FOLDER
from tests.utils import erase_tmp_files
from pddl.pddl_parser import PDDLParser
from pddl.intention_parser import IntentionParser
from generators.miconic.miconic import main, MiconicProblemGenerator


class Test_MiconicGenerator(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        if not os.path.exists(TMP_FOLDER):  # Check we have the output folder created
            os.mkdir(TMP_FOLDER)
        erase_tmp_files()

    def test_miconic_generator_class(self):
        generator = MiconicProblemGenerator(2, 2, None)
        self.assertIsNotNone(generator)

    def test_miconic_command_line(self):
        # argv = []
        # try:
        #     main(argv)
        #     self.assertFalse(True, "This should error")
        # except Exception as e:
        #     self.assertIsNotNone(e)

        try:
            args = "miconic.py -f 40 -fp 19 -tp 20 -"
            argv = args.split()
            main(argv)
            self.assertTrue(True, "This should not error")
            # args = "miconic.py -f 2 -p 4 "+TMP_FOLDER
            args = "miconic.py -f 2 -fp 4 -tp 6 "+TMP_FOLDER
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
                self.assertEqual(parser.domain_name, "miconic")
                actions = parser.grounding()
                self.assertIsNotNone(actions)
        except Exception as e:
            self.assertFalse(True, "Exception %s should not happen" % e)

    def test_miconic_command_line_intention(self):
        try:
            # args = "miconic.py -f 2 -p 4 -o intention "+TMP_FOLDER
            args = "miconic.py -fp 3 -tp 4 -o both "+TMP_FOLDER
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
                self.assertEqual(parser.domain_name, "miconic")
                actions = parser.grounding()
                self.assertIsNotNone(actions)
        except Exception as e:
            self.assertFalse(True, "Exception %s should not happen" % e)