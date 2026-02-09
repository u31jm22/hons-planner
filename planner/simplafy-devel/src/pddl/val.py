#!/usr/bin/env python
# Four spaces as indentation [no tabs]

from pddl.pddl_parser import PDDLParser
from pddl.action import Action
from pddl.state import applicable, apply


class Validator:

    def parse_plan(self, filename):
        with open(filename, 'r') as f:
            plan = []
            for act in f.read().splitlines():
                act = act[1:-1].split()
                plan.append(Action(act[0], tuple(act[1:]), [], [], [], []))
            return plan

    def validate_file(self, domainfile, problemfile, planfile, verbose=True):
        return self.validate_plan(domainfile, problemfile, self.parse_plan(planfile), verbose)

    def validate_plan(self, domainfile, problemfile, plan, verbose=True):
        # Parser
        parser = PDDLParser()
        parser.parse_domain(domainfile)
        parser.parse_problem(problemfile)
        # Grounding process
        ground_actions = []
        for action in parser.actions:
            for act in action.groundify(parser.objects, parser.types):
                ground_actions.append(act)
        return self.validate(ground_actions, parser.state, parser.positive_goals, parser.negative_goals, plan, verbose)

    def validate(self, ground_actions, initial_state, positive_goals, negative_goals, plan, verbose=True):
        state = initial_state
        if verbose:
            print(f"Goal is {positive_goals} and not {negative_goals}")
        for act in plan:
            if verbose:
                print('(' + act.name + ''.join(' ' + p for p in act.parameters) + ')')
            # Act is part of ground actions set
            ground_act = None
            for ground in ground_actions:
                if act.name == ground.name and act.parameters == ground.parameters:
                    ground_act = ground
                    break
            if not ground_act:
                if verbose:
                    print('  Action not found in ground set')
                return False
            # Applicable
            if not applicable(state, ground_act.positive_preconditions, ground_act.negative_preconditions):
                if verbose:
                    print('  Action not applicable')
                return False
            # Apply
            state = apply(state, ground_act.add_effects, ground_act.del_effects)
        reach_goal = applicable(state, positive_goals, negative_goals)
        if verbose:
            print('Goal reached: ' + str(reach_goal))
        return reach_goal


if __name__ == '__main__':  # pragma: no cover
    import sys
    domain = sys.argv[1]
    problem = sys.argv[2]
    plan = sys.argv[3]
    val = Validator()
    if val.validate_file(domain, problem, plan):
        print('Valid plan')
    else:
        print('Invalid plan')
