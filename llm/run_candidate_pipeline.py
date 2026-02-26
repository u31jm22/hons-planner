#!/usr/bin/env python3
"""
Run the complete candidate generation and selection pipeline for a domain.
"""

import sys
import os
import json
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from llm.candidate_pipeline_new import CandidatePipeline
from llm.model_wrapper import OpenAIModel


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("domain_name", help="PDDL domain name (e.g. gripper, depots, blocksworld, logistics)")
    parser.add_argument(
        "--model-name",
        default="gpt-4o-mini",
        help="LLM model identifier (e.g. gpt-4o-mini, gpt-4.1-mini)",
    )
    args = parser.parse_args()

    domain_name = args.domain_name
    model_name = args.model_name

    # Get OpenAI key
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: OPENAI_API_KEY environment variable not set")
        return 1

    # Initialize model and pipeline
    print(f"Using LLM model: {model_name}")
    model = OpenAIModel(api_key=api_key, model=model_name, temperature=0.0)
    pipeline = CandidatePipeline(model=model, project_root=project_root)

    # Training problems p01–p05
    training_problems = ["p01.pddl", "p02.pddl", "p03.pddl"]

    print(f"\n=== Generating candidates for {domain_name} ({model_name}) ===\n")
    candidates = pipeline.generate_candidates(domain_name, num_candidates=5)

    print(f"\n=== Evaluating candidates on training set ===\n")
    evaluation_results = []
    for candidate in candidates:
        print(f"\nEvaluating {candidate['id']}...")
        result = pipeline.evaluate_candidate(candidate, training_problems)
        evaluation_results.append(result)

        print(f"  Coverage: {result['coverage']}/{len(training_problems)}")
        if result["coverage"] > 0:
            print(f"  Avg Expansions: {result['avg_expansions']:.1f}")
            print(f"  Avg Time: {result['avg_time']:.3f}s")

    print(f"\n=== Selecting best candidate for {domain_name} ({model_name}) ===\n")
    best = pipeline.select_best_candidate(domain_name, evaluation_results, model_name=model_name)
    if best is None:
        print("No candidates produced any solution on the training set.")
        return 1

    # Save selection, model-tagged
    selection_dir = project_root / "llm" / "candidates"
    selection_dir.mkdir(exist_ok=True)
    selection_file = selection_dir / f"{domain_name}_selected_{model_name}.json"
    with selection_file.open("w") as f:
        json.dump(best, f, indent=2)

    print(f"\nSaved selection to {selection_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
