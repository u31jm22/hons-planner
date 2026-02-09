#!/usr/bin/env python
# Four spaces as indentation [no tabs]
import random
import itertools
import math
from typing import Tuple, FrozenSet, Collection, List

# An individual problem generator for the Production Cell domain
# In the interests of self containment, I'm replicating a lot of code from my BDI Planner Agent
# This is (or will be) available at https://github.com/meneguzzi/bdi-plan
# This might damn me to programmer's hell

# This code is also partially derived from 


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


class BlocksworldProblem:

    def __init__(self, initial_state: frozenset[tuple], positive_goals: frozenset[tuple], negative_goals: frozenset[tuple]):
        self.initial_state = initial_state
        self.positive_goals = positive_goals
        self.negative_goals = negative_goals

    def goal(self) -> Formula:
        return Formula(self.positive_goals, self.negative_goals)


class BlocksWorld:
    """Production cell problem generator.
    This will work for both PDDL and IntentionPlanning
    This code is directly derived from the Production Cell environment from [BDI-plan](https://github.com/meneguzzi/bdi-plan/blob/main/bdiplan/environments/prodcell.py)
    """

    DOMAIN = "generators/blocksworld/domain.pddl"
    PB_TEMPLATE = "generators/blocksworld/pbTemplate.pddl"
    PB_INTENTION_TEMPLATE = "generators/blocksworld/pbIntentionTemplate.pddl"

    def __init__(self, blocks: int = 4,
                 stacks: int = 4, desires: int = 0,
                 random_seed: float = None):
        self.random = random.Random(random_seed)
        self._blocks = blocks
        self._stacks = stacks
        self._desires = desires
        self._factored_goals = []
        self._activeBlocks = []

    def write_pddl_problem(self, initial_state: FrozenSetState,
                           goal_state: Formula, templateFile: str, instanceFile: str, problemName: str = None):
        with open(templateFile, encoding='UTF-8') as instream:
            with open(instanceFile, 'w', encoding='UTF-8') as outstream:
                for line in instream:
                    if '<BLOCKS>' in line:
                        # outstream.write(' '.join(self._blockNames) + " - object\n")
                        outstream.write(' '.join(self._blockNames) + "\n")
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
                    if '<BLOCKS>' in line:
                        # outstream.write(' '.join(self._blockNames) + " - object\n")
                        outstream.write(' '.join(self._blockNames) + "\n")
                    elif '<INITIAL_STATE>' in line:
                        outstream.write(str(initial_state))
                    elif '<DESIRES>' in line:
                        for desire in desires:
                            outstream.write('(:desire %s)\n' % str(desire.goal()))
                    elif problemName is not None and 'pbTemplateInstance' in line:
                        outstream.write(line.replace('pbTemplateInstance', problemName))
                    else:
                        outstream.write(line)

    def stack_to_predicates(self, stack: List):
        positions = [('clear', stack[0]), ('ontable', stack[-1])]
        for i in range(len(stack)-1):
            positions.append(('on', stack[i], stack[i+1]))
        return positions

    def generate_blocks(self, blocks: int) -> List[str]:
        self._blockNames = ["b%d" % b for b in range(blocks)]
        return self._blockNames

    def generate_stacks(self, blocks: int, stacks: int, blockNames: List[str]) -> Tuple[List[List[str]], List[str]]:
        block_stacks = []
        remaining_blocks = set(blockNames)
        blocks_per_stack = blocks // stacks
        for s in range(stacks):
            k = min(blocks_per_stack, len(remaining_blocks))
            new_stack = random.sample(sorted(remaining_blocks), k=k)
            block_stacks.append(new_stack)
            remaining_blocks = remaining_blocks.difference(new_stack)
        return block_stacks, remaining_blocks

    def generate_configuration(self, blocks: int, stacks: int) -> FrozenSetState:
        """Generates a blocksworld configuration (i.e. the PDDL representation of the initial state) for the parameters given

        Args:
            blocks (int): The number of blocks in the problem
            stacks (int): The number of stacks in which these blocks are organised

        Returns:
            _type_: _description_
        """

        blockNames = self.generate_blocks(blocks)
        block_stacks, remaining_blocks = self.generate_stacks(blocks, stacks, blockNames)

        for block in remaining_blocks:  # Any remaining blocks are left on the table
            block_stacks.append([block])

        self._positions = set()
        self._equalities = set([('equal', b, b) for b in blockNames] + [('handempty',)])

        for stack in block_stacks:
            self._positions = self._positions.union(self.stack_to_predicates(stack))

        initial_state = FrozenSetState(self._positions | self._equalities)
        return initial_state

    def generate_goal(self) -> Formula:
        consolidated_goals = [literal
                              for (_, goal) in self._factored_goals
                              for literal in goal.positive]
        goal_state = Formula(consolidated_goals, frozenset())
        return goal_state

    def generate_desires(self) -> Collection:
        return self._factored_goals

    def generate_problems(self, num_problems: int = 1) -> Collection[BlocksworldProblem]:
        problems = []
        for p in range(num_problems):
            initial_state = self.generate_configuration(self._blocks, self._stacks)
            self._factored_goals = []
            # TODO Rethink this to allow partial stacks
            stacks, _ = self.generate_stacks(self._blocks, self._desires, self._blockNames)
            for stack in stacks:
                positions = self.stack_to_predicates(stack)
                # Remove clear and ontable?
                context = (frozenset(), frozenset())
                desire = Formula(FrozenSetState(positions), frozenset())
                self._factored_goals.append((context, desire))

            goal_state = self.generate_goal()
            problem = BlocksworldProblem(initial_state, goal_state.positive, goal_state.negative)
            problems.append(problem)
        return problems

    def generate_incremental_problems(self, num_problems: int = 1) -> Collection[BlocksworldProblem]:
        problems = []
        initial_state = self.generate_configuration(self._blocks, self._stacks)
        # for p in range(num_problems):
        # TODO Rethink this to allow partial stacks
        stacks, _ = self.generate_stacks(self._blocks, self._desires, self._blockNames)
        for stack in stacks:
            positions = self.stack_to_predicates(stack)
            # Remove clear and ontable?
            context = (frozenset(), frozenset())
            desire = Formula(FrozenSetState(positions), frozenset())
            self._factored_goals.append((context, desire))
            goal_state = self.generate_goal()
            problem = BlocksworldProblem(initial_state, goal_state.positive, goal_state.negative)
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
                    prog='blocksworld',
                    description='Generates domain files for the Blocksworld domain',
                    epilog='Text at the bottom of help',
                    exit_on_error=False)

        parser.add_argument('output', help='Path to output folder')
        parser.add_argument('-s', '--step', default='1', type=int, help='Number of extra blocks per problem')
        parser.add_argument('-fb', '--fromBlocks', default='4', type=int, help='Starting number of blocks in the problem')
        parser.add_argument('-tb', '--toBlocks', default='10', type=int, help='Ending number of blocks in the problem')
        parser.add_argument('-st', '--stacks', default='2', type=int, help='Number of stacks of blocks in the initial state')
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

        step = args.step
        fromBlocks = args.fromBlocks
        toBlocks = args.toBlocks
        stacks = args.stacks
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

        for blocks in range(fromBlocks, toBlocks, step):
            env = BlocksWorld(blocks=blocks, stacks=stacks, desires=goalsPerProblem)
            if incremental_goals:
                problems = env.generate_incremental_problems(goalsPerProblem)
            else:
                problems = env.generate_problems(goalsPerProblem)

            if generate_intention_pddl:
                instanceFile = output_folder+"/pb%s.pddl" % blocks
                env.write_int_pddl_problem(problems[-1].initial_state,
                                           desires=problems,
                                           templateFile=BlocksWorld.PB_INTENTION_TEMPLATE,
                                           instanceFile=instanceFile, problemName='pb%s' % blocks)
            if generate_pddl:
                for p, problem in enumerate(problems):
                    instanceFile = output_folder+"/pb%s-%s.pddl" % (blocks, p)
                    env.write_pddl_problem(problem.initial_state,      
                                           goal_state=problem.goal(),
                                           templateFile=BlocksWorld.PB_TEMPLATE,
                                           instanceFile=instanceFile, problemName='pb%s-%s' % (blocks, p))
        shutil.copy(BlocksWorld.DOMAIN, output_folder+"/domain.pddl")

    except Exception as e:
        parser.print_help()
        raise e


if __name__ == "__main__":  # pragma: no cover
    import sys
    try:
        main(sys.argv)
    except Exception as e:
        print(e)
        sys.exit(-1)
