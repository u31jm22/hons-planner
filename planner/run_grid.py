#!/usr/bin/env python3
import sys
import signal
from pathlib import Path


# Add planner src (where pddl lives) to sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
PLANNER_SRC = PROJECT_ROOT / "planner" / "simplafy-devel" / "src"
if str(PLANNER_SRC) not in sys.path:
    sys.path.insert(0, str(PLANNER_SRC))


import argparse
import csv
import json
import time


from pddl.heuristic_planner import HeuristicPlanner
from pddl.delete_relaxation_h import MaxHeuristic, FastForwardHeuristic, AdditiveHeuristic
from llm.llm_code_heuristic import LLMCodeHeuristic


TIMEOUT_SECONDS = 300


def _timeout_handler(signum, frame):
    raise TimeoutError("Planner exceeded time limit")


def make_baseline_heuristic(name):
    name = name.lower()
    if name == "max":
        return MaxHeuristic()
    if name == "ff":
        return FastForwardHeuristic()
    if name == "add":
        return AdditiveHeuristic()
    raise ValueError("Unknown baseline heuristic {}".format(name))


def load_selected_candidate(domain, model, project_root):
    """Return path to candidate .py for (domain, model)."""
    sel_json = project_root / "llm" / "candidates" / "{}_selected.json".format(domain)
    data = json.loads(sel_json.read_text())
    cand_id = data["candidate_id"]  # e.g. blocksworld_candidate_3
    cand_file = project_root / "llm" / "candidates" / "{}.py".format(cand_id)
    if not cand_file.exists():
        raise FileNotFoundError("Candidate file not found: {}".format(cand_file))
    return cand_file


def load_instances(domain_dir, fname):
    path = domain_dir / fname
    with path.open() as f:
        return [line.strip() for line in f if line.strip()]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--domain", required=True)
    parser.add_argument(
        "--mode",
        choices=["baseline", "llm-selected"],
        required=True,
    )
    parser.add_argument(
        "--baseline",
        choices=["max", "ff", "add"],
        help="Which baseline heuristic to run when mode=baseline",
    )
    parser.add_argument(
        "--model",
        help="Model name label when mode=llm-selected, e.g. gpt-4o-mini",
    )
    parser.add_argument(
        "--instances-file",
        required=True,
        help="Relative file in domains/<domain>/ listing problems, e.g. test_instances.txt",
    )
    parser.add_argument("--output-csv", required=True)
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[1]
    domains_dir = project_root / "domains"
    domain_dir = domains_dir / args.domain

    problems = load_instances(domain_dir, args.instances_file)

    fieldnames = [
        "domain",
        "problem",
        "heuristic",
        "model",
        "coverage",
        "expansions",
        "search_time",
        "plan_length",
    ]
    out_path = Path(args.output_csv)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    signal.signal(signal.SIGALRM, _timeout_handler)

    with out_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for prob in problems:
            domain_path = str(domain_dir / "domain.pddl")
            problem_path = str(domain_dir / prob)

            if args.mode == "baseline":
                heuristic_name = args.baseline
                heuristic = make_baseline_heuristic(heuristic_name)
                model_label = ""
            else:
                heuristic_name = "llm-selected"
                model_label = args.model or ""
                cand_file = load_selected_candidate(args.domain, model_label, project_root)
                heuristic = LLMCodeHeuristic.from_code_file(cand_file)

            # Fresh planner per problem so stats never accumulate
            planner = HeuristicPlanner(heuristic=heuristic, verbose=False)

            signal.alarm(TIMEOUT_SECONDS)
            start = time.time()
            try:
                plan, _ = planner.solve_file(domain_path, problem_path)
            except TimeoutError:
                plan = None
            finally:
                signal.alarm(0)
            end = time.time()

            if plan is None:
                row = {
                    "domain": args.domain,
                    "problem": prob,
                    "heuristic": heuristic_name,
                    "model": model_label,
                    "coverage": 0,
                    "expansions": getattr(planner, "expansions", 0),
                    "search_time": end - start,
                    "plan_length": 0,
                }
            else:
                row = {
                    "domain": args.domain,
                    "problem": prob,
                    "heuristic": heuristic_name,
                    "model": model_label,
                    "coverage": 1,
                    "expansions": getattr(planner, "expansions", 0),
                    "search_time": getattr(planner, "search_time", end - start),
                    "plan_length": len(plan),
                }

            writer.writerow(row)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
