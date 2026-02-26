import argparse
import os
from llm.candidate_pipeline import CandidatePipeline
from llm.correa_prompt import CORREA_DEPOTS_PROMPT, GRIPPER_PROMPT


def build_prompt(domain_name):
    """
    Correa-style prompts for Depots and Gripper only.
    """
    if domain_name == "depots":
        return CORREA_DEPOTS_PROMPT
    elif domain_name == "gripper":
        return GRIPPER_PROMPT
    else:
        raise ValueError(f"Correa pipeline only supports depots and gripper, got {domain_name}")


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "domain",
        help="Domain name, expected 'depots' or 'gripper' for Correa-style prompts.",
    )
    parser.add_argument(
        "--model-name",
        type=str,
        default="gpt-4.1-mini",
        help="LLM model name identifier (stored in selection JSON).",
    )
    args = parser.parse_args(argv)

    domain_name = args.domain
    model_name = args.model_name

    print(f"Using LLM model: {model_name}\n")

    # Paths (mirror the original run_candidate_pipeline.py)
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    domains_dir = os.path.join(repo_root, "domains", domain_name)
    domain_pddl = os.path.join(domains_dir, "domain.pddl")
    train_instances = [os.path.join(domains_dir, f"p0{i}.pddl") for i in range(1, 6)]

    candidates_dir = os.path.join(repo_root, "llm", "candidates")
    os.makedirs(candidates_dir, exist_ok=True)
    candidates_json = os.path.join(candidates_dir, f"{domain_name}_candidates_correa.json")
    selection_json = os.path.join(
        candidates_dir, f"{domain_name}_selected_correa_{model_name}.json"
    )

    # Choose Correa-style prompt for this domain
    prompt_template = build_prompt(domain_name)

    pipeline = CandidatePipeline(
        domain_name=domain_name,
        domain_pddl=domain_pddl,
        train_instances=train_instances,
        candidates_path=candidates_json,
        selection_path=selection_json,
        model_name=model_name,
        prompt_template=prompt_template,
    )

    print(f"=== Generating Correa-style candidates for {domain_name} ({model_name}) ===\n")
    pipeline.generate_candidates(num_candidates=5)

    print(f"\n=== Evaluating candidates on training set ===\n")
    evaluation_results = pipeline.evaluate_candidates(timeout_seconds=90)

    print(f"\n=== Selecting best candidate for {domain_name} ({model_name}) ===\n")
    best = pipeline.select_best_candidate(domain_name, evaluation_results, model_name=model_name)
    if best is None:
        print("No successful candidates to select from.")
        return 1

    pipeline.save_selection(best)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
