#!/usr/bin/env python
# Four spaces as indentation [no tabs]

import unittest
from pddl.action import Action
from pddl.pddl_parser import PDDLParser
from pddl.pddl_planner import PDDLPlanner
from pddl.heuristic_planner import HeuristicPlanner
from pddl.state import applicable, apply, stateToLisp

# ==========================================
# Test PDDL
# ==========================================


class Test_PDDL(unittest.TestCase):

    dwr = "examples/dwr/dwr.pddl"
    pb1_dwr = "examples/dwr/pb1.pddl"
    pb2_dwr = "examples/dwr/pb2.pddl"

    tsp = "examples/tsp/tsp.pddl"
    pb1_tsp = "examples/tsp/pb1.pddl"
    pb2_tsp = "examples/tsp/pb2.pddl"

    dinner = "examples/dinner/dinner.pddl"
    pb1_dinner = "examples/dinner/pb1.pddl"

    blocksworld = "examples/blocksworld/blocksworld.pddl"
    pb1_blocksworld = "examples/blocksworld/pb1.pddl"
    pb2lecture_blocksworld = "examples/blocksworld/pb2lecture.pddl"

    # ------------------------------------------
    # Test scan_tokens
    # ------------------------------------------

    def test_scan_tokens_domain(self):
        parser = PDDLParser()
        self.assertEqual(parser.scan_tokens(Test_PDDL.dinner),
                        ['define', ['domain', 'dinner'],
                        [':requirements', ':strips'],
                        [':predicates', ['clean'], ['dinner'], ['quiet'], ['present'], ['garbage']],
                        [':action', 'cook',
                            ':parameters', [],
                            ':precondition', ['and', ['clean']],
                            ':effect', ['and', ['dinner']]],
                        [':action', 'wrap',
                            ':parameters', [],
                            ':precondition', ['and', ['quiet']],
                            ':effect', ['and', ['present']]],
                        [':action', 'carry',
                            ':parameters', [],
                            ':precondition', ['and', ['garbage']],
                            ':effect', ['and', ['not', ['garbage']], ['not', ['clean']]]],
                        [':action', 'dolly',
                            ':parameters', [],
                            ':precondition', ['and', ['garbage']],
                            ':effect', ['and', ['not', ['garbage']], ['not', ['quiet']]]]]
        )

    def test_scan_tokens_problem(self):
        parser = PDDLParser()
        self.assertEqual(parser.scan_tokens(Test_PDDL.pb1_dinner),
            ['define', ['problem', 'pb1'],
            [':domain', 'dinner'],
            [':init', ['garbage'], ['clean'], ['quiet']],
            [':goal', ['and', ['dinner'], ['present'], ['not', ['garbage']]]]]
        )

    # ------------------------------------------
    # Test parse domain
    # ------------------------------------------

    def test_parse_domain(self):
        parser = PDDLParser()
        parser.parse_domain(Test_PDDL.dinner)
        self.assertEqual(parser.domain_name, 'dinner')
        self.assertEqual(parser.actions,
            [
                Action('cook', tuple(), parser.state_to_tuple([['clean']]), parser.state_to_tuple([]), parser.state_to_tuple([['dinner']]), parser.state_to_tuple([])),
                Action('wrap', tuple(), parser.state_to_tuple([['quiet']]), parser.state_to_tuple([]), parser.state_to_tuple([['present']]), parser.state_to_tuple([])),
                Action('carry', tuple(), parser.state_to_tuple([['garbage']]), parser.state_to_tuple([]), parser.state_to_tuple([]), parser.state_to_tuple([['garbage'], ['clean']])),
                Action('dolly', tuple(), parser.state_to_tuple([['garbage']]), parser.state_to_tuple([]), parser.state_to_tuple([]), parser.state_to_tuple([['garbage'], ['quiet']]))
            ]
        )
        print(repr(parser.actions[0]))  # We had a problem with repr, so this is not so much an assert, but trying to get an exception

        parser = PDDLParser()
        parser.parse_domain(Test_PDDL.tsp)
        self.assertEqual(parser.domain_name, 'tsp')
        print(repr(parser.actions[0]))

    def test_string_to(self):
        parser = PDDLParser()
        predicate = parser.string_to_predicate("(on a b)")
        self.assertIsNotNone(predicate)
        self.assertEqual(predicate[0], "on")
        self.assertEqual(predicate[1], "a")
        self.assertEqual(predicate[2], "b")

    # ------------------------------------------
    # Test parse problem
    # ------------------------------------------

    def test_parse_problem(self):
        parser = PDDLParser()
        parser.parse_domain(Test_PDDL.dinner)
        parser.parse_problem(Test_PDDL.pb1_dinner)
        self.assertEqual(parser.problem_name, 'pb1')
        self.assertEqual(parser.objects, {})
        self.assertEqual(parser.state, parser.state_to_tuple([['garbage'], ['clean'], ['quiet']]))
        self.assertEqual(parser.positive_goals, parser.state_to_tuple([['dinner'], ['present']]))
        self.assertEqual(parser.negative_goals, parser.state_to_tuple([['garbage']]))
        actions = parser.grounding()
        self.assertEqual(len(actions), 4)

    def test_parse_blk_problem(self):
        parser = PDDLParser()
        parser.parse_domain(Test_PDDL.blocksworld)
        parser.parse_problem(Test_PDDL.pb1_blocksworld)
        self.assertEqual(parser.problem_name, 'pb1')
        self.assertEqual(parser.objects, {'object': ['a', 'b']})
        actions = parser.grounding()
        self.assertEqual(len(actions), 12)

    def test_parse_types(self):
        parser = PDDLParser()
        parser.parse_domain(Test_PDDL.dwr)
        parser.parse_problem(Test_PDDL.pb1_dwr)
        self.assertEqual(parser.problem_name, 'pb1')
        print(parser.types)
        # planner = PDDLPlanner()
        grounded_actions = parser.grounding()
        self.assertIsNotNone(grounded_actions)
        self.assertGreater(len(grounded_actions), 0)
        self.assertEqual(grounded_actions[0].name, "move")
        self.assertEqual(grounded_actions[0].parameters[0], "r1")

    def test_neighbourhood(self):
        parser = PDDLParser()
        parser.parse_domain(Test_PDDL.blocksworld)
        parser.parse_problem(Test_PDDL.pb2lecture_blocksworld)
        self.assertEqual(parser.problem_name, 'pb2lecture')
        print(parser.types)
        # planner = HeuristicPlanner()
        grounded_actions = parser.grounding()
        state = parser.state
        for act in grounded_actions:
            if applicable(state, act.positive_preconditions, act.negative_preconditions):
                new_state = apply(state, act.add_effects, act.del_effects)
                print("Action: {} State: {}".format(act, stateToLisp(new_state)))

    def test_action(self):
        parser = PDDLParser()
        parser.parse_domain(Test_PDDL.blocksworld)
        parser.parse_problem(Test_PDDL.pb1_blocksworld)
        action1: Action = parser.actions[0]
        self.assertIsNotNone(action1)
        action2 = action1.__copy__()
        self.assertIsNotNone(action2)
        self.assertEqual(action1.name, action2.name)
        self.assertEqual(action1.parameters, action2.parameters)
        self.assertEqual(action1.positive_preconditions, action2.positive_preconditions)
        self.assertEqual(action1.negative_preconditions, action2.negative_preconditions)
        self.assertEqual(action1.add_effects, action2.add_effects)
        self.assertEqual(action1.del_effects, action2.del_effects)
        self.assertEqual(action1, action2)
        self.assertEqual(action1.signature(), action2.signature())


if __name__ == '__main__':  # pragma: no cover
    # from os import sys, path
    # sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    unittest.main()
