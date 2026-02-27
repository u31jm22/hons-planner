#!/bin/bash -l
#SBATCH --job-name=llm_41mini
#SBATCH --nodes=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --ntasks-per-node=1
#SBATCH --time=04:00:00
#SBATCH --output=logs/llm_41mini_%j.out
#SBATCH --error=logs/llm_41mini_%j.err

echo "Started running on $(hostname)"
date

cd ~/hons-llm-heuristics

module load python/3.11.7
source venv/bin/activate

for domain in gripper depots blocksworld logistics; do
  echo "Running $domain llm-selected gpt-4.1-mini train..."
  python -m planner.run_grid \
    --domain $domain \
    --mode llm-selected \
    --model gpt-4.1-mini \
    --instances-file train_instances.txt \
    --output-csv results/${domain}_gpt-4.1-mini_llm_train.csv

  echo "Running $domain llm-selected gpt-4.1-mini test..."
  python -m planner.run_grid \
    --domain $domain \
    --mode llm-selected \
    --model gpt-4.1-mini \
    --instances-file test_instances.txt \
    --output-csv results/${domain}_gpt-4.1-mini_llm_test.csv
done

echo "Execution Completed!"
date
