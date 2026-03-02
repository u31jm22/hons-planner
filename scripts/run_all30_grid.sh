#!/bin/bash -l
#SBATCH --job-name=all30_grid
#SBATCH --nodes=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=8G
#SBATCH --ntasks-per-node=1
#SBATCH --partition=compute
#SBATCH --time=08:00:00
#SBATCH --output=logs/all30_grid_%j.out
#SBATCH --error=logs/all30_grid_%j.err

echo "Started all30_grid on $(hostname)"
date

cd ~/hons-llm-heuristics

module load python/3.11.7
source venv/bin/activate

for domain in gripper blocksworld logistics miconic; do

  echo "=== $domain: baselines (all 30) ==="
  for h in ff max add; do
    echo "Running $domain baseline=$h (all 30)..."
    python -m planner.run_grid \
      --domain $domain \
      --mode baseline \
      --baseline "$h" \
      --instances-file all_instances.txt \
      --output-csv results/${domain}_${h}_all30.csv
  done

  echo "=== $domain: LLM gpt-4.1-mini (all 30) ==="
  python -m planner.run_grid \
    --domain $domain \
    --mode llm-selected \
    --model gpt-4.1-mini \
    --instances-file all_instances.txt \
    --output-csv results/${domain}_gpt-4.1-mini_llm_all30.csv

done

echo "all30_grid completed"
date
