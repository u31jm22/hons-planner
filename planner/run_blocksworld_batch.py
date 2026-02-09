#!/usr/bin/env python3
"""
Run a batch of Blocksworld problems with different heuristics
and store logs under experiments/.
"""

import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DOMAINS_DIR = PROJECT_ROOT / "domains" / "blocksworld"
EXPERIMENTS_DIR = PROJECT_ROOT / "experiments"

# problems to run (adjust as you add more)
PROBLEMS = ["p01.pddl", "p02.pddl", "p03.pddl", "p04.pddl", "p05.pddl"]


HEURISTICS = ["max", "ff", "add"]  # matches run_single.py choices


def main() -> int:
    EXPERIMENTS_DIR.mkdir(exist_ok=True)

    domain = DOMAINS_DIR / "domain.pddl"

    for prob in PROBLEMS:
        problem = DOMAINS_DIR / prob
        for h in HEURISTICS:
            log_name = f"blocksworld_{prob.replace('.pddl','')}_{h}.txt"
            log_path = EXPERIMENTS_DIR / log_name
            print(f"Running {prob} with {h} -> {log_path}")

            cmd = [
                "python",
                "planner/run_single.py",
                "--domain", str(domain),
                "--problem", str(problem),
                "--heuristic", h,
                "--verbose",
            ]

            with log_path.open("w") as f:
                # stdout+stderr to same log [web:81][web:84]
                subprocess.run(cmd, cwd=PROJECT_ROOT, stdout=f, stderr=subprocess.STDOUT, check=False)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
