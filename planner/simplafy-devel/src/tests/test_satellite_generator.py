import unittest
# import sys
import os
import glob

from tests.test_pddl_constants import TMP_FOLDER
from tests.utils import erase_tmp_files
from pddl.pddl_parser import PDDLParser
from pddl.intention_parser import IntentionParser
from generators.satellite.satellite import main


class Test_SatelliteGenerator(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        if not os.path.exists(TMP_FOLDER):  # Check we have the output folder created
            os.mkdir(TMP_FOLDER)
        erase_tmp_files()

    def test_satellite_command_line(self):
        # argv = []
        # try:
        #     main(argv)
        #     self.assertFalse(True, "This should error")
        # except Exception as e:
        #     self.assertIsNotNone(e)

        try:
            args = "satellite.py 42 5 5 2 2 2"
            argv = args.split()
            main(argv)
            self.assertTrue(True, "This should not error")
            args = "satellite.py 42 5 5 2 2 2 -o "+TMP_FOLDER
            argv = args.split()
            main(argv)
            domain_file = TMP_FOLDER+"domain.pddl"
            self.assertTrue(os.path.exists(domain_file))
            for filename in sorted(glob.glob(os.path.join(TMP_FOLDER, '*.pddl'))):
                if domain_file in filename:
                    # Skip the domain file
                    continue
                parser = PDDLParser(verbose=True)
                parser.parse_domain(domain_file)
                parser.parse_problem(filename)
                self.assertEqual(parser.domain_name, "satellite")
                actions = parser.grounding()
                self.assertIsNotNone(actions)
        except Exception as e:
            self.assertFalse(True, "Exception %s should not happen" % e)

    def test_satellite_command_line_intention(self):
        try:
            args = "satellite.py 42 5 5 2 2 2 --format intention -o"+TMP_FOLDER
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
                self.assertEqual(parser.domain_name, "satellite")
                actions = parser.grounding()
                self.assertIsNotNone(actions)
                self.assertIsNotNone(parser.desires)
        except Exception as e:
            self.assertFalse(True, "Exception %s should not happen" % e)

    # Example unit test usage:

    # def test_basic_strips_problem(self):
    #     result = generate_pddl_problem(
    #         seed=12345,
    #         satellites=2,
    #         instruments=3,
    #         modes=4,
    #         targets=5,
    #         observations=6
    #     )
    #     assert "(define (problem strips-sat-x-1)" in result
    #     assert "(:domain satellite)" in result

    # def test_numeric_problem(self):
    #     result = generate_pddl_problem(
    #         seed=12345,
    #         satellites=1,
    #         instruments=2,
    #         modes=3,
    #         targets=4,
    #         observations=5,
    #         numeric=True
    #     )
    #     assert "(= (fuel-used) 0)" in result
    #     assert "(:metric minimize (fuel-used))" in result

    # def test_command_line_parsing():
    #     # Test that main() can be called with argument strings
    #     import sys
    #     from io import StringIO
        
    #     # Capture stdout
    #     captured_output = StringIO()
    #     sys.stdout = captured_output
        
    #     # Call main with test arguments
    #     main(['12345', '1', '2', '3', '4', '5', '-n'])
        
    #     # Reset stdout
    #     sys.stdout = sys.__stdout__
        
    #     result = captured_output.getvalue()
    #     assert "(= (fuel-used) 0)" in result