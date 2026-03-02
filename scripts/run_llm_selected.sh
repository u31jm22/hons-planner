#!/bin/bash -l
#SBATCH --job-name=llm_selected
#SBATCH --nodes=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --ntasks-per-node=1
#SBATCH --time=02:00:00
#SBATCH --output=logs/llm_selected_%j.out
#SBATCH --error=logs/llm_selected_%j.err

echo "Started running on $(hostname)"
date

cd ~/hons-llm-heuristics

module load python/3.11.7
source venv/bin/activate

for domain in gripper blocksworld logistics miconic; do
  echo "Running $domain llm-selected..."
  python -m planner.run_grid \
    --domain $domain \
    --mode llm-selected \
    --model gpt-4o-mini \
    --instances-file test_instances.txt \
    --output-csv results/${domain}_gpt-4o-mini_llm_test.csv
done

echo "Execution Completed!"
