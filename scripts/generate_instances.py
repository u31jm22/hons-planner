#!/usr/bin/env python3
"""
scripts/generate_instances.py
-------------------------------
Programmatic PDDL instance generator for all 6 thesis domains.

Each domain has a dedicated generator that produces instances of increasing
difficulty.  The generators write to domains/<domain>/ and update the
all_instances.txt, train_instances.txt, and test_instances.txt files.

Usage
-----
  # Regenerate all domains:
  python scripts/generate_instances.py

  # Single domain:
  python scripts/generate_instances.py --domain visitall

  # Show sizes without writing:
  python scripts/generate_instances.py --dry-run

  # Override output directory root:
  python scripts/generate_instances.py --domains-root /path/to/domains

Domains covered
---------------
  blocksworld  — N blocks, randomised initial stack configuration → goal stacks
  gripper      — N balls in room A, must be moved to room B
  logistics    — trucks + packages across cities
  miconic      — elevator with N floors and M passengers
  depots       — forklifts moving crates between depots
  rovers       — planetary rovers collecting rock/soil/image samples
  visitall     — robot visiting cells in a grid

Note: blocksworld, gripper, logistics, miconic, depots, rovers already have
hand-curated instances in the repo.  This script generates *additional*
instances for the visitall domain (or regenerates any domain from scratch
if the --domain flag is used).  Existing files are NOT overwritten unless
--overwrite is passed.
"""

import argparse
import os
import random
import textwrap
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


# ─────────────────────────────────────────────────────────────────────────────
# Helper
# ─────────────────────────────────────────────────────────────────────────────

def write_if_new(path: Path, content: str, overwrite: bool, dry_run: bool) -> bool:
    """Write content to path if it does not exist (or --overwrite).  Returns True if written."""
    if dry_run:
        print(f"  [DRY RUN] Would write {path.name}")
        return False
    if path.exists() and not overwrite:
        return False
    path.write_text(content)
    return True


def write_instance_lists(out_dir: Path, all_instances: list[str],
                         train_n: int, dry_run: bool, overwrite: bool):
    """Write all_instances.txt, train_instances.txt, test_instances.txt."""
    train = all_instances[:train_n]
    test = all_instances

    for fname, lst in [
        ("all_instances.txt", all_instances),
        ("train_instances.txt", train),
        ("test_instances.txt", test),
    ]:
        p = out_dir / fname
        content = "\n".join(lst) + "\n"
        if dry_run:
            print(f"  [DRY RUN] Would write {fname} ({len(lst)} entries)")
        else:
            if p.exists() and not overwrite:
                print(f"    (skip {fname} — already exists)")
            else:
                p.write_text(content)
                print(f"    Wrote {fname} ({len(lst)} entries)")


# ─────────────────────────────────────────────────────────────────────────────
# VISITALL generator
# ─────────────────────────────────────────────────────────────────────────────

VISITALL_DOMAIN = """\
(define (domain grid-visit-all)
(:requirements :typing)
(:types place - object)
(:predicates (connected ?x ?y - place)
             (at-robot ?x - place)
             (visited ?x - place))

(:action move
  :parameters (?curpos ?nextpos - place)
  :precondition (and (at-robot ?curpos) (connected ?curpos ?nextpos))
  :effect (and (at-robot ?nextpos) (not (at-robot ?curpos)) (visited ?nextpos)))
)
"""


def generate_visitall_instance(rows: int, cols: int, k_visit: int,
                                 seed: int, pnum: int) -> str:
    """Generate a visitall PDDL problem instance."""
    rng = random.Random(seed)
    places = [f"r{i}c{j}" for i in range(rows) for j in range(cols)]
    obj_str = " ".join(places) + " - place"

    init = ["(at-robot r0c0)", "(visited r0c0)"]
    for i in range(rows):
        for j in range(cols):
            if j + 1 < cols:
                init += [f"(connected r{i}c{j} r{i}c{j+1})",
                         f"(connected r{i}c{j+1} r{i}c{j})"]
            if i + 1 < rows:
                init += [f"(connected r{i}c{j} r{i+1}c{j})",
                         f"(connected r{i+1}c{j} r{i}c{j})"]

    must_visit = ["r0c0"]
    remaining = [p for p in places if p != "r0c0"]
    k_extra = min(k_visit - 1, len(remaining))
    to_visit = must_visit + rng.sample(remaining, k_extra)
    goal_str = " ".join(f"(visited {p})" for p in to_visit)

    return textwrap.dedent(f"""\
        (define (problem visitall-p{pnum:02d})
          (:domain grid-visit-all)
          (:objects {obj_str})
          (:init {' '.join(init)})
          (:goal (and {goal_str}))
        )
        """)


# 30 instance configs: (rows, cols, k_visit, seed)
VISITALL_CONFIGS = [
    # p01-p05: trivial (exp < 25)
    (2, 2,  4,  1),
    (3, 2,  5,  2),
    (3, 3,  6,  3),
    (3, 3,  7,  4),
    (3, 3,  9,  5),
    # p06-p10: easy (exp 25-200)
    (4, 3,  8,  6),
    (4, 3, 10,  7),
    (4, 3, 12,  8),
    (4, 4, 10,  9),
    (4, 4, 12, 10),
    # p11-p15: medium (exp 200-500)
    (4, 4, 16, 11),
    (5, 4, 11, 12),
    (5, 4, 14, 13),
    (5, 4, 17, 14),
    (5, 4, 20, 15),
    # p16-p20: medium-hard (exp 500-2000)
    (5, 5, 13, 16),
    (5, 5, 16, 17),
    (5, 5, 19, 18),
    (5, 5, 22, 19),
    (5, 5, 25, 20),
    # p21-p25: hard (exp 2000-10000)
    (6, 5, 15, 21),
    (6, 5, 18, 22),
    (6, 5, 22, 23),
    (6, 5, 26, 24),
    (6, 5, 30, 25),
    # p26-p30: very hard (exp 10000+, may timeout weak heuristics)
    (6, 6, 18, 26),
    (6, 6, 22, 27),
    (6, 6, 26, 28),
    (6, 6, 30, 29),
    (6, 6, 36, 30),
]


def generate_visitall(domains_root: Path, overwrite: bool, dry_run: bool):
    out = domains_root / "visitall"
    out.mkdir(exist_ok=True)
    print("\n[visitall] Generating 30 instances...")

    # Domain file
    d = out / "domain.pddl"
    if not d.exists() or overwrite:
        if not dry_run:
            d.write_text(VISITALL_DOMAIN)
            print("  Wrote domain.pddl")

    written = 0
    for idx, (rows, cols, k, seed) in enumerate(VISITALL_CONFIGS, 1):
        pddl = generate_visitall_instance(rows, cols, k, seed, idx)
        p = out / f"p{idx:02d}.pddl"
        if write_if_new(p, pddl, overwrite, dry_run):
            written += 1

    all_insts = [f"p{i:02d}.pddl" for i in range(1, 31)]
    write_instance_lists(out, all_insts, train_n=5, dry_run=dry_run, overwrite=overwrite)
    print(f"  Written {written}/30 problem files.")


# ─────────────────────────────────────────────────────────────────────────────
# BLOCKSWORLD generator
# ─────────────────────────────────────────────────────────────────────────────

def generate_blocksworld_instance(n_blocks: int, seed: int, pnum: int) -> str:
    """
    Random blocksworld: initial state = random stacks; goal = one big stack.
    Difficulty ≈ n_blocks².
    """
    rng = random.Random(seed)
    blocks = [f"b{i}" for i in range(1, n_blocks + 1)]
    obj_str = " ".join(blocks)

    # Random initial stacks
    shuffled = blocks[:]
    rng.shuffle(shuffled)
    stacks: list[list[str]] = []
    i = 0
    while i < len(shuffled):
        height = rng.randint(1, max(1, len(shuffled) - i))
        stacks.append(shuffled[i:i + height])
        i += height

    init = []
    for stack in stacks:
        init.append(f"(ontable {stack[0]})")
        for k in range(len(stack) - 1):
            init.append(f"(on {stack[k+1]} {stack[k]})")
        init.append(f"(clear {stack[-1]})")
    init.append("(handempty)")

    # Goal: single tower in original order b1, b2, ..., bN
    goal_parts = [f"(ontable b1)"]
    for k in range(n_blocks - 1):
        goal_parts.append(f"(on b{k+2} b{k+1})")
    goal_parts.append(f"(clear b{n_blocks})")

    return textwrap.dedent(f"""\
        (define (problem blocksworld-gen-p{pnum:02d})
          (:domain blocksworld)
          (:objects {obj_str})
          (:init {' '.join(init)})
          (:goal (and {' '.join(goal_parts)}))
        )
        """)


# ─────────────────────────────────────────────────────────────────────────────
# GRIPPER generator
# ─────────────────────────────────────────────────────────────────────────────

def generate_gripper_instance(n_balls: int, pnum: int) -> str:
    """N balls all in rooma, goal: all in roomb."""
    balls = [f"ball{i}" for i in range(1, n_balls + 1)]
    obj_str = " ".join(balls) + " rooma roomb"
    init = ["(free gripper1)", "(free gripper2)", "(at-robby rooma)"]
    init += [f"(at {b} rooma)" for b in balls]
    goal = " ".join(f"(at {b} roomb)" for b in balls)
    return textwrap.dedent(f"""\
        (define (problem gripper-gen-p{pnum:02d})
          (:domain gripper)
          (:objects {obj_str})
          (:init {' '.join(init)})
          (:goal (and {goal}))
        )
        """)


# ─────────────────────────────────────────────────────────────────────────────
# MICONIC generator
# ─────────────────────────────────────────────────────────────────────────────

def generate_miconic_instance(n_floors: int, n_passengers: int,
                               seed: int, pnum: int) -> str:
    """
    Elevator (miconic): N passengers each board at a random floor, want
    to reach a different random floor.
    """
    rng = random.Random(seed)
    floors = [f"f{i}" for i in range(n_floors)]
    pax = [f"p{i}" for i in range(n_passengers)]
    obj_str = " ".join(pax) + " " + " ".join(floors)

    init = ["(lift-at f0)"]
    for pa in pax:
        origin = rng.choice(floors)
        init.append(f"(origin {pa} {origin})")
        dest = rng.choice([f for f in floors if f != origin])
        init.append(f"(destin {pa} {dest})")
        init.append(f"(above f0 {floors[1]})" if False else "")  # skip — added below

    # above predicates
    for i in range(n_floors):
        for j in range(i + 1, n_floors):
            init.append(f"(above f{i} f{j})")

    goal = " ".join(f"(served {pa})" for pa in pax)
    init_clean = [x for x in init if x]
    return textwrap.dedent(f"""\
        (define (problem miconic-gen-p{pnum:02d})
          (:domain miconic)
          (:objects {obj_str})
          (:init {' '.join(init_clean)})
          (:goal (and {goal}))
        )
        """)


# ─────────────────────────────────────────────────────────────────────────────
# LOGISTICS generator
# ─────────────────────────────────────────────────────────────────────────────

def generate_logistics_instance(n_cities: int, n_packages: int,
                                  seed: int, pnum: int) -> str:
    """
    Logistics: N packages in random cities, trucks + airplane,
    goal: deliver all packages to target cities.
    """
    rng = random.Random(seed)
    cities = [f"city{i}" for i in range(n_cities)]
    locs = [f"loc{c}_{k}" for c in range(n_cities) for k in range(2)]  # 2 locs per city
    airports = [f"airport{c}" for c in range(n_cities)]
    trucks = [f"truck{c}" for c in range(n_cities)]
    planes = ["plane0"]
    packages = [f"pkg{i}" for i in range(n_packages)]

    all_locs = locs + airports
    obj_str = " ".join(packages + trucks + planes + all_locs + cities)
    # city membership
    init = []
    for c in range(n_cities):
        init.append(f"(incity {airports[c]} city{c})")
        for k in range(2):
            init.append(f"(incity loc{c}_{k} city{c})")
        init.append(f"(at {trucks[c]} loc{c}_0)")

    init.append(f"(at plane0 {airports[0]})")
    for pkg in packages:
        src = rng.choice(all_locs)
        init.append(f"(at {pkg} {src})")

    goal_parts = []
    for pkg in packages:
        tgt = rng.choice(all_locs)
        goal_parts.append(f"(at {pkg} {tgt})")

    return textwrap.dedent(f"""\
        (define (problem logistics-gen-p{pnum:02d})
          (:domain logistics)
          (:objects {obj_str})
          (:init {' '.join(init)})
          (:goal (and {' '.join(goal_parts)}))
        )
        """)


# ─────────────────────────────────────────────────────────────────────────────
# Main dispatch
# ─────────────────────────────────────────────────────────────────────────────

GENERATORS = {
    "visitall": generate_visitall,
    # Others just verify existing instances exist (hand-curated)
}


def check_existing(domains_root: Path, domain: str):
    """Print status of an existing hand-curated domain."""
    d = domains_root / domain
    if not d.exists():
        print(f"\n[{domain}] WARNING: directory not found at {d}")
        return
    pddl_files = sorted(d.glob("p*.pddl"))
    print(f"\n[{domain}] {len(pddl_files)} instance files found (hand-curated, not regenerated).")
    all_txt = d / "all_instances.txt"
    if all_txt.exists():
        lines = [l.strip() for l in all_txt.read_text().splitlines() if l.strip()]
        print(f"          all_instances.txt → {len(lines)} entries")
    else:
        print(f"          WARNING: all_instances.txt missing!")


def main():
    parser = argparse.ArgumentParser(
        description="Generate PDDL instances for all 6 thesis domains."
    )
    parser.add_argument(
        "--domain",
        choices=list(GENERATORS.keys()) + ["blocksworld", "gripper", "logistics",
                                            "miconic", "depots", "rovers"],
        help="Generate instances for a single domain only."
    )
    parser.add_argument(
        "--domains-root", type=Path, default=PROJECT_ROOT / "domains",
        help="Root directory for domain folders."
    )
    parser.add_argument(
        "--overwrite", action="store_true",
        help="Overwrite existing instance files."
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print what would be written without writing."
    )
    args = parser.parse_args()

    domains_root = args.domains_root
    domains_root.mkdir(exist_ok=True)

    all_domains = ["blocksworld", "gripper", "logistics", "miconic",
                   "depots", "rovers", "visitall"]
    target_domains = [args.domain] if args.domain else all_domains

    for dom in target_domains:
        if dom in GENERATORS:
            GENERATORS[dom](domains_root, args.overwrite, args.dry_run)
        else:
            check_existing(domains_root, dom)

    print("\nDone.")


if __name__ == "__main__":
    main()
