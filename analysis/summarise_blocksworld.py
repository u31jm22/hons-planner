#!/usr/bin/env python3
"""
Parse Blocksworld experiment logs into a CSV summary.
"""

import re
from pathlib import Path
import csv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXP_DIR = PROJECT_ROOT / "experiments"
OUT_CSV = EXP_DIR / "blocksworld_summary.csv"

LOG_PATTERN = re.compile(r"blocksworld_p(\d+)_([a-z]+)\.txt")


def parse_log(path: Path):
    text = path.read_text()
    expansions = None
    plan_length = None
    search_time = None

    for line in text.splitlines():
        line = line.strip()
        if line.startswith("# Expansions"):
            expansions = int(line.split(":")[1])
        elif line.startswith("Plan Length"):
            plan_length = int(line.split(":")[1])
        elif line.startswith("Search Time"):
            search_time = float(line.split(":")[1])

    return expansions, plan_length, search_time


def main() -> int:
    rows = []

    for log_path in EXP_DIR.glob("blocksworld_p*.txt"):
        m = LOG_PATTERN.match(log_path.name)
        if not m:
            continue
        problem_num, heuristic = m.groups()
        expansions, plan_length, search_time = parse_log(log_path)
        rows.append({
            "problem": f"p{problem_num}",
            "heuristic": heuristic,
            "expansions": expansions,
            "plan_length": plan_length,
            "search_time": search_time,
        })

    rows.sort(key=lambda r: (r["problem"], r["heuristic"]))

    with OUT_CSV.open("w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["problem", "heuristic", "expansions", "plan_length", "search_time"],
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} rows to {OUT_CSV}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
