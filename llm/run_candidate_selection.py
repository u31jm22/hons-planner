#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

from llm.model_wrapper import OpenAIModel
from llm.candidate_pipeline import CandidatePipeline


def load_instance_list(domain_dir: Path, fname: str) -> list[str]:
    path = domain_dir / fname
    with path.open() as f:
        return [line.strip() for line in f if line.strip()]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--domain", required=True, help="Domain name, e.g. blocksworld")
    parser.add_argument("--model", required=True, help="Model ID, e.g. gpt-4o-mini")
    parser.add_argument("--num-candidates", type=int, default=5)
    parser.add_argument(
        "--train-instances-file",
        default="train_instances.txt",
        help="Relative file in domains/<domain>/ listing training problems",
    )
    parser.add_argument("--api-key", default=None)
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[1]
    domains_dir = project_root / "domains"

    model = OpenAIModel(api_key=args.api_key, model=args.model, temperature=0.2)
    pipeline = CandidatePipeline(model=model, project_root=project_root)

    # 1) Generate candidates
    candidates = pipeline.generate_candidates(
        domain_name=args.domain,
        num_candidates=args.num_candidates,
    )

    # 2) Evaluate candidates on train instances
    train_problems = load_instance_list(
        domains_dir / args.domain,
        args.train_instances_file,
    )
    eval_results = []
    for cand in candidates:
        res = pipeline.evaluate_candidate(cand, training_problems=train_problems)
        eval_results.append(res)

    # 3) Select best and save JSON
    best = pipeline.select_best_candidate(args.domain, eval_results)
    if best is None:
        print("No valid candidates.")
        return 1

    out_path = project_root / "llm" / "candidates" / f"{args.domain}_selected.json"
    out_path.write_text(json.dumps(best, indent=2))
    print(f"Saved best candidate summary to {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
