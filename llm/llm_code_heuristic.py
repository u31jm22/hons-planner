"""
LLM-generated code heuristic for classical planning.
The LLM generates a Python function once, which is then used for all states.
"""
import hashlib
import re
import importlib.util
from pathlib import Path


class LLMCodeHeuristic:
    """
    Heuristic where LLM generates Python code for a heuristic function.
    """

    def __init__(self, model=None, domain_pddl_path: str | None = None,
                 prompt_template: str | None = None, heuristic_fn=None):
        """
        Args:
            model: ModelWrapper instance (for on-the-fly code generation), optional
            domain_pddl_path: Path to PDDL domain file (used when generating code)
            prompt_template: Template for asking LLM to generate code
            heuristic_fn: Optional pre-defined Python function h(state, goals)
        """
        self.model = model
        self.domain_pddl_path = domain_pddl_path
        self.domain_pddl = None
        self.heuristic_code = None

        # Case 1: we are given a ready-made heuristic function
        if heuristic_fn is not None:
            self.heuristic_fn = heuristic_fn
            return

        # Case 2: generate code from LLM using the domain PDDL
        if domain_pddl_path is None or model is None:
            raise ValueError(
                "Either heuristic_fn must be provided, or both model and domain_pddl_path must be set."
            )

        with open(domain_pddl_path, "r") as f:
            self.domain_pddl = f.read()

        if prompt_template is None:
            prompt_template = self._default_prompt_template()

        self.heuristic_code = self._generate_heuristic_code(prompt_template)
        self.heuristic_fn = self._compile_heuristic(self.heuristic_code)

    @classmethod
    def from_code_file(cls, path: Path):
        """
        Load a candidate module that defines h(state, goals) and wrap it.

        This is used for the selected LLM-generated heuristics: the code is
        already on disk, so we just import it and grab the function h.
        """
        path = Path(path)
        spec = importlib.util.spec_from_file_location("llm_candidate_module", path)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)

        if not hasattr(module, "h"):
            raise ValueError(f"No function h(state, goals) in {path}")

        return cls(heuristic_fn=module.h)

    def _default_prompt_template(self):
        return """You are a classical planning expert. Given this PDDL domain, write a Python heuristic function that estimates the distance from a state to the goal.

PDDL Domain:
{domain}

Write a Python function with this exact signature:

def h(state, goals):
    # state is a frozenset of tuples like ('at', 'ball1', 'rooma')
    # goals is a tuple of (positive_goals, negative_goals) where each is a frozenset
    # Return a float/int estimate of steps remaining
    pass

Requirements:
- Return ONLY the Python code, no explanations
- Use simple logic (count unsatisfied goals, check predicates, etc.)
- Must return a numeric value
- Keep it under 20 lines

Your code:"""

    def _generate_heuristic_code(self, prompt_template: str) -> str:
        """
        Ask LLM to generate heuristic code.
        """
        prompt = prompt_template.format(domain=self.domain_pddl)
        response = self.model.predict(prompt)

        # Extract code block if wrapped in ```python ... ```
        code_match = re.search(r"```python\s*(.*?)\s*```", response, re.DOTALL)
        if code_match:
            return code_match.group(1).strip()

        # Otherwise return raw response
        return response.strip()

    def _compile_heuristic(self, code: str):
        """
        Safely compile and extract the heuristic function.
        """
        try:
            namespace: dict = {}
            exec(code, namespace)

            if "h" not in namespace:
                raise ValueError("Generated code does not define function 'h'")

            return namespace["h"]

        except Exception as e:
            print(f"ERROR compiling heuristic code: {e}")
            print(f"Code was:\n{code}")
            # Fallback: return a trivial heuristic
            return lambda state, goals: float(len(goals[0]))

    def __call__(self, actions, state, goals, parent=None):
        """
        Call the generated heuristic function.
        """
        try:
            return float(self.heuristic_fn(state, goals))
        except Exception:
            # Optional: comment out the print if too noisy
            # print(f"ERROR executing heuristic: {e}")
            return float(len(goals[0]))


    def h(self, actions, state, goals, parent):
        """
        Compatibility with planner interface.
        """
        return self.__call__(actions, state, goals, parent)
