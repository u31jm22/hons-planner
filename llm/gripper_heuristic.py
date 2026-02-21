# Auto-generated wrapper that loads the selected candidate heuristic for gripper.
# Selected: gripper_candidate_1

from __future__ import annotations

import importlib.util
from pathlib import Path

from pddl.heuristic import Heuristic


def _load_candidate_func(candidate_filename: str):
    candidates_dir = Path(__file__).parent / "candidates"
    candidate_path = candidates_dir / candidate_filename
    if not candidate_path.exists():
        raise FileNotFoundError(f"Candidate file not found: {candidate_path}")

    spec = importlib.util.spec_from_file_location(candidate_path.stem, candidate_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load spec for: {candidate_path}")

    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[attr-defined]

    if not hasattr(mod, "h"):
        raise AttributeError(f"Candidate module has no function 'h': {candidate_path}")
    return mod.h


# Load the selected candidate's h(state, goals) at import time
_CANDIDATE_H = _load_candidate_func("gripper_candidate_1.py")


class LLMGeneratedHeuristic(Heuristic):
    """
    Domain-specific heuristic wrapper for Gripper.

    Delegates to the selected LLM-generated candidate function:
        h(state, goals) -> float
    where:
      - state is a frozenset of grounded tuples, e.g. ('at', 'ball1', 'rooma')
      - goals is (positive_goals, negative_goals), each a frozenset
    """

    def __init__(self, stats=None):
        super().__init__(
            is_safe=True,
            is_goal_aware=True,
            is_consistent=True,
            stats=stats,
        )

    def h(self, actions, initial_state, goal, parent_node=None) -> float:
        try:
            # initial_state is already the grounded state set used throughout the planner
            return float(_CANDIDATE_H(initial_state, goal))
        except Exception:
            # Fallback: 0 heuristic if candidate errors
            return 0.0
