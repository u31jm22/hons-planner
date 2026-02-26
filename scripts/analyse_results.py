import pandas as pd
from pathlib import Path

# Project root: .../hons-llm-heuristics
ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR = ROOT / "results"


def main():
    # 1) Load planner CSVs (train + test)
    planner_files = list(RESULTS_DIR.glob("*_train.csv")) + list(RESULTS_DIR.glob("*_test.csv"))
    if not planner_files:
        raise SystemExit(f"No *_train.csv or *_test.csv files found in {RESULTS_DIR}")

    frames = []
    for path in planner_files:
        try:
            df = pd.read_csv(path)
        except pd.errors.EmptyDataError:
            print(f"Skipping empty file: {path.name}")
            continue
        if df.empty or "domain" not in df.columns:
            print(f"Skipping non-standard or empty file: {path.name}")
            continue
        df["source_file"] = path.name
        frames.append(df)

    if not frames:
        raise SystemExit("No valid planner CSVs found in results/")

    planner_df = pd.concat(frames, ignore_index=True)


    # 2) Load FD CSV
    fd_path = RESULTS_DIR / "fd_seq-opt-lmcut_test.csv"
    if not fd_path.exists():
        raise SystemExit(f"FD CSV not found at {fd_path}")
    fd_df = pd.read_csv(fd_path)

    # 3) Add method label and range (train/test)

    def label_method(row):
        h = str(row["heuristic"])
        model = str(row.get("model", ""))
        if h.startswith("fd-seq-opt-lmcut"):
            return "fd-lmcut"
        if h == "ff":
            return "ff"
        if h == "max":
            return "max"
        if h == "add":
            return "add"
        if h == "llm-selected":
            # encode model name into method label, e.g. llm-gpt-4o-mini
            return f"llm-{model}" if model else "llm-unknown"
        return h or "unknown"

    # planner data
    planner_df["method"] = planner_df.apply(label_method, axis=1)

    # fd data
    fd_df["method"] = fd_df.apply(label_method, axis=1)

    # mark range by problem id
    def label_range(problem):
        # problem like 'p01.pddl' or 'p01'
        base = str(problem)
        if base.endswith(".pddl"):
            base = base[:-5]
        if base.startswith("p"):
            try:
                idx = int(base[1:])
                return "train" if 1 <= idx <= 5 else "test"
            except ValueError:
                return "unknown"
        return "unknown"

    planner_df["range"] = planner_df["problem"].apply(label_range)
    fd_df["range"] = fd_df["problem"].apply(label_range)

    # Harmonise numeric columns
    for df in (planner_df, fd_df):
        for col in ["expansions", "search_time", "plan_length"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

    # 4) Combine into unified dataframe
    all_df = pd.concat([planner_df, fd_df], ignore_index=True, sort=False)

    # 5) Aggregate metrics per (domain, range, method)
    all_df["solved"] = all_df["coverage"] == 1

    agg_rows = []
    for (domain, rnge, method), group in all_df.groupby(["domain", "range", "method"]):
        n_total = len(group)
        n_solved = int(group["solved"].sum())
        coverage_mean = group["coverage"].mean() if n_total > 0 else float("nan")

        solved = group[group["solved"]]

        def safe_stats(col):
            if col not in solved or solved[col].dropna().empty:
                return float("nan"), float("nan")
            return solved[col].mean(), solved[col].median()

        exp_mean, exp_med = safe_stats("expansions")
        time_mean, time_med = safe_stats("search_time")
        len_mean, len_med = safe_stats("plan_length")

        agg_rows.append(
            {
                "domain": domain,
                "range": rnge,
                "method": method,
                "n_total": n_total,
                "n_solved": n_solved,
                "coverage_mean": coverage_mean,
                "expansions_mean_solved": exp_mean,
                "expansions_median_solved": exp_med,
                "time_mean_solved": time_mean,
                "time_median_solved": time_med,
                "plan_length_mean_solved": len_mean,
                "plan_length_median_solved": len_med,
            }
        )

    summary_df = pd.DataFrame(agg_rows)

    # 6) Save summaries
    RESULTS_DIR.mkdir(exist_ok=True)
    summary_path = RESULTS_DIR / "summary_domain_range_method.csv"
    summary_df.to_csv(summary_path, index=False)

    # Convenience pivot: number of solved tasks per domain/range/method
    cov_pivot = summary_df.pivot_table(
        index=["domain", "range"], columns="method", values="n_solved", fill_value=0
    )
    cov_pivot_path = RESULTS_DIR / "summary_coverage_pivot.csv"
    cov_pivot.to_csv(cov_pivot_path)

    print("Wrote:", summary_path)
    print("Wrote:", cov_pivot_path)


if __name__ == "__main__":
    main()
