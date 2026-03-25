#!/usr/bin/env python3
"""
llm/evaluate_candidate.py
--------------------------
Subprocess helper called by CandidatePipeline._run_planner_with_candidate.

Runs a single (domain, problem, candidate) triple and prints exactly one line:
  SUCCESS <expansions> <time>
  FAILURE

Usage (internal only — not intended to be called directly):
  python llm/evaluate_candidate.py \
      --domain   domains/gripper/domain.pddl \
      --problem  domains/gripper/p01.pddl \
      --candidate llm/candidates/gripper_candidate_1.py \
      --timeout  90
"""

import argparse
import importlib.util
import signal
import sys
import time
from pathlib import Path

# ── Resolve project root so planner src is importable ───────────────────────
PROJECT_ROOT = Path(__file__).resolve().parents[1]
PLANNER_SRC = PROJECT_ROOT / "planner" / "simplafy-devel" / "src"
if str(PLANNER_SRC) not in sys.path:
    sys.path.insert(0, str(PLANNER_SRC))
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from pddl.heuristic_planner import HeuristicPlanner
from llm.llm_code_heuristic import LLMCodeHeuristic


def _timeout_handler(signum, frame):
    raise TimeoutError("evaluation timed out")


def load_candidate(path: Path):
    spec = importlib.util.spec_from_file_location("_cand_module", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    if not hasattr(mod, "h"):
        raise ValueError(f"No function h(state, goals) in {path}")
    return LLMCodeHeuristic(heuristic_fn=mod.h)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--domain",    required=True)
    parser.add_argument("--problem",   required=True)
    parser.add_argument("--candidate", required=True)
    parser.add_argument("--timeout",   type=int, default=90)
    args = parser.parse_args()

    try:
        heuristic = load_candidate(Path(args.candidate))
    except Exception as e:
        print(f"FAILURE  # could not load candidate: {e}")
        return

    planner = HeuristicPlanner(heuristic=heuristic, verbose=False)

    # SIGALRM-based timeout (Unix only)
    signal.signal(signal.SIGALRM, _timeout_handler)
    signal.alarm(args.timeout)

    t0 = time.time()
    try:
        plan, _ = planner.solve_file(args.domain, args.problem)
    except TimeoutError:
        print("FAILURE  # timeout")
        return
    except Exception as e:
        print(f"FAILURE  # exception: {e}")
        return
    finally:
        signal.alarm(0)

    elapsed = time.time() - t0

    if plan is None:
        print("FAILURE  # no plan found")
    else:
        expansions = getattr(planner, "expansions", 0)
        print(f"SUCCESS {expansions} {elapsed:.6f}")


if __name__ == "__main__":
    main()
