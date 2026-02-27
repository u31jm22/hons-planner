import os
import glob
import pandas as pd

RESULTS_DIR = "results"

def parse_filename(path: str):
    # e.g. depots_gpt-4.1-mini_llm_train.csv
    fname = os.path.basename(path)
    name, _ = os.path.splitext(fname)
    parts = name.split("_")
    if len(parts) < 3:
        raise ValueError(f"Unexpected filename format: {fname}")
    domain = parts[0]
    range_ = parts[-1]
    method_tag = "_".join(parts[1:-1])
    return domain, method_tag, range_

def load_gpt41_file(path: str) -> pd.DataFrame:
    domain, method_tag, range_ = parse_filename(path)

    if method_tag != "gpt-4.1-mini_llm":
        raise ValueError(f"Not a gpt-4.1 file: {path}")

    df = pd.read_csv(path)

    # normalise some likely column names
    rename_map = {}
    for logical, candidates in {
        "problem": ["problem", "instance"],
        "solved": ["solved"],
        "expansions": ["expansions", "nodes_expanded"],
        "time": ["time", "runtime", "time_s"],
        "plan_length": ["plan_length", "planlen", "plan_length_steps"],
    }.items():
        for cand in candidates:
            if cand in df.columns:
                rename_map[cand] = logical
                break
    df = df.rename(columns=rename_map)

    df["domain"] = domain
    df["range"] = range_
    df["method"] = "llm-gpt-4.1-mini"
    return df

def aggregate_gpt41():
    pattern = os.path.join(RESULTS_DIR, "*gpt-4.1-mini_llm_*.csv")
    paths = glob.glob(pattern)

    dfs = []
    for p in paths:
        if os.path.getsize(p) == 0:
            print("Skipping empty file:", p)
            continue
        df = load_gpt41_file(p)
        dfs.append(df)

    if not dfs:
        print("No gpt-4.1-mini result CSVs found.")
        return None

    all_df = pd.concat(dfs, ignore_index=True)

    keep_cols = ["domain", "range", "method", "problem", "solved",
                 "expansions", "time", "plan_length"]
    all_df = all_df[[c for c in keep_cols if c in all_df.columns]]

    all_df["solved"] = all_df["solved"].astype(int)

    grouped = all_df.groupby(["domain", "range", "method"], as_index=False)

    gpt41_summary = grouped.apply(
        lambda g: pd.Series({
            "n_total": len(g),
            "n_solved": g["solved"].sum(),
            "coverage_mean": g["solved"].mean(),
            "expansions_mean_solved": g.loc[g["solved"] == 1, "expansions"].mean(),
            "expansions_median_solved": g.loc[g["solved"] == 1, "expansions"].median(),
            "time_mean_solved": g.loc[g["solved"] == 1, "time"].mean(),
            "time_median_solved": g.loc[g["solved"] == 1, "time"].median(),
            "plan_length_mean_solved": g.loc[g["solved"] == 1, "plan_length"].mean(),
            "plan_length_median_solved": g.loc[g["solved"] == 1, "plan_length"].median(),
        })
    ).reset_index(drop=True)

    return gpt41_summary

def main():
    base_summary_path = os.path.join(RESULTS_DIR, "summary_domain_range_method.csv")
    base_cov_path = os.path.join(RESULTS_DIR, "summary_coverage_pivot.csv")

    base_summary = pd.read_csv(base_summary_path)
    base_cov = pd.read_csv(base_cov_path)

    gpt41_summary = aggregate_gpt41()
    if gpt41_summary is None:
        return

    # merge row-wise for the rich summary
    merged_summary = pd.concat([base_summary, gpt41_summary], ignore_index=True)

    out_summary = os.path.join(RESULTS_DIR, "summary_domain_range_method_with_41.csv")
    merged_summary.to_csv(out_summary, index=False)
    print("Wrote", out_summary)

    # recompute coverage pivot including new method
    coverage_pivot = merged_summary.pivot_table(
        index=["domain", "range"],
        columns="method",
        values="n_solved",
        fill_value=0
    ).reset_index()

    out_cov = os.path.join(RESULTS_DIR, "summary_coverage_pivot_with_41.csv")
    coverage_pivot.to_csv(out_cov, index=False)
    print("Wrote", out_cov)

if __name__ == "__main__":
    main()

