#!/bin/bash
#SBATCH --job-name=gripper_depots_grid
#SBATCH --output=logs/gripper_depots_grid_%j.out
#SBATCH --error=logs/gripper_depots_grid_%j.err
#SBATCH --time=02:00:00
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G

set -euo pipefail

cd ~/hons-llm-heuristics

# Activate venv (adjust this if your venv path is different on MacLeod)
source venv/bin/activate

mkdir -p logs results

# Gripper: ff baseline + LLM-selected
python -m planner.run_grid \
  --domain gripper \
  --mode baseline \
  --baseline ff \
  --instances-file test_instances.txt \
  --output-csv results/gripper_ff_test.csv

python -m planner.run_grid \
  --domain gripper \
  --mode llm-selected \
  --model gpt-4o-mini \
  --instances-file test_instances.txt \
  --output-csv results/gripper_gpt-4o-mini_llm_test.csv

# Depots: max/add/ff baselines + LLM-selected
python -m planner.run_grid \
  --domain depots \
  --mode baseline \
  --baseline max \
  --instances-file test_instances.txt \
  --output-csv results/depots_max_test.csv

python -m planner.run_grid \
  --domain depots \
  --mode baseline \
  --baseline add \
  --instances-file test_instances.txt \
  --output-csv results/depots_add_test.csv

python -m planner.run_grid \
  --domain depots \
  --mode baseline \
  --baseline ff \
  --instances-file test_instances.txt \
  --output-csv results/depots_ff_test.csv

python -m planner.run_grid \
  --domain depots \
  --mode llm-selected \
  --model gpt-4o-mini \
  --instances-file test_instances.txt \
  --output-csv results/depots_gpt-4o-mini_llm_test.csv

