#!/usr/bin/env python
# Four spaces as indentation [no tabs]

# Felipe's implementation of Landmark heuristics

from typing import Collection
from collections import defaultdict, deque
from pddl.heuristic import Heuristic
from pddl.state import apply, applicable
from pddl.action import Action
from pddl.pddl_preprocessor import compute_all_facts

from heap_queue import priority_queue

# For stats collection:
import time


class LandmarkGenerator():

    def __init__(self):
        self.fact_landmarks = set()
        self.action_landmarks = set()

    @property
    def get_action_landmarks(self):
        return self.action_landmarks

    @property
    def get_fact_landmarks(self):
        return self.fact_landmarks

    def is_landmark(self, fact: tuple):
        """
        Checks whether fact is a landmark
        :param fact:
        :return:
        :rtype bool
        """
        raise NotImplementedError("Unimplemented")

    def generate_landmarks(self, domain, initial_state, goals):
        """
        :param domain:
        :param initial_state:
        :param goals:
        :return:
        :rtype set
        """
        raise NotImplementedError("Unimplemented")


class DeleteRelaxationLandmarkGenerator(LandmarkGenerator):
    """
    Hoffmann et al paper: Ordered Landmarks in Planning.
    (http://aaaipress.org/Papers/JAIR/Vol22/JAIR-2208.pdf)

    This implementation uses a Relaxed Planning Graph (RPG)
    to extract Conjunctive Landmarks from a planning problem (initial and goal state).
    """
    def __init__(self, actions: Collection[Action]):
        super().__init__()
        self.all_facts = compute_all_facts(actions)

    def generate_landmarks(self, domain: Collection[Action], initial_state: frozenset[tuple], goals: tuple[tuple, tuple]) -> set:
        """Generate delete relaxed landmarks. This code was adapted from Pyperplan

        Args:
            domain (_type_): _description_
            initial_state (_type_): _description_
            goals (_type_): _description_
        """
        (positive_goals, negative_goals) = goals
        fact_landmarks = set(positive_goals)
        possible_landmarks = self.all_facts - positive_goals

        for fact in possible_landmarks:
            current_state = initial_state
            goal_reached = current_state >= positive_goals

            while not goal_reached:
                previous_state = current_state
                for op in domain:
                    if applicable(current_state, op.positive_preconditions, set()) and fact not in op.add_effects:
                        current_state = apply(current_state, op.add_effects, set())
                        if current_state >= positive_goals:
                            break
                if previous_state == current_state and not current_state >= positive_goals:
                    fact_landmarks.add(fact)
                    break
                goal_reached = current_state >= positive_goals
        return fact_landmarks

    def compute_landmark_costs(self, domain: Collection[Action], fact_landmarks: Collection[tuple]):
        op_to_lm = defaultdict(set)  
        for operator in domain:
            op_to_lm[operator] = set()
            for landmark in fact_landmarks:
                if landmark in operator.add_effects:
                    op_to_lm[operator].add(landmark)
        min_cost = defaultdict(lambda: float("inf"))
        # min_cost = dict(lambda: float("inf"))
        for operator, landmarks in op_to_lm.items():
            landmarks_achieving = len(landmarks)
            for landmark in landmarks:
                min_cost[landmark] = min(min_cost[landmark], 1 / landmarks_achieving)
        return min_cost


class NaiveLandmarkHeuristic(Heuristic):
    # TODO: this is a crude replication of a heuristic from pyperplan, it is probably wrong

    def __init__(self, stats=None):
        super().__init__(is_safe=True, is_goal_aware=True, is_consistent=True, stats=stats)
        self.landmarks = None
        self.goals = None

    def compute_landmarks(self, domain: Collection[Action], initial_state: frozenset[tuple], goals: tuple[tuple, tuple]):
        self.task = domain

        # TODO Cache the generator
        generator = DeleteRelaxationLandmarkGenerator(domain)
        self.landmarks = generator.generate_landmarks(domain, initial_state, goals)
        assert goals[0] <= self.landmarks
        self.costs = generator.compute_landmark_costs(domain, self.landmarks)
        # self.node_unreached = {None: self.landmarks - initial_state}
        self.node_unreached = defaultdict(lambda: self.landmarks - initial_state)

    def reset(self, actions, initial_state, goals):
        self.goals = goals
        self.landmarks = None
        self.compute_landmarks(actions, initial_state, goals)

    def h(self, actions, initial_state, goal, parent_node=None):
        # Initialise the heuristic on the first call
        if self.landmarks is None or self.goals != goal:
            self.compute_landmarks(actions, initial_state, goal)
            self.goals = goal
        if parent_node is None:
            unreached = self.landmarks - initial_state
        else:
            if parent_node not in self.node_unreached:
                unreached = self.node_unreached[parent_node[1]] - parent_node[0].add_effects
                self.node_unreached[parent_node] = unreached
            else:
                unreached = self.node_unreached[parent_node]
            unreached = unreached | (goal[0] - initial_state)
        return sum(self.costs[landmark] for landmark in unreached)


class LMCutHeuristic(Heuristic):

    def __init__(self, stats=None, verbose=False):
        super().__init__(is_safe=True, is_goal_aware=True, is_consistent=True, stats=stats)

        # Stores the Relaxed Planning Graph in key/value pairs.
        self.facts = dict()
        self.actions = dict()

        # All reachable facts stored here:
        self.reachable = set()

        # Produce verbose output related to this heuristic if -v flag passed.
        self.verbose = verbose

        # Constants
        self.INF = float("inf")
        self.GOAL_FACT = ('GOAL_FACT')
        self.GOAL_ACTION = "GOAL_ACTION"
        self.DUMMY = ('DUMMY_FACT')

    def reset(self, actions, initial_state, goals):
        # Stores the Relaxed Planning Graph in key/value pairs.
        self.facts = dict()
        self.actions = dict()

        # All reachable facts stored here:
        self.reachable = set()
        self.create_rpg(actions, initial_state, goals)

    def create_rpg(self, actions, initial_state, goal_facts):
        # Retrieve all grounded predicates in the domain from the actions passed in.
        facts = compute_all_facts(actions)

        # Patch fix to account for all states including those that are connected to the initial state.
        facts = facts.union(initial_state)

        # Stores connections between facts and their associated actions - used to help build up the fact nodes.
        fact_preaction = {}
        fact_effaction = {}

        for action in actions:
            # Convert action representation to a string instead of a tuple.
            action_name = str(repr(action))

            # If there are no preconditions, create a dummy fact to link to the
            # action's preconditions (Helmert et al., 2009)
            if action.positive_preconditions is None:
                if self.DUMMY not in self.facts:
                    self.facts[self.DUMMY] = (
                        self.INF,
                        [],
                        [],
                        self.DUMMY
                    )
                action.positive_preconditions = frozenset({self.DUMMY})
                fact_preaction.setdefault(self.DUMMY, []).append(action_name)

            self.actions[action_name] = (
                action.positive_preconditions,      # [0] facts which must be satisfied to apply this action
                1.0,                                # [1] the cost of the action (we will decrease this cost by the minimum cost action on each cut it's involved in)
                action.add_effects,                 # [2] facts which are made true as a result of this action
            )

            for fact in action.positive_preconditions:
                fact_preaction.setdefault(fact, []).append(action_name)

            for fact in action.add_effects:
                fact_effaction.setdefault(fact, []).append(action_name)

        # Create fact nodes using the action connections defined above.
        for fact in facts:
            if fact in goal_facts:
                # Create fact node with goal action connection if this is a goal fact.
                self.facts[fact] = (
                    self.INF,
                    fact_preaction.get(fact, []) + [self.GOAL_ACTION],
                    fact_effaction.get(fact, []),
                    fact
                )
            else:
                self.facts[fact] = (
                    self.INF,                           # [0] the hmax value of the fact (assumed to be infinity unless proven otherwise)
                    fact_preaction.get(fact, []),       # [1] the actions for which this fact is a precondition
                    fact_effaction.get(fact, []),       # [2] the actions for which this fact is an effect
                    fact                                # [3] the fact name itself
                )

        # Create a goal action for which the goal facts are preconditions, and its effect is a singular fact.
        self.actions[self.GOAL_ACTION] = (
            frozenset(goal_facts),                      # [0] all positive goal facts
            0.0,                                        # [1] the action cost - zero, since this is the start of the goal zone
            frozenset({self.GOAL_FACT}),                # [2] the effects of this action, just the goal fact which we use to measure hmax
        )

        # Create a goal fact - used for hmax.
        self.facts[self.GOAL_FACT] = (
            self.INF,
            [],
            frozenset({self.GOAL_ACTION}),
            self.GOAL_FACT
        )

    def compute_hmax(self, state):
        """
            Computes the hmax values for each node in the planning graph using Dijkstra's algorithm.

            Reference: adapted from pyperplan - lm_cut.py
        """
        self.reachable.clear()

        facts_processed = []
        fringe = priority_queue.PriorityQueue()

        if self.facts.get(self.DUMMY) is not None:
            state = state.union({self.DUMMY})

        for fact in self.facts:
            _, pre_of, eff_of, name = self.facts[fact]

            if name in state:
                # Enqueue the initial state facts into the priority queue, all with an hmax value of 0.
                self.facts[fact] = (0.0, pre_of, eff_of, name)
                facts_processed.append(self.facts[fact])
                fringe.push(self.facts[name], 0.0)
            else:
                # Reset all other fact node hmax values to infinity.
                self.facts[fact] = (self.INF, pre_of, eff_of, name)

        # Store the number of preconditions in each action. An action cannot be applied [its effects
        # cannot be explored] until this number reduces to 0.
        unsatisfied_preconditions = {a[0]: len(a[1][0]) for a in self.actions.items()}

        # While facts have yet to be fully explored, do:
        while not fringe.is_empty():
            hmax, pre_of, eff_of, name = fringe.pop()

            self.reachable.add(name)

            # For each action in which this fact appears as a precondition, do:
            for action in pre_of:
                unsatisfied_preconditions[action] -= 1

                if unsatisfied_preconditions[action] == 0:
                    # We will propagate the hmax value forward to the next level of fact nodes in the RPG.
                    # Start by adding the current action cost to the hmax value of the fact node being processed.
                    next_hmax = hmax + self.actions[action][1]

                    # Gets the list of facts featured in this action's add effects list.
                    action_effects = self.actions[action][2]

                    # For each fact in the effects of this action, do:
                    for effect in action_effects:
                        eff_hmax, eff_precond, eff_effects, eff_name = self.facts[effect]

                        # If the hmax value of the effect is less than the hmax value to be propagated, then update.
                        if next_hmax < eff_hmax:
                            self.facts[eff_name] = (next_hmax, eff_precond, eff_effects, eff_name)

                        # Add all neighbouring facts to the fringe for consideration.
                        if self.facts[eff_name] not in facts_processed:
                            facts_processed.append(self.facts[eff_name])
                            fringe.push(self.facts[eff_name], self.facts[eff_name][0])

    def compute_modified_planning_task(self) -> dict:
        """
            Helmert et al. (2009)
            Assuming we have a relaxed planning task with finite hmax values, this function marks the best achieving fact
            from the preconditions of each action, based on the hmax values previously calculated.
        """
        # Stores key/value pairs - key being action name, value being the max achiever fact from the preconditions of action.
        modified_planning_task = dict()

        # For each action in the domain, do:
        for action in self.actions.items():
            # Get each fact node given in the action's preconditions list.
            preconditions = [self.facts[fact] for fact in action[1][0]]

            # If any of this action's preconditions were never reached during hmax computation, ignore.
            if any([fact[0] == self.INF for fact in preconditions]):
                modified_planning_task[action[0]] = None
                continue

            # Collect the maximum achieving fact based on each fact's hmax value - using the fact name
            # as a tiebreaker for equal hmax values.
            max_achieving_fact = max([fact for fact in preconditions], key=lambda f: (f[0], f[3]))

            # Store the fact name inside the modified planning task.
            modified_planning_task[action[0]] = max_achieving_fact[3]

        return modified_planning_task

    def compute_goal_zone_fringe(self, max_achievers) -> set:
        """
            Returns a set of facts that appear on the fringe of the goal zone, using the
            depth-first search algorithm as a base.
        """
        goal_zone = set()

        # Start from the explicit goal fact, we know its only parent action is zero-cost
        # anyway, so at least one fact will be included in the goal zone.
        stack = deque()
        stack.append(self.GOAL_FACT)

        # While we have facts to consider, do:
        while stack:
            fact = stack.pop()

            # If we were able to reach this fact from the initial state, and we haven't
            # already added the fact to the goal zone, add it.
            if fact in self.reachable and fact not in goal_zone:
                goal_zone.add(fact)

                # Then consider the max achieving facts of each action for which this
                # fact appears as an effect.
                effect_of = self.facts[fact][2]

                for action in effect_of:
                    action_cost = self.actions[action][1]

                    # If the action is zero-cost, it's inside the goal-zone, thus we add
                    # its max-achieving fact to the stack for inclusion in the goal zone.
                    if action_cost == 0:
                        max_achiever = max_achievers[action]
                        stack.append(max_achiever)

        return goal_zone

    def next_cut(self, state, goal_zone) -> set:
        """
            Returns a set of disjunctive action landmarks, forming a single cut in the planning graph.

            Reference: adapted from pyperplan - lm_cut.py
        """

        facts_processed = set()
        fringe = deque()

        for fact in state:
            fringe.append(self.facts[fact])
            facts_processed.add(fact)

        cut = set()

        # Store the number of preconditions in each action. An action cannot be applied [its effects
        # cannot be explored] until this number reduces to 0.
        unsatisfied_preconditions = {a[0]: len(a[1][0]) for a in self.actions.items()}

        # While facts have yet to be considered, do:
        while fringe:
            _, pre_of, _, _ = fringe.popleft()

            # Iterate through each action for which this fact appears as a precondition.
            for action in pre_of:
                unsatisfied_preconditions[action] -= 1

                # If all preconditions were satisfied:
                if unsatisfied_preconditions[action] == 0:
                    action_pre, action_cost, action_eff = self.actions[action]

                    # Check if any of its effects are in the goal zone. If they are, then
                    # this action acts as a transition into the goal zone, and should be
                    # included in the cut.
                    for effect in action_eff:
                        if effect in facts_processed:
                            continue
                        if effect in goal_zone:
                            # We include the action name inside the cut entry to refer back to
                            # inside the main h function.
                            cut.add((action_pre, action_cost, action_eff, action))
                            continue
                        else:
                            facts_processed.add(effect)
                            fringe.append(self.facts[effect])

        return cut

    def h(self, actions, initial_state, goal, parent_node=None):
        if self.verbose:
            time_start = time.time()

        # We only consider positive goals.
        goal = goal[0]

        # If we're starting a new heuristic search, there won't be a parent node.
        if not parent_node:
            # Create the Planning Graph.
            self.create_rpg(actions, initial_state, goal)
        else:
            # Reset only those elements of the planning graph that are recomputed on
            # each run - do not reconstruct the full rpg from scratch.
            for f_key, (hmax, pre_of, eff_of, f_name) in self.facts.items():
                if hmax != self.INF:
                    # Reset fact hmax values to infinity.
                    self.facts[f_key] = (self.INF, pre_of, eff_of, f_name)

            for a_key, (action_pre, action_cost, action_eff) in self.actions.items():
                if action_cost != 1.0:
                    # Reset action costs to 1.0
                    self.actions[a_key] = (action_pre, 1.0, action_eff)

        # Tracks the number of landmarks we find in this call.
        lms_found = 0

        # Heuristic Value - the sum of each min-cost action found from each cut
        h = 0.0

        # Perform initial computation of max-heuristic across all actions.
        self.compute_hmax(initial_state)

        # If we cannot reach the converged goal fact given the initial_state, we return
        # infinity (unreachable).
        if self.facts[self.GOAL_FACT][0] == self.INF:
            return self.INF

        # While cuts have yet to be found, do:
        while self.facts[self.GOAL_FACT][0] != 0:
            # Find a cut of disjunctive actions, and extract the minimum cost action.
            cut = self.next_cut(
                initial_state, 
                self.compute_goal_zone_fringe(
                    self.compute_modified_planning_task()
                )
            )

            # For verbose output, collect number of landmarks detected in this h call.
            if cut: lms_found += 1

            # Identify the minimum cost action from the cut and increment the h-value by this cost.
            min_cut_cost = self.INF
            for (action_pre, action_cost, action_eff, action_name) in cut:
                if action_cost >= 1.0 and action_cost < min_cut_cost:
                    min_cut_cost = action_cost
            h += min_cut_cost

            # Reduce all actions in the cut by the minimum action cost.
            for (action_pre, action_cost, action_eff, action_name) in cut:
                self.actions[action_name] = (action_pre, action_cost - min_cut_cost, action_eff)

            # Recompute the fact hmax values based on the new action costs.
            self.compute_hmax(initial_state)

        if self.GOAL_FACT not in self.reachable:
            return self.INF

        if self.verbose:
            print("LM-Cut Heuristic Stats")
            print(f"Number of LMs: {lms_found}")
            print(f"H Comp Time  : {time.time() - time_start}s")

            # Prevent these stats from being printed again.
            self.verbose = False

        return h
