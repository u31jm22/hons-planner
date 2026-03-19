#!/usr/bin/env python3
"""
analysis/plot_results.py
-------------------------
Reads results/summary_all30.csv and generates bar charts with error bars for:
  1. Coverage (n_solved/30) per heuristic per domain
  2. Median expansions per heuristic per domain  (log scale)
  3. Median search time per heuristic per domain (log scale)

Saves all figures as PNGs to figures/

Run from the project root:
    python analysis/plot_results.py
"""

import csv
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR = ROOT / "results"
FIGURES_DIR = ROOT / "figures"

METHOD_ORDER = [
    "ff", "add", "max", "lmcut",
    "llm-gpt-4o-mini", "llm-gpt-4.1-mini", "llm-gpt-4.1", "llm-llama",
]
METHOD_LABELS = {
    "ff":               "FF",
    "add":              "Add",
    "max":              "Max",
    "lmcut":            "LM-Cut",
    "llm-gpt-4o-mini":  "GPT-4o-mini",
    "llm-gpt-4.1-mini": "GPT-4.1-mini",
    "llm-gpt-4.1":      "GPT-4.1",
    "llm-llama":        "LLaMA",
}
DOMAIN_ORDER  = ["blocksworld", "gripper", "logistics", "miconic", "depots", "rovers"]
DOMAIN_LABELS = {d: d.capitalize() for d in DOMAIN_ORDER}

# Colour palette: baselines in greys, LLM methods in blues/greens
COLOURS = {
    "ff":               "#9e9e9e",
    "add":              "#757575",
    "max":              "#424242",
    "lmcut":            "#212121",
    "llm-gpt-4o-mini":  "#42a5f5",
    "llm-gpt-4.1-mini": "#1565c0",
    "llm-gpt-4.1":      "#0d47a1",
    "llm-llama":        "#2e7d32",
}


def load_summary(path: Path) -> dict:
    data = {}
    with path.open(newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            data[(row["domain"], row["method"])] = row
    return data


def safe_float(v):
    try:
        f = float(v)
        return f if f >= 0 else None
    except (TypeError, ValueError):
        return None


def main():
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError:
        print("matplotlib not installed. Run: pip install matplotlib")
        return

    summary_path = RESULTS_DIR / "summary_all30.csv"
    if not summary_path.exists():
        print(f"ERROR: {summary_path} not found. Run aggregate_all30.py first.")
        return

    data = load_summary(summary_path)
    FIGURES_DIR.mkdir(exist_ok=True)

    present_methods = [m for m in METHOD_ORDER if any((d, m) in data for d in DOMAIN_ORDER)]
    present_domains = [d for d in DOMAIN_ORDER if any((d, m) in data for m in present_methods)]

    x = np.arange(len(present_domains))
    n_methods = len(present_methods)
    bar_w = 0.8 / n_methods
    offsets = np.linspace(-(n_methods - 1) * bar_w / 2, (n_methods - 1) * bar_w / 2, n_methods)

    # ----------------------------------------------------------------
    # Fig 1: Coverage
    # ----------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(12, 5))
    for i, method in enumerate(present_methods):
        vals = []
        for d in present_domains:
            row = data.get((d, method), {})
            n_solved = safe_float(row.get("n_solved"))
            vals.append(n_solved if n_solved is not None else 0)
        bars = ax.bar(
            x + offsets[i], vals, bar_w,
            label=METHOD_LABELS.get(method, method),
            color=COLOURS.get(method, "#cccccc"),
            edgecolor="white", linewidth=0.5,
        )

    ax.set_xticks(x)
    ax.set_xticklabels([DOMAIN_LABELS[d] for d in present_domains], fontsize=11)
    ax.set_ylabel("Instances Solved (/ 30)", fontsize=11)
    ax.set_title("Coverage: Instances Solved per Heuristic and Domain", fontsize=13)
    ax.set_ylim(0, 33)
    ax.axhline(30, color="red", linestyle="--", linewidth=0.8, alpha=0.5, label="Max (30)")
    ax.legend(loc="lower right", fontsize=8, ncol=2)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    out = FIGURES_DIR / "coverage.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"Saved {out}")

    # ----------------------------------------------------------------
    # Fig 2: Median expansions (log scale, solved only)
    # ----------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(12, 5))
    for i, method in enumerate(present_methods):
        vals = []
        errs = []
        for d in present_domains:
            row = data.get((d, method), {})
            v = safe_float(row.get("med_expansions"))
            e = safe_float(row.get("std_expansions"))
            vals.append(v if v is not None else 0)
            errs.append(e if e is not None else 0)
        vals = np.array(vals, dtype=float)
        errs = np.array(errs, dtype=float)
        ax.bar(
            x + offsets[i], vals, bar_w,
            yerr=errs, capsize=2,
            label=METHOD_LABELS.get(method, method),
            color=COLOURS.get(method, "#cccccc"),
            edgecolor="white", linewidth=0.5, error_kw={"elinewidth": 0.8},
        )

    ax.set_xticks(x)
    ax.set_xticklabels([DOMAIN_LABELS[d] for d in present_domains], fontsize=11)
    ax.set_ylabel("Median Expansions (log scale)", fontsize=11)
    ax.set_title("Median Node Expansions on Solved Instances", fontsize=13)
    ax.set_yscale("symlog", linthresh=10)
    ax.legend(loc="upper right", fontsize=8, ncol=2)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    out = FIGURES_DIR / "expansions.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"Saved {out}")

    # ----------------------------------------------------------------
    # Fig 3: Median search time (log scale, solved only)
    # ----------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(12, 5))
    for i, method in enumerate(present_methods):
        vals = []
        errs = []
        for d in present_domains:
            row = data.get((d, method), {})
            v = safe_float(row.get("med_search_time"))
            e = safe_float(row.get("std_search_time"))
            vals.append(v if v is not None else 0)
            errs.append(e if e is not None else 0)
        vals = np.array(vals, dtype=float)
        errs = np.array(errs, dtype=float)
        ax.bar(
            x + offsets[i], vals, bar_w,
            yerr=errs, capsize=2,
            label=METHOD_LABELS.get(method, method),
            color=COLOURS.get(method, "#cccccc"),
            edgecolor="white", linewidth=0.5, error_kw={"elinewidth": 0.8},
        )

    ax.set_xticks(x)
    ax.set_xticklabels([DOMAIN_LABELS[d] for d in present_domains], fontsize=11)
    ax.set_ylabel("Median Search Time / s (log scale)", fontsize=11)
    ax.set_title("Median Search Time on Solved Instances", fontsize=13)
    ax.set_yscale("symlog", linthresh=0.001)
    ax.legend(loc="upper right", fontsize=8, ncol=2)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    out = FIGURES_DIR / "search_time.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"Saved {out}")

    # ----------------------------------------------------------------
    # Fig 4: Plan length suboptimality vs lmcut baseline
    # ----------------------------------------------------------------
    lmcut_plan = {d: safe_float(data.get((d, "lmcut"), {}).get("med_plan_length"))
                  for d in present_domains}
    fig, ax = plt.subplots(figsize=(12, 5))
    llm_methods = [m for m in present_methods if m.startswith("llm")]
    llm_offsets = np.linspace(-(len(llm_methods)-1)*bar_w/2,
                               (len(llm_methods)-1)*bar_w/2,
                               len(llm_methods)) if llm_methods else []

    for i, method in enumerate(llm_methods):
        vals = []
        for d in present_domains:
            row = data.get((d, method), {})
            v = safe_float(row.get("med_plan_length"))
            ref = lmcut_plan.get(d)
            if v is not None and ref is not None and ref > 0:
                vals.append(v / ref)
            else:
                vals.append(0)
        ax.bar(
            x + llm_offsets[i], vals, bar_w,
            label=METHOD_LABELS.get(method, method),
            color=COLOURS.get(method, "#cccccc"),
            edgecolor="white", linewidth=0.5,
        )

    ax.axhline(1.0, color="red", linestyle="--", linewidth=1.0, label="LM-Cut baseline (1.0)")
    ax.set_xticks(x)
    ax.set_xticklabels([DOMAIN_LABELS[d] for d in present_domains], fontsize=11)
    ax.set_ylabel("Plan Length Ratio (LLM / LM-Cut)", fontsize=11)
    ax.set_title("Plan Length Suboptimality vs LM-Cut", fontsize=13)
    ax.legend(loc="upper right", fontsize=8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    out = FIGURES_DIR / "plan_length_ratio.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"Saved {out}")

    print(f"\nAll figures saved to {FIGURES_DIR}/")


if __name__ == "__main__":
    main()
