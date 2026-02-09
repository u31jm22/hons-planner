import csv
from pathlib import Path

EXPERIMENTS_DIR = Path("experiments")

# Adjust if you add more domains
DOMAINS = ["blocksworld", "logistics", "gripper"]  # later: ["blocksworld", "logistics", "gripper", ...]


def read_domain_summary(domain: str):
    summary_path = EXPERIMENTS_DIR / f"{domain}_summary.csv"
    rows = []
    if not summary_path.exists():
        return rows

    with summary_path.open() as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["domain"] = domain
            rows.append(row)
    return rows


def main():
    all_rows = []
    for domain in DOMAINS:
        all_rows.extend(read_domain_summary(domain))

    if not all_rows:
        print("No summary rows found.")
        return

    out_path = EXPERIMENTS_DIR / "all_domains_summary.csv"
    fieldnames = ["domain", "problem", "heuristic", "coverage", "expansions", "time"]
    with out_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in all_rows:
            writer.writerow({
                "domain": row["domain"],
                "problem": row.get("problem", ""),
                "heuristic": row.get("heuristic", ""),
                "coverage": row.get("coverage", ""),
                "expansions": row.get("expansions", ""),
                "time": row.get("time", ""),
            })

    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
