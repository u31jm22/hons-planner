#!/bin/bash -l
#SBATCH --job-name=llm_fix
#SBATCH --nodes=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --ntasks-per-node=1
#SBATCH --partition=compute
#SBATCH --time=02:00:00
#SBATCH --output=logs/llm_fix_%j.out
#SBATCH --error=logs/llm_fix_%j.err

echo "Started LLM fix on $(hostname)"
date

cd ~/hons-llm-heuristics
module load python/3.11.7
source venv/bin/activate

# Domains you still need; start with gripper and depots
for domain in gripper depots; do
  echo "Running $domain llm-selected gpt-4o-mini (p06–p10)..."
  python -m planner.run_grid \
    --domain "$domain" \
    --mode llm-selected \
    --model gpt-4o-mini \
    --instances-file test_instances.txt \
    --output-csv "results/${domain}_gpt-4o-mini_llm_test.csv"
done

echo "LLM fix completed"
date

