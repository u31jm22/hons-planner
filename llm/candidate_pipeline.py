"""
Pipeline for generating, evaluating, and selecting LLM-generated heuristic candidates.
"""
import json
import subprocess
from pathlib import Path
from typing import List, Dict, Any


class CandidatePipeline:
    """
    Generates multiple candidate heuristics per domain and selects the best.
    """
    
    def __init__(self, model, project_root: Path):
        self.model = model
        self.project_root = project_root
        self.domains_dir = project_root / "domains"
        self.experiments_dir = project_root / "experiments"
        self.llm_dir = project_root / "llm"
        
        # Ensure directories exist
        self.experiments_dir.mkdir(exist_ok=True)
        (self.llm_dir / "candidates").mkdir(exist_ok=True)
    
    def generate_candidates(self, domain_name: str, num_candidates: int = 5) -> List[Dict[str, Any]]:
        """
        Generate multiple candidate heuristics for a domain.
        
        Args:
            domain_name: e.g., "gripper", "blocksworld", "logistics"
            num_candidates: Number of candidates to generate
            
        Returns:
            List of candidate dicts with 'id', 'code', 'prompt_variant'
        """
        domain_path = self.domains_dir / domain_name / "domain.pddl"
        
        if not domain_path.exists():
            raise FileNotFoundError(f"Domain not found: {domain_path}")
        
        with open(domain_path, 'r') as f:
            domain_pddl = f.read()
        
        candidates = []
        
        # Generate multiple candidates with different prompt variants
        for i in range(num_candidates):
            prompt = self._get_prompt_variant(domain_pddl, variant_id=i)
            
            print(f"Generating candidate {i+1}/{num_candidates} for {domain_name}...")
            response = self.model.predict(prompt)
            
            # Extract code
            code = self._extract_code(response)
            
            candidates.append({
                "id": f"{domain_name}_candidate_{i+1}",
                "code": code,
                "prompt_variant": i,
                "domain": domain_name
            })
        
        # Save candidates to file
        output_file = self.llm_dir / "candidates" / f"{domain_name}_candidates.json"
        with open(output_file, 'w') as f:
            json.dump(candidates, f, indent=2)
        
        print(f"Saved {num_candidates} candidates to {output_file}")
        return candidates
    
    def _get_prompt_variant(self, domain_pddl: str, variant_id: int) -> str:
        """
        Get different prompt variants to encourage diversity.
        """
        base = f"""You are a classical planning expert. Given this PDDL domain, write a Python heuristic function that estimates the distance from a state to the goal.

PDDL Domain:
{domain_pddl}

Write a Python function with this exact signature:

def h(state, goals):
    # state is a frozenset of tuples like ('at', 'ball1', 'rooma')
    # goals is a tuple of (positive_goals, negative_goals) where each is a frozenset
    # Return a float/int estimate of steps remaining
    pass
"""
        
        variants = [
            # Variant 0: Simple goal counting
            base + "\nRequirements:\n- Count unsatisfied goals\n- Return ONLY the Python code\n- Keep it simple (under 10 lines)\n\nYour code:",
            
            # Variant 1: Consider actions needed
            base + "\nRequirements:\n- Estimate based on actions needed to satisfy goals\n- Consider dependencies between predicates\n- Return ONLY the Python code\n- Keep it under 15 lines\n\nYour code:",
            
            # Variant 2: Weighted heuristic
            base + "\nRequirements:\n- Use weighted combinations of different factors\n- Consider both satisfied and unsatisfied goals\n- Return ONLY the Python code\n- Keep it under 20 lines\n\nYour code:",
            
            # Variant 3: Domain-specific features
            base + "\nRequirements:\n- Use domain-specific features from the PDDL\n- Think about what makes a state closer to the goal\n- Return ONLY the Python code\n- Keep it under 15 lines\n\nYour code:",
            
            # Variant 4: Optimistic estimate
            base + "\nRequirements:\n- Provide an optimistic (lower bound) estimate\n- Admissible heuristic preferred\n- Return ONLY the Python code\n- Keep it under 15 lines\n\nYour code:",
        ]
        
        return variants[variant_id % len(variants)]
    
    def _extract_code(self, response: str) -> str:
        """
        Extract Python code from LLM response.
        """
        import re
        
        # Try to extract from ```python ... ```
        code_match = re.search(r'```python\s*(.*?)\s*```', response, re.DOTALL)
        if code_match:
            return code_match.group(1).strip()
        
        # Try to extract from ``` ... ```
        code_match = re.search(r'```\s*(.*?)\s*```', response, re.DOTALL)
        if code_match:
            return code_match.group(1).strip()
        
        # Otherwise return raw response
        return response.strip()
    
    def evaluate_candidate(self, candidate: Dict[str, Any], training_problems: List[str]) -> Dict[str, Any]:
        """
        Evaluate a candidate on training problems.
        
        Args:
            candidate: Candidate dict with 'id', 'code', 'domain'
            training_problems: List of problem file names (e.g., ['p01.pddl', 'p02.pddl'])
            
        Returns:
            Dict with evaluation metrics
        """
        domain_name = candidate['domain']
        candidate_id = candidate['id']
        
        # Write candidate code to a temporary file
        candidate_file = self.llm_dir / "candidates" / f"{candidate_id}.py"
        with open(candidate_file, 'w') as f:
            f.write(candidate['code'])
        
        results = {
            "candidate_id": candidate_id,
            "coverage": 0,
            "total_expansions": 0,
            "total_time": 0.0,
            "solved": [],
            "failed": []
        }
        
        for prob in training_problems:
            prob_path = self.domains_dir / domain_name / prob
            
            print(f"  Testing {candidate_id} on {prob}...")
            
            # Run planner (we'll create a helper script for this)
            success, expansions, time = self._run_planner_with_candidate(
                domain_name, prob, candidate_file
            )
            
            if success:
                results["coverage"] += 1
                results["total_expansions"] += expansions
                results["total_time"] += time
                results["solved"].append(prob)
            else:
                results["failed"].append(prob)
        
        # Calculate averages
        if results["coverage"] > 0:
            results["avg_expansions"] = results["total_expansions"] / results["coverage"]
            results["avg_time"] = results["total_time"] / results["coverage"]
        else:
            results["avg_expansions"] = float('inf')
            results["avg_time"] = float('inf')
        
        return results
    
    def _run_planner_with_candidate(self, domain_name: str, problem_file: str, 
                                     candidate_py_file: Path) -> tuple:
        """
        Run planner with a candidate heuristic.
        Returns (success, expansions, time)
        """
        import subprocess
        
        domain_path = self.domains_dir / domain_name / "domain.pddl"
        problem_path = self.domains_dir / domain_name / problem_file
        
        eval_script = self.llm_dir / "evaluate_candidate.py"
        
        try:
            result = subprocess.run(
                [
                    "python", str(eval_script),
                    "--domain", str(domain_path),
                    "--problem", str(problem_path),
                    "--candidate", str(candidate_py_file),
                    "--timeout", "60"
                ],
                capture_output=True,
                text=True,
                timeout=65
            )
            
            output = result.stdout.strip()
            
            if output.startswith("SUCCESS"):
                parts = output.split()
                expansions = int(parts[1])
                time = float(parts[2])
                return (True, expansions, time)
            else:
                return (False, 0, 0.0)
                
        except Exception as e:
            print(f"    Error running planner: {e}")
            return (False, 0, 0.0)
    
    def select_best_candidate(self, domain_name: str, evaluation_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Select the best candidate based on:
        1. Max coverage
        2. Min expansions (among those with max coverage)
        3. Min time (tie-breaker)
        """
        if not evaluation_results:
            return None
        
        # Sort by: coverage (desc), avg_expansions (asc), avg_time (asc)
        sorted_results = sorted(
            evaluation_results,
            key=lambda r: (-r["coverage"], r["avg_expansions"], r["avg_time"])
        )
        
        best = sorted_results[0]
        
        print(f"\n=== Best candidate for {domain_name} ===")
        print(f"ID: {best['candidate_id']}")
        print(f"Coverage: {best['coverage']}")
        print(f"Avg Expansions: {best.get('avg_expansions', 'N/A')}")
        print(f"Avg Time: {best.get('avg_time', 'N/A')}")
        
        return best
