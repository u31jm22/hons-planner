#!/usr/bin/env python
# Four spaces as indentation [no tabs]


def applicable(state, positive, negative):
    return positive.issubset(state) and not negative.intersection(state)


def apply(state, positive, negative):
    return frozenset(state.difference(negative).union(positive))


def regressable(state, add_effects, del_effects):
    return add_effects.intersection(state) and del_effects.intersection(state)


def regress(state, action):
    return frozenset((state.difference(action.add_effects).union(action.positive_preconditions)))


def stateToLisp(state):
    lisp = '('
    # Nasty iterative way of doing this
    for literal in state:
        parf = ['{!s}' for par in literal]
        parf = ' '.join(parf)
        pars = parf.format(*list(literal))
        lisp += '({!s})'.format(pars)
    lisp += ') '
    return lisp
