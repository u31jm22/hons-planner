import unittest
from tests.test_PDDL import Test_PDDL
from tests.test_bfs_planner import TestBFSPlanner
from tests.test_heuristic_planner import TestHeuristicPlanner
from tests.test_benchmark import TestBenchmark
from tests.test_heuristics import TestHeuristics
from tests.test_pddl_preprocessor import TestPDDLPreprocessor


def suite():  # pragma: no cover
    suite = unittest.TestSuite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestBFSPlanner))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPDDLPreprocessor))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestHeuristicPlanner))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(Test_PDDL))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestBenchmark))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestHeuristics))
    return suite


if __name__ == '__main__':  # pragma: no cover
    runner = unittest.TextTestRunner()
    test_suite = suite()
    runner.run(test_suite)
    # unittest.main()
