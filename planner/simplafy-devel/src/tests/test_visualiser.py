import unittest
import os
from pddl.heuristic_planner import HeuristicPlanner
from pddl.intention import IntentionPlanner, AgentDesire, merge_desires
from pddl.intention_parser import IntentionParser
from pddl.pddl_parser import PDDLParser
from pddl.visualiser import Visualiser
from tests import test_pddl_constants as pddl_constants
from tests import test_pddl_intention_constants as constants
from tests.test_pddl_constants import TMP_FOLDER


class Test_Visualiser(unittest.TestCase):

    def test_heuristic_planner_visualiser(self):
        planner = HeuristicPlanner(visualise=True)
        planner.solve_file(constants.dinner, pddl_constants.pb1_dinner)
        self.assertIsNotNone(planner.visualiser)
        json_string = planner.visualiser.get_json_string()
        self.assertIsNotNone(json_string)
        # with open(TMP_FOLDER+"statespace.json", "w") as file:
        #     file.write(json_string)
        #     file.close()

    @unittest.skipIf("GITHUB_RUN_ID" in os.environ, "Don't test this in Github")
    def test_compare_state_spaces_dinner(self):  # pragma: no cover
        # NB: This is mostly the same test as TestIntentionPlanner.test_compare_priority_queues_dinner
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

        all_goals = merge_desires(desires)

        intention_planner = IntentionPlanner(collect_stats=True, visualise=True)
        intention_planner.visualiser = Visualiser(ground_actions, all_goals)
        intentions = intention_planner.intention_plan(ground_actions, parser.state, desires)
        self.assertIsNotNone(intentions)
        self.assertIsInstance(intentions, list)
        self.assertIsNotNone(intention_planner.visualiser)
        json_string = intention_planner.visualiser.get_json_string()
        self.assertIsNotNone(json_string)
        with open(TMP_FOLDER+"dinner_intention_statespace.json", "w") as file:
            file.write(json_string)
            file.close()

        heuristic_planner = HeuristicPlanner(collect_stats=True, visualise=True)
        heuristic_planner.visualiser = Visualiser(ground_actions, all_goals)
        plan = heuristic_planner.solve(ground_actions, parser.state, all_goals)
        self.assertIsNotNone(plan)
        self.assertIsInstance(plan, list)
        self.assertIsNotNone(heuristic_planner.visualiser)
        json_string = heuristic_planner.visualiser.get_json_string()
        self.assertIsNotNone(json_string)
        with open(TMP_FOLDER+"dinner_statespace.json", "w") as file:
            file.write(json_string)
            file.close()

        diff = intention_planner.visited - heuristic_planner.visited
        print("Different visited states %s" % diff)
    
    @unittest.skipIf("GITHUB_RUN_ID" in os.environ, "Don't test this in Github")
    def test_compare_state_spaces_blocks(self):  # pragma: no cover
        parser = IntentionParser()
        parser.parse_domain(constants.blk)
        parser.parse_problem(constants.pb2_blk)
        # Add asserts here
        ground_actions = parser.grounding()
        self.assertIsNotNone(ground_actions)

        desires = parser.desires
        all_goals = merge_desires(desires)

        intention_planner = IntentionPlanner(collect_stats=True, visualise=True)
        intention_planner.visualiser = Visualiser(ground_actions, all_goals)
        intentions = intention_planner.intention_plan(ground_actions, parser.state, desires)
        self.assertIsNotNone(intentions)
        self.assertIsInstance(intentions, list)
        self.assertIsNotNone(intention_planner.visualiser)
        json_string = intention_planner.visualiser.get_json_string()
        self.assertIsNotNone(json_string)
        with open(TMP_FOLDER+"blocks_intention_statespace.json", "w") as file:
            file.write(json_string)
            file.close()

        heuristic_planner = HeuristicPlanner(collect_stats=True, visualise=True)
        heuristic_planner.visualiser = Visualiser(ground_actions, all_goals)
        plan = heuristic_planner.solve(ground_actions, parser.state, all_goals)
        self.assertIsNotNone(plan)
        self.assertIsInstance(plan, list)
        self.assertIsNotNone(heuristic_planner.visualiser)
        json_string = heuristic_planner.visualiser.get_json_string()
        self.assertIsNotNone(json_string)
        with open(TMP_FOLDER+"blocks_statespace.json", "w") as file:
            file.write(json_string)
            file.close()

        diff = intention_planner.visited - heuristic_planner.visited
        print("Different visited states %s" % diff)