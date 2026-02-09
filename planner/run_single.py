#!/usr/bin/env python3
"""
Minimal driver script to run a single planning problem with a baseline heuristic.
"""

import argparse
import sys
from pathlib import Path

from pddl.heuristic_planner import HeuristicPlanner
from pddl.delete_relaxation_h import (
    MaxHeuristic,
    FastForwardHeuristic,
    AdditiveHeuristic,
)

# Import our LLM heuristics from llm/ folder
sys.path.insert(0, str(Path(__file__).parent.parent))
from llm.llm_heuristic import LLMHeuristic
from llm.llm_code_heuristic import LLMCodeHeuristic
from llm.model_wrapper import DummyModel, OpenAIModel


def build_heuristic(name: str, domain_path: str, openai_key: str = None):
    name = name.lower()
    if name == "max":
        return MaxHeuristic()
    if name == "ff":
        return FastForwardHeuristic()
    if name == "add":
        return AdditiveHeuristic()
    
    if name == "llm":
        # Runtime evaluation: LLM evaluates each state
        template = (
            "You are estimating how many steps are needed to reach the goal in a planning problem.\n"
            "Current state: {state}\n"
            "Goals: {goals}\n"
            "Respond with ONLY a single number (integer) representing your estimate of steps remaining:"
        )
        
        if openai_key:
            model = OpenAIModel(api_key=openai_key, model="gpt-3.5-turbo", temperature=0.0)
        else:
            print("WARNING: No OpenAI key provided, using DummyModel")
            model = DummyModel(fixed_value=5.0)
        
        return LLMHeuristic(model=model, prompt_template=template)
    
    if name == "llm-code":
        # Code generation: LLM generates heuristic function once
        if openai_key:
            model = OpenAIModel(api_key=openai_key, model="gpt-3.5-turbo", temperature=0.0)
        else:
            print("WARNING: No OpenAI key provided, using DummyModel")
            model = DummyModel(fixed_value=5.0)
        
        return LLMCodeHeuristic(model=model, domain_pddl_path=domain_path)
    
    raise ValueError(f"Unknown heuristic '{name}'. Use one of: max, ff, add, llm, llm-code.")


def main():
    parser = argparse.ArgumentParser(description="Run a single planning problem")
    parser.add_argument("--domain", type=Path, required=True)
    parser.add_argument("--problem", type=Path, required=True)
    parser.add_argument(
        "--heuristic",
        type=str,
        default="max",
        choices=["max", "ff", "add", "llm", "llm-code"],
        help=(
            "Heuristic to use: "
            "max (MaxHeuristic), ff (FastForward), add (Additive), "
            "llm (LLM runtime eval), llm-code (LLM generated code)"
        ),
    )
    parser.add_argument(
        "--openai-key",
        type=str,
        default=None,
        help="OpenAI API key (required for --heuristic llm/llm-code with real model)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print planner statistics (expansions, time, etc.)",
    )
    args = parser.parse_args()

    domain_path = str(args.domain)
    problem_path = str(args.problem)

    print(f"Domain: {domain_path}")
    print(f"Problem: {problem_path}")
    print(f"Heuristic: {args.heuristic}")

    heuristic = build_heuristic(args.heuristic, domain_path, args.openai_key)
    
    # For llm-code, print the generated code
    if args.heuristic == "llm-code" and hasattr(heuristic, 'heuristic_code'):
        print("\n=== Generated Heuristic Code ===")
        print(heuristic.heuristic_code)
        print("=================================\n")
    
    planner = HeuristicPlanner(heuristic=heuristic, verbose=True)

    # Solve the task
    plan, _ = planner.solve_file(domain_path, problem_path)

    if plan is None:
        print("✗ No plan found")
        return 1

    print("✓ Plan found")
    print("Plan:")
    for i, action in enumerate(plan):
        print(f"{i+1}: {action}")

    # --- Statistics for the summariser ---
    expansions = getattr(planner, "expansions", None)
    search_time = getattr(planner, "search_time", None)
    plan_length = len(plan)

    if expansions is not None:
        print(f"# Expansions : {expansions}")
    else:
        print("# Expansions : 0")

    print(f"Plan Length : {plan_length}")

    if search_time is not None:
        print(f"Search Time : {search_time}")
    else:
        print("Search Time : 0.0")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
