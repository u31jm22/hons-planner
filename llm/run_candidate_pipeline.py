#!/usr/bin/env python3
"""
Run the complete candidate generation and selection pipeline for a domain.
"""
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from llm.candidate_pipeline import CandidatePipeline
from llm.model_wrapper import OpenAIModel


def main():
    if len(sys.argv) < 2:
        print("Usage: python run_candidate_pipeline.py <domain_name>")
        print("Example: python run_candidate_pipeline.py gripper")
        return 1
    
    domain_name = sys.argv[1]
    
    # Get OpenAI key
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: OPENAI_API_KEY environment variable not set")
        return 1
    
    # Initialize model and pipeline
    model = OpenAIModel(api_key=api_key, model="gpt-3.5-turbo", temperature=0.7)
    pipeline = CandidatePipeline(model=model, project_root=project_root)
    
    # Define training problems (p01-p03)
    training_problems = ["p01.pddl", "p02.pddl", "p03.pddl"]
    
    print(f"\n=== Generating candidates for {domain_name} ===\n")
    
    # Generate 5 candidates
    candidates = pipeline.generate_candidates(domain_name, num_candidates=5)
    
    print(f"\n=== Evaluating candidates on training set ===\n")
    
    # Evaluate each candidate
    evaluation_results = []
    for candidate in candidates:
        print(f"\nEvaluating {candidate['id']}...")
        result = pipeline.evaluate_candidate(candidate, training_problems)
        evaluation_results.append(result)
        
        print(f"  Coverage: {result['coverage']}/{len(training_problems)}")
        if result['coverage'] > 0:
            print(f"  Avg Expansions: {result['avg_expansions']:.1f}")
            print(f"  Avg Time: {result['avg_time']:.3f}s")
    
    # Select best candidate
    print(f"\n=== Selecting best candidate ===\n")
    best = pipeline.select_best_candidate(domain_name, evaluation_results)
    
    # Save selection
    import json
    selection_file = project_root / "llm" / "candidates" / f"{domain_name}_selected.json"
    with open(selection_file, 'w') as f:
        json.dump(best, f, indent=2)
    
    print(f"\nSaved selection to {selection_file}")
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
