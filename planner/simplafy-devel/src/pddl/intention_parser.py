import os
import glob

from pddl.pddl_parser import PDDLParser
from collections import namedtuple

AgentDesire = namedtuple("AgentDesire", "context desire priority")
AgentIntention = namedtuple("AgentIntention", "desire plan")


class IntentionParser(PDDLParser):

    def __init__(self, verbose=False) -> None:
        super(IntentionParser, self).__init__(verbose)

    def parse_intention_planning_from_gp(self, problem_folder: str, domain_filename: str = "domain.pddl") -> None:
        """Parses an intention planning problem from a generalised planning folder

        Args:
            problem_folder (str): A folder in which a PDDL version of a generalised planning problem resides

        Returns:
            None
        """
        domain_path = problem_folder+"/"+domain_filename
        if not os.path.isfile(domain_path):
            raise FileNotFoundError("Domain file %s not found :(" % domain_path)
        self.parse_domain(domain_path)
        initial_states = set()
        desires = []
        for filename in sorted(glob.glob(os.path.join(problem_folder, '*.pddl'))):
            if domain_filename not in filename:
                problem_path = filename
                super().parse_problem(problem_path)
                # At the moment I am just doing the union of all the predicates, under the assumption that they do not conflict
                # TODO Revise this behaviour at some point
                initial_states = initial_states.union(self.state)
                desire_formula = (frozenset(self.positive_goals), frozenset(self.negative_goals))
                desire = AgentDesire(None, desire_formula, 1)
                desires.append(desire)
        # FIXME (Not quite wrong but inefficient way of erasing object redeclarations)
        objects = dict()
        for obj_type in self.objects:
            objects[obj_type] = list(set(self.objects[obj_type]))
        self.objects = objects
        self.state = frozenset(initial_states)
        self.desires = desires

    def parse_desires(self, group: list, t) -> list[AgentDesire]:
        desires = []
        for desire_tokens in group:
            t = desire_tokens.pop(0)
            desire_formula = desire_tokens
            if t == ':desire':
                positive_goals = []
                negative_goals = []
                self.split_predicates(desire_formula[0], positive_goals, negative_goals, '', 'desires')
                self.positive_goals = self.frozenset_of_tuples(positive_goals)
                self.negative_goals = self.frozenset_of_tuples(negative_goals)
                desire = AgentDesire(None, (self.positive_goals, self.negative_goals), 1)
                desires.append(desire)
            else:
                self.parse_problem_extended(t, group)
                raise Exception('Parse error near %s, context %s ' % (t, group))
        return desires

    def parse_problem(self, problem_filename: str):
        tokens = self.scan_tokens(problem_filename)
        if type(tokens) is list and tokens.pop(0) == 'define':
            self.problem_name = 'unknown'
            self.state = frozenset()
            self.positive_goals = frozenset()
            self.negative_goals = frozenset()
            while tokens:
                group = tokens.pop(0)
                t = group.pop(0)
                if t == 'problem':
                    self.problem_name = group[0]
                elif t == ':domain':
                    if self.domain_name != group[0]:
                        raise Exception('Different domain specified in problem file')
                elif t == ':requirements':
                    pass  # Ignore requirements in problem, parse them in the domain
                elif t == ':objects':
                    self.parse_objects(group, t)
                elif t == ':init':
                    self.state = self.frozenset_of_tuples(group)
                elif t == ':desires':
                    self.desires = self.parse_desires(group, t)
                else: self.parse_problem_extended(t, group)
        else:
            raise Exception('File ' + problem_filename + ' does not match problem pattern')