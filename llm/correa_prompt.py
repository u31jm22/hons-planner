# llm/correa_prompt.py

CORREA_DEPOTS_PROMPT = """
You are a highly skilled professor in AI planning and a proficient Python programmer.
Your task is to design a domain-dependent heuristic for the classical planning domain "Depots".

The planner represents states and goals as follows:
- state: a frozenset of tuples like ('at', 'crate1', 'depot0'),
         ('in', 'crate2', 'truck0'),
         ('at-truck', 'truck0', 'distributor1'),
         ('clear', 'crate3'), etc.
- goals: (positive_goals, negative_goals), each a frozenset of tuples in the same format.

You must implement the following Python function:

    def h(state, goals):
        \"\"\"
        Domain-specific heuristic for the Depots domain.
        state: frozenset of ground predicates describing the current world.
        goals: (positive_goals, negative_goals), each a frozenset of ground predicates.
        Returns: a non-negative int or float estimating the remaining number of actions
                 needed to reach a goal state from the current state.
        The heuristic must be deterministic and must not modify state or goals.
        It must run quickly and avoid any form of search.
        \"\"\"

High-level guidance for the heuristic:
1. Interpret the goal: for each crate, identify its desired destination location in positive_goals.
2. From the current state, determine for each crate:
   - where it is (on the ground at some location, in a truck, on another crate, etc.),
   - whether it is already at its goal location.
3. For crates that are not yet at their goal, estimate:
   - how many load/unload operations are needed,
   - whether a truck must drive between locations, and count such moves,
   - any extra steps needed to clear blocking crates or free hoists.
4. Combine these estimates into a single heuristic value:
   - sum contributions over all crates,
   - optionally add small extra costs when trucks or hoists are far from useful positions.

Constraints:
- Do NOT perform search or simulate full plans.
- Do NOT call external libraries or random functions.
- The function must be pure: no I/O, no global state.
- Always return a non-negative number, even if some goal appears already satisfied.

Now write only the Python code for the function h(state, goals), with no explanation or comments outside the code block.
"""

GRIPPER_PROMPT = """
You are a highly skilled professor in AI planning and a proficient Python programmer.
Your task is to design a domain-dependent heuristic for the classical planning domain "Gripper".

The planner represents states and goals as follows:
- state: a frozenset of tuples like
    ('at-robby', 'rooma'),
    ('at', 'ball1', 'rooma'),
    ('carry', 'ball2', 'left'),
    ('free', 'right'), etc.
- goals: (positive_goals, negative_goals), each a frozenset of tuples,
  e.g. ('at', 'ball1', 'roomb') meaning ball1 should end up in roomb.

You must implement the following Python function:

    def h(state, goals):
        \"\"\"
        Domain-specific heuristic for the Gripper domain.
        state: frozenset of ground predicates describing the current world.
        goals: (positive_goals, negative_goals), each a frozenset of ground predicates.
        Returns: a non-negative int or float estimating the remaining number of actions
                 needed to reach a goal state from the current state.
        The heuristic must be deterministic and must not modify state or goals.
        It must run quickly and avoid any form of search.
        \"\"\"

High-level guidance for the heuristic:
1. Interpret the goal:
   - identify, for each ball, its desired destination room from positive_goals.
2. From the current state, determine:
   - the current room of the robot,
   - for each ball, whether it is already at its goal room,
   - which balls are currently carried in the left or right gripper, and which grippers are free.
3. For balls that are not yet at their goal room, estimate:
   - whether the robot must move from its current room to the ball's room,
   - whether it must pick up the ball (respecting the two-gripper capacity),
   - whether it must move to the goal room,
   - whether it must drop the ball there.
4. Combine these estimates into a single heuristic value:
   - roughly count the remaining moves, picks, and drops,
   - take into account that the robot has two grippers and can sometimes carry two balls per trip.

Constraints:
- Do NOT perform search or simulate full plans.
- Do NOT call external libraries or random functions.
- The function must be pure: no I/O, no global state.
- Always return a non-negative number, even if some goal appears already satisfied.

Now write only the Python code for the function h(state, goals), with no explanation or comments outside the code block.
"""

