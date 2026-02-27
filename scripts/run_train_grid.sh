#!/bin/bash -l
#SBATCH --job-name=train_grid
#SBATCH --nodes=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --ntasks-per-node=1
#SBATCH --partition=compute
#SBATCH --time=02:00:00
#SBATCH --output=logs/train_grid_%j.out
#SBATCH --error=logs/train_grid_%j.err

echo "Started train_grid on $(hostname)"
date

cd ~/hons-llm-heuristics

module load python/3.11.7
source venv/bin/activate

for domain in gripper depots blocksworld logistics; do
  # Baselines: ff, max, add for p01–p05
  for h in ff max add; do
    echo "Running $domain baseline=$h (p01–p05)..."
    python -m planner.run_grid \
      --domain "$domain" \
      --mode baseline \
      --baseline "$h" \
      --instances-file train_instances.txt \
      --output-csv "results/${domain}_${h}_train.csv"
  done

  # LLM-selected gpt-4o-mini for p01–p05
  echo "Running $domain llm-selected gpt-4o-mini (p01–p05)..."
  python -m planner.run_grid \
    --domain "$domain" \
    --mode llm-selected \
    --model gpt-4o-mini \
    --instances-file train_instances.txt \
    --output-csv "results/${domain}_gpt-4o-mini_llm_train.csv"
done

echo "train_grid completed"
date
