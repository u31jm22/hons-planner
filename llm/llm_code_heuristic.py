"""
LLM-generated code heuristic for classical planning.
The LLM generates a Python function once, which is then used for all states.
"""
import hashlib
import re


class LLMCodeHeuristic:
    """
    Heuristic where LLM generates Python code for a heuristic function.
    """
    
    def __init__(self, model, domain_pddl_path: str, prompt_template: str = None):
        """
        Args:
            model: ModelWrapper instance
            domain_pddl_path: Path to PDDL domain file
            prompt_template: Template for asking LLM to generate code
        """
        self.model = model
        self.domain_pddl_path = domain_pddl_path
        
        # Read domain PDDL
        with open(domain_pddl_path, 'r') as f:
            self.domain_pddl = f.read()
        
        # Default prompt if none provided
        if prompt_template is None:
            prompt_template = self._default_prompt_template()
        
        # Generate the heuristic function code
        self.heuristic_code = self._generate_heuristic_code(prompt_template)
        
        # Compile and store the function
        self.heuristic_fn = self._compile_heuristic(self.heuristic_code)
    
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
        code_match = re.search(r'```python\s*(.*?)\s*```', response, re.DOTALL)
        if code_match:
            return code_match.group(1).strip()
        
        # Otherwise return raw response
        return response.strip()
    
    def _compile_heuristic(self, code: str):
        """
        Safely compile and extract the heuristic function.
        """
        try:
            # Create a safe namespace
            namespace = {}
            
            # Execute the code in the namespace
            exec(code, namespace)
            
            # Extract the 'h' function
            if 'h' not in namespace:
                raise ValueError("Generated code does not define function 'h'")
            
            return namespace['h']
        
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
        except Exception as e:
            print(f"ERROR executing heuristic: {e}")
            # Fallback to simple heuristic
            return float(len(goals[0]))
    
    def h(self, actions, state, goals, parent):
        """
        Compatibility with planner interface.
        """
        return self.__call__(actions, state, goals, parent)
