#!/usr/bin/env python3
"""
Helper script to evaluate a single candidate heuristic on a problem.
Used by candidate_pipeline.py
"""
import sys
import argparse
from pathlib import Path

# Add project root and planner src to path
PROJECT_ROOT = Path(__file__).parent.parent
PLANNER_SRC = PROJECT_ROOT / "planner" / "simplafy-devel" / "src"
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PLANNER_SRC))


from pddl.heuristic_planner import HeuristicPlanner


class CandidateHeuristicWrapper:
    """
    Wraps a candidate heuristic function from a file.
    """
    
    def __init__(self, code_file: Path):
        self.code_file = code_file
        
        # Load and compile the code
        with open(code_file, 'r') as f:
            code = f.read()
        
        namespace = {}
        try:
            exec(code, namespace)
            if 'h' not in namespace:
                raise ValueError("Candidate code must define function 'h'")
            self.h_func = namespace['h']
        except Exception as e:
            # Fallback to trivial heuristic if code fails
            print(f"ERROR loading candidate: {e}", file=sys.stderr)
            self.h_func = lambda state, goals: float(len(goals[0]))
    
    def __call__(self, actions, state, goals, parent=None):
        """
        Make callable for planner.
        """
        try:
            return float(self.h_func(state, goals))
        except Exception as e:
            print(f"ERROR executing heuristic: {e}", file=sys.stderr)
            return float(len(goals[0]))
    
    def h(self, actions, state, goals, parent):
        return self.__call__(actions, state, goals, parent)


def main():
    parser = argparse.ArgumentParser(description="Evaluate a candidate heuristic")
    parser.add_argument("--domain", type=Path, required=True)
    parser.add_argument("--problem", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True, 
                        help="Path to .py file with candidate heuristic")
    parser.add_argument("--timeout", type=int, default=300,
                        help="Timeout in seconds")
    args = parser.parse_args()
    
    # Load candidate heuristic
    heuristic = CandidateHeuristicWrapper(args.candidate)
    
    # Run planner
    planner = HeuristicPlanner(heuristic=heuristic, verbose=False)
    
    try:
        plan, _ = planner.solve_file(str(args.domain), str(args.problem))
        
        if plan is None:
            print("FAILED")
            return 1
        
        # Print results in parseable format
        expansions = getattr(planner, "expansions", 0)
        search_time = getattr(planner, "search_time", 0.0)
        
        print(f"SUCCESS {expansions} {search_time}")
        return 0
        
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        print("FAILED")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
