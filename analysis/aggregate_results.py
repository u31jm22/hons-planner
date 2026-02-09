#!/usr/bin/env python3
from __future__ import annotations

import csv
from pathlib import Path
from statistics import mean, median


TRAIN_PROBLEMS = {"p01", "p02", "p03"}
TEST_PROBLEMS = {"p04", "p05"}

HEURISTICS = ["max", "add", "ff", "llm"]


def load_rows(path: Path):
    with path.open() as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["expansions"] = int(row["expansions"])
            row["plan_length"] = int(row["plan_length"])
            row["search_time"] = float(row["search_time"])
            yield row


def split_rows(rows):
    train = []
    test = []
    for r in rows:
        if r["problem"] in TRAIN_PROBLEMS:
            train.append(r)
        elif r["problem"] in TEST_PROBLEMS:
            test.append(r)
    return train, test


def aggregate(rows):
    """
    rows: list of dicts for a single domain.
    Returns a dict[(split, heuristic)] -> stats dict.
    """
    train_rows, test_rows = split_rows(rows)
    out = {}

    for split_name, subset in (("train", train_rows), ("test", test_rows)):
        for h in HEURISTICS:
            h_rows = [r for r in subset if r["heuristic"] == h]
            if not h_rows:
                continue
            expansions = [r["expansions"] for r in h_rows]
            times = [r["search_time"] for r in h_rows]

            out[(split_name, h)] = {
                "coverage": len(h_rows),
                "mean_expansions": mean(expansions),
                "median_expansions": median(expansions),
                "mean_time": mean(times),
                "median_time": median(times),
            }
    return out


def print_table(domain_name: str, stats: dict):
    print(f"\n=== {domain_name} ===")
    print("split,heuristic,coverage,mean_expansions,median_expansions,mean_time,median_time")
    for split in ("train", "test"):
        for h in HEURISTICS:
            key = (split, h)
            if key not in stats:
                continue
            s = stats[key]
            print(
                f"{split},{h},{s['coverage']},"
                f"{s['mean_expansions']:.2f},{s['median_expansions']:.2f},"
                f"{s['mean_time']:.6f},{s['median_time']:.6f}"
            )


def main():
    base = Path("experiments")

    # Blocksworld
    bw_rows = list(load_rows(base / "blocksworld_summary.csv"))
    bw_stats = aggregate(bw_rows)
    print_table("Blocksworld", bw_stats)

    # Logistics
    lg_rows = list(load_rows(base / "logistics_summary.csv"))
    lg_stats = aggregate(lg_rows)
    print_table("Logistics", lg_stats)


if __name__ == "__main__":
    main()

