#!/usr/bin/env python3
"""
analysis/generate_latex_tables.py
-----------------------------------
Reads results/summary_all30.csv (produced by aggregate_all30.py) and
generates LaTeX tables for the thesis.

Tables produced:
  1. Coverage table  — n_solved / 30 per (domain x method)
  2. Per-domain detail tables — median expansions, search time, plan length

Output: analysis/tables.tex  (\\input{analysis/tables.tex} in your thesis)

Run from the project root:
    python analysis/aggregate_all30.py   # first
    python analysis/generate_latex_tables.py
"""

import csv
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR = ROOT / "results"
OUT_TEX = ROOT / "analysis" / "tables.tex"

# Display order and labels for methods
METHOD_ORDER = [
    "ff",
    "add",
    "max",
    "lmcut",
    "llm-gpt-4o-mini",
    "llm-gpt-4.1-mini",
    "llm-gpt-4.1",
    "llm-llama",
]

METHOD_LABELS = {
    "ff":               r"\textsc{FF}",
    "add":              r"\textsc{Add}",
    "max":              r"\textsc{Max}",
    "lmcut":            r"\textsc{LM-Cut}",
    "llm-gpt-4o-mini":  r"LLM (\texttt{gpt-4o-mini})",
    "llm-gpt-4.1-mini": r"LLM (\texttt{gpt-4.1-mini})",
    "llm-gpt-4.1":      r"LLM (\texttt{gpt-4.1})",
    "llm-llama":        r"LLM (\texttt{LLaMA})",
}

DOMAIN_ORDER = ["blocksworld", "gripper", "logistics", "miconic", "depots", "rovers"]
DOMAIN_LABELS = {d: d.capitalize() for d in DOMAIN_ORDER}


def load_summary(path: Path) -> dict:
    """Returns dict: (domain, method) -> row dict."""
    data = {}
    with path.open(newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = (row["domain"], row["method"])
            data[key] = row
    return data


def safe(v, fmt="{:.1f}"):
    if v is None or v == "" or v == "None":
        return "--"
    try:
        return fmt.format(float(v))
    except (ValueError, TypeError):
        return "--"


def coverage_str(row) -> str:
    if not row:
        return "--"
    try:
        return f"{int(row['n_solved'])}/30"
    except (KeyError, ValueError):
        return "--"


# ---------------------------------------------------------------------------
# Table 1 — Coverage
# ---------------------------------------------------------------------------

def build_coverage_table(data: dict, domains: list, methods: list) -> str:
    present_domains = [d for d in domains if any((d, m) in data for m in methods)]
    present_methods = [m for m in methods if any((d, m) in data for d in present_domains)]

    col_spec = "l" + "c" * len(present_domains)
    domain_header = " & ".join(DOMAIN_LABELS.get(d, d) for d in present_domains)

    lines = []
    lines.append(r"\begin{table}[t]")
    lines.append(r"\centering")
    lines.append(r"\caption{Coverage (instances solved / 30) per heuristic and domain. "
                 r"Time limit: 300\,s per instance.}")
    lines.append(r"\label{tab:coverage}")
    lines.append(rf"\begin{{tabular}}{{{col_spec}}}")
    lines.append(r"\toprule")
    lines.append(f"Heuristic & {domain_header} \\\\")
    lines.append(r"\midrule")

    for m in present_methods:
        label = METHOD_LABELS.get(m, m)
        cells = [label]
        for d in present_domains:
            row = data.get((d, m))
            cells.append(coverage_str(row))
        lines.append(" & ".join(cells) + r" \\")

        # Add midrule between baselines and LLM methods
        if m == "lmcut" and any(pm.startswith("llm") for pm in present_methods):
            lines.append(r"\midrule")

    lines.append(r"\bottomrule")
    lines.append(r"\end{tabular}")
    lines.append(r"\end{table}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Table 2+ — Per-domain detail (expansions, time, plan length)
# ---------------------------------------------------------------------------

def build_domain_detail_table(data: dict, domain: str, methods: list) -> str:
    present_methods = [m for m in methods if (domain, m) in data]
    if not present_methods:
        return f"% No data for {domain}\n"

    lines = []
    lines.append(rf"\begin{{table}}[t]")
    lines.append(r"\centering")
    lines.append(
        rf"\caption{{Results for \textbf{{{DOMAIN_LABELS.get(domain, domain)}}}. "
        rf"Coverage (solved/30), median expansions, median search time (s), "
        rf"median plan length on solved instances. ``--'' = no solved instances.}}"
    )
    lines.append(rf"\label{{tab:{domain}}}")
    lines.append(r"\begin{tabular}{lcccc}")
    lines.append(r"\toprule")
    lines.append(r"Heuristic & Cov & Med.\ Exp & Med.\ Time (s) & Med.\ Plan Len \\")
    lines.append(r"\midrule")

    for m in present_methods:
        row = data.get((domain, m), {})
        label = METHOD_LABELS.get(m, m)
        cov   = coverage_str(row)
        exp   = safe(row.get("med_expansions"), "{:.0f}")
        time_ = safe(row.get("med_search_time"), "{:.3f}")
        plen  = safe(row.get("med_plan_length"), "{:.0f}")
        lines.append(f"{label} & {cov} & {exp} & {time_} & {plen} \\\\")

        if m == "lmcut":
            lines.append(r"\midrule")

    lines.append(r"\bottomrule")
    lines.append(r"\end{tabular}")
    lines.append(r"\end{table}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    summary_path = RESULTS_DIR / "summary_all30.csv"
    if not summary_path.exists():
        print(f"ERROR: {summary_path} not found.")
        print("Run:  python analysis/aggregate_all30.py  first.")
        return

    data = load_summary(summary_path)
    print(f"Loaded {len(data)} (domain, method) entries from {summary_path}")

    parts = []

    parts.append("% ============================================================")
    parts.append("% Auto-generated by analysis/generate_latex_tables.py")
    parts.append("% ============================================================")
    parts.append("")

    # Table 1: coverage
    parts.append("% --- Table 1: Coverage ---")
    parts.append(build_coverage_table(data, DOMAIN_ORDER, METHOD_ORDER))
    parts.append("")

    # Per-domain detail tables
    for d in DOMAIN_ORDER:
        parts.append(f"% --- Table: {d} detail ---")
        parts.append(build_domain_detail_table(data, d, METHOD_ORDER))
        parts.append("")

    tex = "\n".join(parts)

    out_dir = ROOT / "analysis"
    out_dir.mkdir(exist_ok=True)
    OUT_TEX.write_text(tex)
    print(f"Wrote {OUT_TEX}")
    print(f"In your thesis: \\input{{analysis/tables}}")


if __name__ == "__main__":
    main()
