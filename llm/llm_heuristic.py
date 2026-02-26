from typing import Any, Dict, Iterable, Tuple
import re

"""
LLM-based heuristic for classical planning.
"""


class LLMHeuristic:
    """
    LLM-based heuristic integrated with Felipe's Python planner.

    - Constructed once per problem.
    - Called as h(actions, state, goals, parent=None) -> numeric heuristic.
    - All LLM-specific logic (prompt building, API calls, caching) lives here.
    """

    def __init__(
        self,
        domain_name: str,
        model: Any,
        prompt_template: str,
        goal_description: str | None = None,
        cache: Dict[str, float] | None = None,
    ) -> None:
        self.domain_name = domain_name
        self.model = model
        self.prompt_template = prompt_template
        self.goal_description = goal_description or ""
        self.cache = cache or {}

    def __call__(
        self,
        actions: Iterable[Any],
        state: Any,
        goals: Tuple[Iterable[Any], Iterable[Any]],
        parent: Any | None = None,
    ) -> float:
        """
        Compute a heuristic estimate for the given search state.

        Parameters
        ----------
        actions : iterable
            Ground actions available in the current problem (unused for now).
        state : Any
            Current search state object.
        goals : (positive_goals, negative_goals)
            Goal description from the planner (unused for now; we use goal_description).
        parent : Any | None
            Parent node in the search tree (unused, kept for interface compatibility).
        """
        key = self._state_key(state)
        if key in self.cache:
            return self.cache[key]

        prompt = self._build_prompt(state)
        raw_answer = self.model.predict(prompt)
        h_value = self._parse_answer(raw_answer)

        # Safety: ensure non-negative numeric heuristic
        h_value = max(0.0, float(h_value))

        self.cache[key] = h_value
        return h_value

    # -------- internal helpers --------

    def _state_key(self, state: Any) -> str:
        """
        Build a deterministic key for this state for caching.
        """
        facts = getattr(state, "facts", [])
        return "|".join(sorted(map(str, facts)))

    def _build_prompt(self, state: Any) -> str:
        """
        Turn the current state + goal into a concrete LLM prompt.
        """
        state_repr = self._state_to_text(state)
        return self.prompt_template.format(
            domain=self.domain_name,
            state=state_repr,
            goal=self.goal_description,
        )

    def _state_to_text(self, state: Any) -> str:
        """
        Convert planner state into a textual description for the LLM.
        """
        facts = getattr(state, "facts", [])
        return "\n".join(sorted(map(str, facts)))

    def _parse_answer(self, answer: str) -> float:
        """
        Parse the LLM's answer string into a numeric heuristic value.
        """
        m = re.search(r"-?\d+(\.\d+)?", answer)
        if not m:
            return 0.0
        return float(m.group(0))
