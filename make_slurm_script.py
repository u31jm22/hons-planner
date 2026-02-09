content = """#!/bin/bash -l

## Submit with: sbatch run_baselines_slurm.sh

#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=32G
#SBATCH --partition=uoa-compute

#SBATCH --mail-type=ALL
#SBATCH --mail-user=j.mccolgan.22@abdn.ac.uk

module load miniconda3

echo "Started running on $(hostname)"
date
pwd

conda info --envs
conda activate hons-llm-heuristics   # TODO: change to your actual env name on MacLeod

echo "Conda env: $CONDA_DEFAULT_ENV"
echo "Prefix: $CONDA_PREFIX"

echo "Running baselines..."

# TODO: adjust these to match your scripts
bash scripts/run_blocksworld_baseline.sh max all
bash scripts/run_blocksworld_baseline.sh add all
bash scripts/run_blocksworld_baseline.sh ff  all

bash scripts/run_logistics_baseline.sh max all
bash scripts/run_logistics_baseline.sh add all
bash scripts/run_logistics_baseline.sh ff  all

echo "Done."
date
"""

with open("run_baselines_slurm.sh", "w") as f:
    f.write(content)

