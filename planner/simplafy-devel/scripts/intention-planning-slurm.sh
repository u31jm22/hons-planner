#!/bin/bash -l

## We need to submit this using the logged in options because otherwise I cannot access pre-configured conda environments
## Don't forget to run this script with sbatch

#SBATCH --nodes=1                 # number of nodes (ideally this gets me better cache efficiency)
#SBATCH --ntasks=1               # total number of parallel tasks you want to run (maxwell seems to have a problem with this)
#SBATCH --cpus-per-task=1         # 1 CPU per task
#SBATCH --mem-per-cpu=48G         # memory per CPU
#SBATCH --partition=uoa-compute 

#SBATCH --mail-type=ALL
#SBATCH --mail-user=felipe.meneguzzi@abdn.ac.uk  # gets username from hpc env login (change as appropriate)

module load miniconda3

echo "Started running on $(hostname)"
date

pwd
conda info --envs
conda activate simplafy

echo $CONDA_DEFAULT_ENV
echo $CONDA_PREFIX

echo "${@:1}"

srun python3 -m pddl.run_benchmark "${@:1}" &

wait