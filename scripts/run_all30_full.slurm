#!/bin/bash -l
#SBATCH --job-name=all30_full
#SBATCH --nodes=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=16G
#SBATCH --ntasks-per-node=1
#SBATCH --partition=compute
#SBATCH --time=48:00:00
#SBATCH --output=logs/all30_full_%j.out
#SBATCH --error=logs/all30_full_%j.err
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=j.mccolgan.22@abdn.ac.uk

# ============================================================
# scripts/run_all30_full.slurm
#
# Runs the complete 30-instance grid for ALL (domain, model,
# heuristic) combinations required for the thesis.
#
# Domains (7): blocksworld gripper logistics miconic depots rovers visitall
# Baselines (3): ff add max
# LLM models (4): gpt-4o-mini gpt-4.1-mini gpt-4.1 llama
#
# Submit with:
#   sbatch scripts/run_all30_full.slurm
#
# Results are written to results/<domain>_<method>_all30.csv
# Only missing/incomplete CSVs are run — existing ones are skipped.
#
# NOTE: The 'llama' model requires LM Studio to be running and
# accessible.  On MacLeod, run llama experiments separately on
# your local Mac via:
#   python -m planner.run_grid --domain <d> --mode llm-selected \
#     --model llama --instances-file all_instances.txt \
#     --output-csv results/<d>_llama_llm_all30.csv
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
DOMAINS="blocksworld gripper logistics miconic depots rovers visitall"
# NOTE: Remove 'llama' below if running on MacLeod without LM Studio tunnel
LLM_MODELS="gpt-4o-mini gpt-4.1-mini gpt-4.1"
BASELINES="ff add max"
TIMEOUT=300   # seconds per problem (handled inside run_grid.py)

# ---- Helper: skip if CSV already has ≥30 rows --------------------
needs_run() {
    local csv_path="$1"
    local expected_rows="${2:-30}"
    if [ ! -f "$csv_path" ]; then return 0; fi
    local rows
    rows=$(tail -n +2 "$csv_path" | wc -l)
    if [ "$rows" -lt "$expected_rows" ]; then
        echo "  [INCOMPLETE: $rows/$expected_rows rows] Re-running $csv_path"
        return 0
    fi
    echo "  [SKIP] $csv_path already complete ($rows rows)"
    return 1
}

# How many instances per domain
domain_count() {
    local domain="$1"
    local f="domains/${domain}/all_instances.txt"
    if [ -f "$f" ]; then
        wc -l < "$f" | tr -d ' '
    else
        echo 30
    fi
}

# ---- 1. Classical baselines (ff, add, max) -----------------------
echo ""
echo "=== Classical baselines (ff, add, max) ==="
for domain in $DOMAINS; do
    n=$(domain_count "$domain")
    for h in $BASELINES; do
        out="results/${domain}_${h}_all30.csv"
        if needs_run "$out" "$n"; then
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

# ---- 2. LLM heuristics (OpenAI models) ---------------------------
echo ""
echo "=== LLM heuristics (gpt-4o-mini, gpt-4.1-mini, gpt-4.1) ==="
for domain in $DOMAINS; do
    n=$(domain_count "$domain")
    for model in $LLM_MODELS; do
        # Check selected candidate JSON exists
        sel_json="llm/candidates/${domain}_selected_${model}.json"
        if [ ! -f "$sel_json" ]; then
            echo "  [SKIP] $sel_json not found — skipping ${domain}/${model}"
            continue
        fi

        out="results/${domain}_${model}_llm_all30.csv"
        if needs_run "$out" "$n"; then
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

# ---- 3. LLaMA (local only — skipped on HPC by default) -----------
# Uncomment the block below only if LM Studio is tunnelled to MacLeod.
# Otherwise run this separately on your local Mac.
#
# echo ""
# echo "=== LLM heuristics (llama via LM Studio) ==="
# for domain in $DOMAINS; do
#     n=$(domain_count "$domain")
#     sel_json="llm/candidates/${domain}_selected_llama.json"
#     if [ ! -f "$sel_json" ]; then
#         echo "  [SKIP] $sel_json not found"
#         continue
#     fi
#     out="results/${domain}_llama_llm_all30.csv"
#     if needs_run "$out" "$n"; then
#         echo "Running: domain=$domain model=llama -> $out"
#         LMSTUDIO_BASE_URL="http://localhost:1234/v1" \
#         python -m planner.run_grid \
#             --domain "$domain" \
#             --mode llm-selected \
#             --model llama \
#             --instances-file all_instances.txt \
#             --output-csv "$out"
#     fi
# done

# ---- 4. Aggregate results ----------------------------------------
echo ""
echo "=== Generating summary ==="
python analysis/aggregate_all30.py

echo ""
echo "=============================="
echo "all30_full completed"
date
echo "=============================="
