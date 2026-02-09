#!/usr/bin/env python3
"""
Minimal driver script to run a single planning problem with a baseline heuristic.
"""

import argparse
from pathlib import Path

from pddl.heuristic_planner import HeuristicPlanner
from pddl.delete_relaxation_h import MaxHeuristic, FastForwardHeuristic, AdditiveHeuristic


def build_heuristic(name: str):
    name = name.lower()
    if name == "max":
        return MaxHeuristic()
    if name == "ff":
        return FastForwardHeuristic()
    if name == "add":
        return AdditiveHeuristic()
    raise ValueError(f"Unknown heuristic '{name}'. Use one of: max, ff, add.")


def main():
    parser = argparse.ArgumentParser(description="Run a single planning problem")
    parser.add_argument("--domain", type=Path, required=True)
    parser.add_argument("--problem", type=Path, required=True)
    parser.add_argument(
        "--heuristic",
        type=str,
        default="max",
        choices=["max", "ff", "add"],
        help="Heuristic to use: max (MaxHeuristic), ff (FastForward), add (Additive)",
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

    heuristic = build_heuristic(args.heuristic)
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

    # --- New: statistics for the summariser ---
    # Adjust attribute names if your HeuristicPlanner uses different ones.
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
