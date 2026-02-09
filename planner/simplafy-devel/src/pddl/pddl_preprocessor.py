#!/usr/bin/env python
# Four spaces as indentation [no tabs]

#
#  pddl_preprocessor.py
#  pddl
#
#  Created by Felipe Meneguzzi on 2021-04-20.
#  Copyright 2021 Felipe Meneguzzi. All rights reserved.
#
import logging
from typing import Set, Any, Collection

from pddl.state import applicable
from pddl.action import Action


def compute_all_facts(actions: Collection[Action]):
    """Helper function to compute all the facts in a problem (as represented by the actions)

    Args:
        actions (_type_): _description_
    """
    all_facts = set()
    for a in actions:
        all_facts |= a.add_effects
        all_facts |= a.positive_preconditions
        all_facts |= a.del_effects  # TODO I may not need to consider all this crap
        all_facts |= a.negative_preconditions  # TODO I may not need to consider all this crap
    all_facts = frozenset(all_facts)
    return all_facts


class PDDLPreprocessor:
    """A class to preprocess PDDL domains"""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose

    def preprocess_actions(self, actions, initial_state, goal):
        """Preprocess actions
        :param actions - Actions to be preprocessed
        :param initial_state - The initial state of a PDDL problem
        :param goal - The goal state """
        raise NotImplementedError("Unimplemented")

    def preprocess_states(self, states, initial_state, goal):
        """"Somehow preprocess states for some purpose"""
        raise NotImplementedError("Unimplemented")


class RPGReachabilityPreprocessor(PDDLPreprocessor):

    def __init__(self):
        super().__init__()

    def preprocess_actions(self, actions, initial_state, goal):
        """Uses the RPG to eliminate unreachable actions"""
        positive_g, negative_g = goal
        reachable_literals = initial_state
        positive_literals = None
        reachable_actions: Set[Any] = set()
        while positive_literals != reachable_literals:
            # XXX: Recall that we need to run this until we reach a fixpoint (not the goal)
            # if positive_g.issubset(reachable_literals):
            #     return reachable_actions
            positive_literals = reachable_literals
            for a in actions:
                if applicable(positive_literals, a.positive_preconditions, frozenset([])):  # TODO: This does not handle negative preconditions correctly
                    reachable_actions.add(a)
                    reachable_literals = reachable_literals.union(a.add_effects)

        return list(reachable_actions)

    def preprocess_states(self, states, initial_state, goal):
        return states


class PyperPreprocessor(PDDLPreprocessor):

    def __init__(self):
        super().__init__()

    def preprocess_actions(self, actions, initial_state, goal):
        """Preprocess of operators based on relevance analysis, adapted from PyperPlan"""
        debug = False
        debug_pruned_op = set()

        relevant_facts = set()
        old_relevant_facts = set()
        changed = True
        for fact in goal[0]:
            relevant_facts.add(fact)
        for fact in goal[1]:
            relevant_facts.add(fact)

        while changed:
            # set next relevant facts to current facts
            # if we do not add anything in the following for loop
            # we have already found a fixpoint
            old_relevant_facts = relevant_facts.copy()
            # compute cut of relevant facts with effects of all operators
            for op in actions:
                new_addlist = op.add_effects & relevant_facts
                new_dellist = op.del_effects & relevant_facts
                if new_addlist or new_dellist:
                    # add all preconditions to relevant facts
                    relevant_facts |= op.positive_preconditions
                    relevant_facts |= op.negative_preconditions
            changed = old_relevant_facts != relevant_facts

        # delete all irrelevant effects
        del_operators = set()
        for op in actions:
            # calculate new effects
            new_addlist = op.add_effects & relevant_facts
            new_dellist = op.del_effects & relevant_facts
            if debug:
                debug_pruned_op |= op.add_effects - relevant_facts
                debug_pruned_op |= op.del_effects - relevant_facts
            # store new effects?
            op.add_effects = frozenset(new_addlist)
            op.del_effects = frozenset(new_dellist)
            if not new_addlist and not new_dellist:
                if self.verbose:
                    logging.debug("Relevance analysis removed operator %s" % op.name)
                del_operators.add(op)
        if debug:
            logging.info("Relevance analysis removed %d facts" % len(debug_pruned_op))
        # remove completely irrelevant operators
        return [op for op in actions if op not in del_operators]

    def preprocess_states(self, states, initial_state, goal):
        return states
