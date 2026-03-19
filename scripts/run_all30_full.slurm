#!/bin/bash -l
#SBATCH --job-name=all30_full
#SBATCH --nodes=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=16G
#SBATCH --ntasks-per-node=1
#SBATCH --partition=compute
#SBATCH --time=24:00:00
#SBATCH --output=logs/all30_full_%j.out
#SBATCH --error=logs/all30_full_%j.err

# ============================================================
# scripts/run_all30_full.slurm
#
# Runs the complete 30-instance grid for ALL (domain, model,
# heuristic) combinations required for the thesis.
#
# Submit with:
#   sbatch scripts/run_all30_full.slurm
#
# Results are written to results/<domain>_<method>_all30.csv
# Only missing CSVs are run — existing ones are skipped.
# ============================================================

set -euo pipefail

echo "=============================="
echo "all30_full started on $(hostname)"
date
echo "=============================="

cd ~/hons-llm-heuristics
mkdir -p logs results

module load python/3.11.7
source venv/bin/activate

echo "Python: $(which python)"
echo "Venv active: $VIRTUAL_ENV"
echo ""

# ---- Config -------------------------------------------------------
DOMAINS="blocksworld gripper logistics miconic depots rovers"
LLM_MODELS="gpt-4o-mini gpt-4.1-mini gpt-4.1 llama"
BASELINES="ff add max"
TIMEOUT=300   # seconds per problem

# LLaMA: LM Studio must be running locally with a tunnelled port.
# If you are running on MacLeod without a local LM Studio server,
# comment out 'llama' from LLM_MODELS above and add it separately
# when running locally.

# ---- Helper: skip if CSV already has ≥30 rows --------------------
needs_run() {
    local csv_path="$1"
    if [ ! -f "$csv_path" ]; then return 0; fi
    local rows
    rows=$(tail -n +2 "$csv_path" | wc -l)
    if [ "$rows" -lt 30 ]; then
        echo "  [INCOMPLETE: $rows rows] Re-running $csv_path"
        return 0
    fi
    echo "  [SKIP] $csv_path already has $rows rows"
    return 1
}

# ---- 1. Classical baselines (ff, add, max) -----------------------
echo ""
echo "=== Classical baselines ==="
for domain in $DOMAINS; do
    for h in $BASELINES; do
        out="results/${domain}_${h}_all30.csv"
        if needs_run "$out"; then
            echo "Running: domain=$domain baseline=$h -> $out"
            python -m planner.run_grid \
                --domain "$domain" \
                --mode baseline \
                --baseline "$h" \
                --instances-file all_instances.txt \
                --output-csv "$out"
        fi
    done
done

# ---- 2. LLM heuristics -------------------------------------------
echo ""
echo "=== LLM heuristics ==="
for domain in $DOMAINS; do
    for model in $LLM_MODELS; do
        # Check selected candidate JSON exists
        sel_json="llm/candidates/${domain}_selected_${model}.json"
        if [ ! -f "$sel_json" ]; then
            echo "  [SKIP] $sel_json not found — skipping ${domain}/${model}"
            continue
        fi

        out="results/${domain}_${model}_llm_all30.csv"
        if needs_run "$out"; then
            echo "Running: domain=$domain model=$model -> $out"
            python -m planner.run_grid \
                --domain "$domain" \
                --mode llm-selected \
                --model "$model" \
                --instances-file all_instances.txt \
                --output-csv "$out"
        fi
    done
done

# ---- 3. Summary --------------------------------------------------
echo ""
echo "=== Generating summary ==="
python analysis/aggregate_all30.py

echo ""
echo "=============================="
echo "all30_full completed"
date
echo "=============================="
