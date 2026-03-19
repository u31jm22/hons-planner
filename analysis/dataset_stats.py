#!/usr/bin/env python3
"""
analysis/dataset_stats.py
--------------------------
Compute structural statistics for each domain's PDDL instance set.
Run from the project root:
    python analysis/dataset_stats.py

Outputs:
    - Prints a Markdown table to stdout
    - Writes analysis/dataset_section.md  (copy-paste into thesis)
    - Writes analysis/dataset_section.tex (\\input{} into thesis)
"""

import re
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------------
# Per-domain parsers
# ---------------------------------------------------------------------------

def parse_blocksworld(pddl: str) -> dict:
    """Count blocks (objects of type block or plain objects in BLOCKS domain)."""
    obj_match = re.search(r":objects(.*?)(?=\(:|$)", pddl, re.DOTALL | re.IGNORECASE)
    if not obj_match:
        return {"blocks": 0, "stacks": 0}
    obj_text = obj_match.group(1)
    # objects listed as 'A B C D - block' or just 'A B C D'
    blocks = re.findall(r'\b([A-Za-z]\w*)\b', obj_text)
    blocks = [b for b in blocks if b.lower() not in ('block', 'blocks', '-')]
    n_blocks = len(blocks)

    # Count stacks: groups of blocks with on/ontable relationships
    init_match = re.search(r":init(.*?)(?=:goal)", pddl, re.DOTALL | re.IGNORECASE)
    n_stacks = 0
    if init_match:
        ontable = re.findall(r'\(ontable\s+\w+\)', init_match.group(1), re.IGNORECASE)
        n_stacks = len(ontable)
    return {"blocks": n_blocks, "stacks": n_stacks}


def parse_gripper(pddl: str) -> dict:
    obj_match = re.search(r":objects(.*?)(?=:init)", pddl, re.DOTALL | re.IGNORECASE)
    balls = rooms = 0
    if obj_match:
        obj_text = obj_match.group(1)
        # objects like: rooma roomb ball4 ball3 ball2 ball1 left right
        tokens = re.findall(r'\b(\w+)\b', obj_text)
        balls = sum(1 for t in tokens if t.lower().startswith('ball'))
        rooms = sum(1 for t in tokens if t.lower().startswith('room'))
    return {"balls": balls, "rooms": rooms}


def parse_logistics(pddl: str) -> dict:
    obj_match = re.search(r":objects(.*?)(?=:init)", pddl, re.DOTALL | re.IGNORECASE)
    packages = locs = cities = trucks = planes = 0
    if obj_match:
        obj_text = obj_match.group(1)
        # typed objects: 'apn1 - airplane', 'tru1 tru2 - truck', 'obj11 obj12 - package'
        type_blocks = re.findall(r'([\w\s]+)-\s*(\w+)', obj_text)
        for names_str, type_name in type_blocks:
            names = names_str.split()
            n = len(names)
            t = type_name.lower()
            if 'package' in t or 'object' in t:
                packages += n
            elif 'location' in t:
                locs += n
            elif 'city' in t:
                cities += n
            elif 'truck' in t:
                trucks += n
            elif 'airplane' in t or 'plane' in t:
                planes += n
    return {
        "packages": packages,
        "locations": locs,
        "cities": cities,
        "trucks": trucks,
        "planes": planes,
    }


def parse_miconic(pddl: str) -> dict:
    obj_match = re.search(r":objects(.*?)(?=:init)", pddl, re.DOTALL | re.IGNORECASE)
    passengers = floors = 0
    if obj_match:
        obj_text = obj_match.group(1)
        type_blocks = re.findall(r'([\w\s]+)-\s*(\w+)', obj_text)
        for names_str, type_name in type_blocks:
            names = names_str.split()
            n = len(names)
            t = type_name.lower()
            if 'passenger' in t:
                passengers += n
            elif 'floor' in t:
                floors += n
    # fallback: count 'p\d' tokens for passengers, 'f\d' for floors
    if passengers == 0 and floors == 0:
        tokens = re.findall(r'\b(\w+)\b', obj_match.group(1) if obj_match else "")
        passengers = sum(1 for t in tokens if re.match(r'^p\d', t))
        floors = sum(1 for t in tokens if re.match(r'^f\d', t))
    return {"passengers": passengers, "floors": floors}


def parse_depots(pddl: str) -> dict:
    obj_match = re.search(r":objects(.*?)(?=:init)", pddl, re.DOTALL | re.IGNORECASE)
    depots = distributors = trucks = pallets = crates = hoists = 0
    if obj_match:
        obj_text = obj_match.group(1)
        type_blocks = re.findall(r'([\w\s]+)-\s*(\w+)', obj_text)
        for names_str, type_name in type_blocks:
            names = names_str.split()
            n = len(names)
            t = type_name.lower()
            if t == 'depot':
                depots += n
            elif t == 'distributor':
                distributors += n
            elif t == 'truck':
                trucks += n
            elif t == 'pallet':
                pallets += n
            elif t == 'crate':
                crates += n
            elif t == 'hoist':
                hoists += n
    return {
        "depots": depots,
        "distributors": distributors,
        "trucks": trucks,
        "pallets": pallets,
        "crates": crates,
        "hoists": hoists,
    }


def parse_rovers(pddl: str) -> dict:
    obj_match = re.search(r":objects(.*?)(?=:init)", pddl, re.DOTALL | re.IGNORECASE)
    rovers = waypoints = cameras = objectives = 0
    if obj_match:
        obj_text = obj_match.group(1)
        type_blocks = re.findall(r'([\w\s]+)-\s*(\w+)', obj_text)
        for names_str, type_name in type_blocks:
            names = names_str.split()
            n = len(names)
            t = type_name.lower()
            if t == 'rover':
                rovers += n
            elif t == 'waypoint':
                waypoints += n
            elif t == 'camera':
                cameras += n
            elif t == 'objective':
                objectives += n
    return {
        "rovers": rovers,
        "waypoints": waypoints,
        "cameras": cameras,
        "objectives": objectives,
    }


DOMAIN_PARSERS = {
    "blocksworld": parse_blocksworld,
    "gripper": parse_gripper,
    "logistics": parse_logistics,
    "miconic": parse_miconic,
    "depots": parse_depots,
    "rovers": parse_rovers,
}

DOMAIN_STAT_KEYS = {
    "blocksworld": ["blocks", "stacks"],
    "gripper":     ["balls", "rooms"],
    "logistics":   ["packages", "locations", "cities", "trucks", "planes"],
    "miconic":     ["passengers", "floors"],
    "depots":      ["depots", "distributors", "trucks", "pallets", "crates", "hoists"],
    "rovers":      ["rovers", "waypoints", "cameras", "objectives"],
}


# ---------------------------------------------------------------------------
# Aggregation
# ---------------------------------------------------------------------------

def load_instances(domain: str, instance_file: str = "all_instances.txt") -> list[Path]:
    inst_path = ROOT / "domains" / domain / instance_file
    if not inst_path.exists():
        # fallback: glob all pXX.pddl
        return sorted((ROOT / "domains" / domain).glob("p*.pddl"))
    names = [l.strip() for l in inst_path.read_text().splitlines() if l.strip()]
    return [ROOT / "domains" / domain / n for n in names]


def compute_domain_stats(domain: str) -> dict:
    parser = DOMAIN_PARSERS.get(domain)
    if parser is None:
        return {}

    paths = load_instances(domain)
    if not paths:
        return {}

    all_stats = []
    for p in paths:
        if not p.exists():
            continue
        pddl = p.read_text(errors="ignore")
        stats = parser(pddl)
        all_stats.append(stats)

    if not all_stats:
        return {}

    keys = DOMAIN_STAT_KEYS[domain]
    result = {"n_instances": len(all_stats)}
    for k in keys:
        vals = [s.get(k, 0) for s in all_stats]
        result[f"{k}_min"]    = min(vals)
        result[f"{k}_median"] = statistics.median(vals)
        result[f"{k}_max"]    = max(vals)
    return result


# ---------------------------------------------------------------------------
# Output formatters
# ---------------------------------------------------------------------------

def _fmt(v) -> str:
    if isinstance(v, float) and v == int(v):
        return str(int(v))
    if isinstance(v, float):
        return f"{v:.1f}"
    return str(v)


def render_markdown(all_results: dict) -> str:
    lines = []
    lines.append("## Dataset\n")
    lines.append(
        "We evaluate on 30 benchmark instances per domain, drawn from the "
        "IPC benchmark set (aibasel/downward-benchmarks). "
        "Instances p01–p05 are used as the training split (for LLM candidate selection); "
        "all 30 instances are used for the test evaluation reported in the results.\n"
    )

    for domain, stats in all_results.items():
        if not stats:
            continue
        n = stats["n_instances"]
        keys = DOMAIN_STAT_KEYS[domain]
        lines.append(f"### {domain.capitalize()} ({n} instances)\n")
        lines.append("| Statistic | Min | Median | Max |")
        lines.append("|-----------|-----|--------|-----|")
        for k in keys:
            row = (
                f"| {k.replace('_',' ').title()} "
                f"| {_fmt(stats[f'{k}_min'])} "
                f"| {_fmt(stats[f'{k}_median'])} "
                f"| {_fmt(stats[f'{k}_max'])} |"
            )
            lines.append(row)
        lines.append("")

    return "\n".join(lines)


def render_latex(all_results: dict) -> str:
    lines = []
    lines.append(r"\subsection*{Dataset}")
    lines.append(
        r"We evaluate on 30 benchmark instances per domain, drawn from the "
        r"IPC benchmark set~\cite{downward-benchmarks}. "
        r"Instances \texttt{p01}--\texttt{p05} are used as the training split "
        r"for LLM candidate selection; all 30 instances are used for evaluation."
    )
    lines.append("")

    for domain, stats in all_results.items():
        if not stats:
            continue
        n = stats["n_instances"]
        keys = DOMAIN_STAT_KEYS[domain]
        lines.append(r"\paragraph{" + domain.capitalize() + rf"} ({n} instances)")
        lines.append(r"\begin{table}[h]\centering")
        lines.append(r"\begin{tabular}{lccc}\toprule")
        lines.append(r"Statistic & Min & Median & Max \\ \midrule")
        for k in keys:
            label = k.replace("_", " ").title()
            row = (
                f"{label} & {_fmt(stats[f'{k}_min'])} "
                f"& {_fmt(stats[f'{k}_median'])} "
                f"& {_fmt(stats[f'{k}_max'])} \\\\"
            )
            lines.append(row)
        lines.append(r"\bottomrule\end{tabular}")
        lines.append(rf"\caption{{Instance statistics for {domain.capitalize()} domain.}}")
        lines.append(r"\end{table}")
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    domains = ["blocksworld", "gripper", "logistics", "miconic", "depots", "rovers"]
    all_results = {}
    for d in domains:
        domain_path = ROOT / "domains" / d
        if not domain_path.exists():
            print(f"[SKIP] {d} — domain directory not found")
            continue
        print(f"Computing stats for {d}...")
        all_results[d] = compute_domain_stats(d)

    md = render_markdown(all_results)
    tex = render_latex(all_results)

    out_dir = ROOT / "analysis"
    out_dir.mkdir(exist_ok=True)

    md_path = out_dir / "dataset_section.md"
    tex_path = out_dir / "dataset_section.tex"

    md_path.write_text(md)
    tex_path.write_text(tex)

    print("\n" + md)
    print(f"\nWrote {md_path}")
    print(f"Wrote {tex_path}")


if __name__ == "__main__":
    main()
