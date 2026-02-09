#!/usr/bin/env python3
"""
Run a batch of Blocksworld problems with different heuristics
and store logs under experiments/.
"""

from pathlib import Path
import subprocess

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DOMAINS_DIR = PROJECT_ROOT / "domains" / "logistics"
EXPERIMENTS_DIR = PROJECT_ROOT / "experiments"

PROBLEMS = ["p01.pddl", "p02.pddl", "p03.pddl", "p04.pddl", "p05.pddl"]
HEURISTICS = ["max", "ff", "add"]


def main() -> int:
    EXPERIMENTS_DIR.mkdir(exist_ok=True)

    domain = DOMAINS_DIR / "domain.pddl"

    for prob in PROBLEMS:
        problem = DOMAINS_DIR / prob
        for h in HEURISTICS:
            log_name = f"logistics_{prob.replace('.pddl','')}_{h}.txt"
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
                subprocess.run(
                    cmd,
                    cwd=PROJECT_ROOT,
                    stdout=f,
                    stderr=subprocess.STDOUT,
                    check=False,
                )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
