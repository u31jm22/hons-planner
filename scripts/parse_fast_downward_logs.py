import re
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FD_RESULTS_DIR = ROOT / "results_fd"
OUT_CSV = ROOT / "results" / "fd_seq-opt-lmcut_test.csv"

LOG_PATTERN = re.compile(r"fd_seq-opt-lmcut_(?P<domain>[^_]+)_(?P<problem>[^.]+)\.log$")

def parse_log(path: Path):
    """
    Parse a single Fast Downward log file.

    Returns:
        dict with keys:
        - domain, problem, heuristic, model
        - coverage (0/1)
        - expansions (int or None)
        - search_time (float or None)
        - plan_length (int or None)
    """
    m = LOG_PATTERN.search(path.name)
    if not m:
        return None

    domain = m.group("domain")
    problem = m.group("problem")

    # Defaults
    coverage = 0
    expansions = None
    search_time = None
    plan_length = None

    # Regexes for the lines we saw in your logs
    re_plan_length = re.compile(r"Plan length:\s*(\d+)\s*step")
    re_expanded = re.compile(r"Expanded\s+(\d+)\s+state")
    re_search_time = re.compile(r"Search time:\s*([0-9.]+)s")
    re_solution_found = re.compile(r"Solution found\.")

    with path.open("r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()

            if re_solution_found.search(line):
                coverage = 1

            m_len = re_plan_length.search(line)
            if m_len:
                try:
                    plan_length = int(m_len.group(1))
                except ValueError:
                    pass

            m_exp = re_expanded.search(line)
            if m_exp:
                try:
                    expansions = int(m_exp.group(1))
                except ValueError:
                    pass

            m_time = re_search_time.search(line)
            if m_time:
                try:
                    search_time = float(m_time.group(1))
                except ValueError:
                    pass

    return {
        "domain": domain,
        "problem": problem,
        "heuristic": "fd-seq-opt-lmcut",
        "model": "fd",
        "coverage": coverage,
        "expansions": expansions if expansions is not None else "",
        "search_time": search_time if search_time is not None else "",
        "plan_length": plan_length if plan_length is not None else "",
    }

def main():
    FD_RESULTS_DIR.mkdir(exist_ok=True)
    OUT_CSV.parent.mkdir(exist_ok=True)

    rows = []

    for path in sorted(FD_RESULTS_DIR.glob("fd_seq-opt-lmcut_*.log")):
        parsed = parse_log(path)
        if parsed is None:
            continue
        rows.append(parsed)

    if not rows:
        raise SystemExit(f"No FD logs parsed from {FD_RESULTS_DIR}")

    # Write CSV
    fieldnames = ["domain", "problem", "heuristic", "model",
                  "coverage", "expansions", "search_time", "plan_length"]

    with OUT_CSV.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    print(f"Wrote FD CSV to {OUT_CSV}")


if __name__ == "__main__":
    main()
