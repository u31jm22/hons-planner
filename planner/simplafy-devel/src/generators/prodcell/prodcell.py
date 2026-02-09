#!/usr/bin/env python
# Four spaces as indentation [no tabs]
import random
import itertools
import math
from typing import Tuple, FrozenSet, Collection

# An individual problem generator for the Production Cell domain
# In the interests of self containment, I'm replicating a lot of code from my BDI Planner Agent
# This is (or will be) available at https://github.com/meneguzzi/bdi-plan
# This might damn me to programmer's hell


# from collections import namedtuple
# FrozenSetState = Tuple[FrozenSet[Tuple], FrozenSet[Tuple]]
# Formula = namedtuple('SimpleConjunctiveFormula', 'positive negative')


# Evil copy and paste
# TODO Create a proper library for this
def tuple_to_lisp(fluent: tuple) -> str:
    return "("+' '.join(fluent)+") "


class FrozenSetState(FrozenSet):

    def __str__(self) -> str:
        # res = ""
        # for atom in iter(self):
        #     res += "("+' '.join(atom)+") "
        # return res
        return repr(self)

    def __repr__(self) -> str:
        res = ""
        for atom in iter(self):
            # res += "("+' '.join(atom)+") "
            res += tuple_to_lisp(atom)
        return res


class Formula:

    def __init__(self, positive: FrozenSetState, negative: FrozenSetState = frozenset()) -> None:
        # TODO Autoconvert other types of positive and negative into the state type
        self.positive = FrozenSetState(positive)
        self.negative = FrozenSetState(negative)
        self._repr = None

    def __hash__(self) -> int:
        return self.positive.__hash__() + self.negative.__hash__()

    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, Formula):
            return self.positive == __value.positive and self.negative == __value.negative
        else:
            return super().__eq__(__value)

    def __repr__(self) -> str:
        # if self._repr is None:
        #     positive = ""
        #     for fluent in self.positive:
        #         positive += " "+str(fluent)
        #     negative = ""
        #     for fluent in self.negative:
        #         negative += " (not {0})".format(str(fluent))
        #     self._repr = "(and {0} {1})".format(positive, negative)
        # return self._repr
        if self._repr is None:
            positive = ""
            for fluent in self.positive:
                # positive += " "+str(fluent)
                positive += " "+tuple_to_lisp(fluent)
            negative = ""
            for fluent in self.negative:
                # negative += " (not {0})".format(str(fluent))
                negative += " (not {0})".format(tuple_to_lisp(fluent))
            self._repr = "(and {0} {1})".format(positive, negative)
        return self._repr

    def __getitem__(self, item: int) -> frozenset:
        if item == 0:
            return self.positive
        elif item == 1:
            return self.negative
        else:
            raise IndexError("Out of bounds")


class ProdCellProblem:

    def __init__(self, initial_state: frozenset[tuple], positive_goals: frozenset[tuple], negative_goals: frozenset[tuple]):
        self.initial_state = initial_state
        self.positive_goals = positive_goals
        self.negative_goals = negative_goals

    def goal(self) -> Formula:
        return Formula(self.positive_goals, self.negative_goals)


class ProdCell:
    """Production cell problem generator.
    This will work for both PDDL and IntentionPlanning
    This code is directly derived from the Production Cell environment from [BDI-plan](https://github.com/meneguzzi/bdi-plan/blob/main/bdiplan/environments/prodcell.py)
    """

    DOMAIN = "generators/prodcell/domain.pddl"
    PB_TEMPLATE = "generators/prodcell/pbTemplate.pddl"
    PB_INTENTION_TEMPLATE = "generators/prodcell/pbIntentionTemplate.pddl"

    def __init__(self, procUnits: int = 4, 
                 blocks: int = 4, belts: int = 2,
                 procsPerBlock: int = 1, desires: int = 0,
                 random_seed: float = None):
        self.random = random.Random(random_seed)
        self._procUnits = procUnits
        self._blocks = blocks
        self._belts = belts
        self._procsPerBlock = procsPerBlock
        self._currentBlock = 0
        self._desires = desires
        self._factored_goals = []
        self._activeBlocks = []

    def write_pddl_problem(self, initial_state: FrozenSetState,
                           goal_state: Formula, templateFile: str, instanceFile: str, problemName: str = None):
        with open(templateFile, encoding='UTF-8') as instream:
            with open(instanceFile, 'w', encoding='UTF-8') as outstream:
                for line in instream:
                    if '<BELTS>' in line:
                        outstream.write(' '.join(self._beltNames) + " - belt\n")
                    elif '<PROCUNITS>' in line:
                        outstream.write(' '.join(self._unitNames) + " - procunit\n")
                    elif '<BLOCKS>' in line:
                        outstream.write(' '.join(self._blockNames) + " - block\n")
                    elif '<INITIAL_STATE>' in line:
                        outstream.write(str(initial_state))
                    elif '<GOAL_STATE>' in line:
                        outstream.write(str(goal_state))
                    elif problemName is not None and 'pbTemplateInstance' in line:
                        outstream.write(line.replace('pbTemplateInstance', problemName))
                    else:
                        outstream.write(line)

    def write_int_pddl_problem(self, initial_state: FrozenSetState,
                               desires: Collection, templateFile: str, instanceFile: str, problemName: str = None):
        with open(templateFile, encoding='UTF-8') as instream:
            with open(instanceFile, 'w', encoding='UTF-8') as outstream:
                for line in instream:
                    if '<BELTS>' in line:
                        outstream.write(' '.join(self._beltNames) + " - belt\n")
                    elif '<PROCUNITS>' in line:
                        outstream.write(' '.join(self._unitNames) + " - procunit\n")
                    elif '<BLOCKS>' in line:
                        outstream.write(' '.join(self._blockNames) + " - block\n")
                    elif '<INITIAL_STATE>' in line:
                        outstream.write(str(initial_state))
                    elif '<DESIRES>' in line:
                        for desire in desires:
                            outstream.write('(:desire %s)\n' % str(desire.goal()))
                    elif problemName is not None and 'pbTemplateInstance' in line:
                        outstream.write(line.replace('pbTemplateInstance', problemName))
                    else:
                        outstream.write(line)

    def generate_configuration(self, procUnits: int, blocks: int, belts: int) -> FrozenSetState:
        """Generates a production cell configuration (i.e. the PDDL representation of the initial state) for the parameters given

        Args:
            procUnits (int): The number of processing units in the production cell
            blocks (int): The number of blocks to be processed
            belts (int): The number of belts

        Returns:
            _type_: _description_
        """
        self._unitNames = ["pu%d" % pu for pu in range(procUnits)]
        self._beltNames = ["belt%d" % b for b in range(belts)]  # + ["feedBelt"]
        self._blockNames = ["block%d" % b for b in range(blocks)]
        self._connections = [('connected', a, b) for (a, b) in itertools.product(self._unitNames, self._beltNames)]
        self._connections += [('connected', b, a) for (a, b) in itertools.product(self._unitNames, self._beltNames)]
        self._connections += [('connected', a, b) for (a, b) in itertools.product(self._beltNames + ['feedBelt'], self._beltNames)]
        self._connections += [('connected', a, 'depositBelt') for a in self._beltNames]

        self._empties = [('empty', device) for device in self._unitNames + self._beltNames + ["depositBelt"]]
        # self._beltNames += ["feedBelt"]
        # self._positions = [('over', self._blockNames[0], 'feedBelt')]
        self._positions = []
        initial_state = FrozenSetState(self._connections+self._empties+self._positions)
        return initial_state

    def introduce_block(self, procUnits: int, block: int, belts: int, in_feedbelt: bool = True):
        self._activeBlocks.append('block%s' % block)
        units = self.random.sample([i for i in range(procUnits)], k=self._procsPerBlock)
        procs = [('processed', 'block%s' % block, "pu%d" % pu) for pu in units]
        procs += [('finished', 'block%s' % block)]
        # context = parse_formula('(over block%d feedbelt)' % block)

        target_device = None
        if in_feedbelt:
            target_device = 'feedbelt'
        else:
            target_device = 'feedbelt'  # TODO Change this to another device

        self._positions.append(('over', 'block%s' % self._currentBlock, target_device))
        self._currentBlock += 1
        context = (frozenset(), frozenset([('finished', 'block%d' % block)]))
        desire = Formula(FrozenSetState(procs), frozenset())
        self._factored_goals.append((context, desire))

    def generate_goal(self) -> Formula:
        consolidated_goals = [literal
                              for (_, goal) in self._factored_goals
                              for literal in goal.positive]
        goal_state = Formula(consolidated_goals, frozenset())
        return goal_state

    def generate_desires(self) -> Collection:
        return self._factored_goals

    def generate_problems(self, num_problems: int = 1) -> Collection[ProdCellProblem]:
        problems = []
        for p in range(num_problems):
            initial_state = self.generate_configuration(self._procUnits, self._blocks, self._belts)
            for b in range(self._blocks):
                self.introduce_block(self._procUnits, b, self._belts)
            initial_state = FrozenSetState(initial_state | set(self._positions))
            goal_state = self.generate_goal()
            problem = ProdCellProblem(initial_state, goal_state.positive, goal_state.negative)
            problems.append(problem)
        return problems

    def generate_incremental_problems(self, num_problems: int = 1) -> Collection[ProdCellProblem]:
        problems = []
        current_block = 0

        # Compute how many blocks we process in each problem
        blocks_per_problem = math.ceil(self._blocks/num_problems)
        blocks = []
        for i in range(num_problems):
            blocks.append(blocks_per_problem)
        while sum(blocks) > self._blocks:
            blocks[-1] -= 1

        # if blocks_per_problem * num_problems > self._blocks:

        initial_state = self.generate_configuration(self._procUnits, self._blocks, self._belts)

        for p in range(num_problems):
            for b in range(blocks[p]):
                self.introduce_block(self._procUnits, current_block, self._belts)
                current_block += 1
            initial_state = FrozenSetState(initial_state | set(self._positions))
            goal_state = self.generate_goal()
            problem = ProdCellProblem(initial_state, goal_state.positive, goal_state.negative)
            problems.append(problem)
        return problems

    def factored_goal_formulas(self) -> Collection[Tuple[Formula, Formula]]:
        return self._factored_goals


# Reading command line parameters
def main(argv):
    import shutil
    import argparse
    if len(argv) < 2: raise IndexError
    try:
        parser = argparse.ArgumentParser(
                    prog='prodcell',
                    description='Generates domain files for the Production Cell domain',
                    epilog='Text at the bottom of help',
                    exit_on_error=False)

        parser.add_argument('output', help='Path to output folder')
        parser.add_argument('-p', '--procUnits', default='4', type=int, help='Number of processing units in the production cell')
        parser.add_argument('-fb', '--fromBlocks', default='4', type=int, help='Starting number of blocks in the production cell')
        parser.add_argument('-tb', '--toBlocks', default='10', type=int, help='Ending number of blocks in the production cell')
        parser.add_argument('-b', '--belts', default='2', type=int, help='Number of conveyor belts in the production cell')
        parser.add_argument('-pb', '--procsPerBlock', default='2', type=int, help='Number of processing units required for each block')
        parser.add_argument('-g', '--goalsPerProblem', default='2', type=int, help='Number of sub goals per problem (for intention planning)')
        parser.add_argument('-i', '--incrementalGoals', action='store_true', help='Whether multiple goals are incremental (for intention planning)')
        parser.add_argument('-v', '--verbose', action='store_true')
        parser.add_argument('-f', '--format', choices=['pddl', 'intention', 'both'], default="pddl", help='The format of the resulting problems')

        args = parser.parse_args(argv[1:])

        # procUnits = int(argv[1])
        # fromBlocks = int(argv[2])
        # toBlocks = int(argv[3])
        # belts = int(argv[4])
        # procsPerBlock = int(argv[5])
        # goalsPerProblem = int(argv[6])
        # output_folder = argv[7]

        procUnits = args.procUnits
        fromBlocks = args.fromBlocks
        toBlocks = args.toBlocks
        belts = args.belts
        procsPerBlock = args.procsPerBlock
        goalsPerProblem = args.goalsPerProblem
        output_folder = args.output

        # incremental_goals = True
        incremental_goals = args.incrementalGoals

        generate_intention_pddl = False
        generate_pddl = False

        if args.format == 'intention':
            generate_intention_pddl = True
        elif args.format == 'pddl':
            generate_pddl = True
        elif args.format == 'both':
            generate_pddl = generate_intention_pddl = True

        for blocks in range(fromBlocks, toBlocks):
            env = ProdCell(procUnits=procUnits, blocks=blocks, belts=belts, procsPerBlock=procsPerBlock)
            if incremental_goals:
                problems = env.generate_incremental_problems(goalsPerProblem)
            else:
                problems = env.generate_problems(goalsPerProblem)

            if generate_intention_pddl:
                instanceFile = output_folder+"/pb%s.pddl" % blocks
                env.write_int_pddl_problem(problems[-1].initial_state,
                                           desires=problems,
                                           templateFile=ProdCell.PB_INTENTION_TEMPLATE,
                                           instanceFile=instanceFile, problemName='pb%s' % blocks)
            if generate_pddl:
                for p, problem in enumerate(problems):
                    instanceFile = output_folder+"/pb%s-%s.pddl" % (blocks, p)
                    env.write_pddl_problem(problem.initial_state,      
                                           goal_state=problem.goal(),
                                           templateFile=ProdCell.PB_TEMPLATE,
                                           instanceFile=instanceFile, problemName='pb%s-%s' % (blocks, p))
        shutil.copy(ProdCell.DOMAIN, output_folder+"/domain.pddl")

    except Exception as e:
        # print("Usage: ")
        # print(argv[0] + " <proc_units> <from_blocks> <to_blocks> <belts> <procs_per_block> <goals_per_problem> <outfolder>")
        # print(argv[0] + " 4 4 10 2 1 2 tmp/")
        parser.print_help()
        raise e


if __name__ == "__main__":  # pragma: no cover
    import sys
    try:
        main(sys.argv)
    except Exception as e:
        print(e)
        sys.exit(-1)
