#!/usr/bin/env python3
"""
analysis/aggregate_all30.py
----------------------------
Reads all *_all30.csv result files from results/ and produces a unified
summary CSV with per-(domain, heuristic/model) aggregated metrics.

Naming convention expected:
    results/<domain>_<heuristic>_all30.csv          # baselines: ff, add, max, lmcut
    results/<domain>_<model>_llm_all30.csv          # LLM runs: gpt-4o-mini, gpt-4.1-mini, gpt-4.1, llama

Columns expected in each CSV (from planner/run_grid.py):
    domain, problem, heuristic, model, coverage, expansions, search_time, plan_length

Run from the project root:
    python analysis/aggregate_all30.py
"""

import glob
import os
import re
import statistics
from pathlib import Path

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR = ROOT / "results"

DOMAINS = ["blocksworld", "gripper", "logistics", "miconic", "depots", "rovers"]
MODELS  = ["gpt-4o-mini", "gpt-4.1-mini", "gpt-4.1", "llama"]
BASELINES = ["ff", "add", "max", "lmcut"]


def parse_csv_rows(path: Path) -> list[dict]:
    """Minimal CSV reader that doesn't require pandas."""
    import csv
    rows = []
    with path.open(newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def safe_float(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def infer_method_from_filename(fname: str) -> tuple[str, str]:
    """
    Returns (domain, method_label) from an *_all30.csv filename.
    E.g.:
      blocksworld_ff_all30.csv          -> (blocksworld, ff)
      blocksworld_lmcut_all30.csv       -> (blocksworld, lmcut)
      blocksworld_gpt-4o-mini_llm_all30.csv -> (blocksworld, llm-gpt-4o-mini)
      blocksworld_gpt-4.1_llm_all30.csv     -> (blocksworld, llm-gpt-4.1)
    """
    name = fname.replace("_all30.csv", "")
    parts = name.split("_")
    domain = parts[0]

    # Check if it ends with _llm
    if parts[-1] == "llm":
        model = "_".join(parts[1:-1])  # e.g. gpt-4o-mini or gpt-4.1-mini
        method = f"llm-{model}"
    else:
        method = "_".join(parts[1:])  # e.g. ff, add, max, lmcut

    return domain, method


def aggregate_rows(rows: list[dict]) -> dict:
    """Compute metrics from a list of result rows."""
    n_total = len(rows)
    if n_total == 0:
        return {}

    solved_rows = [r for r in rows if safe_float(r.get("coverage", 0)) == 1.0]
    n_solved = len(solved_rows)
    coverage = n_solved / n_total

    def median_of(col):
        vals = [safe_float(r.get(col)) for r in solved_rows]
        vals = [v for v in vals if v is not None]
        if not vals:
            return None
        return statistics.median(vals)

    def std_of(col):
        vals = [safe_float(r.get(col)) for r in solved_rows]
        vals = [v for v in vals if v is not None]
        if len(vals) < 2:
            return None
        return statistics.stdev(vals)

    # Map column names (run_grid.py uses search_time; older files may use time)
    time_col = "search_time" if (rows and "search_time" in rows[0]) else "time"

    return {
        "n_total":            n_total,
        "n_solved":           n_solved,
        "coverage":           round(coverage, 4),
        "med_expansions":     median_of("expansions"),
        "std_expansions":     std_of("expansions"),
        "med_search_time":    median_of(time_col),
        "std_search_time":    std_of(time_col),
        "med_plan_length":    median_of("plan_length"),
    }


def main():
    pattern = str(RESULTS_DIR / "*_all30.csv")
    files = sorted(glob.glob(pattern))

    if not files:
        print(f"No *_all30.csv files found in {RESULTS_DIR}")
        print("Run the experiments first (scripts/run_all30_full.slurm).")
        return

    print(f"Found {len(files)} all30 result files.")

    summary_rows = []

    for fpath in files:
        fname = Path(fpath).name
        rows = parse_csv_rows(Path(fpath))
        if not rows:
            print(f"  [EMPTY] {fname}")
            continue

        domain, method = infer_method_from_filename(fname)
        agg = aggregate_rows(rows)
        if not agg:
            continue

        summary_rows.append({
            "domain":          domain,
            "method":          method,
            "n_total":         agg["n_total"],
            "n_solved":        agg["n_solved"],
            "coverage":        agg["coverage"],
            "med_expansions":  agg["med_expansions"],
            "std_expansions":  agg["std_expansions"],
            "med_search_time": agg["med_search_time"],
            "std_search_time": agg["std_search_time"],
            "med_plan_length": agg["med_plan_length"],
        })

        print(
            f"  {domain:12s} {method:25s} | "
            f"cov={agg['n_solved']}/{agg['n_total']} "
            f"med_exp={agg['med_expansions']} "
            f"med_time={agg['med_search_time']}"
        )

    if not summary_rows:
        print("No data to summarise.")
        return

    # Write summary CSV
    import csv
    fieldnames = list(summary_rows[0].keys())
    out_path = RESULTS_DIR / "summary_all30.csv"
    with out_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(summary_rows)

    print(f"\nWrote {out_path}")
    return summary_rows


if __name__ == "__main__":
    main()
