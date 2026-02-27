import os
import glob
import pandas as pd

RESULTS_DIR = "results"

def load_result_file(path: str) -> pd.DataFrame:
    """Load one result CSV and infer domain, range, method from filename."""
    fname = os.path.basename(path)
    name, _ = os.path.splitext(fname)

    # Examples:
    #   blocksworld_add_test.csv
    #   depots_ff_train.csv
    #   blocksworld_gpt-4o-mini_llm_test.csv
    #   depots_gpt-4.1-mini_llm_train.csv
    parts = name.split("_")

    domain = parts[0]
    range_ = parts[-1]  # train / test
    method_tag = "_".join(parts[1:-1])

    if method_tag in {"add", "ff", "max"}:
        method = method_tag
    elif method_tag in {"fd-seq-opt-lmcut", "fd_seq-opt-lmcut"}:
        method = "fd-lmcut"
    elif method_tag == "gpt-4o-mini_llm":
        method = "llm-gpt-4o-mini"
    elif method_tag == "gpt-4.1-mini_llm":
        method = "llm-gpt-4.1-mini"
    else:
        method = method_tag  # fallback

    df = pd.read_csv(path)

    # Normalise column names
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
    df["method"] = method
    return df

def main():
    # run from project root
    pattern = os.path.join(RESULTS_DIR, "*.csv")
    paths = [
        p for p in glob.glob(pattern)
        if not os.path.basename(p).startswith("summary_")
    ]

    dfs = []
    for p in paths:
        dfs.append(load_result_file(p))

    all_df = pd.concat(dfs, ignore_index=True)

    # keep only needed columns
    keep_cols = ["domain", "range", "method", "problem", "solved",
                 "expansions", "time", "plan_length"]
    all_df = all_df[[c for c in keep_cols if c in all_df.columns]]

    all_df["solved"] = all_df["solved"].astype(int)

    grouped = all_df.groupby(["domain", "range", "method"], as_index=False)

    summary = grouped.apply(
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

    summary_path = os.path.join(RESULTS_DIR, "summary_domain_range_method_full.csv")
    summary.to_csv(summary_path, index=False)
    print("Wrote", summary_path)

    pivot = summary.pivot_table(
        index=["domain", "range"],
        columns="method",
        values="n_solved",
        fill_value=0
    ).reset_index()

    pivot_path = os.path.join(RESULTS_DIR, "summary_coverage_pivot_full.csv")
    pivot.to_csv(pivot_path, index=False)
    print("Wrote", pivot_path)

if __name__ == "__main__":
    main()

