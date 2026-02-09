"""
LLM-based heuristic for classical planning.
"""
import hashlib


class LLMHeuristic:
    """
    Heuristic that calls an LLM to estimate distance to goal.
    """
    
    def __init__(self, model, prompt_template: str, cache=None):
        """
        Args:
            model: ModelWrapper instance
            prompt_template: String with {state} and {goals} placeholders
            cache: Dict for caching heuristic values by state
        """
        self.model = model
        self.prompt_template = prompt_template
        self.cache = cache if cache is not None else {}
    
    def __call__(self, actions, state, goals, parent=None):
        """
        Make the heuristic callable to match planner interface.
        Planner calls: self.h(actions, state, goals, parent)
        """
        return self.h(actions, state, goals, parent)
    
    def h(self, actions, state, goals, parent):
        """
        Compute heuristic value for given state.
        Must match Felipe's planner interface: h(actions, state, goals, parent)
        """
        # Build cache key from state
        state_key = self._hash_state(state)
        
        if state_key in self.cache:
            return self.cache[state_key]
        
        # Convert state and goals to text
        state_text = self._state_to_text(state)
        goals_text = self._goals_to_text(goals)
        
        # Fill prompt template
        prompt = self.prompt_template.format(
            state=state_text,
            goals=goals_text
        )
        
        # Call model
        response = self.model.predict(prompt)
        
        # Parse heuristic value
        h_val = self._parse_response(response)
        
        # Cache and return
        self.cache[state_key] = h_val
        return h_val
    
    def _hash_state(self, state):
        """Create a hashable key from state."""
        # State is a frozenset of tuples, convert to sorted tuple for hashing
        state_tuple = tuple(sorted(state))
        return hashlib.md5(str(state_tuple).encode()).hexdigest()
    
    def _state_to_text(self, state):
        """Convert state (frozenset of predicates) to readable text."""
        facts = sorted(list(state))
        return f"{len(facts)} facts: " + ", ".join(str(f) for f in facts[:10])
    
    def _goals_to_text(self, goals):
        """Convert goals to readable text."""
        goal_list = sorted(list(goals))
        return f"{len(goal_list)} goals: " + ", ".join(str(g) for g in goal_list)
    
    def _parse_response(self, response: str) -> float:
        """
        Extract a numeric heuristic value from LLM response.
        Fallback to 0 if parsing fails.
        """
        try:
            # Try to find first number in response
            import re
            match = re.search(r'\d+\.?\d*', response)
            if match:
                return float(match.group())
            return 0.0
        except:
            return 0.0
