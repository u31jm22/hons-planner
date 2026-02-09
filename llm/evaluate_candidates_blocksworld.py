#!/usr/bin/env python3
"""
Generate and evaluate multiple LLM heuristic candidates for Blocksworld
on the TRAIN instances (p01–p03). Results go to notes/llm_candidates_blocksworld.csv.

Later you can adapt this pattern for Logistics or generalise it.
"""

import csv
import subprocess
from pathlib import Path

N_CANDIDATES = 5
DOMAIN_NAME = "blocksworld"
DOMAIN_PDDL = Path("domains/blocksworld/domain.pddl")
TRAIN_INSTANCES = ["01", "02", "03"]

ROOT = Path(__file__).resolve().parents[1]
LLM_DIR = ROOT / "llm"
NOTES_DIR = ROOT / "notes"
NOTES_DIR.mkdir(exist_ok=True)

OUT_CSV = NOTES_DIR / "llm_candidates_blocksworld.csv"

def run_cmd(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=ROOT, check=False, text=True, capture_output=True)

def main():
    rows = []
    for k in range(1, N_CANDIDATES + 1):
        # 1) Generate candidate heuristic file (overwrite for now)
        print(f"=== Candidate {k} ===")
        gen_cmd = [
            "python",
            "llm/generate_heuristic.py",
            "--domain-name", DOMAIN_NAME,
            "--domain-pddl", str(DOMAIN_PDDL),
        ]
        gen_res = run_cmd(gen_cmd)
        print(gen_res.stdout)
        if gen_res.returncode != 0:
            print(f"[WARN] generate_heuristic failed (candidate {k})")
            continue

        # 2) Evaluate on training instances with heuristic=llm
        total_solved = 0
        total_expansions = 0
        total_time = 0.0

        for inst in TRAIN_INSTANCES:
            print(f"  -> p{inst}")
            run_cmd([
                "./scripts/run_blocksworld_baseline.sh",
                "llm",
                "train",
            ])
            # After this, experiments/blocksworld_summary.csv has latest stats.
            summary_path = ROOT / "experiments" / "blocksworld_summary.csv"
            with summary_path.open() as f:
                reader = csv.DictReader(f)
                # Find the row for this problem + llm
                for row in reader:
                    if row["problem"] == f"p{inst}" and row["heuristic"] == "llm":
                        total_solved += 1
                        total_expansions += int(float(row["expansions"]))
                        total_time += float(row["search_time"])
                        break

        rows.append({
            "candidate_id": k,
            "solved": total_solved,
            "total_expansions": total_expansions,
            "total_time": total_time,
        })

    # Write summary CSV
    with OUT_CSV.open("w", newline="") as f:
        fieldnames = ["candidate_id", "solved", "total_expansions", "total_time"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

    print(f"Wrote candidate summary to {OUT_CSV}")

if __name__ == "__main__":
    main()
