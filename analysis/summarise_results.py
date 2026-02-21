#!/usr/bin/env python3
import argparse
import csv
from pathlib import Path
from collections import defaultdict

def load_results(csv_path):
    rows = []
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Convert numeric fields
            row["coverage"] = int(row["coverage"])
            row["expansions"] = int(row["expansions"])
            row["search_time"] = float(row["search_time"])
            row["plan_length"] = int(row["plan_length"])
            rows.append(row)
    return rows

def summarise_domain(domain, results_dir=Path("results"), output_dir=Path("analysis")):
    results_dir = Path(results_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Find all *_test.csv for this domain
    pattern = f"{domain}_*_test.csv"
    files = sorted(results_dir.glob(pattern))

    if not files:
        raise SystemExit(f"No test CSVs found for domain '{domain}' in {results_dir}")

    # Aggregate by (heuristic, model)
    stats = defaultdict(lambda: {"instances": 0, "coverage": 0, "expansions": 0, "search_time": 0.0, "plan_length": 0})

    for csv_path in files:
        rows = load_results(csv_path)
        for row in rows:
            key = (row["heuristic"], row["model"])
            s = stats[key]
            s["instances"] += 1
            s["coverage"] += row["coverage"]
            s["expansions"] += row["expansions"]
            s["search_time"] += row["search_time"]
            s["plan_length"] += row["plan_length"]

    # Write summary CSV
    out_path = output_dir / f"{domain}_summary.csv"
    with open(out_path, "w", newline="") as f:
        fieldnames = [
            "domain",
            "heuristic",
            "model",
            "instances",
            "coverage",
            "coverage_rate",
            "avg_expansions",
            "avg_search_time",
            "avg_plan_length",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for (heuristic, model), s in sorted(stats.items()):
            n = s["instances"]
            if n == 0:
                continue
            coverage_rate = s["coverage"] / n
            writer.writerow({
                "domain": domain,
                "heuristic": heuristic,
                "model": model,
                "instances": n,
                "coverage": s["coverage"],
                "coverage_rate": coverage_rate,
                "avg_expansions": s["expansions"] / n,
                "avg_search_time": s["search_time"] / n,
                "avg_plan_length": s["plan_length"] / n,
            })

    print(f"Wrote summary to {out_path}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--domain", required=True, help="Domain name, e.g. blocksworld, logistics")
    parser.add_argument("--results-dir", default="results")
    parser.add_argument("--output-dir", default="analysis")
    args = parser.parse_args()

    summarise_domain(args.domain, results_dir=Path(args.results_dir), output_dir=Path(args.output_dir))

if __name__ == "__main__":
    main()
