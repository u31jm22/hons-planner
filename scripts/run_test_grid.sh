#!/bin/bash -l
#SBATCH --job-name=test_grid
#SBATCH --nodes=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --ntasks-per-node=1
#SBATCH --partition=compute
#SBATCH --time=02:00:00
#SBATCH --output=logs/test_grid_%j.out
#SBATCH --error=logs/test_grid_%j.err

echo "Started running on $(hostname)"
date

cd ~/hons-llm-heuristics

module load python/3.11.7
source venv/bin/activate

for domain in gripper blocksworld logistics miconic; do
  for h in ff max add; do
    echo "Running $domain baseline=$h (p06–p10)..."
    python -m planner.run_grid \
      --domain "$domain" \
      --mode baseline \
      --baseline "$h" \
      --instances-file test_instances.txt \
      --output-csv "results/${domain}_${h}_test.csv"
  done

  echo "Running $domain llm-selected gpt-4o-mini (p06–p10)..."
  python -m planner.run_grid \
    --domain "$domain" \
    --mode llm-selected \
    --model gpt-4o-mini \
    --instances-file test_instances.txt \
    --output-csv "results/${domain}_gpt-4o-mini_llm_test.csv"
done

echo "Execution Completed!"
