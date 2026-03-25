#!/usr/bin/env python3
"""
scripts/run_candidate_pipeline_all.py
--------------------------------------
Master script that runs the full LLM candidate generation + selection pipeline
for every combination of domain × model.

Domains (6):
  blocksworld, gripper, logistics, miconic, depots, rovers, visitall

Models (4):
  gpt-4o-mini, gpt-4.1-mini, gpt-4.1, llama

Each (domain, model) pair calls:
  python llm/run_candidate_pipeline.py <domain> --model-name <model>

On success, this writes:
  llm/candidates/<domain>_selected_<model>.json
  llm/candidates/<domain>_candidate_N.py  (if new candidates were generated)

Usage
-----
  # Run everything (24 combos):
  python scripts/run_candidate_pipeline_all.py

  # Single domain:
  python scripts/run_candidate_pipeline_all.py --domain blocksworld

  # Single model:
  python scripts/run_candidate_pipeline_all.py --model gpt-4.1-mini

  # Skip LLaMA (needs LM Studio running locally):
  python scripts/run_candidate_pipeline_all.py --skip-llama

  # Force re-run even if selected JSON already exists:
  python scripts/run_candidate_pipeline_all.py --force

  # Dry run — print what would be executed:
  python scripts/run_candidate_pipeline_all.py --dry-run

Environment variables
---------------------
  OPENAI_API_KEY      required for gpt-* models
  LMSTUDIO_BASE_URL   optional override (default: http://localhost:1234/v1)
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from datetime import datetime

# ── Project layout ───────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parents[1]
CANDIDATES_DIR = PROJECT_ROOT / "llm" / "candidates"
PIPELINE_SCRIPT = PROJECT_ROOT / "llm" / "run_candidate_pipeline.py"

DOMAINS = [
    "blocksworld",
    "gripper",
    "logistics",
    "miconic",
    "depots",
    "rovers",
    "visitall",
]

MODELS = [
    "gpt-4o-mini",
    "gpt-4.1-mini",
    "gpt-4.1",
    "llama",
]

LLAMA_MODELS = {"llama"}


def selected_json_path(domain: str, model: str) -> Path:
    return CANDIDATES_DIR / f"{domain}_selected_{model}.json"


def already_done(domain: str, model: str) -> bool:
    """Return True if a valid (non-stub) selected JSON exists for this pair."""
    p = selected_json_path(domain, model)
    if not p.exists():
        return False
    try:
        data = json.loads(p.read_text())
        # A stub has no real candidate — check that the .py file exists
        cand_id = data.get("candidate_id", "")
        if not cand_id:
            return False
        cand_py = CANDIDATES_DIR / f"{cand_id}.py"
        return cand_py.exists()
    except Exception:
        return False


def run_pipeline(domain: str, model: str, dry_run: bool, extra_env: dict) -> bool:
    """
    Invoke llm/run_candidate_pipeline.py for one (domain, model) pair.
    Returns True on success, False on failure.
    """
    cmd = [
        sys.executable,
        str(PIPELINE_SCRIPT),
        domain,
        "--model-name", model,
    ]
    label = f"{domain} / {model}"
    print(f"\n{'='*60}")
    print(f"  Running pipeline: {label}")
    print(f"  Command: {' '.join(cmd)}")
    print(f"{'='*60}")

    if dry_run:
        print("  [DRY RUN] Skipping execution.")
        return True

    env = os.environ.copy()
    env.update(extra_env)

    try:
        result = subprocess.run(
            cmd,
            cwd=str(PROJECT_ROOT),
            env=env,
            timeout=3600,  # 1 hour max per run
        )
        if result.returncode == 0:
            print(f"  ✓ {label} — pipeline completed successfully.")
            return True
        else:
            print(f"  ✗ {label} — pipeline exited with code {result.returncode}.")
            return False
    except subprocess.TimeoutExpired:
        print(f"  ✗ {label} — pipeline TIMED OUT (>1h).")
        return False
    except Exception as e:
        print(f"  ✗ {label} — unexpected error: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Run candidate pipeline for all domain × model combos."
    )
    parser.add_argument(
        "--domain", choices=DOMAINS,
        help="Restrict to a single domain."
    )
    parser.add_argument(
        "--model", choices=MODELS,
        help="Restrict to a single model."
    )
    parser.add_argument(
        "--skip-llama", action="store_true",
        help="Skip the LLaMA model (requires LM Studio to be running locally)."
    )
    parser.add_argument(
        "--force", action="store_true",
        help="Re-run even if selected JSON already exists."
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print what would be run without executing."
    )
    parser.add_argument(
        "--lmstudio-url", default="http://localhost:1234/v1",
        help="Base URL for LM Studio server (default: http://localhost:1234/v1)."
    )
    args = parser.parse_args()

    domains = [args.domain] if args.domain else DOMAINS
    models = [args.model] if args.model else MODELS
    if args.skip_llama:
        models = [m for m in models if m not in LLAMA_MODELS]

    extra_env = {
        "LMSTUDIO_BASE_URL": args.lmstudio_url,
    }

    combos = [(d, m) for d in domains for m in models]
    total = len(combos)

    print(f"\nCandidate pipeline — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Domains : {domains}")
    print(f"Models  : {models}")
    print(f"Combos  : {total}")
    print(f"Force   : {args.force}")
    print(f"Dry run : {args.dry_run}")

    results = {}
    skipped = 0
    success = 0
    failed = 0

    for i, (domain, model) in enumerate(combos, 1):
        label = f"{domain}/{model}"
        print(f"\n[{i}/{total}] {label}")

        # Skip if already done (unless --force)
        if not args.force and already_done(domain, model):
            print(f"  → Already done (use --force to re-run). Skipping.")
            results[label] = "skipped"
            skipped += 1
            continue

        ok = run_pipeline(domain, model, args.dry_run, extra_env)
        if ok:
            results[label] = "success"
            success += 1
        else:
            results[label] = "failed"
            failed += 1

    # Summary
    print(f"\n{'='*60}")
    print(f"SUMMARY — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")
    print(f"  Total   : {total}")
    print(f"  Success : {success}")
    print(f"  Skipped : {skipped}")
    print(f"  Failed  : {failed}")
    if failed:
        print("\n  Failed combos:")
        for label, status in results.items():
            if status == "failed":
                print(f"    ✗ {label}")
    print()

    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
