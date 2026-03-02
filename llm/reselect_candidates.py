#!/usr/bin/env python3
"""
Re-evaluate all existing candidate .py files for each domain on the full
p01-p05 training set and write corrected *_selected_gpt-4.1-mini.json files.
No API calls. Uses only already-generated candidate .py files.

Usage (from project root, venv active):
    PYTHONPATH=. python3 llm/reselect_candidates.py
    PYTHONPATH=. python3 llm/reselect_candidates.py --domains blocksworld logistics gripper
"""
import sys
import json
import signal
import time
import argparse
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PLANNER_SRC = PROJECT_ROOT / "planner" / "simplafy-devel" / "src"
for p in [str(PROJECT_ROOT), str(PLANNER_SRC)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from pddl.heuristic_planner import HeuristicPlanner
from llm.llm_code_heuristic import LLMCodeHeuristic

TIMEOUT_SECONDS = 300
MODEL_NAME = "gpt-4.1-mini"
TRAIN_INSTANCES = ["p01.pddl", "p02.pddl", "p03.pddl", "p04.pddl", "p05.pddl"]


def _timeout_handler(signum, frame):
    raise TimeoutError("Planner exceeded time limit")


def evaluate_candidate(cand_file, domain_dir, problems):
    solved, failed = [], []
    total_expansions, total_time = 0, 0.0

    for prob in problems:
        domain_path = str(domain_dir / "domain.pddl")
        problem_path = str(domain_dir / prob)
        try:
            heuristic = LLMCodeHeuristic.from_code_file(cand_file)
        except Exception as e:
            print(f"    [LOAD ERROR] {cand_file.name} on {prob}: {e}")
            failed.append(prob)
            continue

        planner = HeuristicPlanner(heuristic=heuristic, verbose=False)
        signal.signal(signal.SIGALRM, _timeout_handler)
        signal.alarm(TIMEOUT_SECONDS)
        start = time.time()
        try:
            plan, _ = planner.solve_file(domain_path, problem_path)
        except TimeoutError:
            plan = None
        except Exception as e:
            print(f"    [RUNTIME ERROR] {prob}: {e}")
            plan = None
        finally:
            signal.alarm(0)
        elapsed = time.time() - start

        if plan is not None:
            solved.append(prob)
            total_expansions += getattr(planner, "expansions", 0)
            total_time += elapsed
        else:
            failed.append(prob)

    coverage = len(solved)
    avg_exp = (total_expansions / coverage) if coverage > 0 else float("inf")
    avg_time = (total_time / coverage) if coverage > 0 else 0.0
    return {
        "candidate_id": cand_file.stem,
        "coverage": coverage,
        "total_expansions": total_expansions,
        "total_time": total_time,
        "solved": solved,
        "failed": failed,
        "avg_expansions": avg_exp,
        "avg_time": avg_time,
        "model_name": MODEL_NAME,
    }


def select_best(results):
    valid = [r for r in results if r["coverage"] > 0]
    if not valid:
        return None
    best_cov = max(r["coverage"] for r in valid)
    top = [r for r in valid if r["coverage"] == best_cov]
    return min(top, key=lambda r: r["avg_expansions"])


def reselect_domain(domain):
    candidates_dir = PROJECT_ROOT / "llm" / "candidates"
    domain_dir = PROJECT_ROOT / "domains" / domain
    if not domain_dir.exists():
        print(f"  [SKIP] No domain dir: {domain_dir}")
        return
    cand_files = sorted(candidates_dir.glob(f"{domain}_candidate_*.py"))
    if not cand_files:
        print(f"  [SKIP] No candidate .py files for {domain}")
        return

    print(f"\n{'='*60}")
    print(f"Domain: {domain}  ({len(cand_files)} candidates, evaluating on p01-p05)")
    print(f"{'='*60}")

    results = []
    for cand_file in cand_files:
        print(f"\n  Evaluating {cand_file.name} ...")
        res = evaluate_candidate(cand_file, domain_dir, TRAIN_INSTANCES)
        results.append(res)
        if res["coverage"] > 0:
            print(f"    Coverage: {res['coverage']}/5  avg_exp: {res['avg_expansions']:.1f}  avg_time: {res['avg_time']:.3f}s")
            print(f"    Solved: {res['solved']}")
            if res["failed"]:
                print(f"    Failed: {res['failed']}")
        else:
            print(f"    Coverage: 0/5  (all timed out or errored)")

    best = select_best(results)
    if best is None:
        print(f"\n  [WARNING] No candidate solved any training instance for {domain}!")
        return

    out_path = candidates_dir / f"{domain}_selected_{MODEL_NAME}.json"
    with out_path.open("w") as f:
        json.dump(best, f, indent=2)

    print(f"\n  >>> SELECTED: {best['candidate_id']}")
    print(f"  >>> Coverage: {best['coverage']}/5  avg_expansions: {best['avg_expansions']:.1f}")
    print(f"  >>> Written to: {out_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Re-select best candidate on full p01-p05. No API calls."
    )
    parser.add_argument(
        "--domains", nargs="+",
                default=["blocksworld", "logistics", "gripper", "miconic"],
        help="Domains to process (default: all four)"
    )
    args = parser.parse_args()
    print(f"Model label : {MODEL_NAME}")
    print(f"Train set   : {TRAIN_INSTANCES}")
    print(f"Domains     : {args.domains}")
    for domain in args.domains:
        reselect_domain(domain)
    print("\nAll done.")


if __name__ == "__main__":
    main()
